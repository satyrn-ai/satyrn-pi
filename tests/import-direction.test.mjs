// One-way import check: the worker never imports the eval package, and the eval
// package never imports worker internals. Filesystem reads only.
import test from "node:test";
import assert from "node:assert/strict";
import { mkdtemp, mkdir, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import {
  checkEvalSources,
  checkWorkerSources,
  collectEvalSources,
  collectWorkerSources,
} from "../scripts/import-direction.mjs";

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const jsCheck = (text) => checkWorkerSources({ path: "extensions/x.ts", text });
const pyCheck = (text) => checkEvalSources({ path: "src/satyrn_pi/x.py", text });

test("a worker import of the eval package fails", () => {
  const findings = jsCheck('import { run } from "satyrn_pi";\n');
  assert.equal(findings.length, 1);
  assert.equal(findings[0].rule, "import-direction");
});

test("a worker import of a Python path fails", () => {
  assert.equal(jsCheck('import x from "../src/satyrn_pi/cli.py";\n').length, 1);
});

test("a worker import of its own remedies passes", () => {
  assert.equal(jsCheck('import { guard } from "./remedies/guard/x.ts";\n').length, 0);
});

test("an eval import of a worker module fails", () => {
  assert.equal(pyCheck("from remedies.guard import x\n").length, 1);
  assert.equal(pyCheck("import extensions\n").length, 1);
});

test("an eval import of the standard library passes", () => {
  assert.equal(pyCheck("import json\nfrom pathlib import Path\n").length, 0);
});

test("the collector finds worker files in a temporary tree", async (t) => {
  const dir = await mkdtemp(path.join(tmpdir(), "satyrn-import-"));
  t.after(() => rm(dir, { recursive: true, force: true }));
  await mkdir(path.join(dir, "extensions"), { recursive: true });
  await writeFile(path.join(dir, "extensions", "worker.ts"), "export {};\n");
  await mkdir(path.join(dir, "src", "satyrn_pi"), { recursive: true });
  await writeFile(path.join(dir, "src", "satyrn_pi", "cli.py"), "import json\n");
  const workers = await collectWorkerSources(dir);
  assert.deepEqual(workers.map((f) => f.path), ["extensions/worker.ts"]);
  const evals = await collectEvalSources(dir);
  assert.deepEqual(evals.map((f) => f.path), ["src/satyrn_pi/cli.py"]);
});

test("the repository passes in both directions", async () => {
  const workers = await collectWorkerSources(repoRoot);
  const evals = await collectEvalSources(repoRoot);
  assert.deepEqual(workers.flatMap(checkWorkerSources), []);
  assert.deepEqual(evals.flatMap(checkEvalSources), []);
});
