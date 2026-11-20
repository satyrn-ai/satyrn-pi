// Retired product vocabulary and the product-facing scan scope. Contributor and
// source-mapping records are excluded; they legitimately name the old concepts.
export const RETIRED_TERMS = Object.freeze([
  {
    term: "stage",
    pattern: /\bstages?\b/i,
    guidance: 'Say Vanilla, Base, Easy, Medium or Hard, or "preset".',
  },
  { term: "floor", pattern: /\bfloors?\b/i, guidance: "Say Vanilla or baseline." },
  { term: "remedy unit", pattern: /\bremedy units?\b/i, guidance: "Say remedy." },
  {
    term: "tier",
    pattern: /\btiers?\b/i,
    guidance: "Say preset, or name the task collection or integration tests.",
  },
  {
    term: "ladder",
    pattern: /\bladders?\b/i,
    guidance: "Source mapping only; name the eval package or suite.",
  },
  {
    term: "rung",
    pattern: /\brungs?\b/i,
    guidance: "Source mapping only; name the task or cycle.",
  },
]);

export const SCOPE_INCLUDE = Object.freeze(["README.md", "AGENTS.md", "BACKLOG.md", "docs"]);

export const SCOPE_EXCLUDE = Object.freeze([
  "docs/sdd.md",
  "docs/rules-applicability.md",
  "docs/superpowers",
  "docs/provenance",
]);
