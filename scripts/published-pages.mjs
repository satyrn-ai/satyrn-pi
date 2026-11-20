// Which Markdown files the site publishes. Filesystem reads only: the build
// itself is a subprocess and cannot run in the default suite, so this module
// re-derives the published set from `zensical.toml` and the tree, and the test
// around it is what stops an internal document reaching a stranger.
import { readdir, readFile } from "node:fs/promises";
import path from "node:path";

const BLOCK = /exclude_docs\s*=\s*"""([\s\S]*?)"""/;

/** Patterns from the `exclude_docs` block, in configuration order. */
export function parseExcludeDocs(tomlText) {
  const match = BLOCK.exec(tomlText);
  if (!match) return [];
  return match[1]
    .split("\n")
    .map((line) => line.trim())
    .filter((line) => line !== "" && !line.startsWith("#"));
}

/**
 * Whether a docs-relative path is excluded.
 *
 * The patterns are a subset of gitignore's: a trailing slash matches everything
 * under that directory, a pattern with no slash matches that basename at any
 * depth, and a pattern with a slash matches its own path and anything under it.
 */
export function isExcluded(relativePath, patterns) {
  const rel = relativePath.split(path.sep).join("/");
  const base = rel.slice(rel.lastIndexOf("/") + 1);
  return patterns.some((pattern) => {
    if (pattern.endsWith("/")) return rel.startsWith(pattern);
    if (!pattern.includes("/")) return base === pattern;
    return rel === pattern || rel.startsWith(`${pattern}/`);
  });
}

/** Every Markdown file under `docs`, as docs-relative paths, sorted. */
export async function collectMarkdown(docsDir, prefix = "") {
  const entries = await readdir(path.join(docsDir, prefix), {
    withFileTypes: true,
  });
  const found = [];
  for (const entry of entries.sort((a, b) => a.name.localeCompare(b.name))) {
    const rel = prefix ? `${prefix}/${entry.name}` : entry.name;
    if (entry.isDirectory()) {
      found.push(...(await collectMarkdown(docsDir, rel)));
    } else if (entry.name.endsWith(".md")) {
      found.push(rel);
    }
  }
  return found;
}

/** The published pages: Markdown files that no pattern excludes. */
export async function publishedPages(root) {
  const toml = await readFile(path.join(root, "zensical.toml"), "utf8");
  const patterns = parseExcludeDocs(toml);
  const all = await collectMarkdown(path.join(root, "docs"));
  return { pages: all.filter((rel) => !isExcluded(rel, patterns)), patterns };
}
