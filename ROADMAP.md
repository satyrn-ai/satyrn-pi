# Satyrn Pi roadmap

Scope: [BRIEF](BRIEF.md). Process: [Superpowers/SDD and roadmap rules](docs/rules-applicability.md#roadmap-workflow).

## Now

In flight: [P3.1](#phase-3--zensical-documentation), the site's identity, with P3.2's deployment and P3.3's glossary links stacked above it; all three await review of #13–#16.
Parked: preset choices and rented-host qualification await their [research owners](BRIEF.md#decisions-the-research-documents-own).
Closed: Phase 1 and Phase 2 merged to `main` on 2026-11-20 as PRs #2–#12.

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
| **P1.2** | Documentation: worker/eval responsibilities, import direction and shared run meaning in `docs/domain.md`; canonical terms in `docs/glossary.md`, with a numeric jargon budget and checker scope for phase 2. Apply the [vocabulary decisions](docs/superpowers/research/2026-11-16-vocabulary-review.md#port-acceptance); review Vanilla on the Easy suite and Base with an empty preset to expose ambiguity. | Runtime code; a generic domain framework; detailed CLI/schema design; new names for concepts ordinary language already explains. | closed 2026-11-20 — merged as PR #6 with its plan; the jargon budget and retired-term check were carried into P2.4 |

## Phase 2 — SDD setup

| Cycle | Ships | Excludes | Status |
| --- | --- | --- | --- |
| **P2.1** | Infrastructure: contributor `README.md`; `npm run setup` running locked `npm ci`/`uv sync` and installing Superpowers as a ref-pinned Pi git package (`bb92a77`, `v7.0.0`), refusing a different existing ref without `--yes`; the revision and setup record with its upgrade policy; a fresh-clone proof. The rows below record the split of the original phase 2 scope. | Runtime code; root `AGENTS.md`; wrapper skill; executable gates; loading skills into the subject worker. | closed 2026-11-20 — merged as PR #7; `npm run setup` pins Superpowers `bb92a77` and refuses a different ref without `--yes` |
| **P2.2** | Infrastructure: root `AGENTS.md` as the index to the effective rules; a thin local wrapper skill pointing at repository policy without duplicating Superpowers; `BACKLOG.md`; `docs/pathologies.md`; byte-verification of the preserved `docs/sdd.md` and `docs/provenance/mellum-worker-AGENTS.md` against source `0e4a9b68`. Adds numeric document budgets: a required ≤ 30-line reviewer brief at the top of a spec; rationale beyond the brief links to a research note, plans reference spec decisions instead of restating them, and a decision that would otherwise be lost moves to the decisions table — it is never dropped to meet the budget. | Education material; copying Superpowers into the repository; transplanting source tests; executable gates (P2.3–P2.5). | closed 2026-11-20 — merged as PR #8; root `AGENTS.md`, the routing skill, the backlog and pathology records, and the budgets P2.3 enforces |
| **P2.3** | Infrastructure: re-earned cap, plan-lifecycle and evidence-wording checks, each shown to fail first, wired into the default Node suite. The cap check enforces P2.2's budgets (spec 150, plan 250, reviewer brief 30), the lifecycle check covers plans, and the wording check covers research notes; an over-budget document goes to a research note or a split cycle, not deletion. | Runtime measurement claims; tests requiring obsolete glossary headings; the vocabulary gates (P2.4). | closed 2026-11-20 — merged as PR #9; cap, lifecycle and wording checks in `npm test`, each shown to fail first |
| **P2.4** | Infrastructure: P1.2's numeric jargon budget and retired-term check, with point-of-use exemptions and a planted violation that fails before it is reverted. | A blanket ban on ordinary English; editing documents from the check; hand-maintained exemption lists. | closed 2026-11-20 — merged as PR #10; the 25-term jargon budget and retired-term check with point-of-use exemptions |
| **P2.5** | Infrastructure: the default-test tripwire and the one-way import check, each shown to fail first. | Runtime code; model, network or subprocess in the default suites. | closed 2026-11-20 — merged as PR #11; the default-test tripwire and the one-way import check, each with a planted proof |
| **P2.6** | A new contributor's agent finds the rules and follows a cycle, using this phase's own artifacts; phase close resolves every active path and runs both default suites. | Inventing a product feature to prove process; an unreviewed negative outcome; runtime setup claims. | closed 2026-11-20 — merged as PR #12; the discovery run is recorded, every active path resolves, and both default suites pass |

## Phase 3 — Zensical documentation

| Cycle | Ships | Excludes | Status |
| --- | --- | --- | --- |
| **P3.1** | Infrastructure: a minimal `zensical.toml` (`strict = true`, `docs_dir = docs`, `site_dir = site`, palette and features only), the Satyrn stylesheet and overrides adopted from `satyrn-ai/satyrn-website` at `7508bd7` with the adopted assets recorded, Home and Glossary navigation, and a home page. Publishes exactly those two pages: the glossary stays the single source at [docs/glossary.md](docs/glossary.md), edited only enough to keep both pages inside the site. A file-reading check asserts the published set is exactly `index.md` and `glossary.md`, because exclusion alone fails open. `uv run zensical serve` is the local preview under the [site acceptance rules](docs/rules-applicability.md#documentation-site-acceptance). | CI, Pages or any deployment; `zensical_glossary` and automatic term links; alias changes; installer or contributor guides; the source site's blog, hero, feed and landing config; a shared theme package. | proposed 2026-11-19 — first of three cycles split at the phase-3 brainstorm; starts after Phase 2 closes. The URL defaults to `https://satyrn-ai.github.io/satyrn-pi/`; a custom domain would be a later recorded change. Spec owed at cycle start. |
| **P3.2** | Infrastructure: one GitHub Actions workflow — a build job on pull requests and main (`astral-sh/setup-uv`, `uv sync --locked`, `uv run zensical build --strict --clean`), then a deploy job gated to main with the `github-pages` environment, Pages permissions and a concurrency group; Pages configured to publish from Actions; the public URL recorded here and in `README.md`; the deployed site verified in light and dark under its base path. | New content; glossary configuration; a custom domain; caching Zensical's output; claiming the URL before it is verified. | proposed 2026-11-19 — after P3.1, and only once the site builds strictly. The recorded `site_url` is `https://satyrn-ai.github.io/satyrn-pi/`. Spec owed at cycle start. |
| **P3.3** | `zensical_glossary` configured against [docs/glossary.md](docs/glossary.md) — `heading_level = 3`, `first_only = true`, and `base_url` matching the deployed path — with aliases reviewed against the [vocabulary decisions](docs/superpowers/research/2026-11-16-vocabulary-review.md#port-acceptance), first-prose-occurrence links and tooltips verified in rendered pages, exclusions confirmed for code, headings and existing links, and a planted term shown to fail the link check before it passes. | New glossary entries beyond the alias review; a repository-wide terminology sweep; hand-linked prose terms; misleading legacy aliases. | proposed 2026-11-19 — last, because links must be checked under the deployed base path rather than `/`. Spec owed at cycle start. |

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
