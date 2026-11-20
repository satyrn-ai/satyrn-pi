// Document budget checks. Filesystem reads only: no model, network or subprocess.
import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { BUDGET } from "../scripts/doc-budgets.mjs";
import { checkCaps, collectDocuments, countLines, fencedShare } from "../scripts/doc-checks.mjs";

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const lines = (n) => Array.from({ length: n }, (_, i) => `line ${i + 1}`).join("\n");
const specText = (n, briefLines = 10) =>
  `# Spec\n\n## Reviewer brief\n${lines(briefLines)}\n\n## Body\n${lines(n)}`;

test("BUDGET holds the agreed numbers", () => {
  assert.deepEqual({ ...BUDGET }, {
    spec: 150,
    plan: 250,
    brief: 30,
    agents: 80,
    roadmap: 400,
    ships: 900,
    excludes: 900,
    status: 1000,
    backlogEntry: 1200,
    planFenced: 0.25,
    glossary: 25,
  });
});

test("countLines matches wc -l and fencedShare counts fence bodies", () => {
  assert.equal(countLines("a\nb\n"), 2);
  assert.equal(countLines("a\nb"), 2);
  assert.equal(fencedShare("a\n```\nb\n```\nc\n"), 1 / 5);
});

test("every repository document fits its budget", async () => {
  const docs = await collectDocuments(repoRoot);
  const findings = [
    ...docs.specs.map((d) => ({ ...d, kind: "spec" })),
    ...docs.plans.map((d) => ({ ...d, kind: "plan" })),
    docs.agents && { ...docs.agents, kind: "agents" },
    docs.roadmap && { ...docs.roadmap, kind: "roadmap" },
    docs.backlog && { ...docs.backlog, kind: "backlog" },
  ]
    .filter(Boolean)
    .flatMap((doc) => checkCaps(doc, BUDGET));
  assert.deepEqual(findings, [], JSON.stringify(findings, null, 2));
});

test("AGENTS.md states the four budget numbers", async () => {
  const text = await readFile(path.join(repoRoot, "AGENTS.md"), "utf8");
  const section = text.match(/^## Document budgets\n([\s\S]*?)(?=^## )/m)?.[1] ?? "";
  for (const number of [BUDGET.spec, BUDGET.plan, BUDGET.brief, BUDGET.agents]) {
    assert.match(section, new RegExp(`\\b${number}\\b`), `missing ${number}`);
  }
});

test("a spec over 150 lines or without a brief fails", () => {
  assert.equal(checkCaps({ path: "s.md", text: specText(160), kind: "spec" }, BUDGET).length, 1);
  const noBrief = checkCaps({ path: "s.md", text: `# S\n${lines(10)}`, kind: "spec" }, BUDGET);
  assert.equal(noBrief.length, 1);
  assert.equal(noBrief[0].rule, "spec-brief");
  const longBrief = checkCaps({ path: "s.md", text: specText(10, 31), kind: "spec" }, BUDGET);
  assert.equal(longBrief.length, 1);
  assert.equal(longBrief[0].rule, "spec-brief-length");
  assert.equal(checkCaps({ path: "s.md", text: specText(10, 30), kind: "spec" }, BUDGET).length, 0);
});

test("a plan over 250 lines or over 25% fenced fails", () => {
  assert.equal(checkCaps({ path: "p.md", text: lines(251), kind: "plan" }, BUDGET).length, 1);
  const fenced = `# P\n\n${"```\ncode\n```\n".repeat(20)}${lines(10)}`;
  const findings = checkCaps({ path: "p.md", text: fenced, kind: "plan" }, BUDGET);
  assert.ok(findings.some((f) => f.rule === "plan-fenced"));
});

test("roadmap lines and cells are capped", () => {
  const row = (ships, excludes = "e", status = "s") =>
    `| **P9.9** | ${ships} | ${excludes} | ${status} |`;
  const ok = `# R\n\n${row("s".repeat(900))}\n`;
  assert.equal(checkCaps({ path: "ROADMAP.md", text: ok, kind: "roadmap" }, BUDGET).length, 0);
  const tooWide = `# R\n\n${row("s".repeat(901))}\n`;
  assert.equal(checkCaps({ path: "ROADMAP.md", text: tooWide, kind: "roadmap" }, BUDGET).length, 1);
  const tooLong = `# R\n${lines(400)}\n`;
  assert.ok(checkCaps({ path: "ROADMAP.md", text: tooLong, kind: "roadmap" }, BUDGET).some((f) => f.rule === "roadmap-lines"));
});

test("an empty backlog passes and entries are capped with a reopen condition", () => {
  assert.equal(checkCaps({ path: "BACKLOG.md", text: "# B\n\n## Entries\n\nNone.\n", kind: "backlog" }, BUDGET).length, 0);
  const good = "# B\n\n## Entries\n\n### Item\n\n- **Reopen when:** later\n";
  assert.equal(checkCaps({ path: "BACKLOG.md", text: good, kind: "backlog" }, BUDGET).length, 0);
  const noReopen = "# B\n\n## Entries\n\n### Item\n\n- **Deferred:** now\n";
  assert.ok(checkCaps({ path: "BACKLOG.md", text: noReopen, kind: "backlog" }, BUDGET).some((f) => f.rule === "backlog-reopen"));
  const longEntry = `# B\n\n## Entries\n\n### Item\n\n- **Reopen when:** later\n${"x".repeat(1300)}\n`;
  assert.ok(checkCaps({ path: "BACKLOG.md", text: longEntry, kind: "backlog" }, BUDGET).some((f) => f.rule === "backlog-length"));
});

test("checking does not modify repository files", async () => {
  const before = await readFile(path.join(repoRoot, "AGENTS.md"), "utf8");
  const docs = await collectDocuments(repoRoot);
  docs.specs.forEach((d) => checkCaps({ ...d, kind: "spec" }, BUDGET));
  docs.plans.forEach((d) => checkCaps({ ...d, kind: "plan" }, BUDGET));
  assert.equal(await readFile(path.join(repoRoot, "AGENTS.md"), "utf8"), before);
});
