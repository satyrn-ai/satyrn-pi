// Default-test tripwire: no process, network or model dependency may enter the
// default suite. Pure functions over text; collectTestFiles reads the filesystem.
import { readFileSync } from "node:fs";
import { readdir } from "node:fs/promises";
import { existsSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const RULES_PATH = path.join(path.dirname(fileURLToPath(import.meta.url)), "default-test-rules.json");

export function loadRules(file = RULES_PATH) {
  return JSON.parse(readFileSync(file, "utf8"));
}

const stripComment = (line) => line.replace(/\/\/.*$/, "");

export function checkTestText(doc, rules = loadRules()) {
  const findings = [];
  doc.text.split("\n").forEach((raw, index) => {
    const line = stripComment(raw);
    const lineNumber = index + 1;
    for (const match of line.matchAll(/(?:from\s+|require\(\s*|import\(\s*)["']([^"']+)["']/g)) {
      const specifier = match[1].replace(/^node:/, "");
      if (rules.jsModules.includes(specifier)) {
        findings.push({
          path: doc.path,
          rule: "default-test",
          line: lineNumber,
          message: `default tests must not import ${match[1]}`,
        });
      }
    }
    for (const call of rules.jsCalls) {
      if (new RegExp(`(?:globalThis\\.)?${call}\\s*\\(`).test(line)) {
        findings.push({
          path: doc.path,
          rule: "default-test",
          line: lineNumber,
          message: `default tests must not call ${call}()`,
        });
      }
    }
  });
  return findings;
}

async function walk(dir, root, out) {
  const full = path.join(root, dir);
  if (!existsSync(full)) return;
  for (const entry of await readdir(full, { withFileTypes: true })) {
    const rel = path.posix.join(dir, entry.name);
    if (entry.isDirectory()) await walk(rel, root, out);
    else if (entry.name.endsWith(".mjs")) {
      out.push({ path: rel, text: readFileSync(path.join(root, rel), "utf8") });
    }
  }
}

export async function collectTestFiles(root) {
  const out = [];
  await walk("tests", root, out);
  return out.sort((a, b) => a.path.localeCompare(b.path));
}
