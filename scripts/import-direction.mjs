// One-way import check: the worker package never imports the eval package, and
// the eval package never imports worker internals. Reports only.
import { existsSync } from "node:fs";
import { readdir, readFile } from "node:fs/promises";
import path from "node:path";

const SKIP = new Set([
  "node_modules",
  ".venv",
  ".git",
  ".superpowers",
  ".agents",
  "docs",
  "tests",
  "scripts",
  "runs",
  "dist",
  "__pycache__",
  ".pytest_cache",
]);

const JS = /\.(?:js|mjs|ts)$/;
const PY = /\.py$/;
const WORKER_ROOTS = new Set(["remedies", "extensions", "worker"]);
const SPECIFIER = /(?:from\s+|require\(\s*|import\(\s*)["']([^"']+)["']/g;

async function walk(dir, root, out, matches) {
  const full = path.join(root, dir);
  if (!existsSync(full)) return;
  for (const entry of await readdir(full, { withFileTypes: true })) {
    const rel = path.posix.join(dir, entry.name);
    if (entry.isDirectory()) {
      if (!SKIP.has(entry.name)) await walk(rel, root, out, matches);
    } else if (matches(entry.name)) {
      out.push({ path: rel, text: await readFile(path.join(root, rel), "utf8") });
    }
  }
}

export async function collectWorkerSources(root) {
  const out = [];
  await walk("", root, out, (name) => JS.test(name));
  return out.sort((a, b) => a.path.localeCompare(b.path));
}

export async function collectEvalSources(root) {
  const out = [];
  await walk("src/satyrn_pi", root, out, (name) => PY.test(name));
  return out.sort((a, b) => a.path.localeCompare(b.path));
}

export function checkWorkerSources(doc) {
  const findings = [];
  doc.text.split("\n").forEach((line, index) => {
    for (const match of line.matchAll(SPECIFIER)) {
      const specifier = match[1];
      if (
        specifier.includes("satyrn_pi") ||
        specifier.includes("src/satyrn_pi") ||
        specifier.endsWith(".py")
      ) {
        findings.push({
          path: doc.path,
          rule: "import-direction",
          line: index + 1,
          message: `worker code must not import the eval package (${specifier})`,
        });
      }
    }
  });
  return findings;
}

export function checkEvalSources(doc) {
  const findings = [];
  doc.text.split("\n").forEach((line, index) => {
    const match = line.match(/^\s*(?:from|import)\s+([A-Za-z0-9_.]+)/);
    if (!match) return;
    const specifier = match[1];
    const root = specifier.split(".")[0];
    if (WORKER_ROOTS.has(root) || /\.(?:js|mjs|ts)$/.test(specifier)) {
      findings.push({
        path: doc.path,
        rule: "import-direction",
        line: index + 1,
        message: `eval code must not import worker internals (${specifier})`,
      });
    }
  });
  return findings;
}
