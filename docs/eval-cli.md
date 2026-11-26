# Running an eval

`satyrn-pi eval` resolves every input the result will cite, refuses to start when
one of them is wrong or ambiguous, and writes a record of what it resolved before
anything is asked of a model.

**Availability:** P5.1 ships resolution and records. P5.2 prepares each trial's
workspace. P5.3 starts one Pi child per trial in print mode. P5.4 bounds that child
with a deadline and records a stopped trial as stopped. No task is graded and no
verdict exists; P6.1 adds suites and grading. Until then a run proves what ran and
how far, not how well.

## Before you start

- Node.js 22.19 or newer, and `npm ci` so `node_modules/.bin/pi` exists. The
  repository pins Pi at 1.5.2, which is the version this is verified against; your
  global Pi is not used and not modified.
- `uv` for the Python package.
- A server answering on the base URL. `llama-server` on `http://127.0.0.1:8001/v1`
  is what the reference configuration uses.

## Run it

```sh
uvx satyrn-pi eval --suite basic
```

From a checkout, before the package is published:

```sh
uvx --from . satyrn-pi eval --suite basic
```

Until P6.1 ships suite data, point the CLI at a fixtures directory:

```sh
SATYRN_PI_SUITES=tests/python/fixtures/eval uv run satyrn-pi eval --suite basic \
  --worker tests/python/fixtures/eval/worker-stub
```

Options: `--suite <name>` (required), `--worker <path>` (explicit worker),
`--base-url <url>` (default `http://127.0.0.1:8001/v1`), and `--deadline <seconds>`
(default 300), the longest one session may run.

## What it prints, and what it records

One line per resolved input, then the path of the record:

```
worker   0.0.1 tests/python/fixtures/eval/worker-stub (explicit)
pi       1.5.2 (verified, project)
suite    stub 0.0.1, 1 tasks
server   http://127.0.0.1:8001/v1
sessions 1 ended, 0 failed, 0 stopped, 10 model requests
records  runs/2026-11-26-stub/2026-11-26T145653Z-6e6868
```

`job.json` is the citable copy of those facts: suite and version, CLI version,
worker path and version and whether it was explicit or installed, Pi path and
version and whether it is the verified target, the model, the base URL, the
extensions loaded in order and the deadline. `run.json` is written last and carries the status, the
counts, the failures and the exit status. A directory with `job.json` but no
`run.json` is a job that stopped.

Each task also gets a trial directory:

```text
trial-01/
  trial.json       status, provenance and the session's own facts — replaced at each boundary
  prompt.txt       what the agent was asked
  workspace/       the task's base files, with its variant overlay and deletions applied
  agent/           the child's private PI_CODING_AGENT_DIR, including its provider profile
  trajectory.jsonl Pi's own session record, copied here when the child exits
```

The child runs with `workspace/` as its working directory, `/dev/null` as stdin,
and the prompt as an argument, so the prompt never enters the tree the agent can
read. Extensions are named with `-e` and discovery is off: the list in `job.json`
is the list that loaded. The agent directory holds only the provider profile the
CLI writes from the job's base URL and pinned model, plus whatever Pi stores there.

`trial.json` is written **before** anything runs, so a trial that never got
further says `prepared` rather than looking like a result. `running` is written
before the spawn and `session-ended` or `stopped` after it, so a kill in between
leaves an honest record. The statuses are a closed set — `prepared`, `running`,
`session-ended`, `graded`, `stopped` — and `write_trial` refuses anything else.
Only `graded` and `stopped` are final, a final record cannot be reopened, and only
`graded` may carry a verdict or a score: a stopped trial never looks like a judged
one.

## The deadline

Each session gets `--deadline` seconds. The child is started in its own process
group; when the deadline fires, the CLI kills that group — not just the child — so
a tool the agent started cannot outlive the trial. The trial is then recorded as
`stopped` with `"stopped_by": "deadline"`, the exit status the kill produced, the
time it ran, the requests it made and whatever trajectory existed. The job writes
`run.json` with status `stopped` and exits 2, and it starts no further trials: once
a bound has fired, more sessions are not bounded.

A stopped trial is a stop, not a failure. It says the deadline was reached; it does
not say the task could not be done, and it carries no verdict.

## Counting

- **Model requests** is the sum over trials, counted from each
  `trajectory.jsonl`: one assistant message is one model response. Since P5.3
  `run.json` says `"counts_source": "sessions"`. A child that left no trajectory
  counts zero rather than guessing.
- **Elapsed seconds** is this process's own wall clock. It is not the sum of trial
  clocks; adding them double-counts time the job was not running.

## Exit codes

| Code | Meaning |
| --- | --- |
| 0 | Every session ended and exited zero. |
| 2 | Stopped, with the reason on stderr. A child that exited non-zero is counted in `failures`; a session that outlived the deadline is counted in `stopped`. |

A stop before the job directory exists writes nothing at all: no worker and no
installed package, an ambiguous worker, a Pi outside the declared peer range, an
unknown suite, or no server answering. A stop **after** it — a fixture that cannot
be prepared — leaves `job.json` and the trials already written, and no `run.json`.
That is deliberate: a partial record stays inspectable, and a directory without
`run.json` is a job that stopped rather than one that succeeded.

## What a stopped run does not prove

A stopped run proves the bound held and the process group died. It does not prove
the task was too hard, that the model stalled, or that a longer run would have
failed — only that this session did not finish within the deadline. Read
`elapsed_seconds` and `model_requests` beside `stopped_by`; a stop with zero
requests usually means the child never reached the model at all.

## What a session-ended run does not prove

A session ended is not work done well. The child may have changed nothing, changed
the wrong file, or answered without using a tool; `session-ended` says only that
the process exited. Nothing has graded the workspace, `trial.json` carries no
verdict and no score, and `run.json` does not call the job a result. Grading and
verdicts arrive in P6.1.

## What a passing run does not prove

The health check proves **something** answers on the base URL. The agent profile
records the model the child was told to use, and the trajectory records the
provider and model Pi actually selected, so a mismatch is inspectable — but nothing
here proves which build or which weights answered. On a machine where another
inference server holds port 8001 — one that may serve a different Mellum under the
same name — a run can be green against the wrong server. Read the server's own
startup log, which names the build and the model file it loaded.
