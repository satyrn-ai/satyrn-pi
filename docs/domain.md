# Domain

This map explains which components do what and where their responsibilities meet.
Use it to decide where a change belongs and which implementation to inspect.
It describes architecture and run behavior; the glossary defines the terms used here.
Start with the two packages, then follow a run and its data across their boundary.

## Current and planned implementation

**Current implementation:** P1.1 provides package skeletons only. The npm package
has no worker or remedies yet, and `src/satyrn_pi/` contains only the package
version. Eval execution, suites and grading are not available yet.

**Port decision:** the concept relationships, ownership rules and boundaries below
are the target architecture. Paths marked planned become real in their owning
roadmap cycles.

**Source evidence:** the remedy-hook table reports behavior observed in the pinned
source. It informs the port but does not claim that those hooks are implemented.

## Core architecture

An [agent](glossary.md#agent) is a composition, not a model. The worker is an
optional component of that composition; the model and host remain inputs outside
it.

```text
Agent = Pi + optional worker + recorder + selected remedies
Model and host = external inputs

Preset selects remedies
Eval suite selects tasks and grading expectations
Neither selection implies the other
```

The worker supplies model switching and span reporting. The recorder observes the
session. Remedies supply explicit behavior at Pi seams. A [preset](glossary.md#preset)
names the resolved remedy selection; an [Eval suite](glossary.md#eval-suite) names
the work and grading expectations. Every run records both choices independently.

Evaluation has three nested boundaries:

```text
Job: one eval CLI invocation
 └─ Trial: one agent attempt at one task
     ├─ Workspace: prepared before execution
     ├─ Pi session: child-process chain → Trajectory
     └─ Grader: runs after the session → Verdict
```

A [job](glossary.md#job) aggregates trials. A [trial](glossary.md#trial) joins one
agent to one [task](glossary.md#task), covers its Pi session and subsequent grading,
and ends with a verdict or an explicit incomplete state. The Pi session ends when
its last child exits; grading then becomes part of the trial's evidence. The
[trajectory](glossary.md#trajectory) records execution, not the grading result.

## The two packages

Both published artefacts are named `satyrn-pi`, but they have different jobs.

| Artefact | Owns | Does not own |
| --- | --- | --- |
| npm package | The Pi extension: the thin worker and its mode machinery, remedies, prompt fragments and presets. | Eval orchestration, suites, grading, run records or the model. |
| Python package | The eval CLI, suite data, graders, workspace preparation, process orchestration and run records. | Worker internals, remedy behaviour, Pi's session state or the model. |

### The Pi package

The worker is deliberately thin: it switches to the subject model, drops
pre-marker history, tracks and records the worker span, writes its report, and
restores the main model. The command and mode machinery exist only to support
that transition.

The worker bundles nothing else. It installs no prompt replacement, tool
restriction, project facts or guards. Those behaviors belong to explicit
[remedies](glossary.md#remedy), each implemented in one inspectable TypeScript
file under the planned `remedies/<kind>/` tree.

The npm loader resolves `base.json` at session start. Eval reads the same
selection at run start and records the resolved list, order and each file's
SHA-256. The worker adds nothing behind that list; adjacent presets may be equal
without becoming the same architectural role.

### The Python package

The Python package supplies measurement. Its CLI resolves and runs a job,
prepares each workspace, starts Pi sessions, invokes the grader, and writes
records. Suites and graders are package data rather than a checkout-local
source tree.

The planned runtime lives under `src/satyrn_pi/`. The CLI never imports the
worker's TypeScript or reaches into its extension state. It invokes a resolved
worker and observes the files and process results that cross the package
boundary.

## Where a change belongs

| Changing… | Owner and location | Status |
| --- | --- | --- |
| Model switching, worker span or report | npm worker extension | Planned; Base lands in P8.1 |
| A pathology-specific behavior | `remedies/<kind>/<name>.ts` in the npm package | Planned; remedy cycles begin in P10.1 |
| Remedy selection or order | Preset JSON in the npm package | Planned with Base and later presets |
| Recorder output | Recorder extension in the npm package | Planned with Vanilla in P7.1 |
| CLI resolution or process orchestration | `src/satyrn_pi/` | Package root current; runtime planned in P5.1 |
| Tasks, fixtures or variants | Python suite package data | Planned in P6.1 |
| Grading expectations or checks | Python grader package data | Planned in P6.1 |
| Process deadlines or redispatch | Python eval orchestration | Planned in P5.1 and later acceptance work |
| Record contents and provenance | Python run-record implementation; output under ignored `runs/` | `runs/` ignore current; records planned from P5.1 |
| Vocabulary or architectural ownership | `docs/glossary.md` or `docs/domain.md` | Current P1.2 documentation |

## Import direction and the boundary

The worker never imports the eval package. The eval package never imports worker
internals. No package imports or in-process calls cross the boundary. P2.1's
one-way import check enforces this direction.

Process orchestration still crosses it explicitly:

- **Into Pi:** a resolved worker path, selected extension and preset paths,
  configuration, prompt, workspace, arguments and environment.
- **Out of Pi:** the trajectory, the worker's report, the finished workspace,
  process status and usage evidence.
- **Into the trial after its session:** the eval package's own grader copy. The
  grader runs from a sandboxed copy outside the workspace, so the agent can
  neither read nor edit what grades it.

A worker path and version identify the code that ran; records, not imports,
connect it to the measurement. Grader code is copied only after the session and
is never loaded by the worker. No suite answer crosses into the agent.

## A run

The eval CLI executes a job; run remains ordinary language for that execution.
Its boundary is the CLI invocation, not an individual model request or Pi
session.

### Run and evidence architecture

| Step | Owner | Produces |
| --- | --- | --- |
| Resolve and prepare | Python CLI | Job configuration, workspace and prompt |
| Execute | Pi, worker, recorder and remedies | Trajectory, worker report and finished workspace |
| Grade | Python grader | Trust markers and verdict |
| Summarize | Python CLI | Job summary and CI status |

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

The CLI prepares the trial's workspace by copying the fixture's base and the
selected variant's overlay, including deletions and prompt files. It records the
prompt and the pinned model here. At this point nothing is running: the
workspace is only a directory on disk.

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
runs them. The worker cannot substitute a test or alter the grader copy.
**Source evidence:** the pinned source's grading step records `leaked.json`,
`layout.json`, the contamination marker, `acceptance.json` and `stalled.json`
before it produces a verdict. P6.1 owns whether the port keeps or revises those
artifact names. The trial includes this grading step even though its Pi session
has already ended.

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

**Configuration evidence** names the agent, resolved preset with per-file
SHA-256 hashes, worker path and version, Pi version, suite and grader version,
model, host card and prompt. It identifies what was asked to run before terminal
output can be trusted.

**Execution evidence** contains the trajectory, finished workspace, process
status, deadline and stall markers, and number of model requests. It shows what
ran and how far it progressed.

**Result evidence** contains `verdict.json`, per-check results, grader version,
trust markers and score when grading completed. `run.json` summarises the job,
and the CLI exit status carries the verdict for CI. A killed job can leave no
summary; its partial records remain inspectable.

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

## Vanilla and Base in the architecture

The desk walk runs [Vanilla](glossary.md#vanilla) and [Base](glossary.md#base) on
the same Easy suite. Vanilla follows the worker-free agent composition. Base
follows the active-worker composition and resolves the empty `base.json`
selection. The suite, grader, model and host can stay fixed while those agent
architectures differ.

Vanilla exposes the small model's expected failures. Base supplies the minimum
research environment in which individual pathologies and remedies become
investigable. Empty Base and Vanilla can therefore behave alike without becoming
interchangeable; equal scores do not erase the worker, preset and research-role
differences. Both use the eval machinery to record quality and budget evidence.

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

These are architecture seams, not definitions. Contributors place each
implementation under the matching `remedies/<kind>/` path and record its evidence.
The exact port hooks are verified against the targeted Pi version in their owning
implementation cycles; this table does not turn source evidence into current code.

## Driving the system

Humans and agents start with the same discovery route: identify the concept here,
use the change-location table, then open the owning operational guide. Planned
destinations are named without links until those documents exist.

| Intent | Canonical destination | Availability |
| --- | --- | --- |
| Understand concepts and ownership | `docs/domain.md` | Current in P1.2 |
| Contribute through repository workflows | Root `AGENTS.md` and contributor guidance | Current in P2.2 |
| Run an eval | Eval CLI guide | Planned in P5.1 |
| Write a suite, task or grader | Eval authoring guide | Planned in P6.1 |
| Interpret scores and evidence | Scoring and evidence guide | Planned in P6.1 |

The P2.2 rules index (`AGENTS.md`) links this domain document, making it
reachable from an agent's normal entry point. The P5.1 operational guide owns
copyable commands, prerequisites, outputs and failure behavior. The P6.1 guides
own suite and grader authoring contracts and score interpretation.

Until those cycles land, the eval runtime and authoring interfaces are planned,
not executable. After a run becomes available, verification uses configuration evidence, execution evidence and result evidence
rather than terminal output alone. This routing section discovers capabilities;
it does not duplicate their operational manuals.

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
