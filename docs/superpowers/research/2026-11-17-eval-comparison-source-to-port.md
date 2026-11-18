# Eval comparison: source evidence versus port commitments

Input for the phase-6 suites spec. It states what the source tree's evals
currently report, what this repository has already committed to, where the two
match and where they diverge on purpose, and what phase 6 must therefore
re-earn. It decides nothing: preset membership and any ported number are earned
by runs on this repository's own stack, under
[grading compatibility](2026-11-16-grading-compatibility.md) and
[remedy credit](2026-11-16-remedy-credit.md).

## What is measured / what is conjecture

**What is measured:** retrieval on 2026-11-17 of the source repository
`andrevanzuydam/mellum-worker` at `main` (`9478baed`), its preset files and its
recorded screens. These are the source's own n=3 screens — leads in that
project, not settled rates, and here they are provenance, not this repository's
results.
**What is conjecture:** that a rewritten satyrn-pi stack reproduces any of these
numbers. No satyrn-pi eval has run; the eval CLI is P5.1 and the suites are P6.1.

## The provenance boundary this note sits behind

The seed pin is `0e4a9b68` (2026-11-13); the [brief](../../../BRIEF.md) keeps it
there and treats a later source commit as "one named adoption with its own
review, not a background refresh." Most eval evidence below landed **past the
pin** and is therefore **source drift, not adopted scope**:

- `9ffcc799` — baseline-worker becomes the tested base; tier presets nest on it.
- `2bdd36cc` — the baseline gains `guard/no-live-server`.
- `003fa16c` / `9cacaba0` — the medium preset screened on Medium (2026-11-17).
- `22a04824`, `9478baed` — Hermes/DeepSeek-harness learnings and a plain-Python
  Satyrn harness sketch; research, nothing run on the subject.

Phase 6 copies fixtures and expectations from the pinned revision. Adopting any
post-pin preset or screen is a separate, named decision with its own review, not
a thing this note or the P6 spec may import silently.

## Source evals as they stand (provenance)

Presets in the source are **measured, nested** settings. Verified in the current
tree:

| Source preset | Units | Latest recorded screen |
| --- | --- | --- |
| `baseline-worker` = `easy` | `prompt/name-the-layout`, `prompt/python-developer`, `guard/foreground-server`, `prompt/verify-the-spec`, `guard/no-live-server` (5) | Easy 6 of 6 on the four units that passed, no-live-server folded in (`9ffcc799`, `2bdd36cc`) |
| `medium` | the baseline five + `guard/repeat-loops`, `guard/outside-workspace`, `guard/exists`, `nudge/redirect-followed` (9) | 18/18 on 2 of 3, mean 73 requests (`9cacaba0`); prior screen 18/18 on 3 of 3 at 42 |
| `hard` | identical to `medium` at this revision | not yet differentiated |

Grade identity, carried verbatim: Easy is a **four-check** grade; Medium is an
**18-check** grade. The source's published Easy rates (for example 5/6 on
2026-11-12) are four-check numbers. Cost is **requests**, with `turns` equal to
`requests` in the source harness and `wall` read from the trace span; the source
reply acknowledges the turns/requests conflation. The medium-on-Medium screen's
one miss is the Phase-4 id behaviour (distinct auto ids, resolve, reopen), and
the expected/observed messages did not close it at n=3 — a lead the source
itself flags, not a rate.

## What this repository has already committed

- **Presets start empty.** `base.json`, `easy.json`, `medium.json` and
  `hard.json` begin with empty remedy lists, filled only by runs on this stack
  ([brief](../../../BRIEF.md), "Presets are results"). This is the deliberate
  divergence from the source's nested measured presets; Andre's refusal to empty
  the source presets and the disagreement are preserved in
  [remedy credit](2026-11-16-remedy-credit.md).
- **Grades are preserved and versioned, never silently corrected.** The
  inherited grade stays the primary number; Easy's four checks stay primary. A
  stricter or corrected grade runs beside it under its own name and version
  ([grading compatibility](2026-11-16-grading-compatibility.md)).
- **Cost reported as Model requests and Elapsed seconds**, with documented
  counting and aggregation (roadmap P5.1); imported records keep the source's
  historical turns/requests meaning, and new accurate fields get their own
  definitions.
- **Excluded:** "inherited rates presented as new-stack measurements" (roadmap
  P7.1); a settle/redispatch remedy enabled inside P6 (roadmap P6.1).

## Where they match

- **Methodology is identical.** Requests-as-cost; an n=3 screen is a lead and
  the verdict is a preregistered ladder run; grades preserved and versioned;
  failed, unrun and grader-blind cases distinguished.
- **The remedy units port over.** This repository's remedy kinds — `guard`,
  `nudge`, `prompt`, `context`, `tool`, `check`, `workflow` — already cover every
  unit the source presets name (`guard/no-live-server`, `nudge/redirect-followed`,
  `prompt/name-the-layout`, and the rest). The ingredients cross the boundary;
  the recipe does not.
- **The grader contract matches.** Easy's four-check grade is primary on both
  sides; Medium's 18-check grade is the source's reported number and P6 copies
  its expectations unchanged.

## Where they diverge, on purpose

- **The numbers do not carry over.** Easy 6/6 and Medium 18/18-on-2-of-3 are
  source evidence, not satyrn-pi results. The port rebuilds each preset from zero
  and must reproduce or dispute those numbers on the rewritten stack.
- **Preset shape differs.** The source nests *measured* presets from a non-empty
  baseline; this repository starts every preset empty and earns each addition
  through its own cycle and promotion decision, with affected later presets
  requalified before any new claim.

## What phase 6 must do with this

1. Copy the pinned Easy/Medium/Hard fixtures and expectations verbatim; record
   their source hashes. Do not import a post-pin preset or screen.
2. Keep Easy's four-check grade primary; version any stricter grade separately.
3. Define the Model-requests and Elapsed-seconds fields before publishing a
   score; do not compare them against the source's historical `turns`.
4. Treat the source's nested presets and its medium-on-Medium screen as leads
   about *where* remedies may help (the Phase-4 id miss, the no-live-server
   addition), not as settings to adopt. Each lands, if at all, as a P10–P12
   remedy cycle with its own screen and preregistered promotion.
5. Report turns and wall per rep and rank passes by cost: among passes, a
   shorter run is the stronger result. (This is the one source reporting rule
   the brief records the showing half of but not yet the ranking half; P6 should
   state it.)

## What would falsify this

A mismatch between the pinned fixture/expectation hashes and what P6 copies
falsifies the verbatim-copy claim. A rewritten grader disagreeing with a
preserved source witness build needs diagnosis before any compatibility claim.
Treating any source screen above as a satyrn-pi rate — rather than as
provenance — violates the brief's exclusion and this note.

## Risks

The source numbers are n=3 screens and read as more settled than they are; the
one Medium miss shows the spread. The pin will keep drifting as the source adds
eval work, so this comparison is dated; re-retrieve before the P6 spec is
written and record any newly landed screen as drift until named for adoption.
