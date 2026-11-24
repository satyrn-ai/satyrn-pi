# Running an eval

`satyrn-pi eval` resolves every input the result will cite, refuses to start when
one of them is wrong or ambiguous, and writes a record of what it resolved before
anything is asked of a model.

**Availability:** P5.1 ships resolution and records. It starts no Pi session, runs
no task and produces no verdict. P5.2 adds the session; P6.1 adds suites and
grading. Until then a run proves the record, not a measurement.

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
`--base-url <url>` (default `http://127.0.0.1:8001/v1`).

## What it prints, and what it records

One line per resolved input, then the path of the record:

```
worker   0.0.1 tests/python/fixtures/eval/worker-stub (explicit)
pi       1.5.2 (verified, project)
suite    basic 0.0.1, 3 tasks
server   http://127.0.0.1:8001/v1
records  runs/2026-11-24-basic/2026-11-24T152922Z-00d9b4
```

`job.json` is the citable copy of those facts: suite and version, CLI version,
worker path and version and whether it was explicit or installed, Pi path and
version and whether it is the verified target, the model and the base URL.
`run.json` is written last and carries the status, the counts and the exit status.
A directory with `job.json` but no `run.json` is a job that stopped.

## Counting

- **Model requests** is the sum over trials. In P5.1 the trials are fixtures, so
  `run.json` says `"counts_source": "fixtures"` — the number is a demonstration of
  the rule, never a measurement.
- **Elapsed seconds** is this process's own wall clock. It is not the sum of trial
  clocks; adding them double-counts time the job was not running.

## Exit codes

| Code | Meaning |
| --- | --- |
| 0 | Resolved, recorded. |
| 2 | Stopped. Nothing was written, and the reason is on stderr. |

A stop includes: no worker and no installed package, an ambiguous worker, a Pi
outside the declared peer range, an unknown suite, or no server answering.

## What a passing run does not prove

The health check proves **something** answers on the base URL, not which build or
model answered. On a machine where another inference server holds port 8001 — one
that may serve a different Mellum under the same name — a run can be green against
the wrong server. P5.2 records the model and the session; until then, read the
server's own startup log, which names the build and the model file it loaded.
