# Grading environment and suite provenance

## What is measured / what is conjecture

**What is settled here:** the decisions the P6.0 spec needs for P6.1 and P6.2 —
provenance categories, the authored suite manifest, the pytest isolation policy, the
grading bound and its outcomes, the exit contract, and joined-prompt comparability.
These follow from `BRIEF.md` (graders run from a copy outside the workspace; default
tests spawn nothing), the [grading note](2026-11-16-grading-compatibility.md) (copy
fixtures and expectations, re-earn graders, qualify against worker-controlled pytest
configuration) and the pinned source at `0e4a9b68`.

**What is conjecture:** that a rewritten grader agrees with every preserved check on
every witness, and that the controlled environment reproduces the source's outcomes.
P6.2–P6.5 produce that evidence; nothing here claims it yet.

## Provenance categories

`SOURCES.json` per suite has three lists.

| Category | Contents | Local file |
| --- | --- | --- |
| `copied` | 95 files: `base/`, `fixtures/known-good/`, `fixtures/known-broken/`, `expected.json`, `layout.json`, `prompts/` | yes, byte for byte |
| `reference` | 24 source grader files under `grader/`, 13 of them test modules, plus the `canary` token | no |
| `authored` | the suite manifest and the rewritten graders | yes, port-owned |

Each entry carries its source path, the commit `0e4a9b68` and its SHA-256. A test
recomputes every `copied` hash from disk and fails on a one-byte edit.

The loader compares the suite's file set against `copied` plus `authored` **only**.
`reference` entries name files that exist in the source and deliberately not here, so
they must never read as missing; the first implementation that ignores this turns 24
remote references into 24 false failures. `reference` is evidence that the rewrite was
made against a pinned original, not a copy waiting to be written.

`grader/` is not copied at all. [Grading compatibility](2026-11-16-grading-compatibility.md)
fixes the boundary: fixtures, expectations and run records verbatim; grader
implementation and tests re-earned. Copying the graders and executing the copy would
be a transplant, which BRIEF's "what is re-earned" forbids.

## The authored suite manifest

`resolve_suite` reads `suite-<name>/suite.json` and requires `id`, `instructions`,
`fixture` and `verification` on every task. The source has no such file, so each
suite gains an authored one with a single task:

- `fixture: "source"` — `workspace.prepare` resolves `fixture/base`, so the copied
  `source/base/` is the starting workspace with no code change;
- `instructions` — the suite's prompts, joined in order;
- `promptMode: joined` — part of the task's identity, not decoration (below);
- `verification` — a sentence naming the preserved expectation file, so the task
  describes what it is graded by without restating it.

## Joined prompts

The source loads `prompts/*.md` in sorted order and, in its own `single_prompt` mode,
delivers them as one message joined by blank lines (`learn/code/harness.py:669`).
Easy has one prompt; Medium has four and Hard eleven, and every suite's `01.md` asks
only for the home page. Delivering `01.md` alone and then grading 18 or 34 checks
would grade work the agent was never asked to do, so the port joins them and records
`promptMode: joined`.

A joined trial is comparable with a source run made in the same mode. It is not
comparable with the source's per-prompt sessions, which restart Pi per prompt and
interleave acceptance gates; comparing the two needs its own qualification, and the
scoring guide says so.

## Pytest isolation

Grading runs after the session, outside the workspace. The suite's `graders/` is
copied to a temporary directory that becomes the working directory, and the workspace
sits on `PYTHONPATH` so the candidate's `app` is what the graders import. The
workspace therefore holds no grader files at all — the source instead copies them to
`<workspace>/grader_tests`, which BRIEF's boundary forbids and this note records as a
deliberate difference from the source execution path.

Disabling configuration discovery is not enough, because the worker controls the
workspace. The grading run must:

- never read the workspace's `conftest.py`, `pyproject.toml`, `pytest.ini` or
  `setup.cfg`;
- drop inherited `PYTEST_ADDOPTS` and `PYTEST_PLUGINS` rather than pass them through;
- disable plugin autoloading, so an installed plugin cannot change collection;
- record the interpreter, argv, working directory and complete environment in the
  verdict, and hash the argv and environment into the grade.

A hostile witness in P6.5 proves a workspace `conftest.py`, a workspace
`pyproject.toml` and an inherited `PYTEST_ADDOPTS` cannot change a verdict.

## Bound and outcomes

Graders import and run candidate code, so grading needs its own bound: Pi's deadline
ends the session, not the grader. The runner takes a timeout; on expiry the adapter
kills the process group, and an interrupted run does the same cleanup.

`outcome` is `graded`, `timed-out` or `grader-error`, and only `graded` sets `passed`
or moves `trial.json` to `graded`. A time-out or error writes the record, leaves the
trial at `session-ended` — never inventing a verdict or a score — ends the run as
`stopped`, and starts no further trial. A trial already `stopped` is never graded;
`trial.py` refuses to leave a final status.

## Exit status

`cli.py` returns 0 for a clean run and 2 for a stopped one. Grading extends that
without changing the existing meaning:

| Outcome | Trial | `run.json` | Exit |
| --- | --- | --- | --- |
| every trial graded and passed | `graded` | `graded` | 0 |
| a completed grade fails its primary checks | `graded` | `graded` | 1 |
| grader error or no grader ran | `session-ended` | `graded` | 1 |
| deadline or grader time-out | `stopped` / `session-ended` | `stopped` | 2 |

## Weight

The copy is 95 files and 867,403 bytes; with the tree's 128 files and 922,653 bytes
that is 223 files and 1,790,056 bytes before the rewritten graders and their tests.
The budget rises from 200 files and 1 MB to 320 files and 2.5 MB. The check exists to
keep run output, traces and workspaces out of the tree; pinned inputs and re-earned
graders are neither.

## The verdict

`verdict.json` sits beside `trial.json` and separates what was graded from how it ran.

| Field | Contents |
| --- | --- |
| `suite` | suite name and version |
| `grade` | `id` (`<suite>/<grade_version>`), `primary` flag, `hash` |
| `checks` | `[{id, passed}]`, one entry per expected ID |
| `missing` | the expected IDs without a `PASSED` line |
| `outcome` | `graded`, `timed-out` or `grader-error`; only `graded` carries `passed` |
| `environment` | interpreter, argv, working directory, pytest environment |
| `grader` | copied-from path and per-file SHA-256 |

A grade's hash covers `checks`, the grader hashes, the argv and the environment — not the
feedback rule, which carries its own version and hash. The two are separate claims: a message
can change what the agent does next without changing what its finished work earned.

## Left to the builder

- Module layout: whether suites, grading and feedback are one module or three.
- The exact pytest flags and interpreter resolution that satisfy the isolation above, and
  whether the workspace's own environment is reached through `uv` or an interpreter path.
- How the stub represents a time-out and a grader error, and how the adapter reports the
  process group's death.
