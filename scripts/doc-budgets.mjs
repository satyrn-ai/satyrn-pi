// Document budgets for this repository. AGENTS.md states the first four;
// tests/doc-caps.test.mjs keeps the prose and these numbers in step.
export const BUDGET = Object.freeze({
  spec: 150,
  plan: 250,
  brief: 30,
  agents: 80,
  roadmap: 400,
  ships: 900,
  excludes: 900,
  status: 1000,
  backlogEntry: 1200,
  planFenced: 0.25,
});

// Archived before the lifecycle gate existed; archived plans are never edited.
export const LEGACY_ARCHIVED_WITHOUT_RESULT = Object.freeze([
  "docs/superpowers/plans/archive/2026-11-17-p1.1-repository-setup.md",
]);
