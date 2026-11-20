// Evidence-wording checks for research notes. No model, network or subprocess.
import test from "node:test";
import assert from "node:assert/strict";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { checkEvidenceWording, collectDocuments } from "../scripts/doc-checks.mjs";

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const check = (text) => checkEvidenceWording({ path: "docs/superpowers/research/x.md", text });
const section = (title, body) => `## ${title}\n${body}\n`;

test("every research note passes the wording rule", async () => {
  const docs = await collectDocuments(repoRoot);
  assert.deepEqual(docs.research.flatMap(checkEvidenceWording), []);
});

test("n = 1 with a banned claim in the same section fails", () => {
  const findings = check(section("Screen", "One run at n = 1 showed the guard fired; the arms were separated."));
  assert.equal(findings.length, 1);
  assert.equal(findings[0].rule, "evidence-wording");
  assert.match(findings[0].message, /Screen/);
  assert.match(findings[0].message, /separated/);
});

test("n=1 with a case variant of a banned word fails", () => {
  assert.equal(check(section("Screen", "At n=1 the result was NuLL.")).length, 1);
  assert.equal(check(section("Screen", "At n=1 the result was void.")).length, 1);
});

test("n >= 1 does not count as n = 1", () => {
  assert.equal(check(section("Screen", "At n >= 1 the arms were separated.")).length, 0);
});

test("claims in different sections do not collide", () => {
  const text = `${section("Presence", "At n = 1 the block arrived.")}${section("Comparison", "At n = 3 the arms were separated.")}`;
  assert.equal(check(text).length, 0);
});

test("n = 1 without a banned claim passes", () => {
  assert.equal(check(section("Presence", "At n = 1 the guard fired.")).length, 0);
});

test("a claim in the preamble is checked", () => {
  const text = "At n = 1 the arms were separated.\n\n## Notes\n";
  const findings = check(text);
  assert.equal(findings.length, 1);
  assert.match(findings[0].message, /preamble/);
});
