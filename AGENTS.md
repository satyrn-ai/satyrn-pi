# Satyrn Pi — agent notes

Satyrn Pi is a small local model as a bounded coding worker inside Pi. The port
is in progress: this repository has package skeletons, contributor setup and the
process records; the worker, remedies, eval CLI, suites and grading arrive in
later cycles.

`docs/provenance/` holds verbatim source documents. They are evidence for the
port, not this repository's active rules.

## Read first

1. [BRIEF.md](BRIEF.md) — scope and fixed decisions.
2. [docs/rules-applicability.md](docs/rules-applicability.md) — how the preserved
   source rules map onto this repository, with the dated mappings.
3. [docs/sdd.md](docs/sdd.md) — the preserved process, caps and close checklist.
4. [ROADMAP.md](ROADMAP.md) — the current cycle in `## Now`, and the rows.

Where the preserved wording and this port disagree, BRIEF's fixed decisions and
the applicability mappings govern. Explicit user instructions come first.

## The cycle

Every cycle runs brainstorm → spec → plan → execute → review/close, sized to the
change. Get human approval before implementation; Nicola approves pull requests.
Plans carry front matter (`phase`, `feature_cycle`, `cycle`, `lifecycle`) and a
`## Result` only at close. A phase is a container; each cycle ships one bounded
deliverable or explicitly named infrastructure.

## Document budgets

- Spec: 150 lines, with a reviewer brief of at most 30 lines at the top.
- Plan: 250 lines.
- This file: 80 lines.

These tighten the preserved 400-line caps for new work; `docs/sdd.md` stays
unchanged and keeps the original numbers. Rationale beyond the brief links to a
research note. A decision that would otherwise be lost moves to the spec's
`## Decisions` section — it is never dropped to meet a budget. Over budget means
split the cycle or link evidence, not delete reasoning.

## Checks

Run `npm test` and `uv run pytest`. Both stay model-, network- and
subprocess-free. A cap, lifecycle and evidence check arrives in P2.3; run its
command once it exists. Every new test is shown to fail before the code that
passes it.

## Boundaries

- Contributor skills (Superpowers) are for contributors. The subject worker
  loads none of them.
- Do not edit `docs/sdd.md` or `docs/provenance/`; a dated correction belongs in
  the document that supersedes them.
- Runtime code, remedies, eval execution and measurement claims belong to their
  named cycles. Do not claim a planned component exists.

## Vocabulary

[docs/glossary.md](docs/glossary.md) is the product vocabulary, capped at the
budget recorded there. Contributor-process terms are defined where they are used;
they do not enter the product glossary.

## Where things are

- [README.md](README.md) — contributor setup and default checks.
- [docs/domain.md](docs/domain.md) — components, responsibilities and run boundaries.
- [docs/superpowers/setup.md](docs/superpowers/setup.md) — Superpowers revision and setup record.
- [docs/superpowers/plans/](docs/superpowers/plans/) — active and archived plans.
