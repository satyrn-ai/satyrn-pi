// Repository-weight check (BRIEF.md: "Check weight from phase one").
// Default suite: no model, no network, no subprocess — the walk uses fs only.
import test from "node:test";
import assert from "node:assert/strict";
import { mkdtemp, mkdir, rm, writeFile, readFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { BUDGET, IGNORED_DIRECTORIES, checkWeight, walkTree } from "../scripts/repo-weight.mjs";

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

test("repository tree stays within the weight budget", async () => {
  const stats = await walkTree(repoRoot);
  assert.deepEqual(
    checkWeight(stats),
    [],
    `repository is over budget: ${stats.files} files, ${stats.bytes} bytes`,
  );
});

test("runs/ is git-ignored and skipped by the walk", async () => {
  const gitignore = await readFile(path.join(repoRoot, ".gitignore"), "utf8");
  assert.match(gitignore, /^runs\/$/m, ".gitignore must ignore runs/");
  assert.ok(IGNORED_DIRECTORIES.has("runs"), "the weight walk must skip runs/");
});

test("over-budget tree fails the check", async (t) => {
  const dir = await mkdtemp(path.join(tmpdir(), "satyrn-weight-"));
  t.after(() => rm(dir, { recursive: true, force: true }));
  await writeFile(path.join(dir, "a.txt"), "alpha");
  await writeFile(path.join(dir, "b.txt"), "beta");
  const stats = await walkTree(dir);
  const violations = checkWeight(stats, { maxFiles: 1, maxBytes: 4 });
  assert.equal(violations.length, 2, "file-count and byte violations are both reported");
});

test("under-budget tree passes the check", async (t) => {
  const dir = await mkdtemp(path.join(tmpdir(), "satyrn-weight-"));
  t.after(() => rm(dir, { recursive: true, force: true }));
  await writeFile(path.join(dir, "a.txt"), "alpha");
  const stats = await walkTree(dir);
  assert.deepEqual(checkWeight(stats, { maxFiles: 10, maxBytes: 1000 }), []);
});

test("ignored directories are not walked", async (t) => {
  const dir = await mkdtemp(path.join(tmpdir(), "satyrn-weight-"));
  t.after(() => rm(dir, { recursive: true, force: true }));
  await mkdir(path.join(dir, "node_modules", "dep"), { recursive: true });
  await writeFile(path.join(dir, "node_modules", "dep", "index.js"), "x".repeat(5000));
  await writeFile(path.join(dir, "keep.txt"), "kept");
  const stats = await walkTree(dir);
  assert.equal(stats.files, 1, "node_modules content is not counted");
});
