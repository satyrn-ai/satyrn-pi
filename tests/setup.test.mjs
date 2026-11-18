// Contributor setup checks. Default suite: no model, no network, no subprocess —
// subprocesses are fakes and settings live in temporary directories.
import test from "node:test";
import assert from "node:assert/strict";
import { mkdtemp, mkdir, readFile, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import {
  SUPERPOWERS,
  decideAction,
  findSuperpowersEntry,
  installArgs,
  runSetup,
} from "../scripts/setup.mjs";

const PIN = "bb92a77741419a4ab5f06e711a283343f1ada0c3";
const SOURCE = "git:github.com/obra/superpowers";

test("SUPERPOWERS is a frozen pin", () => {
  assert.equal(SUPERPOWERS.source, SOURCE);
  assert.equal(SUPERPOWERS.commit, PIN);
  assert.equal(SUPERPOWERS.describe, "v6.1.1-56-gbb92a77");
  assert.ok(Object.isFrozen(SUPERPOWERS));
});

test("findSuperpowersEntry reports absent entries", () => {
  assert.deepEqual(findSuperpowersEntry({}), { status: "absent" });
  assert.deepEqual(findSuperpowersEntry({ packages: [] }), { status: "absent" });
});

test("findSuperpowersEntry reports unpinned entries", () => {
  const settings = { packages: ["npm:@upstash/context7-pi", SOURCE] };
  assert.deepEqual(findSuperpowersEntry(settings), {
    status: "unpinned",
    entry: SOURCE,
  });
});

test("findSuperpowersEntry reports pinned entries", () => {
  const entry = `${SOURCE}@${PIN}`;
  assert.deepEqual(findSuperpowersEntry({ packages: [entry] }), {
    status: "pinned",
    entry,
    ref: PIN,
  });
});

test("findSuperpowersEntry ignores unrelated packages", () => {
  const settings = {
    packages: [
      "npm:@upstash/context7-pi",
      "git:github.com/obra/superpowers-fork",
      "git:github.com/obra/superpowers-fork@v1",
    ],
  };
  assert.deepEqual(findSuperpowersEntry(settings), { status: "absent" });
});

test("decideAction installs when absent", () => {
  assert.equal(decideAction({ status: "absent" }).action, "install");
});

test("decideAction is a no-op at the pinned commit", () => {
  assert.equal(
    decideAction({ status: "pinned", ref: PIN, entry: `${SOURCE}@${PIN}` }).action,
    "none",
  );
});

test("decideAction refuses a different pin without consent", () => {
  const decision = decideAction({ status: "pinned", ref: "a".repeat(40), entry: "" });
  assert.equal(decision.action, "refuse");
  assert.match(decision.reason, /--yes/);
});

test("decideAction refuses an unpinned entry without consent", () => {
  const decision = decideAction({ status: "unpinned", entry: SOURCE });
  assert.equal(decision.action, "refuse");
  assert.match(decision.reason, /--yes/);
});

test("decideAction changes a different pin with consent", () => {
  assert.equal(
    decideAction({ status: "pinned", ref: "a".repeat(40) }, { yes: true }).action,
    "change",
  );
  assert.equal(
    decideAction({ status: "unpinned", entry: SOURCE }, { yes: true }).action,
    "change",
  );
});

test("installArgs pins the exact commit", () => {
  assert.deepEqual(installArgs(), ["install", `${SOURCE}@${PIN}`]);
});

async function scratchSettings(settings) {
  const dir = await mkdtemp(path.join(tmpdir(), "satyrn-setup-"));
  if (settings !== undefined) {
    await mkdir(dir, { recursive: true });
    await writeFile(path.join(dir, "settings.json"), JSON.stringify(settings));
  }
  return dir;
}

function fakeExec(failOn = () => false) {
  const calls = [];
  const exec = (command, args) => {
    calls.push([command, ...args].join(" "));
    return { code: failOn([command, ...args].join(" ")) ? 1 : 0 };
  };
  return { calls, exec };
}

test("runSetup fails before installing when a required tool is missing", async (t) => {
  const dir = await scratchSettings({ packages: [] });
  t.after(() => rm(dir, { recursive: true, force: true }));
  const { calls, exec } = fakeExec((call) => call.startsWith("uv "));

  await assert.rejects(
    runSetup({ exec, log: () => {}, env: { PI_CODING_AGENT_DIR: dir } }),
    /uv/,
  );
  assert.ok(!calls.includes("npm ci"), "npm ci must not run before tool checks");
});

test("runSetup installs in order and logs the steps", async (t) => {
  const dir = await scratchSettings({ packages: [] });
  t.after(() => rm(dir, { recursive: true, force: true }));
  const { calls, exec } = fakeExec();
  const logged = [];

  await runSetup({
    exec,
    log: (line) => logged.push(line),
    env: { PI_CODING_AGENT_DIR: dir },
  });

  assert.deepEqual(calls, [
    "pi --version",
    "uv --version",
    "npm ci",
    "uv sync",
    `pi ${installArgs().join(" ")}`,
  ]);
  assert.ok(logged.some((line) => line.includes("npm ci")));
});

test("runSetup does not reinstall at the pinned commit", async (t) => {
  const dir = await scratchSettings({ packages: [`${SOURCE}@${PIN}`] });
  t.after(() => rm(dir, { recursive: true, force: true }));
  const { calls, exec } = fakeExec();

  await runSetup({ exec, log: () => {}, env: { PI_CODING_AGENT_DIR: dir } });

  assert.ok(!calls.some((call) => call.startsWith("pi install")));
});

test("runSetup aborts on a failing subprocess without claiming success", async (t) => {
  const dir = await scratchSettings({ packages: [] });
  t.after(() => rm(dir, { recursive: true, force: true }));
  const { exec } = fakeExec((call) => call === "npm ci");
  const logged = [];

  await assert.rejects(
    runSetup({
      exec,
      log: (line) => logged.push(line),
      env: { PI_CODING_AGENT_DIR: dir },
    }),
    /npm ci/,
  );
  assert.ok(
    !logged.some((line) => /complete|ready|success/i.test(line)),
    "no success summary after a failed step",
  );
});

test("runSetup refuses to rewrite an unpinned entry without --yes", async (t) => {
  const dir = await scratchSettings({ packages: [SOURCE] });
  t.after(() => rm(dir, { recursive: true, force: true }));
  const { calls, exec } = fakeExec();

  await assert.rejects(
    runSetup({ exec, log: () => {}, env: { PI_CODING_AGENT_DIR: dir } }),
    /--yes/,
  );
  assert.ok(!calls.some((call) => call.startsWith("pi install")));
});

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

test("README and revision record match the script pin", async () => {
  const readme = await readFile(path.join(repoRoot, "README.md"), "utf8");
  const record = await readFile(
    path.join(repoRoot, "docs/superpowers/setup.md"),
    "utf8",
  );
  const pkg = JSON.parse(await readFile(path.join(repoRoot, "package.json"), "utf8"));

  for (const document of [readme, record]) {
    assert.ok(
      document.includes(SUPERPOWERS.commit),
      "each document must carry the pinned commit",
    );
  }
  for (const text of ["npm run setup", "npm test", "uv run pytest", "--yes"]) {
    assert.ok(readme.includes(text), `README must document ${text}`);
  }
  assert.equal(pkg.scripts.setup, "node scripts/setup.mjs");
});
