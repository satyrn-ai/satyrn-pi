// A copy-paste page must not write into a directory it never creates.
//
// Ben found this the expensive way: step 2 piped `curl -o ~/models/...` on a
// clean machine, and `~/models` did not exist, so the download failed on the
// line the reader had just copied. Reading the page text only: no filesystem,
// no network, no subprocess.

import path from "node:path";

const FENCE = /^```[a-z]*\n([\s\S]*?)^```$/gm;

/** Fenced commands on the page, with backslash continuations joined. */
export function commands(text) {
  const lines = [...text.matchAll(FENCE)]
    .flatMap((m) => m[1].split("\n"))
    .map((line) => line.trim())
    .filter((line) => line && !line.startsWith("#"));

  const joined = [];
  for (const line of lines) {
    const previous = joined.at(-1);
    if (previous !== undefined && previous.endsWith("\\")) {
      joined[joined.length - 1] = `${previous.slice(0, -1).trim()} ${line}`;
    } else {
      joined.push(line);
    }
  }
  return joined;
}

/** Directories the page creates, in the order it creates them. */
export function createdDirs(text) {
  const dirs = [];
  for (const command of commands(text)) {
    const match = command.match(/^mkdir\s+(?:-[A-Za-z]+\s+)*(\S+)$/);
    if (match) dirs.push(match[1].replace(/\/+$/, ""));
  }
  return dirs;
}

/** Files the page writes with curl, in the order it writes them. */
export function writtenFiles(text) {
  const writes = [];
  for (const command of commands(text)) {
    const tokens = command.split(/\s+/);
    if (tokens[0] !== "curl") continue;
    const at = tokens.findIndex((t) => t === "-o" || t === "--output");
    const inline = tokens.map((t) => t.match(/^--output=(.+)$/)).find(Boolean);
    const target = at === -1 ? inline?.[1] : tokens[at + 1];
    if (target) writes.push({ command, target });
  }
  return writes;
}

/** Findings for writes whose parent directory no earlier command creates. */
export function checkPagePaths(text, pagePath = "the page") {
  const created = createdDirs(text);
  const findings = [];
  for (const { command, target } of writtenFiles(text)) {
    const dir = path.posix.dirname(target.replace(/^~/, "~"));
    if (dir === "." || dir === "~" || created.includes(dir)) continue;
    findings.push({
      rule: "uncreated-directory",
      page: pagePath,
      message: `"${command}" writes ${target} but no earlier "mkdir -p ${dir}" creates ${dir}`,
    });
  }
  return findings;
}
