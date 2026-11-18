// Repository-weight check (BRIEF.md: "Check weight from phase one").
// Default suite: no model, no network, no subprocess — the walk uses fs only.
import test from "node:test";
import assert from "node:assert/strict";
import { mkdtemp, mkdir, rm, writeFile, readFile, symlink } from "node:fs/promises";
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

test("a symlink out of the tree is neither counted nor followed", async (t) => {
  const outside = await mkdtemp(path.join(tmpdir(), "satyrn-weight-out-"));
  const inside = await mkdtemp(path.join(tmpdir(), "satyrn-weight-in-"));
  t.after(() => rm(outside, { recursive: true, force: true }));
  t.after(() => rm(inside, { recursive: true, force: true }));
  // Two files outside the tree the walk must never reach.
  await writeFile(path.join(outside, "secret-a.txt"), "x".repeat(500));
  await writeFile(path.join(outside, "secret-b.txt"), "y".repeat(500));
  // One real file inside, plus a symlink to the outside dir and to an outside file.
  await writeFile(path.join(inside, "real.txt"), "kept");
  await symlink(outside, path.join(inside, "link-to-dir"));
  await symlink(path.join(outside, "secret-a.txt"), path.join(inside, "link-to-file"));
  const stats = await walkTree(inside);
  assert.deepEqual(
    stats,
    { files: 1, bytes: 4 },
    "only the real in-tree file is counted; symlinks are not followed and not counted",
  );
});

test("an in-tree symlink does not double-count its target", async (t) => {
  const dir = await mkdtemp(path.join(tmpdir(), "satyrn-weight-"));
  t.after(() => rm(dir, { recursive: true, force: true }));
  await writeFile(path.join(dir, "real.txt"), "kept");
  await symlink(path.join(dir, "real.txt"), path.join(dir, "alias.txt"));
  const stats = await walkTree(dir);
  assert.equal(stats.files, 1, "the target is counted once; the symlink adds nothing");
});
