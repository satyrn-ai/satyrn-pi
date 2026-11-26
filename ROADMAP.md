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
| **I.2** | Ben's two page findings, plus a third the walk found: `mkdir -p ~/models` before the weights download, now guarded by a check that fails any page writing into a directory it never creates; a 16 GB memory line citing both machines — about 8 GiB resident on the reference rig against his 16 GB laptop at 8.5 GB and swapping; and `max_tokens` raised to 1024, because at 256 the model spent the whole budget thinking and returned an empty `content`. A copy-paste walk in a throwaway `$HOME` proves steps 1–5. | New platforms; new pins; a measurement claimed as a rate; the 404, closed by I.1. | in flight — this pull request; Ben's prose. |
| **I.3** | The stack re-cut: #23 rebased onto `main` and merged, then P5.1–P5.4 cut fresh from their surviving commits, each carrying only its own cycle, with findings 2–3 fixed inside P5.3 and 4–5 inside P5.1. The four old requests close with pointers to their replacements. | Scope beyond each cycle's own commits; merging in this cycle. | proposed — the stack's first move. |
| **I.4** | The landings as merge commits, then one records PR closing P5.1–P5.4, closing phase 4's records, moving `## Now` past phase 5, and adding the retarget-and-align line to this file's preamble. | Renumbering; preserved-record edits; a second records PR. | proposed. |

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
