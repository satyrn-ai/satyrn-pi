// The published page must carry the pins the reference card records.
//
// A digest that lives only in a repository research note cannot be checked by the
// person downloading an 8 GB file, and a digest copied into prose drifts the
// moment either side is edited. So the page repeats the card's pinned values, and
// this compares the two as text: no network, no build, filesystem reads only.
//
// Only two kinds of value count. Full-length hex (a git commit, a Hugging Face
// revision, a sha256) and the build tag the card declares in its own `Tag` row.
// Anything else the card mentions — another release's tag, a truncated commit —
// belongs to someone else's pin and does not have to reach the page.
const LONG_HEX = /\b[0-9a-f]{40,64}\b/gi;
const TAG_ROW = /^\|\s*Tag\s*\|\s*`(b\d+)`/m;

export function extractPins(text) {
  const found = new Set();
  for (const match of text.match(LONG_HEX) ?? []) found.add(match.toLowerCase());
  return found;
}

export function declaredTag(cardText) {
  return TAG_ROW.exec(cardText)?.[1].toLowerCase() ?? null;
}

export function missingPins(cardText, pageText) {
  const page = extractPins(pageText);
  const missing = [...extractPins(cardText)].filter((pin) => !page.has(pin));
  const tag = declaredTag(cardText);
  if (tag && !pageText.toLowerCase().includes(tag)) missing.push(tag);
  return missing.sort();
}

export function checkPins({ card, page }) {
  return missingPins(card.text, page.text).map((pin) => ({
    path: page.path,
    rule: "missing-pin",
    message: `${pin} is recorded in ${card.path} but absent from the page`,
  }));
}
