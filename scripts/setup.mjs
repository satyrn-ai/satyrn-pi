#!/usr/bin/env node
// Contributor setup: locked dependency installs plus a ref-pinned Superpowers
// package for the contributor's Pi. The decision logic is pure so the default
// suite can test it without subprocesses, network or a real Pi config.
import { spawnSync } from "node:child_process";
import { readFileSync } from "node:fs";
import { homedir } from "node:os";
import path from "node:path";
import { pathToFileURL } from "node:url";

export const SUPERPOWERS = Object.freeze({
  source: "git:github.com/obra/superpowers",
  commit: "bb92a77741419a4ab5f06e711a283343f1ada0c3",
  describe: "v6.1.1-56-gbb92a77",
});

export function settingsPath(env = process.env) {
  const dir = env.PI_CODING_AGENT_DIR || path.join(homedir(), ".pi", "agent");
  return path.join(dir, "settings.json");
}

export function findSuperpowersEntry(settings) {
  const packages = Array.isArray(settings?.packages) ? settings.packages : [];
  for (const entry of packages) {
    if (typeof entry !== "string") continue;
    if (entry === SUPERPOWERS.source) {
      return { status: "unpinned", entry };
    }
    if (entry.startsWith(`${SUPERPOWERS.source}@`)) {
      return { status: "pinned", entry, ref: entry.slice(SUPERPOWERS.source.length + 1) };
    }
  }
  return { status: "absent" };
}

export function decideAction(entry, { yes = false } = {}) {
  if (entry.status === "absent") {
    return { action: "install", reason: "Superpowers is not configured" };
  }
  if (entry.status === "pinned" && entry.ref === SUPERPOWERS.commit) {
    return { action: "none", reason: `already pinned at ${SUPERPOWERS.commit}` };
  }

  const current = entry.status === "pinned" ? entry.ref : "no pinned ref";
  const reason =
    `existing Superpowers entry is ${current}, this repository wants ` +
    `${SUPERPOWERS.commit} (${SUPERPOWERS.describe}); re-run with --yes to change it`;
  return { action: yes ? "change" : "refuse", reason };
}

export function installArgs() {
  return ["install", `${SUPERPOWERS.source}@${SUPERPOWERS.commit}`];
}

function readSettings(file) {
  try {
    return JSON.parse(readFileSync(file, "utf8"));
  } catch (error) {
    if (error.code === "ENOENT") return {};
    throw new Error(`cannot read ${file}: ${error.message}`);
  }
}

function defaultExec(command, args, options = {}) {
  const result = spawnSync(command, args, { stdio: "inherit", ...options });
  if (result.error) return { code: 1, error: result.error };
  return { code: result.status ?? 1 };
}

export async function runSetup({
  exec = defaultExec,
  log = console.log,
  env = process.env,
  yes = false,
  cwd = process.cwd(),
} = {}) {
  log("Satyrn Pi contributor setup");

  for (const tool of ["pi", "uv"]) {
    log(`checking ${tool}`);
    const result = exec(tool, ["--version"], { cwd });
    if (result.code !== 0) {
      throw new Error(
        `required tool not found: ${tool}. Install it and re-run npm run setup.`,
      );
    }
  }

  for (const [label, command, args] of [
    ["npm ci", "npm", ["ci"]],
    ["uv sync", "uv", ["sync"]],
  ]) {
    log(`running ${label}`);
    const result = exec(command, args, { cwd });
    if (result.code !== 0) {
      throw new Error(`${label} failed with exit code ${result.code ?? "unknown"}`);
    }
  }

  const settings = readSettings(settingsPath(env));
  const decision = decideAction(findSuperpowersEntry(settings), { yes });

  if (decision.action === "refuse") {
    throw new Error(decision.reason);
  }
  if (decision.action === "none") {
    log(`Superpowers ${decision.reason}; nothing to install`);
  } else {
    log(
      decision.action === "install"
        ? `installing Superpowers ${SUPERPOWERS.describe} (${SUPERPOWERS.commit})`
        : `changing Superpowers to ${SUPERPOWERS.describe} (${SUPERPOWERS.commit})`,
    );
    const result = exec("pi", installArgs(), { cwd });
    if (result.code !== 0) {
      throw new Error(`pi install failed with exit code ${result.code ?? "unknown"}`);
    }
  }

  log("setup complete; open Pi in this repository and its skills are available");
  log(`default checks: npm test and uv run pytest`);
}

const invokedDirectly =
  process.argv[1] &&
  import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href;

if (invokedDirectly) {
  runSetup({ yes: process.argv.includes("--yes") }).catch((error) => {
    console.error(`setup failed: ${error.message}`);
    process.exitCode = 1;
  });
}
