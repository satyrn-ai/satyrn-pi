# Satyrn Pi roadmap

Scope: [BRIEF](BRIEF.md). Process: [Superpowers/SDD and roadmap rules](docs/rules-applicability.md#roadmap-workflow).

## Now

In flight: [P2.2](#phase-2--sdd-setup), the rules index and mapped records, stacked on [P2.1](#phase-2--sdd-setup) while that cycle is in review (#7).
Parked: preset choices and rented-host qualification await their [research owners](BRIEF.md#decisions-the-research-documents-own).
Next: [P2.3](#phase-2--sdd-setup), the cap, lifecycle and evidence gates, after P2.2.

Rows are initial proposals. Brainstorm each phase during the port and split or
add cycles before implementation; one row does not limit a phase to one cycle.
Each cycle lands in the port repository at `~/projects/satyrn/satyrn-pi` as one
pull request for Nicola; a cycle that cannot be reviewed as one pull request is
too big and splits.
Use [Vanilla → Base → Easy → Medium → Hard](docs/glossary.md); suites select tasks,
presets select remedies.

## Phase 1 — Repository and dependencies

| Cycle | Ships | Excludes | Status |
| --- | --- | --- | --- |
| **P1.1** | Infrastructure: `github.com/satyrn-ai/satyrn-pi` seeded from this tree, npm and Python package layout and dependency locks, default test commands, ignored runs, and a repository-weight check. Record the Pi version the port targets, declare it as the package's peer range, and claim both registry names: a PyPI pending trusted publisher for `satyrn-pi`, and an npm name checked and, if it must be held, published as an agreed placeholder. Both package names are `satyrn-pi`. Include Zensical and `zensical-glossary` in the docs development dependencies; theme and extension setup land in P3.1. | Publishing empty packages; worker behaviour; eval execution; OpenCode. | closed 2026-11-17 — seed copied byte-for-byte from staging `44bdbd61` (staging README excluded) in PR #2 (issue #1 holds the first number). npm and Python `satyrn-pi` 0.1.0 skeletons with locks; default suites `npm test` and `uv run pytest` (no model, network or subprocess); `runs/` ignored; weight check passes at 27 files. Pi peer range `^1.1.0`, targeting 1.5.2; npm name checked unclaimed, PyPI publisher postponed to the first release cycle. [Plan](docs/superpowers/plans/archive/2026-11-17-p1.1-repository-setup.md). |
| **P1.2** | Documentation: worker/eval responsibilities, import direction and shared run meaning in `docs/domain.md`; canonical terms in `docs/glossary.md`, with a numeric jargon budget and checker scope for phase 2. Apply the [vocabulary decisions](docs/superpowers/research/2026-11-16-vocabulary-review.md#port-acceptance); review Vanilla on the Easy suite and Base with an empty preset to expose ambiguity. | Runtime code; a generic domain framework; detailed CLI/schema design; new names for concepts ordinary language already explains. | proposed — after P1.1 and before P2.1; Nicola reviews with implementers and Ben. Later cycles record justified refinements. [Plan](docs/superpowers/plans/2026-11-16-vocabulary.md) carries the budget, the rejected alternatives and the retired-term check. |

## Phase 2 — SDD setup

| Cycle | Ships | Excludes | Status |
| --- | --- | --- | --- |
| **P2.1** | Infrastructure: contributor `README.md`; `npm run setup` running locked `npm ci`/`uv sync` and installing Superpowers as a ref-pinned Pi git package (`bb92a77`, `v7.0.0`), refusing a different existing ref without `--yes`; the revision and setup record with its upgrade policy; a fresh-clone proof. The rows below record the split of the original phase 2 scope. | Runtime code; root `AGENTS.md`; wrapper skill; executable gates; loading skills into the subject worker. | in flight 2026-11-18 — stacked on P1.2 (`015c93d`) in review. [Spec](docs/superpowers/specs/2026-11-18-p2.1-contributor-setup-design.md), [plan](docs/superpowers/plans/2026-11-18-p2.1-contributor-setup.md). |
| **P2.2** | Infrastructure: root `AGENTS.md` as the index to the effective rules; a thin local wrapper skill pointing at repository policy without duplicating Superpowers; `BACKLOG.md`; `docs/pathologies.md`; byte-verification of the preserved `docs/sdd.md` and `docs/provenance/mellum-worker-AGENTS.md` against source `0e4a9b68`. Adds numeric document budgets: a required ≤ 30-line reviewer brief at the top of a spec; rationale beyond the brief links to a research note, plans reference spec decisions instead of restating them, and a decision that would otherwise be lost moves to the decisions table — it is never dropped to meet the budget. | Education material; copying Superpowers into the repository; transplanting source tests; executable gates (P2.3–P2.5). | in flight 2026-11-18 — stacked on P2.1 (PR #7); links only existing destinations, P2.6 resolves every active path. [Spec](docs/superpowers/specs/2026-11-18-p2.2-rules-index-design.md), [plan](docs/superpowers/plans/2026-11-18-p2.2-rules-index.md). |
| **P2.3** | Infrastructure: re-earned cap, plan-lifecycle and evidence-wording checks, each shown to fail first, wired into the default Node suite. The cap check enforces P2.2's budgets (proposed: spec 150 lines, plan 250, reviewer brief 30) and sends an over-budget document to a research note or a split cycle rather than to deletion. | Runtime measurement claims; tests requiring obsolete glossary headings; the vocabulary gates (P2.4). | proposed — after P2.2, when `BACKLOG.md` and plan records exist. |
| **P2.4** | Infrastructure: P1.2's numeric jargon budget and retired-term check, with point-of-use exemptions and a planted violation that fails before it is reverted. | A blanket ban on ordinary English; editing documents from the check; hand-maintained exemption lists. | proposed — after P2.3; consumes the P1.2 glossary, domain map and plan. |
| **P2.5** | Infrastructure: the default-test tripwire and the one-way import check, each shown to fail first. | Runtime code; model, network or subprocess in the default suites. | proposed — after P2.4. |
| **P2.6** | A new contributor's agent finds the rules and follows a cycle, using this phase's own artifacts; phase close resolves every active path and runs both default suites. | Inventing a product feature to prove process; an unreviewed negative outcome; runtime setup claims. | proposed — after P2.5. |

## Phase 3 — Zensical documentation

| Cycle | Ships | Excludes | Status |
| --- | --- | --- | --- |
| **P3.1** | Infrastructure: a Zensical site over plain Markdown, adapting `satyrn-ai/satyrn-website`'s Satyrn theme, with installer/contributor navigation. Configure `zensical-glossary` against `docs/glossary.md`: `###` entries, reviewed aliases and automatic first-prose-occurrence links. Set up GitHub Actions for strict builds on PRs and GitHub Pages deployment from main; record and verify the public website URL. Check theme rendering, glossary links and preview under the [site acceptance rules](docs/rules-applicability.md#documentation-site-acceptance). Ben reviews navigation and terminology. | Learning centre, lessons, challenge and gamification; website blog/hero features; runtime setup claims; misleading legacy aliases. | proposed — after P2.1. |

## Phase 4 — Getting Started setup: llama.cpp

| Cycle | Ships | Excludes | Status |
| --- | --- | --- | --- |
| **P4.1** | Getting Started setup for the Q4_K_M subject on llama-server b12066 at `127.0.0.1:8001`; record the actual GGUF digest, platform artifact and serve flags, and demonstrate a response on the documented reference platform. See [rig](docs/superpowers/research/2026-11-16-reference-rig.md). | Eval-managed server lifecycle; pod provisioning; implying other hosts or historical runs used this exact build. | proposed — after P3.1; document other platforms as unverified until exercised. |

## Phase 5 — Eval CLI

| Cycle | Ships | Excludes | Status |
| --- | --- | --- | --- |
| **P5.1** | The Python CLI entry `uvx satyrn-pi eval --suite <name>`, worker resolution via explicit `--worker` else installed npm package, printed and recorded resolution, `--base-url`, and `runs/` output including `run.json`. Distinguish a run from a Pi session; use Model requests and Elapsed seconds in output, with documented counting and aggregation. Prove resolution and orchestration with fixtures; actual suites, Vanilla and Base land next. | Server or pod provisioning; selecting arbitrary workers on ambiguity; a fake run reported as a model measurement; treating repetitions as random seeds. | proposed — after P4.1; document checkout invocation and package artifact verification. |

## Phase 6 — Suites

| Cycle | Ships | Excludes | Status |
| --- | --- | --- | --- |
| **P6.1** | Preserved Easy/Medium/Hard fixtures and expectations, rewritten grading, witness qualification, grade identity and score provenance. Easy's four-check inherited grade remains primary. One scoring/evidence guide distinguishes failed or unrun tests, grader access, feedback and evidence strength. Qualify expected/observed feedback separately from the oracle grade, using [Andre's supplement](docs/superpowers/research/2026-11-16-upstream-acceptance-feedback.md). See [grading](docs/superpowers/research/2026-11-16-grading-compatibility.md). | Silently correcting historical grades; merging gate-message versions; enabling a settle/redispatch remedy; Education challenge UI. | proposed — after P5.1; qualify verdicts and feedback before trusting a model score or later gate. |

## Phase 7 — Vanilla

| Cycle | Ships | Excludes | Status |
| --- | --- | --- | --- |
| **P7.1** | Vanilla: only Pi and the trace recorder, no worker or remedies; isolated settings, resolved model/host/grader provenance, and a recorded baseline. Specify how to select Vanilla independently of the suite. Fix the intended context-file policy and other run settings before deciding runs. | Preset promotion; a worker-loaded run described as Vanilla; inherited rates presented as new-stack measurements. | proposed — after P6.1; screens precede any preregistered comparison. |

## Phase 8 — Base

| Cycle | Ships | Excludes | Status |
| --- | --- | --- | --- |
| **P8.1** | Base: thin worker command and mode machinery, subject-model switch, pre-marker history integrity, span record, worker report and main-model restoration, eval selection and package-boundary verification. `base.json` starts empty; earned common remedies may be added explicitly in later cycles. | The source `baseline-worker` bundle or label; bundled prompt replacement, guards, facts, tool narrowing or delegation nudges; a public `bare` option. | proposed — after P7.1; measure the rewritten worker before crediting remedies. |

## Phase 9 — Finish Getting Started

| Cycle | Ships | Excludes | Status |
| --- | --- | --- | --- |
| **P9.1** | An installer walkthrough from the npm Pi package and running server to a completed worker task, plus a contributor walkthrough using uvx eval with the resolved worker printed in the record. Exercise package artifacts. Apply the [vocabulary acceptance checklist](docs/superpowers/research/2026-11-16-vocabulary-review.md#port-acceptance): plain product names, suite/preset distinction, accurate source-backed settings, and workflow terms confined to contributor guidance. | Requiring installers to clone; a course; claiming rates from onboarding smoke runs; teaching `arm`, `bare`, ladder/rung or Baseline Worker as product choices. | proposed — after P8.1; Ben owns onboarding acceptance. |

## Phase 10 — Easy remedies

| Cycle | Ships | Excludes | Status |
| --- | --- | --- | --- |
| **P10.1** | One agnostic remedy candidate addressing an observed Easy failure; its additive selection interface for live Pi and eval; flat cumulative presets and their checks; screen evidence and a preregistered promotion decision if warranted. Declare whether the remedy earns a common Base addition or an Easy addition, and qualify affected presets. Follow [credit](docs/superpowers/research/2026-11-16-remedy-credit.md). | A prefilled Easy stack; multiple new remedies in one cycle; suite-specific answers. | proposed — after P9.1; add one row per further candidate, and close the phase with the measured preset or an explicit unmet target. |

## Phase 11 — Medium remedies

| Cycle | Ships | Excludes | Status |
| --- | --- | --- | --- |
| **P11.1** | One agnostic remedy candidate for an observed Medium failure, measured against the declared baseline with grade and cost meanings fixed. Retain Easy's remedies explicitly and qualify the cumulative Medium preset. If acceptance redispatch is chosen, use the qualified expected/observed feedback contract from [the upstream supplement](docs/superpowers/research/2026-11-16-upstream-acceptance-feedback.md), with its own gate identity and preregistered promotion rule. | Assuming Easy gains transfer without measurement; multiple new remedies per cycle; promoting Andre's n=3 screen as a rate. | proposed — after phase 10 closes; further candidates each get a row and promotion decision. |

## Phase 12 — Hard remedies

| Cycle | Ships | Excludes | Status |
| --- | --- | --- | --- |
| **P12.1** | One agnostic remedy candidate for an observed Hard failure, its evidence and promotion decision, then a verdict against the Hard suite's preregistered target. A documented failure to reach the target is an admissible outcome. | Fine-tuning, DPO or SFT; a reserved model-training phase; retrospective changes to n or grading to obtain a pass. | proposed — after phase 11 closes; further candidates each get a row. |

Closure, releases and ongoing development follow the [same workflow](docs/rules-applicability.md#roadmap-workflow).
