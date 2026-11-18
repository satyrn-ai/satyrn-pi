# Changelog

## [Unreleased]

- Seed the repository from the `mellum-worker` staging tree at `44bdbd61`,
  excluding only the staging-only `README.md`.
- Add the npm and Python package skeletons, `satyrn-pi` in both, with locked
  dependencies and a Pi peer range of `^1.1.0`.
- Add model-free default test suites: `npm test` and `uv run pytest`.
- Ignore `runs/`, and add the repository-weight check with its fail path
  exercised on a fixture tree.
- Add the contributor README and `npm run setup`, which runs the locked
  dependency installs and pins Superpowers for contributor Pi at
  `bb92a77` (`v6.1.1-56-gbb92a77`).
- Split phase 2 into six stacked cycles, P2.1 to P2.6, in the roadmap.
