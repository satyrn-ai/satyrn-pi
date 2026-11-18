# Satyrn Pi glossary

Use Vanilla → Base → Easy → Medium → Hard directly. Each names an agent; Easy, Medium and Hard also name an eval suite and a preset, so say which you mean.
This dictionary defines the project's shared vocabulary in short, reusable entries.
Use it to check a term while reading; aliases support automatic site links.
It carries definitions, not architectural obligations; see [Domain](domain.md) for responsibilities and where things live.

### Agent

<!-- zensical-glossary-aliases: agent configuration -->

An agent: the task-completing program, Pi plus its trace recorder, the optional worker extension and the remedies it loads, separate from the model it uses. Vanilla, Base, Easy, Medium and Hard are agents; they differ in worker state and enabled remedies, not in kind.

### Vanilla

<!-- zensical-glossary-aliases: Vanilla Pi, Vanilla agent -->

An agent: Pi using the subject model, with the trace recorder and no worker extension or remedies. It establishes the lowest-level baseline expected of regular Pi with a small model, and it is expected to fail. It loads no remedy preset.

### Base

<!-- zensical-glossary-aliases: Base agent -->

An agent: the thin worker in its active mode, plus the remedies explicitly listed in `base.json`. The list starts empty. It provides the minimum research environment for investigating individual pathologies and remedies. The worker switches to the subject model, drops pre-marker history, tracks and records the span, then restores the main model. It bundles no prompt replacement, tool restriction, project facts or guards.

### Remedy

One explicit, additive behaviour addressing an observed failure, implemented in one inspectable TypeScript file under `remedies/<kind>/`. Its applicability and evidence are recorded; it encodes no suite-specific answer. A guard blocks an action; a nudge adds a corrective message; other remedies can change the prompt, context or available tools.

### Preset

A named, ordered JSON list of remedies, with no includes or implicit additions. `base.json`, `easy.json`, `medium.json` and `hard.json` each list their complete contents. Easy retains Base's remedies, Medium retains Easy's, and Hard retains Medium's; each adds only remedies earned through measurement. Adjacent lists may be equal. Loading a preset selects remedies, not a model or a suite, and does not prove a passing result. A preset is narrower than an agent; experimental arms add the run settings needed for a comparison.

### Eval suite

<!-- zensical-glossary-aliases: Dataset -->

The tasks and fixtures to run, with their grading expectations. Easy, Medium and Hard name suites as well as presets; say "Easy suite" or "Easy preset" where the distinction matters. Compare Vanilla and Base on the same suite; retaining Easy's remedies does not establish that they help on Medium or Hard.

### Task

One unit of work in an eval suite: its fixture, prompt and grading expectations. A trial attempts one task.

### Job

One complete eval CLI invocation. It resolves the worker, Pi, suite and server before any Pi session begins, then aggregates the trials for its tasks.

### Trial

One agent attempt at one task within a job, covering its Pi session and subsequent grading. Its session may include a child-process chain that keeps one session ID; its record ends in a verdict or remains explicitly incomplete.

### Trajectory

<!-- zensical-glossary-aliases: session record -->

The recorder's session artifact: the ordered conversation and actions produced during one trial's Pi session.
