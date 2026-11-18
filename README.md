# Satyrn Pi

A small local model as a bounded coding worker inside Pi.

**Port status:** this repository currently ships package skeletons only. The
worker, remedies, eval CLI, suites and grading are not implemented yet; see
[ROADMAP.md](ROADMAP.md).

## Prerequisites

- Node.js 20 or newer
- [uv](https://docs.astral.sh/uv/)
- Pi within this package's peer range `^1.1.0` (the port targets 1.5.2)

## Set up

```sh
git clone git@github.com:satyrn-ai/satyrn-pi.git
cd satyrn-pi
npm run setup
```

`npm run setup` runs `npm ci` and `uv sync`, then installs the Superpowers
contributor skills into your user-level Pi configuration
(`~/.pi/agent/settings.json`, or `$PI_CODING_AGENT_DIR` if set) at the pinned
commit `bb92a77741419a4ab5f06e711a283343f1ada0c3` (`v7.0.0`).
That last step changes configuration shared with your other Pi projects: if a
Superpowers entry already exists at a different or unpinned revision, setup
refuses and tells you to re-run with `npm run setup -- --yes` to change it.
See [docs/superpowers/setup.md](docs/superpowers/setup.md).

Then open Pi in the repository; its skills are available to your agent.

## Default checks

The default suites use no model, network or subprocess:

```sh
npm test
uv run pytest
```

## Where things are

- [AGENTS.md](AGENTS.md) — the rules index to read first
- [BRIEF.md](BRIEF.md) — scope and fixed decisions
- [ROADMAP.md](ROADMAP.md) — feature cycles and current work
- [BACKLOG.md](BACKLOG.md) — deferred work and reopen conditions
- [docs/pathologies.md](docs/pathologies.md) — observed failure shapes and evidence
- [docs/domain.md](docs/domain.md) — components, responsibilities and run boundaries
- [docs/glossary.md](docs/glossary.md) — canonical vocabulary
- [docs/sdd.md](docs/sdd.md) — process, document caps and evidence rules
- [docs/rules-applicability.md](docs/rules-applicability.md) — how the preserved rules apply here
- [docs/superpowers/setup.md](docs/superpowers/setup.md) — Superpowers revision and setup record
