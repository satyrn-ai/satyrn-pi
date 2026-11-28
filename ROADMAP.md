# Satyrn Pi roadmap

Scope: [BRIEF](BRIEF.md). Process: [Superpowers/SDD and roadmap rules](docs/rules-applicability.md#roadmap-workflow).

## Now

In flight: [P4.5](#phase-45--integration), the integration interval, opened by this pull request. Phase 4 is closed: P4.2 merged as #20, and P4.3 landed on `main` through #27 after missing it by thirteen seconds in #21.
Held: [P5.1](#phase-5--eval-cli)–[P5.4](#phase-5--eval-cli) wait for I.3's re-cut, because the review found six issues in the stack and one of them moved P5.1's implementation into #26.
Parked: preset choices and rented-host qualification await their [research owners](BRIEF.md#decisions-the-research-documents-own).
Next: [I.2](#phase-45--integration), Ben's two page findings, and [I.3](#phase-45--integration), the re-cut.

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
| **P3.1** | Infrastructure: a minimal `zensical.toml` (`strict = true`, `docs_dir = docs`, `site_dir = site`, palette and features only), the Satyrn stylesheet adopted from `satyrn-ai/satyrn-website` at `7508bd7` with the adopted assets recorded, Home and Glossary navigation, and a home page. Publishes exactly those two pages: the glossary stays the single source at [docs/glossary.md](docs/glossary.md), edited only enough to keep both pages inside the site. A file-reading check asserts the published set is exactly `index.md` and `glossary.md`, because exclusion alone fails open. `uv run zensical serve` is the local preview under the [site acceptance rules](docs/rules-applicability.md#documentation-site-acceptance). | CI, Pages or any deployment; `zensical_glossary` and automatic term links; alias changes; installer or contributor guides; the source site's blog, hero, feed and landing config; a shared theme package. | closed 2026-11-20 — merged as PR #14; `zensical build --strict` green, 16 files out (two pages, `404.html`, `sitemap.xml`, `search.json`, assets), and the published-set test fails on a planted page. Live at the site address |
| **P3.2** | Infrastructure: the repository's first workflow — one file, two jobs. A build job on pull requests and `main` (`actions/checkout`, Node at the `package.json` engines floor, `npm ci`, `astral-sh/setup-uv`, `uv sync --locked`, `npm test`, `uv run pytest`, `uv run zensical build --strict --clean`) uploads the Pages artifact; a deploy job gated to `main` with the `github-pages` environment, Pages permissions and a concurrency group publishes it. `site_url` becomes the deployed address, recorded here and in `README.md`, and verified by opening the deployed pages after the first `main` deploy. | New content; glossary configuration; a custom domain; caching Zensical's output; marked integration tests; branch protection as a policy change. | closed 2026-11-20 — merged as PR #15; the workflow is green on pull requests and on `main`, and the first `main` deploy succeeded. <https://satyrn-ai.github.io/satyrn-pi/> answers 200 with the stylesheet and font, and the glossary page loads |
| **P3.3** | `zensical_glossary` configured against [docs/glossary.md](docs/glossary.md) — `heading_level = 3`, `first_only = true`, `base_url` matching the deployed page — with aliases reviewed against the [vocabulary decisions](docs/superpowers/research/2026-11-16-vocabulary-review.md#port-acceptance), first-prose-occurrence links and tooltips verified in rendered pages, exclusions confirmed for code, headings and existing links, the same term shown to stay plain inside a code span, and the list of terms that actually fired read on both pages. | New glossary entries beyond the alias review; a repository-wide terminology sweep; hand-linked prose terms; misleading legacy aliases. | closed 2026-11-20 — merged as PR #16; the deployed home page links `task` once, to `glossary/#task`, with tooltips on. Aliases reviewed: `agent configuration` and `session record` removed, three kept |

## Phase 4 — Getting Started setup: llama.cpp

The phase's shared calls — who the page serves, what it promises, the platform,
and which build and weights are the subject — are settled in the
[P4.0 spec](docs/superpowers/specs/2026-11-21-p4.0-getting-started-design.md).
Each row below carries its own plan when it opens.

| Cycle | Ships | Excludes | Status |
| --- | --- | --- | --- |
| **P4.1** | The reference host card: llama.cpp b12066's source commit and the official `llama-b12066-bin-macos-arm64.tar.gz` asset digest, the Q4_K_M GGUF's Hugging Face revision, size and sha256, the preserved settings, and the whole serve command, each quoted with the metadata it came from. Darwin arm64 is the documented reference platform; every other platform is published as unverified. | Fetching an artifact; a running server; any site change; a second quant or build. | closed 2026-11-24 — merged as PR #19. The card pins b12066 by commit and asset digest and Q4_K_M by revision and sha256; Andre's review corrected the premise that a container digest was ever the llama batch's. [Card](docs/superpowers/research/2026-11-21-reference-host-card.md). |
| **P4.2** | b12066 installed beside Homebrew's 12110 from that asset, the weights fetched and verified against the card, a served model at `127.0.0.1:8001`, a demonstrated answer, the walk through the page's steps from a directory with neither build nor weights, and the startup allocation with the observed footprint. | Publishing; prose; an eval-managed server lifecycle; a machine nobody here has touched. | closed 2026-11-24 — merged as #20. The walk is recorded, the pinned binary and weights served, and the answer came from that server ([plan](docs/superpowers/plans/2026-11-21-p4.2-reproduce-reference.md)). |
| **P4.3** | Getting Started at `docs/getting-started.md`: numbered steps rendered from P4.2's walk, the digests and build tag, the two macOS failures named, a nav section, the site's third published page with its published-set test updated deliberately, and a check that the page's digests still match the card. | Phase 9's walkthrough sections; setup for unverified platforms; a fourth page. | closed 2026-11-26 — merged into the stack as #21 and landed on `main` by #27 (`6abddbd`). The page answers 200 with its five steps; Ben's page findings are I.2's. |

## Phase 4.5 — Integration

The interval that holds the phase-5 stack until its review findings close. Its calls, its cycle boundaries and its merge order are settled in the [P4.5 spec](docs/superpowers/specs/2026-11-26-integration-phase-design.md); it ends rather than becoming a standing chore.

| Cycle | Ships | Excludes | Status |
| --- | --- | --- | --- |
| **I.1** | Opens the phase: this section, the dated line in `BRIEF.md`, `## Now` naming the hold, and the P4.3 landing recorded, including the realignment of the local `p4.2/reproduce-reference` branch. | Product change; a plan — a record cycle needs none. | proposed — this pull request. |
| **I.2** | Ben's two page findings: `mkdir -p ~/models` before the weights download, and a memory line citing both machines — the reference rig's 7.95 GiB RSS against his 16 GB laptop at 8.5 GB and swapping — advising 16 GB, with a copy-paste walk as proof. | New platforms; new pins; a measurement claimed as a rate; the 404, closed by I.1. | proposed — independent of the stack; Ben's prose. |
| **I.3** | The stack re-cut: #23 rebased onto `main` and merged, then P5.1–P5.4 cut fresh from their surviving commits, each carrying only its own cycle, with findings 2–3 fixed inside P5.3 and 4–5 inside P5.1. The four old requests close with pointers to their replacements. | Scope beyond each cycle's own commits; merging in this cycle. | in flight — [plan](docs/superpowers/plans/2026-11-26-p4.5-i3-recut.md) merged; the cut is under way. |
| **I.4** | The landings as merge commits, then one records PR closing P5.1–P5.4, closing phase 4's records, moving `## Now` past phase 5, and adding the retarget-and-align line to this file's preamble. | Renumbering; preserved-record edits; a second records PR. | proposed. |

## Phase 5 — Eval CLI

The phase's shared calls — what P5.1 owns, the resolution order, the record
contents and the counting rules — are settled in the
[P5.0 spec](docs/superpowers/specs/2026-11-24-p5.0-eval-cli-design.md).

| Cycle | Ships | Excludes | Status |
| --- | --- | --- | --- |
| **P5.1** | The `satyrn-pi eval` entry point: worker resolution via explicit `--worker` else the installed npm package, Pi resolved and checked against the declared peer range, suite selection, `--base-url` with a preflight health check, printed resolution, `job.json` and `run.json` under `runs/`, and the counting rules for Model requests and Elapsed seconds — proved with fixtures. | Any child process; workspaces; deadlines; suites and graders; a verdict or a score; publishing the package. | in flight — resolution, records and the eval guide are built and tested on fixtures; 59 pytest. |
| **P5.2** | Workspace preparation from a task's fixture: base copy, variant overlay including deletions, the prompt written beside it, and `trial.json` at `prepared`. A partial trial is repudiated as non-final rather than presented as a result. | Any child process; spawning Pi; a deadline; grading. | proposed — stacked on P5.1. |
| **P5.3** | The Pi child in print mode: a private agent directory, closed stdin, a shared session directory, extensions loaded in order, the `session ended` boundary in `trial.json`, and the trajectory captured as a session artifact. | The deadline and process-group kill, which P5.4 owns; grading; remedies. | proposed — stacked on P5.2, and the first cycle needing a deliberate test path. |
| **P5.4** | The deadline and the process-group kill, `stopped` as a status distinct from `failed`, and one trial end to end against a stub task with a real Pi session. | Grading, which P6.1 owns; suites; a verdict or a score. | proposed — stacked on P5.3. |

## Phase 6 — Suites

The phase's shared calls — the six cycles, the copy and its provenance categories, the
authored suite manifests, the grading seam, the isolation and bound, grade identity and
the primary grade — are settled in the
[P6.0 spec](docs/superpowers/specs/2026-11-26-p6.0-suites-and-grading-design.md), with
its [grading environment note](docs/superpowers/research/2026-11-26-grading-environment.md).
The P5.4 row and the P5.0 spec say grading belongs to P6.1; I.3 corrects both to
"grading starts in P6.2", and this phase checks the inherited wording after the stack
rebases.

| Cycle | Ships | Excludes | Status |
| --- | --- | --- | --- |
| **P6.1** | Suite data and provenance: the 95 non-grader files copied byte-verbatim from `mellum-worker` `0e4a9b68` into `src/satyrn_pi/suites/suite-<name>/source/`; `SOURCES.json` distinguishing `copied`, `reference` (the 24 source grader files, no local copy) and `authored`, with the hashes recomputed by a test and the loader's file-set check counting only `copied` and `authored`; an authored `suite.json` per suite, its instruction the joined prompts under `promptMode: joined`; loader refusals for a duplicated expected ID, an absent grader module, a wrong prefix and a stray file; the repository-weight budget raised to 320 files and 2.5 MB. | Grading; any child process; a verdict; copied graders; the source's layout, leak and contamination markers. | in flight — suite data, manifest and loader built and tested; graders land in P6.2 ([plan](docs/superpowers/plans/2026-11-26-p6.1-suite-data.md)). |
| **P6.2** | Bounded grading for Easy: the `grade(workspace, suite, *, graders, runner, timeout)` seam, a stub runner in the default suite and the spawning adapter beside `RealProcess`; the grader copy outside the workspace with the workspace's pytest configuration, `PYTEST_ADDOPTS`, `PYTEST_PLUGINS` and plugin autoloading suppressed and the environment recorded; `verdict.json` with its outcome; the trial reaching `graded`; the timeout with process-group cleanup; exit 0/1/2 as the outcome table fixes; Easy's four graders re-earned and proven against its known-good and known-broken trees. | Medium's and Hard's graders; cross-suite qualification; feedback; the guide. | proposed — stacked on P6.1. |
| **P6.3** | Medium's grader: its 18 preserved checks re-earned under the source's module and test names, proven against Medium's own known-good and known-broken trees, with any divergence recorded rather than reconciled. | Making a check agree with its witness; Hard's grader; the gap record. | proposed — stacked on P6.2. |
| **P6.4** | Hard's grader: its 34 preserved checks re-earned the same way, including the migration and visit checks, proven against Hard's own witnesses. | The same exclusions as P6.3; a demo or fine-tune answer. | proposed — stacked on P6.3, because Hard's contract differs from Medium's. |
| **P6.5** | Cross-suite qualification: `witnesses.json` per suite recording, per check, whether the inherited grade accepts or rejects each witness; the gaps that leniency leaves visible; execution-environment witnesses — a hostile workspace `conftest.py` and `pyproject.toml`, an inherited `PYTEST_ADDOPTS`, and a hanging app that must end `timed-out` with its group gone; the marked integration path and its skip test; the qualification record with commands, tails and hashes. | Correcting inherited semantics; a model run; CI running the marked test; a measured rate. | proposed — stacked on P6.4. |
| **P6.6** | Feedback and the guide: expected/observed feedback under its own rule version and hash, re-earned from `3e20e161` with the wrong-favicon and route-only-ID witnesses and recorded apart from the grade's `0e4a9b68`; `docs/scoring-and-evidence.md`; glossary entries for grade, verdict and witness. | Redispatch or settle gates; merging gate-message versions; the Education challenge UI; a measured rate. | proposed — stacked on P6.5; closes the phase. |

## Phase 7 — Vanilla

| Cycle | Ships | Excludes | Status |
| --- | --- | --- | --- |
| **P7.1** | Vanilla: only Pi and the trace recorder, no worker or remedies; isolated settings, resolved model/host/grader provenance, and a recorded baseline. Specify how to select Vanilla independently of the suite. Fix the intended context-file policy and other run settings before deciding runs. | Preset promotion; a worker-loaded run described as Vanilla; inherited rates presented as new-stack measurements. | proposed — after phase 6 closes: its baseline needs qualified grading, not just suite data. |

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
