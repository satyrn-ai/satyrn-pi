#!/usr/bin/env node
// Document gates: caps, plan lifecycle and research-note wording. Pure functions
// over text; the repository scans use the filesystem only (no model, network or
// subprocess). Findings are { path, rule, message } and never edit a document.
import { existsSync } from "node:fs";
import { readdir, readFile } from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { BUDGET, LEGACY_ARCHIVED_WITHOUT_RESULT } from "./doc-budgets.mjs";

export { BUDGET };

export function countLines(text) {
  if (text === "") return 0;
  const body = text.endsWith("\n") ? text.slice(0, -1) : text;
  return body.split("\n").length;
}

export function fencedShare(text) {
  const total = countLines(text);
  if (total === 0) return 0;
  let fenced = 0;
  let inside = false;
  for (const line of text.split("\n")) {
    if (line.startsWith("```")) {
      inside = !inside;
      continue;
    }
    if (inside) fenced += 1;
  }
  return fenced / total;
}

function sectionBody(text, title) {
  const match = text.match(new RegExp(`^## ${title}\\n([\\s\\S]*?)(?=^## |$(?![\\s\\S]))`, "m"));
  return match ? match[1].replace(/\n+$/, "") : null;
}

function finding(doc, rule, message) {
  return { path: doc.path, rule, message };
}

function capFindings(doc, limit, rule, label) {
  const n = countLines(doc.text);
  return n > limit ? [finding(doc, rule, `${label} is ${n} lines, limit ${limit}`)] : [];
}

export function checkCaps(doc, budget = BUDGET) {
  switch (doc.kind) {
    case "spec": {
      const findings = capFindings(doc, budget.spec, "spec-lines", "spec");
      const brief = sectionBody(doc.text, "Reviewer brief");
      if (brief === null) {
        findings.push(finding(doc, "spec-brief", "spec has no ## Reviewer brief"));
      } else if (countLines(brief) > budget.brief) {
        findings.push(
          finding(
            doc,
            "spec-brief-length",
            `reviewer brief is ${countLines(brief)} lines, limit ${budget.brief}`,
          ),
        );
      }
      return findings;
    }
    case "plan": {
      const findings = capFindings(doc, budget.plan, "plan-lines", "plan");
      const share = fencedShare(doc.text);
      if (share > budget.planFenced) {
        findings.push(
          finding(doc, "plan-fenced", `plan is ${Math.round(share * 100)}% fenced, limit 25%`),
        );
      }
      return findings;
    }
    case "agents":
      return capFindings(doc, budget.agents, "agents-lines", "AGENTS.md");
    case "roadmap": {
      const findings = capFindings(doc, budget.roadmap, "roadmap-lines", "ROADMAP.md");
      for (const row of doc.text.split("\n").filter((l) => /^\|\s*\*\*/.test(l))) {
        const [, cycle, ships, excludes, status] = row.split("|").map((c) => c.trim());
        if (ships?.length > budget.ships) {
          findings.push(finding(doc, "roadmap-ships", `${cycle} Ships is ${ships.length} chars`));
        }
        if (excludes?.length > budget.excludes) {
          findings.push(
            finding(doc, "roadmap-excludes", `${cycle} Excludes is ${excludes.length} chars`),
          );
        }
        if (status?.length > budget.status) {
          findings.push(finding(doc, "roadmap-status", `${cycle} Status is ${status.length} chars`));
        }
      }
      return findings;
    }
    case "backlog": {
      const body = doc.text.split(/^## Entries\n/m)[1] ?? "";
      if (body.trim() === "" || /^none\.?$/im.test(body.trim())) return [];
      const findings = [];
      for (const block of body.split(/^### /m).slice(1)) {
        const title = block.split("\n")[0].trim();
        if (block.length > budget.backlogEntry) {
          findings.push(
            finding(doc, "backlog-length", `backlog entry "${title}" is ${block.length} chars`),
          );
        }
        if (!/reopen when/i.test(block)) {
          findings.push(
            finding(doc, "backlog-reopen", `backlog entry "${title}" has no reopen condition`),
          );
        }
      }
      return findings;
    }
    default:
      return [];
  }
}

const PLAN_KEYS = ["phase", "feature_cycle", "cycle", "lifecycle"];
const LIFECYCLES = new Set(["active", "closed", "superseded"]);

export function parseFrontMatter(text) {
  const match = text.match(/^---\n([\s\S]*?)\n---\n/);
  if (!match) return null;
  const fields = {};
  for (const line of match[1].split("\n")) {
    const field = line.match(/^([A-Za-z_]+):\s*(.+?)\s*$/);
    if (field) fields[field[1]] = field[2];
  }
  return fields;
}

export function checkLifecycle(doc) {
  const findings = [];
  const fields = parseFrontMatter(doc.text);
  if (!fields) {
    return [finding(doc, "plan-front-matter", "plan has no front matter")];
  }
  const missing = PLAN_KEYS.filter((key) => !fields[key]);
  if (missing.length > 0) {
    findings.push(
      finding(doc, "plan-front-matter", `front matter missing ${missing.join(", ")}`),
    );
  }
  const state = fields.lifecycle;
  if (state && !LIFECYCLES.has(state)) {
    findings.push(finding(doc, "plan-lifecycle", `unknown lifecycle "${state}"`));
  }
  const headings = [...doc.text.matchAll(/^## (.+)$/gm)].map((m) => m[1].trim());
  if (doc.archived) {
    if (state && state !== "closed" && state !== "superseded") {
      findings.push(finding(doc, "plan-lifecycle", `archived plan has lifecycle "${state}"`));
    }
    const terminal = headings.at(-1) === "Result";
    if (!terminal && !LEGACY_ARCHIVED_WITHOUT_RESULT.includes(doc.path)) {
      findings.push(
        finding(doc, "plan-archive-result", "archived plan has no terminal ## Result"),
      );
    }
  } else {
    if (state && state !== "active") {
      findings.push(finding(doc, "plan-lifecycle", `active plan has lifecycle "${state}"`));
    }
    if (headings.includes("Result")) {
      findings.push(finding(doc, "plan-active-result", "active plan has a ## Result"));
    }
  }
  return findings;
}

export function checkEvidenceWording(doc) {
  const findings = [];
  for (const section of doc.text.split(/^## /m).slice(1)) {
    if (!/\bn\s*=\s*1\b/.test(section)) continue;
    const terms = [...new Set([...section.matchAll(/\b(null|void|separated)\b/gi)].map((m) => m[1].toLowerCase()))];
    if (terms.length > 0) {
      const heading = section.split("\n")[0].trim();
      findings.push(
        finding(
          doc,
          "evidence-wording",
          `section "${heading}" states n = 1 and says ${terms.join(", ")}`,
        ),
      );
    }
  }
  return findings;
}

async function readMarkdown(dir, root) {
  const full = path.join(root, dir);
  if (!existsSync(full)) return [];
  const files = (await readdir(full)).filter((f) => f.endsWith(".md")).sort();
  return Promise.all(
    files.map(async (file) => ({
      path: path.posix.join(dir, file),
      text: await readFile(path.join(full, file), "utf8"),
    })),
  );
}

async function walkMarkdown(dir, root) {
  const full = path.join(root, dir);
  if (!existsSync(full)) return [];
  const out = [];
  for (const entry of await readdir(full, { withFileTypes: true })) {
    const rel = path.posix.join(dir, entry.name);
    if (entry.isDirectory()) out.push(...(await walkMarkdown(rel, root)));
    else if (entry.name.endsWith(".md")) {
      out.push({ path: rel, text: await readFile(path.join(root, rel), "utf8") });
    }
  }
  return out.sort((a, b) => a.path.localeCompare(b.path));
}

async function readTopLevel(name, root) {
  const full = path.join(root, name);
  return existsSync(full) ? { path: name, text: await readFile(full, "utf8") } : null;
}

export async function collectDocuments(root) {
  const specs = await readMarkdown("docs/superpowers/specs", root);
  const active = await readMarkdown("docs/superpowers/plans", root);
  const archived = (await readMarkdown("docs/superpowers/plans/archive", root)).map((doc) => ({
    ...doc,
    archived: true,
  }));
  const plans = [
    ...active.map((doc) => ({ ...doc, archived: false })),
    ...archived,
  ];
  return {
    specs,
    plans,
    research: await walkMarkdown("docs/superpowers/research", root),
    agents: await readTopLevel("AGENTS.md", root),
    roadmap: await readTopLevel("ROADMAP.md", root),
    backlog: await readTopLevel("BACKLOG.md", root),
  };
}

const invokedDirectly =
  process.argv[1] &&
  import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href;

if (invokedDirectly) {
  const root = process.cwd();
  const docs = await collectDocuments(root);
  const findings = [
    ...docs.specs.map((d) => capFor(d, "spec")),
    ...docs.plans.map((d) => capFor(d, "plan")),
    docs.agents && capFor(docs.agents, "agents"),
    docs.roadmap && capFor(docs.roadmap, "roadmap"),
    docs.backlog && capFor(docs.backlog, "backlog"),
  ]
    .filter(Boolean)
    .flat();
  for (const item of findings) console.log(`${item.path}: ${item.rule}: ${item.message}`);
  if (findings.length > 0) process.exitCode = 1;
  else console.log("document checks: no findings");
}

function capFor(doc, kind) {
  return checkCaps({ ...doc, kind });
}
