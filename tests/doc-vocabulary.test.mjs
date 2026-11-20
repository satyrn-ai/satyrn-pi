// Vocabulary checks: retired product terms and the glossary budget.
// In-memory fixtures and filesystem reads only; no model, network or subprocess.
import test from "node:test";
import assert from "node:assert/strict";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { readFile } from "node:fs/promises";
import { BUDGET } from "../scripts/doc-budgets.mjs";
import { checkGlossaryBudget, checkRetiredTerms, collectScope } from "../scripts/vocabulary-checks.mjs";

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const check = (text, p = "docs/example.md") => checkRetiredTerms({ path: p, text });

test("a retired term in prose fails", () => {
  const findings = check("The stage is not a product concept.\n");
  assert.equal(findings.length, 1);
  assert.equal(findings[0].rule, "retired-term");
  assert.match(findings[0].message, /stage/);
});

test("plurals fail and longer words pass", () => {
  assert.equal(check("The stages are listed.\n").length, 1);
  assert.equal(check("The remedy units are listed.\n").length, 1);
  assert.equal(check("Staging the release.\n").length, 0);
});

test("fenced blocks are skipped", () => {
  assert.equal(check("```sh\n# stage 2: run tests\n```\n").length, 0);
});

test("same-line and preceding-line exemptions pass", () => {
  assert.equal(check("The stage <!-- vocabulary: source quotation -->\n").length, 0);
  assert.equal(check("<!-- vocabulary: source quotation -->\nThe stage\n").length, 0);
});

test("an empty exemption reason does not exempt", () => {
  assert.equal(check("The stage <!-- vocabulary: -->\n").length, 1);
});

test("a heading fails even with an exemption", () => {
  const findings = check("## Stage <!-- vocabulary: source quotation -->\n");
  assert.equal(findings.length, 1);
  assert.match(findings[0].message, /stage/);
});

test("the scope includes product docs and excludes process records", async () => {
  const docs = await collectScope(repoRoot);
  const paths = docs.map((d) => d.path);
  for (const wanted of ["README.md", "AGENTS.md", "BACKLOG.md", "docs/domain.md", "docs/glossary.md", "docs/pathologies.md"]) {
    assert.ok(paths.includes(wanted), `scope missing ${wanted}`);
  }
  for (const unwanted of [
    "BRIEF.md",
    "ROADMAP.md",
    "docs/sdd.md",
    "docs/rules-applicability.md",
  ]) {
    assert.ok(!paths.includes(unwanted), `scope must exclude ${unwanted}`);
  }
  assert.ok(!paths.some((p) => p.startsWith("docs/superpowers/")), "plans, specs and research are excluded");
  assert.ok(!paths.some((p) => p.startsWith("docs/provenance/")), "provenance is excluded");
});

test("the repository scope returns no retired-term findings", async () => {
  const docs = await collectScope(repoRoot);
  assert.deepEqual(docs.flatMap(checkRetiredTerms), []);
});

test("a glossary over 25 terms fails", () => {
  const entries = (n) => Array.from({ length: n }, (_, i) => `### Term ${i + 1}`).join("\n\n");
  const over = checkGlossaryBudget(entries(26));
  assert.equal(over.length, 1);
  assert.equal(over[0].rule, "glossary-budget");
  assert.equal(checkGlossaryBudget(entries(25)).length, 0);
  const aliases = entries(25).replace("### Term 1", "### Term 1\n\n<!-- zensical-glossary-aliases: x -->");
  assert.equal(checkGlossaryBudget(aliases).length, 0);
});

test("the repository glossary fits its budget and states the number", async () => {
  const text = await readFile(path.join(repoRoot, "docs/glossary.md"), "utf8");
  assert.equal(checkGlossaryBudget(text, BUDGET.glossary).length, 0);
  assert.match(text, /Vocabulary budget:\*\* 25/);
});

test("fence handling follows common Markdown forms", () => {
  assert.equal(check("```\n# stage\n  ```\nThe stage is outside.\n").length, 1);
  assert.equal(check("~~~\n# stage\n~~~\n").length, 0);
  assert.equal(check("  ```\n  # stage\n  ```\n").length, 0);
  assert.equal(check("```\n# stage\n").length, 0);
});

test("an indented heading is never exempt", () => {
  assert.equal(check("  ## Stage <!-- vocabulary: source quotation -->\n").length, 1);
});

test("fence handling applies to glossary counting", () => {
  assert.equal(checkGlossaryBudget("```\n### Fake\n  ```\n### Real\n", 0).length, 1);
});
