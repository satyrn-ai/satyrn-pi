// Default-test tripwire. The guard's own forbidden examples are assembled from
// parts so this file never contains a complete matching pattern.
import test from "node:test";
import assert from "node:assert/strict";
import { mkdtemp, mkdir, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { checkTestText, collectTestFiles, loadRules } from "../scripts/default-test-guard.mjs";

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const moduleName = (name) => ["node:", name].join("");
const importOf = (name) => ["import { x }", "from", JSON.stringify(moduleName(name)) + ";"].join(" ");
const requireOf = (name) => ["const x =", "require(" + JSON.stringify(moduleName(name)) + ");"].join(" ");
const callOf = (name, args = "") => [name + "(", args + ")"].join("");
const rules = loadRules();
const check = (text) => checkTestText({ path: "tests/example.test.mjs", text }, rules);

test("the rule table lists the forbidden modules", () => {
  assert.ok(rules.jsModules.includes(["child", "process"].join("_")));
  assert.ok(rules.pythonModules.includes(["sub", "process"].join("")));
});

test("a forbidden import, require or call fails", () => {
  assert.equal(check(importOf(["child", "process"].join("_"))).length, 1);
  assert.equal(check(requireOf(["child", "process"].join("_"))).length, 1);
  assert.equal(check(callOf(["fet", "ch"].join(""), JSON.stringify("/x"))).length, 1);
  assert.equal(
    check("globalThis." + callOf(["fet", "ch"].join(""), JSON.stringify("/x"))).length,
    1,
  );
});

test("allowed modules pass", () => {
  assert.equal(check(importOf("fs")).length, 0);
  assert.equal(check(importOf("path")).length, 0);
});

test("comments and prose do not trip the guard", () => {
  assert.equal(check("// " + importOf(["child", "process"].join("_"))).length, 0);
  assert.equal(check("// the default suite never calls " + ["fet", "ch"].join("") + "()").length, 0);
});

test("collectTestFiles finds nested test files", async (t) => {
  const dir = await mkdtemp(path.join(tmpdir(), "satyrn-guard-"));
  t.after(() => rm(dir, { recursive: true, force: true }));
  await mkdir(path.join(dir, "tests", "nested"), { recursive: true });
  await writeFile(path.join(dir, "tests", "a.test.mjs"), "// ok\n");
  await writeFile(path.join(dir, "tests", "nested", "b.test.mjs"), "// ok\n");
  const found = (await collectTestFiles(dir)).map((f) => f.path).sort();
  assert.deepEqual(found, ["tests/a.test.mjs", "tests/nested/b.test.mjs"]);
});

test("the repository's default tests pass the tripwire", async () => {
  const files = await collectTestFiles(repoRoot);
  assert.ok(files.length > 0, "no default tests found");
  assert.deepEqual(files.flatMap((file) => checkTestText(file, rules)), []);
});

test("side-effect imports and string-bearing lines are caught", () => {
  const sideEffect = (name) => "import " + JSON.stringify(moduleName(name)) + ";";
  assert.equal(check(sideEffect(["child", "process"].join("_"))).length, 1);
  const url = "const url = " + JSON.stringify("https://example.test") + "; " + callOf(["fet", "ch"].join(""), "url");
  assert.equal(check(url).length, 1);
});

test("method calls named fetch or prefetch pass", () => {
  assert.equal(check("client." + callOf(["fet", "ch"].join(""), "url")).length, 0);
  assert.equal(check("pre" + callOf(["fet", "ch"].join(""), "url")).length, 0);
});
