// The page and the card must not drift.
//
// In-memory fixtures and filesystem reads only: no model, no network, no subprocess.
import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { checkPins, declaredTag, extractPins, missingPins } from "../scripts/reference-pins.mjs";

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const CARD = "docs/superpowers/research/2026-11-21-reference-host-card.md";
const PAGE = "docs/getting-started.md";

const SHA_A = "a".repeat(64);
const SHA_B = "b".repeat(64);
const COMMIT = "c".repeat(40);
const CARD_TEXT = `| Tag | \`b12066\`, released 2026-11-03 |\n| sha256 | \`${SHA_A}\` |\n`;

test("every pinned value in the card also appears on the page", async () => {
  const card = { path: CARD, text: await readFile(path.join(repoRoot, CARD), "utf8") };
  const page = { path: PAGE, text: await readFile(path.join(repoRoot, PAGE), "utf8") };
  assert.deepEqual(checkPins({ card, page }), []);
});

test("a digest recorded only in the card is a finding", () => {
  const findings = checkPins({
    card: { path: CARD, text: CARD_TEXT },
    page: { path: PAGE, text: "no digests here" },
  });
  assert.ok(findings.length >= 1);
  assert.ok(findings.every((f) => f.rule === "missing-pin"));
  assert.ok(findings.some((f) => f.message.includes(SHA_A)));
});

test("a page carrying the card's values passes", () => {
  assert.deepEqual(missingPins(CARD_TEXT, `${SHA_A} b12066`), []);
});

test("the build tag the card declares is a pin too", () => {
  assert.deepEqual(missingPins(CARD_TEXT, SHA_A), ["b12066"]);
});

test("another release's tag is not this card's pin", () => {
  const card = `${CARD_TEXT}\nvastai/llama-cpp:b11985-mix-c116c32-cuda-12.9\n`;
  assert.deepEqual(missingPins(card, `${SHA_A} b12066`), []);
});

test("a commit and a revision are pins; a truncated commit is not", () => {
  assert.deepEqual(missingPins(`commit ${COMMIT}`, ""), [COMMIT]);
  assert.equal(extractPins("build 12110, commit cd959bae9").size, 0);
});

test("pins are compared regardless of case", () => {
  assert.deepEqual(missingPins(`shasum ${SHA_A.toUpperCase()}`, SHA_A), []);
});

test("a card without a Tag row declines to check a tag", () => {
  assert.equal(declaredTag("no table here"), null);
});
