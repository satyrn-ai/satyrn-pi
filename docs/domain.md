# Domain

This map explains which components do what and where their responsibilities meet.
Use it to decide where a change belongs and which implementation to inspect.
It describes architecture and run behavior; the glossary defines the terms used here.
Start with the two packages, then follow a run and its data across their boundary.

This is the target architecture. P1.1 provides package skeletons only: the npm
package has no worker or remedies yet, and `src/satyrn_pi/` contains only the
package version. Sections below distinguish current locations from components
planned by later cycles.

## The two packages

Both published artefacts are named `satyrn-pi`, but they have different jobs.

| Artefact | Owns | Does not own |
| --- | --- | --- |
| npm package | The Pi extension: the thin worker and its mode machinery, remedies, prompt fragments and presets. | Eval orchestration, suites, grading, run records or the model. |
| Python package | The eval CLI, suite data, graders, workspace preparation, process orchestration and run records. | Worker internals, remedy behaviour, Pi's session state or the model. |

### The Pi package

The npm package supplies the task-completing [agent](glossary.md#agent) inside
Pi. Its worker is deliberately thin: it switches to the subject model, drops
pre-marker history, tracks and records the worker span, writes its report, and
restores the main model. The command and mode machinery exist only to support
that transition.

The worker bundles nothing else. It installs no prompt replacement, tool
restriction, project facts or guards. Everything of that kind is an explicit
[remedy](glossary.md#remedy), implemented in one inspectable TypeScript file
under the planned `remedies/<kind>/` tree. A [preset](glossary.md#preset) stores
an ordered remedy list, initially empty, and adds no hidden defaults.

[Vanilla](glossary.md#vanilla) is also an agent in the npm package, but it loads
Pi with the trace recorder and no worker extension or remedies. It is the
ordinary-Pi baseline with a small model; it is expected to fail. [Base](glossary.md#base)
is the thin worker in active mode plus the remedies explicitly named in
`base.json`. Base exists to make individual pathologies and remedies
investigable, not to disguise the baseline's failures.

### The Python package

The Python package supplies measurement. Its CLI resolves and runs an eval
[job](glossary.md#job), prepares each workspace, starts Pi sessions, invokes the
grader, and writes records. An [Eval suite](glossary.md#eval-suite) selects
[tasks](glossary.md#task) and their grading expectations; presets select
remedies. Neither choice implies the
other, so every run names both.

The planned runtime lives under `src/satyrn_pi/`; suites and graders are package
data rather than a checkout-local ladder. The CLI never imports the worker's
TypeScript or reaches into its extension state. It invokes a resolved worker and
observes the files and process results that cross the package boundary.

## Import direction and the boundary

The worker never imports the eval package. The eval package never imports worker
internals. It resolves a worker executable by explicit path or installed npm
package, records that resolution, and starts Pi as a child process. P2.1's
one-way import check enforces this direction.

Only data crosses the boundary:

- **Out of Pi:** the [trajectory](glossary.md#trajectory), the worker's report,
  the finished workspace, process status and usage evidence.
- **Into the completed trial:** the eval package's own grader copy after the
  session has ended. The grader runs from a sandboxed copy outside the
  workspace, so the agent can neither read nor edit what grades it.

No remedy, grader, suite answer or executable code crosses in either direction.
A worker path and version identify the code that ran; records, not imports,
connect it to the measurement.

## A run

A run is the ordinary word for executing a [job](glossary.md#job). Its boundary
is the CLI invocation, not an individual model request or Pi session.

### 1. Resolve before anything starts

The CLI resolves and prints everything the result will cite:

- the worker path and version, from `--worker <path>` or the installed npm
  package; ambiguity stops the run;
- the Pi binary and Pi version, which must satisfy the declared peer range;
- the suite and grader version, selected from the Python package's data;
- the server, from `--base-url` with its default; a failed health check stops
  before a long session begins.

It then creates the job directory and writes `job.json` with the suite and suite
version, CLI version, repetition count and any preregistered decision rule.

### 2. Prepare a trial before its session exists

A [trial](glossary.md#trial) is one agent attempt at one task. The CLI first
materialises the workspace by copying the fixture's base and the selected
variant's overlay, including deletions and prompt files. It records the prompt
and the pinned model here. At this point nothing is running: the workspace is
only a directory on disk.

### 3. Bound the Pi session by processes

A Pi session is a child-process boundary:

- it begins after the workspace and profile exist, when the first Pi child is
  spawned;
- it ends when the last child exits, whether cleanly, on error, or after a
  deadline kills the process group.

The CLI starts Pi in print mode with the workspace as its working directory,
stdin closed, a private `PI_CODING_AGENT_DIR`, a shared session ID and directory,
and extensions in load order: the agent's selected extensions first, the
recorder last so it observes the worker's appended facts.

Inside the session, the recorder writes the trajectory; the worker switches to
the subject model, drops pre-marker history, records its span, restores the
parent model and reports back; remedies fire at their Pi seams.

A session does not end merely because the model stops speaking. A settle gate is
a hook inside the same session. If it sends work back, the CLI starts another
child under the same session ID, continuing the conversation. Redispatch retains
one session ID: the whole child-process chain remains one trial, not several.
Only the final child's exit ends that trial's session. The deadline is the other
end: it writes a deadline or stalled marker, kills the process group, and records
the trial as stopped rather than failed.

### 4. Grade after the session

Grading happens after the Pi session, outside it and outside the workspace. With
the child processes gone, the eval package copies its own grader tests in and
runs them. The worker cannot substitute a test or alter the grader copy. The
grading stage records `leaked.json`, `layout.json`, the contamination marker,
`acceptance.json` and `stalled.json` before it produces a verdict.

### 5. Keep the evidence

The planned record tree separates job, trial, session artifact and verdict:

```text
runs/<date>-<suite>/<job>/
  job.json          suite and version, CLI version, repetition count, decision rule
  trial-01/
    trial.json      agent, resolved preset, worker and Pi provenance, status, markers
    prompt.txt      what the agent was asked
    trajectory.jsonl  the recorder's session artifact
    verdict.json    per-check result, grader version and score
  run.json          job summary, written last
```

`trial.json` names at least the worker path and version, Pi version, suite and
grader version, host card, score when grading completed, and number of model
requests. It
also names the agent, the resolved preset with per-file SHA-256 hashes, the
prompt, session identity, exit status, deadline and stall markers. `run.json`
summarises the job, and the CLI exit status carries the verdict for CI.

`trial.json` is created before the Pi process starts and atomically replaced at
each boundary: prepared, running, session ended, graded. If the whole CLI is
killed, the last persisted state remains available; partial is a status, not a
failure. A partial trial never invents a verdict or a score, and it never looks
complete. If only the child is stopped, the CLI records that outcome explicitly.

### The three boundaries

| Boundary | Owner | What crosses |
| --- | --- | --- |
| CLI to workspace | Python | Fixture files, variant overlay and prompt text. |
| Session start and end | Pi child process | Arguments, environment, session ID and working directory in; trajectory and finished workspace out. |
| Session to grader | Python | A finished workspace; nothing live from the session. |

## Remedy seams

The seven kinds group remedies by the Pi extension boundary they use. The names
come from the pinned source and describe seams, not presets. A kind can use more
than one hook, and a preset selects individual remedies, not whole kinds.

| Kind | Pi hooks used by the source | Responsibility |
| --- | --- | --- |
| guard | `tool_call`, with turn state from `turn_end` and `agent_before_settle` | Block or rewrite a requested action that would cause a known failure. |
| nudge | `turn_end`, `agent_before_settle`, `tool_result` | Add a corrective message or request continuation without replacing the conversation. |
| context | `before_provider_request`, `tool_result`, `message_end` | Transform request-local context, narrow tools or repair malformed messages. |
| prompt | `before_provider_request` | Add one small prompt fragment; the worker itself performs no prompt replacement. |
| tool | Tool registration and `tool_call` | Add or adapt a model-callable operation, such as backgrounding a long command. |
| check | `agent_before_settle` | Run an explicit quality or evidence check before the agent may finish. |
| workflow | Registered workflow tools and `tool_call` | Sequence a plan, gates and checkpoints across a larger task. |

These are architecture seams, not definitions. The glossary defines remedy,
preset and agent; contributors place each implementation under the matching
`remedies/<kind>/` path and record its evidence.

## Outside the product

Satyrn Education begins outside this repository. The learning centre, lessons,
challenge and gamification are not owned by Satyrn Pi, even where they use its
worker or published evidence.

The model and its weights are not ours. Fine-tuning, DPO, SFT and model training
have no design in this port and no reserved phase. The contributor's rig, the
local server and host cards are measurement conditions, not the product. They
are recorded so results can be reproduced and compared; their local setup does
not become a Satyrn Pi responsibility.

The product owns the Pi worker, remedies, presets, eval CLI, suites, graders,
run records and the documentation that serves installers and contributors. It
does not absorb the systems it measures or the education product built on top.
