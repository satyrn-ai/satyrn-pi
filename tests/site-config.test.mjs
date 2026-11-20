// The site's two addresses agree, and the glossary source exists.
//
// `base_url` is written out by hand rather than derived, which is what makes a
// base-path mistake visible in review — but also what lets a later edit move one
// address and leave the other. This reads `zensical.toml` and nothing else, so
// it runs in the default suite where a build cannot.
import test from "node:test";
import assert from "node:assert/strict";
import { access, readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

async function readConfig() {
  const toml = await readFile(path.join(repoRoot, "zensical.toml"), "utf8");
  const value = (key) => {
    const match = new RegExp(`^\\s*${key}\\s*=\\s*"([^"]*)"`, "m").exec(toml);
    return match ? match[1] : null;
  };
  return {
    siteUrl: value("site_url"),
    baseUrl: value("base_url"),
    glossaryFile: value("glossary_file"),
    docsDir: value("docs_dir"),
  };
}

test("base_url sits under site_url", async () => {
  const { siteUrl, baseUrl } = await readConfig();
  assert.ok(siteUrl, "zensical.toml sets site_url");
  assert.ok(baseUrl, "zensical.toml sets base_url");
  assert.ok(
    baseUrl.startsWith(siteUrl),
    `base_url ${baseUrl} must start with site_url ${siteUrl}`,
  );
});

test("both addresses end in a slash", async () => {
  const { siteUrl, baseUrl } = await readConfig();
  assert.ok(siteUrl.endsWith("/"), "site_url keeps its trailing slash");
  assert.ok(baseUrl.endsWith("/"), "base_url keeps its trailing slash");
});

test("the glossary source resolves inside docs_dir", async () => {
  const { glossaryFile, docsDir } = await readConfig();
  assert.ok(glossaryFile, "zensical.toml names a glossary file");
  assert.equal(docsDir, "docs");
  await access(path.join(repoRoot, docsDir, glossaryFile));
});
