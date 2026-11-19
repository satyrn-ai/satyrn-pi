// Active documentation links resolve. Filesystem reads only.
import test from "node:test";
import assert from "node:assert/strict";
import { mkdtemp, mkdir, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { checkLinks, collectLinkDocuments } from "../scripts/doc-links.mjs";

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

async function tree(t, files) {
  const dir = await mkdtemp(path.join(tmpdir(), "satyrn-links-"));
  t.after(() => rm(dir, { recursive: true, force: true }));
  for (const [name, text] of Object.entries(files)) {
    const full = path.join(dir, name);
    await mkdir(path.dirname(full), { recursive: true });
    await writeFile(full, text);
  }
  return dir;
}

test("a relative link resolves", async (t) => {
  const dir = await tree(t, {
    "docs/a.md": "[b](b.md)\n",
    "docs/b.md": "# B\n",
  });
  const docs = await collectLinkDocuments(dir);
  assert.deepEqual(checkLinks(docs[0], dir), []);
});

test("a missing relative link fails", async (t) => {
  const dir = await tree(t, { "docs/a.md": "[missing](nope.md)\n" });
  const docs = await collectLinkDocuments(dir);
  const findings = checkLinks(docs[0], dir);
  assert.equal(findings.length, 1);
  assert.equal(findings[0].rule, "broken-link");
});

test("external, anchor and mail links are ignored", async (t) => {
  const dir = await tree(t, {
    "docs/a.md": "[w](https://example.test) [a](#here) [m](mailto:x@y.test)\n",
  });
  const docs = await collectLinkDocuments(dir);
  assert.deepEqual(checkLinks(docs[0], dir), []);
});

test("an anchor is stripped before resolution", async (t) => {
  const dir = await tree(t, {
    "docs/a.md": "[b](b.md#section)\n",
    "docs/b.md": "## Section\n",
  });
  const docs = await collectLinkDocuments(dir);
  assert.deepEqual(checkLinks(docs[0], dir), []);
});

test("preserved, provenance and archived files are excluded", async (t) => {
  const dir = await tree(t, {
    "docs/sdd.md": "[x](../learn/pathologies.md)\n",
    "docs/provenance/README.md": "[x](./README.md)\n",
    "docs/superpowers/plans/archive/a.md": "[x](./nope.md)\n",
    "docs/kept.md": "# Kept\n",
  });
  const paths = (await collectLinkDocuments(dir)).map((d) => d.path);
  assert.deepEqual(paths, ["docs/kept.md"]);
});

test("the repository's active documents resolve", async () => {
  const docs = await collectLinkDocuments(repoRoot);
  assert.ok(docs.length > 0, "no active documents found");
  assert.deepEqual(docs.flatMap((doc) => checkLinks(doc, repoRoot)), []);
});

test("links inside inline and fenced code are ignored", async (t) => {
  const dir = await tree(t, {
    "docs/a.md": "Use `[x](nope.md)` in prose.\n\n```md\n[x](also-nope.md)\n```\n",
  });
  const docs = await collectLinkDocuments(dir);
  assert.deepEqual(checkLinks(docs[0], dir), []);
});
