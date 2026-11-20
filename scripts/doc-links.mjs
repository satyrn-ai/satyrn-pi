// Active documentation links resolve. Reads files only; reports, never edits.
import { existsSync } from "node:fs";
import { readdir, readFile } from "node:fs/promises";
import path from "node:path";
import { scanFences } from "./markdown-fence.mjs";

const EXCLUDE = ["docs/sdd.md", "docs/provenance", "docs/superpowers/plans/archive"];

const excluded = (rel) => EXCLUDE.some((entry) => rel === entry || rel.startsWith(`${entry}/`));

async function walk(dir, root, out) {
  const full = path.join(root, dir);
  if (!existsSync(full)) return;
  for (const entry of await readdir(full, { withFileTypes: true })) {
    const rel = path.posix.join(dir, entry.name);
    if (excluded(rel)) continue;
    if (entry.isDirectory()) await walk(rel, root, out);
    else if (entry.name.endsWith(".md")) {
      out.push({ path: rel, text: await readFile(path.join(root, rel), "utf8") });
    }
  }
}

export async function collectLinkDocuments(root) {
  const out = [];
  for (const entry of await readdir(root, { withFileTypes: true })) {
    if (entry.isFile() && entry.name.endsWith(".md")) {
      out.push({
        path: entry.name,
        text: await readFile(path.join(root, entry.name), "utf8"),
      });
    }
  }
  await walk("docs", root, out);
  return out.sort((a, b) => a.path.localeCompare(b.path));
}

function withoutCode(text) {
  const { inFence } = scanFences(text);
  return text
    .split("\n")
    .map((line, index) => (inFence[index] ? "" : line))
    .join("\n")
    .replace(/`[^`\n]*`/g, "");
}

export function checkLinks(doc, root) {
  const findings = [];
  const base = path.posix.dirname(doc.path);
  const text = withoutCode(doc.text);
  for (const match of text.matchAll(/\]\(([^)]+)\)/g)) {
    const target = match[1].trim().split(/\s+/)[0];
    if (!target || /^(?:https?:|mailto:|#)/.test(target)) continue;
    const clean = target.split("#")[0];
    if (!clean) continue;
    const resolved = path.posix.normalize(path.posix.join(base, clean));
    if (!existsSync(path.join(root, resolved))) {
      findings.push({
        path: doc.path,
        rule: "broken-link",
        message: `${target} does not resolve`,
      });
    }
  }
  return findings;
}
