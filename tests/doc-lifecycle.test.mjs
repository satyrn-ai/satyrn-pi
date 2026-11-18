// Plan lifecycle checks. Filesystem reads only: no model, network or subprocess.
import test from "node:test";
import assert from "node:assert/strict";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { LEGACY_ARCHIVED_WITHOUT_RESULT } from "../scripts/doc-budgets.mjs";
import { checkLifecycle, collectDocuments, parseFrontMatter } from "../scripts/doc-checks.mjs";

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const active = (body = "## Tasks\n") =>
  `---\nphase: P2\nfeature_cycle: P2.9\ncycle: 1\nlifecycle: active\n---\n\n# Plan\n\n${body}`;
const archived = (body, lifecycle = "closed") =>
  `---\nphase: P2\nfeature_cycle: P2.9\ncycle: 1\nlifecycle: ${lifecycle}\n---\n\n# Plan\n\n${body}`;
const check = (path, text, isArchived = false) =>
  checkLifecycle({ path, text, archived: isArchived });

test("parseFrontMatter reads the four keys", () => {
  assert.deepEqual(parseFrontMatter(active()), {
    phase: "P2",
    feature_cycle: "P2.9",
    cycle: "1",
    lifecycle: "active",
  });
  assert.equal(parseFrontMatter("# No front matter\n"), null);
});

test("every repository plan passes lifecycle", async () => {
  const docs = await collectDocuments(repoRoot);
  assert.deepEqual(docs.plans.flatMap(checkLifecycle), []);
});

test("a plan without front matter fails", () => {
  const findings = check("docs/superpowers/plans/x.md", "# Plan\n");
  assert.equal(findings.length, 1);
  assert.equal(findings[0].rule, "plan-front-matter");
  const missingKey = check("x.md", active().replace("cycle: 1\n", ""));
  assert.equal(missingKey[0].rule, "plan-front-matter");
});

test("an unknown lifecycle value fails", () => {
  const findings = check("x.md", active().replace("lifecycle: active", "lifecycle: draft"));
  assert.ok(findings.some((f) => f.rule === "plan-lifecycle"));
});

test("an active plan with a Result fails", () => {
  const findings = check("x.md", active("## Result\n\nDone.\n"));
  assert.ok(findings.some((f) => f.rule === "plan-active-result"));
});

test("an archived plan needs a terminal Result", () => {
  assert.equal(check("archive/x.md", archived("## Result\n\nDone.\n"), true).length, 0);
  const noResult = check("archive/x.md", archived("## Notes\n"), true);
  assert.ok(noResult.some((f) => f.rule === "plan-archive-result"));
  const notTerminal = check(
    "archive/x.md",
    archived("## Result\n\nDone.\n\n## Notes\n"),
    true,
  );
  assert.ok(notTerminal.some((f) => f.rule === "plan-archive-result"));
});

test("only the named legacy archive is excused", () => {
  const legacy = LEGACY_ARCHIVED_WITHOUT_RESULT[0];
  assert.equal(LEGACY_ARCHIVED_WITHOUT_RESULT.length, 1);
  assert.equal(check(legacy, archived("## Notes\n"), true).length, 0);
  const other = check("archive/2026-11-18-other.md", archived("## Notes\n"), true);
  assert.ok(other.some((f) => f.rule === "plan-archive-result"));
});
