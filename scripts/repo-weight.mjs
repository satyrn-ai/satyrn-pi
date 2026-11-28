// Repository-weight check (BRIEF.md: "Check weight from phase one").
// Walks the tree with the filesystem only: no model, no network, no subprocess.
import { readdir, stat } from "node:fs/promises";
import path from "node:path";

// Raised in P6.1 from 200 files and 1 MB to hold the pinned suite data: 95 copied
// files and 867,403 bytes, 725,873 of them three uv.lock files, two of which are the
// same blob. The check exists to keep run output, traces and workspaces out of the
// tree; pinned inputs and re-earned graders are none of those.
export const BUDGET = Object.freeze({ maxFiles: 320, maxBytes: 2_500_000 });

// Kept in step with .gitignore by tests/repo-weight.test.mjs.
export const IGNORED_DIRECTORIES = new Set([
  ".git",
  "node_modules",
  ".venv",
  "runs",
  "dist",
  "site",
  "__pycache__",
  ".pytest_cache",
  ".idea",
  ".ruff_cache",
  ".mypy_cache",
  // Contributor scratch the other scanners already skip. The superpowers workspace
  // git-ignores itself, and counting it would make a local run disagree with CI.
  ".superpowers",
]);

const isIgnored = (name) =>
  IGNORED_DIRECTORIES.has(name) || name.endsWith(".egg-info");

export function checkWeight(stats, budget = BUDGET) {
  const violations = [];
  if (stats.files > budget.maxFiles) {
    violations.push(`files: ${stats.files} > ${budget.maxFiles}`);
  }
  if (stats.bytes > budget.maxBytes) {
    violations.push(`bytes: ${stats.bytes} > ${budget.maxBytes}`);
  }
  return violations;
}

export async function walkTree(root) {
  const stats = { files: 0, bytes: 0 };

  async function walk(directory) {
    const entries = await readdir(directory, { withFileTypes: true });
    for (const entry of entries) {
      const entryPath = path.join(directory, entry.name);
      if (entry.isDirectory()) {
        if (!isIgnored(entry.name)) {
          await walk(entryPath);
        }
      } else if (entry.isFile()) {
        stats.files += 1;
        stats.bytes += (await stat(entryPath)).size;
      }
    }
  }

  await walk(root);
  return stats;
}
