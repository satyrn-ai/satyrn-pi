// Vocabulary checks: retired product terms and the glossary budget. Pure
// functions over text; collectScope reads the filesystem only.
import { existsSync } from "node:fs";
import { readdir, readFile } from "node:fs/promises";
import path from "node:path";
import { BUDGET } from "./doc-budgets.mjs";
import { RETIRED_TERMS, SCOPE_EXCLUDE, SCOPE_INCLUDE } from "./retired-terms.mjs";

const EXEMPTION = /<!--\s*vocabulary:\s*(\S.*?)\s*-->/;
const FENCE = /^ {0,3}(`{3,}|~{3,})(.*)$/;

// CommonMark-style fences: up to three leading spaces, backtick or tilde, and a
// closing delimiter of the same character at least as long as the opener.
function fenceMask(text) {
  const mask = new Array(text.split("\n").length).fill(false);
  let open = null;
  text.split("\n").forEach((line, index) => {
    const match = FENCE.exec(line);
    if (!open) {
      if (match && !(match[1][0] === "`" && match[2].includes("`"))) {
        open = { char: match[1][0], length: match[1].length };
        mask[index] = true;
      }
      return;
    }
    mask[index] = true;
    if (
      match &&
      match[1][0] === open.char &&
      match[1].length >= open.length &&
      match[2].trim() === ""
    ) {
      open = null;
    }
  });
  return mask;
}

export function checkRetiredTerms(doc) {
  const findings = [];
  const masked = fenceMask(doc.text);
  let exemptNext = false;
  doc.text.split("\n").forEach((line, index) => {
    if (masked[index]) {
      exemptNext = false;
      return;
    }
    const heading = /^ {0,3}#{1,6}[ \t]/.test(line);
    const comments = EXEMPTION.exec(line);
    const exempt = !heading && (Boolean(comments) || exemptNext);
    exemptNext = Boolean(comments) && !heading;
    if (exempt) return;
    for (const { term, pattern, guidance } of RETIRED_TERMS) {
      if (pattern.test(line)) {
        findings.push({
          path: doc.path,
          rule: "retired-term",
          line: index + 1,
          message: `"${term}": ${guidance}`,
        });
      }
    }
  });
  return findings;
}

export function checkGlossaryBudget(text, budget = BUDGET.glossary) {
  const masked = fenceMask(text);
  let count = 0;
  text.split("\n").forEach((line, index) => {
    if (!masked[index] && /^### /.test(line)) count += 1;
  });
  return count > budget
    ? [
        {
          path: "docs/glossary.md",
          rule: "glossary-budget",
          message: `glossary has ${count} terms, limit ${budget}`,
        },
      ]
    : [];
}

function excluded(rel) {
  return SCOPE_EXCLUDE.some((prefix) => rel === prefix || rel.startsWith(`${prefix}/`));
}

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

export async function collectScope(root) {
  const out = [];
  for (const item of SCOPE_INCLUDE) {
    const full = path.join(root, item);
    if (!existsSync(full)) continue;
    if (item.endsWith(".md")) {
      out.push({ path: item, text: await readFile(full, "utf8") });
    } else {
      await walk(item, root, out);
    }
  }
  return out.sort((a, b) => a.path.localeCompare(b.path));
}
