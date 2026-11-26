// The page's commands must run in the order a reader copies them.
//
// In-memory fixtures and one file read: no model, no network, no subprocess.
import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { checkPagePaths, commands, createdDirs, writtenFiles } from "../scripts/page-paths.mjs";

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const PAGE = "docs/getting-started.md";

test("the page creates every directory it writes into", async () => {
  const text = await readFile(path.join(repoRoot, PAGE), "utf8");
  assert.deepEqual(checkPagePaths(text, PAGE), []);
});

test("a page that creates the directory first passes", () => {
  const text = ["```sh", "mkdir -p ~/models", "curl -sSL -o ~/models/w.gguf https://x/w.gguf", "```"].join("\n");
  assert.deepEqual(checkPagePaths(text, "fixture.md"), []);
});

test("a write into a directory nothing creates is a finding", () => {
  const text = [
    "```sh",
    "mkdir -p ~/.local/share/satyrn-llama/b12066",
    "curl -sSL -o ~/models/w.gguf https://x/w.gguf",
    "```",
  ].join("\n");
  const findings = checkPagePaths(text, "fixture.md");
  assert.equal(findings.length, 1);
  assert.equal(findings[0].rule, "uncreated-directory");
  assert.match(findings[0].message, /mkdir -p ~\/models/);
});

test("writing into the working directory needs no mkdir", () => {
  const text = ["```sh", "curl -sSL -O https://x/w.gguf", "curl -sSL -o w.gguf https://x/w.gguf", "```"].join("\n");
  assert.deepEqual(checkPagePaths(text, "fixture.md"), []);
});

test("--output= spells the target too", () => {
  const text = ["```sh", "curl -sSL --output=~/models/w.gguf https://x/w.gguf", "```"].join("\n");
  assert.equal(checkPagePaths(text, "fixture.md").length, 1);
});

test("a continued command is read as one line", () => {
  const text = [
    "```sh",
    "mkdir -p ~/models",
    "curl -sSL -o ~/models/w.gguf \\",
    "  https://x/w.gguf",
    "```",
  ].join("\n");
  assert.deepEqual(commands(text), [
    "mkdir -p ~/models",
    "curl -sSL -o ~/models/w.gguf https://x/w.gguf",
  ]);
  assert.deepEqual(createdDirs(text), ["~/models"]);
  assert.deepEqual(
    writtenFiles(text).map((w) => w.target),
    ["~/models/w.gguf"],
  );
});

test("a comment inside a fence is not a command", () => {
  assert.deepEqual(commands(["```sh", "# never run me", "curl -sSL -O https://x", "```"].join("\n")), [
    "curl -sSL -O https://x",
  ]);
});
