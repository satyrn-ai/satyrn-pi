// The site publishes the home page and the glossary, and nothing else.
//
// A strict build does not warn about an extra page: a planted third page builds
// and publishes silently. So the published set is asserted here, against the
// same configuration the build reads. Filesystem reads only.
import test from "node:test";
import assert from "node:assert/strict";
import { mkdtemp, mkdir, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import {
  collectMarkdown,
  isExcluded,
  parseExcludeDocs,
  publishedPages,
} from "../scripts/published-pages.mjs";

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

const CONFIG = `[project]
docs_dir = "docs"
exclude_docs = """
internal.md
notes/
superpowers/plans/
"""
`;

async function tree(t, files) {
  const dir = await mkdtemp(path.join(tmpdir(), "satyrn-pages-"));
  t.after(() => rm(dir, { recursive: true, force: true }));
  for (const [name, text] of Object.entries(files)) {
    const full = path.join(dir, name);
    await mkdir(path.dirname(full), { recursive: true });
    await writeFile(full, text);
  }
  return dir;
}

test("the real tree publishes exactly the home page and the glossary", async () => {
  const { pages } = await publishedPages(repoRoot);
  assert.deepEqual(pages, ["glossary.md", "index.md"]);
});

test("an unexcluded page joins the published set", async (t) => {
  const dir = await tree(t, {
    "zensical.toml": CONFIG,
    "docs/index.md": "# Home\n",
    "docs/glossary.md": "# Glossary\n",
    "docs/third.md": "# Third\n",
  });
  const { pages } = await publishedPages(dir);
  assert.deepEqual(pages, ["glossary.md", "index.md", "third.md"]);
});

test("excluding the planted page restores the set", async (t) => {
  const dir = await tree(t, {
    "zensical.toml": CONFIG.replace("internal.md", "internal.md\nthird.md"),
    "docs/index.md": "# Home\n",
    "docs/glossary.md": "# Glossary\n",
    "docs/third.md": "# Third\n",
  });
  const { pages } = await publishedPages(dir);
  assert.deepEqual(pages, ["glossary.md", "index.md"]);
});

test("a nested document is excluded by its directory pattern", async (t) => {
  const dir = await tree(t, {
    "zensical.toml": CONFIG,
    "docs/index.md": "# Home\n",
    "docs/notes/deep/page.md": "# Deep\n",
  });
  const { pages } = await publishedPages(dir);
  assert.deepEqual(pages, ["index.md"]);
});

test("a basename pattern matches at any depth, a path pattern does not", () => {
  const patterns = parseExcludeDocs(CONFIG);
  assert.equal(isExcluded("sdd.md", ["sdd.md"]), true);
  assert.equal(isExcluded("research/sdd.md", ["sdd.md"]), true);
  assert.equal(isExcluded("superpowers/plans/p.md", patterns), true);
  assert.equal(isExcluded("superpowers/specs/p.md", patterns), false);
});

test("comments and blank lines are not patterns", () => {
  const patterns = parseExcludeDocs(`exclude_docs = """
# a comment
sdd.md

"""`);
  assert.deepEqual(patterns, ["sdd.md"]);
});

test("a missing block means nothing is excluded", () => {
  assert.deepEqual(parseExcludeDocs("[project]\ndocs_dir = \"docs\"\n"), []);
});

test("markdown is collected from nested directories", async (t) => {
  const dir = await tree(t, {
    "docs/a.md": "# A\n",
    "docs/nested/b.md": "# B\n",
    "docs/nested/image.png": "binary",
  });
  assert.deepEqual(await collectMarkdown(path.join(dir, "docs")), [
    "a.md",
    "nested/b.md",
  ]);
});
