// Default-test tripwire: no process, network or model dependency may enter the
// default suite. Pure functions over text; collectTestFiles reads the filesystem.
import { readFileSync, existsSync } from "node:fs";
import { readdir } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { findSpecifiers, lineOf, stripJsComments } from "./js-specifiers.mjs";

const RULES_PATH = path.join(path.dirname(fileURLToPath(import.meta.url)), "default-test-rules.json");

export function loadRules(file = RULES_PATH) {
  return JSON.parse(readFileSync(file, "utf8"));
}

export function checkTestText(doc, rules = loadRules()) {
  const findings = [];
  const clean = stripJsComments(doc.text);
  for (const { specifier, index } of findSpecifiers(doc.text)) {
    if (rules.jsModules.includes(specifier.replace(/^node:/, ""))) {
      findings.push({
        path: doc.path,
        rule: "default-test",
        line: lineOf(clean, index),
        message: `default tests must not import ${specifier}`,
      });
    }
  }
  for (const call of rules.jsCalls) {
    const pattern = new RegExp(`(?<![\\w$.])(?:globalThis\\.)?${call}\\s*\\(`, "g");
    for (const match of clean.matchAll(pattern)) {
      findings.push({
        path: doc.path,
        rule: "default-test",
        line: lineOf(clean, match.index),
        message: `default tests must not call ${call}()`,
      });
    }
  }
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
