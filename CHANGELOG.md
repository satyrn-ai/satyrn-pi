# Changelog

## [Unreleased]

- Seed the repository from the `mellum-worker` staging tree at `44bdbd61`,
  excluding only the staging-only `README.md`.
- Add the npm and Python package skeletons, `satyrn-pi` in both, with locked
  dependencies and a Pi peer range of `^1.1.0`.
- Add model-free default test suites: `npm test` and `uv run pytest`.
- Ignore `runs/`, and add the repository-weight check with its fail path
  exercised on a fixture tree.
