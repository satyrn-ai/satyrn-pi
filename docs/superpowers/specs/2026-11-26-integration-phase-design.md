# Phase 4.5 — Integration: hold, re-cut, land

## Reviewer brief

**Intent:** hold the phase-5 merges until the review's six findings close, open
the phase in the records so the hold is visible, answer Ben's two open page
findings, and leave every record agreeing with what merged. (Paul, 2026-11-26.)

**Decisions:** the phase sits between phases 4 and 5 as **Phase 4.5 —
Integration**; the decimal keeps P5.1–P12.1 stable and the preserved records
untouched, at the cost of one dated line in `BRIEF.md`. The stack is re-cut
rather than repaired: #25/#26/#28/#29 close and P5.1–P5.4 are cut fresh from
their surviving commits, because comment history is not worth preserving on a
new project (Paul, 2026-11-26). Findings 2–5 are fixed inside the re-cut cycles
that own them, so no reviewer sees a broken boundary followed by a patch on it.
Four cycles: open the phase and record #27; correct the page for Ben; re-cut and
review the stack on top of #23; land it with merge commits and reconcile the
records. Nicola approves every pull request; Paul and agents perform the merges
(Paul).

**Non-goals:** phase 5's features; renumbering; a drift-checking script (a
backlog entry with a reopen condition, not machinery); edits to `docs/sdd.md` or
`docs/provenance/`; new measurements; Andre's upstream tree.

**Verification:** every finding closes with a named test shown to fail first, or
a cited record where no test applies; the deployed page already answers 200;
after the landings `git log origin/main..<branch>` is empty for P5.1–P5.4 and the
combined tree re-passes both suites, the document checks and the strict build.

## Intent and why

`main` and the roadmap disagreed with what merged, twice in one week: #21 merged
into `p4.2/reproduce-reference` thirteen seconds after #20 left it (#27's body),
and the approval rule was committed after #18 merged (#22's body). A reviewer
then found six issues in the phase-5 stack, and Ben's read of the published page
produced three findings with no home. This phase is the bounded interval that
closes all of it and ends; it is not a standing chore.

## Position and name

Renumbering phases 5–12 rewrites row IDs across every plan, spec, research note
and BACKLOG entry that says "phase 6" or "phases 10–12" — records this
repository does not edit. Folding the work into phase 4 as P4.4–P4.6 pretends
five phase-5 findings are phase-4 scope. **Phase 4.5** costs one dated line in
`BRIEF.md` ("How we develop"), one clause in its ordered list in "Where to
start", and nothing else. (Assistant.)

## The cycles

| Cycle | Ships | Excludes | Status |
| --- | --- | --- | --- |
| **I.1** | Opens the phase in the records: a `## Phase 4.5 — Integration` section in `ROADMAP.md` carrying these rows, the dated line in `BRIEF.md`, `## Now` naming the hold and phase 5's stack, and the P4.3 landing recorded — merge `6abddbd` (2026-11-26T16:22Z), `/getting-started/` answering 200 (Site run 45858115573), local `p4.2/reproduce-reference` realigned to `08ea436` tracking its own ref. | Any product change; a plan — a record cycle needs none. | proposed — first; nothing is visibly held until this lands. |
| **I.2** | Ben's two open page findings: `mkdir -p ~/models` before the weights `curl`, which fails on a clean machine otherwise; a memory line citing both observations — the reference M5 Max (`ps -o rss` 7.95 GiB, `footprint` 634 MB peak, `plans/2026-11-21-p4.2-reproduce-reference.md` Task 4 Step 2) and Ben's 16 GB laptop at 8.5 GB and swapping — advising 16 GB. A copy-paste walk from a directory with neither folder nor weights proves steps 1–5. Changelog line. | New platforms; new pins; a measurement claimed as a rate; the 404, closed by I.1. | proposed — independent of the stack. |
| **I.3** | The stack re-cut, reviewed as one set of fresh requests. #23 is rebased onto `main` and merged — it carries the phase-5 spec and no implementation, and its discussion is where the shared calls were settled. Then P5.1, P5.2, P5.3 and P5.4 are cut in sequence, each from `main` and then from its parent, each carrying only its own cycle's commits: the inventory is located by subject, never by a remembered SHA, because #25's force-push left the three old ones unreachable. #25 authored seven commits and keeps its four planning ones; the three implementation ones — `b89046c` resolve/gate/record, `990e851` validate resolution, `5ad91dc` require the pinned model — are reachable only through #26 today, so P5.1 takes them and P5.2's cut drops them rather than duplicating them. The old four requests close with a comment naming their replacements. Findings 2–3 are fixed inside P5.3, the cycle that owns the session boundary; findings 4–5 inside P5.1, the cycle that owns resolution and records. Each fix arrives with its failing-first test in the same request. | Findings 6 (closed by hand); scope beyond each cycle's own commits; merging anything in this cycle. | proposed — the stack's first move. |
| **I.4** | The landings and the records: merge P5.1–P5.4 in order as merge commits, restacking each descendant after its parent lands (`BACKLOG.md` and `CHANGELOG.md` conflicts expected, union-resolved in merge order), then one records PR closing the P4.3 and P5.1–P5.4 rows, closing phase 4, moving `## Now` past phase 5, reconciling the changelog, adding the retarget-and-align line to `ROADMAP.md`'s preamble, and the BACKLOG entry below. | Renumbering; preserved-record edits; a second records PR. | proposed — I.1's rows are what this closes. |

BRIEF rule 2 reads per cycle as: I.3's reviewable unit is the four fresh
requests, each one cycle's commits, and I.4 ships through them; I.1, I.2 and the
closing records PR are one new PR each.

## Where each finding lives

| Finding | Destination |
| --- | --- |
| 1. Boundary lost in rebase | I.3's cut restores it by construction — each new request is a diff of its own cycle's commits; the P5.1 row in I.4 describes the merged diff, not the plan. |
| 2. Orphaned child on interrupt | P5.3's test: interrupt a dummy child, assert the group is killed and reaped. |
| 3. Subject loads contributor skills | P5.3's test: a fresh private agent directory loads zero skills; the decision lands in the P5.0 spec's decisions, which I.3 can edit because it re-cuts after #23 merges. |
| 4. Installed-worker resolution | P5.1's sibling pair: `node_modules/satyrn-pi` resolves; two candidates refuse loudly. |
| 5. Late resolution print | P5.1's test: the resolution lines reach stdout before the first spawn. |
| 6. Stale local branch | Closed by hand on 2026-11-26 (`08ea436`, upstream its own ref); recurrence stopped by I.4's procedure line: fetch, confirm the branch tracks its own ref and matches the PR head, and before retargeting check `git log origin/main..HEAD` holds only this cycle's commits. |
| Ben: mkdir, memory | I.2's page and walk; 404 closed and verified live in I.1. |
| Stacked-merge races (#21, #22) | The same procedure line; no pathology entry, because `docs/pathologies.md` records worker failure shapes and these are process findings. |

## Merge order and the stack

I.1 first, because a hold nobody can read is a freeze. I.2 is independent. #23
rebases onto `main`, resolving `CHANGELOG.md` by keeping both entry sets in merge
order — P4.3's lines, then phase 5's — and merges on Nicola's approval of it.
The four re-cut requests follow, each reviewed as a diff against its parent, not
as a range-diff against a force-pushed branch. Each is rebased as its parent
lands. Nothing merges before Nicola approves that request; Paul or an agent
clicks the merge. (Paul, 2026-11-26.)

## Goals, non-goals, anti-goals

Goals: the six findings and Ben's three each have exactly one permanent home; the
roadmap, changelog and `## Now` describe the merged reality; the phase closes.
Anti-goals: a drift check that drags git or network into the default suites
(rule 3; the tripwire stands); a re-cut that changes what a cycle does rather
than where its commits live; a hold that becomes a standing freeze or a phase
that never closes; a P5.1 row claiming what P5.1 does not contain; Ben's
observation restated without its source.

## Constraints

Rules 2, 3, 5 and 9 apply; the re-cut touches only the eval package and the
phase-5 records. Default suites stay model-, network- and subprocess-free.
Budgets hold: this spec at 150 lines, each plan at 250. `docs/sdd.md` and
`docs/provenance/` stay byte-for-byte.

## Decisions

- Phase named **4.5 — Integration**; no renumbering. (Assistant.)
- #27 landed ahead of the phase, on my recommendation. (Paul, 2026-11-26.)
- The stack is re-cut, not repaired: #25/#26/#28/#29 close, P5.1–P5.4 are cut
  fresh from their surviving commits, comment history is not preserved. (Paul:
  "this is a new project".)
- The phase owns the re-cut and the landing; Nicola approves, Paul or an agent
  merges. (Paul.)
- Findings 2–5 fold into the cycles that own them rather than shipping as a
  repair PR, because the re-cut is happening anyway and one review should see
  the whole truth. (Assistant.)
- Findings 2, 3 and 5 are unit-tested through an injected spawner and argv
  builder: the suites ban subprocess, the guard scans every `tests/` file, and Pi
  is a peer dependency, so CI has no Pi to load. The real-child skill check goes
  to BACKLOG with a reopen condition. (Assistant.)
- The SHAs this spec first cited were orphaned by #25's force-push; the cut
  locates commits by subject and checks reachability first. (Assistant, after
  the builder check.)
- #23 is rebased rather than re-cut: it carries no implementation, and its
  discussion is where the shared calls were settled. (Assistant.)
- The phase opens in the records before any repair, so the hold is readable.
  (Assistant.)
- Process findings become a procedure line in `ROADMAP.md`'s preamble, not
  pathology entries; that file maps preserved source rules. (Assistant.)
- The page advises 16 GB, citing both machines: Ben's prose and my call, not a
  measurement of this stack. (Assistant.)
- I.2 merges on the documentation rule — green check plus Paul's authorisation —
  with Ben's read advisory. (Assistant.)

## Delegated decisions

None outstanding. The re-cut question was answered on 2026-11-26, and a fold-in
that turns out to be wrong costs one extra review round, which this phase has
room for.

## Left to the builder

The exact Pi 1.5.2 mechanism that disables skill discovery; how the injected
spawner is shaped, since it becomes the extension point (rule 6); the page's
sentences (Ben's lane); the cut sequence and how each old request is closed; the
BACKLOG entries' wording.

## Verification

Every finding's test is shown to fail before its fix, inside the re-cut cycle.
After I.4: `git log origin/main..<branch>` is empty for P5.1–P5.4; the combined
tree passes both suites, the document checks and the strict build (the review's
baseline: 158 pytest, 111 node); the P4.3 and P5.x rows match the merged diffs;
`## Now` points past phase 5.
