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
  `bb92a77` (`v7.0.0`).
- Split phase 2 into six stacked cycles, P2.1 to P2.6, in the roadmap.
- Add the root rules index, a routing skill, and the backlog and pathology
  records, with document budgets tightening the preserved caps for new work.
- Add the documentation site's identity: a Zensical configuration, the Satyrn
  stylesheet and display face adopted from `satyrn-website` at `7508bd7`, and a
  home page, publishing only the home page and the glossary.
- Add the repository's first workflow: pull requests run both default suites and
  a strict site build, and `main` publishes to GitHub Pages, whose address is
  recorded in `README.md`.
- Link the first prose use of each glossary term on the site from the single
  glossary source, with tooltips, and review the aliases: two ordinary or
  ambiguous ones removed.
- Split phase 4 into three stacked cycles, P4.1 to P4.3, after the phase's
  brainstorm: a pinned reference host card, a recorded setup walk, and the
  published Getting Started page.
- Record the review order for pull requests: Nicola leads and is assigned, every
  request mentions Andre and Ben for their lanes, code and the reference
  configuration merge on his approval, and documentation on its own merges on a
  green required check plus Paul's recorded authorisation. GitHub refuses
  self-approval, so that authorisation is a comment rather than a review.
- Enable the default-branch ruleset: `main` now requires a pull request and the
  `Default suites and strict build` check, with no required approval, so the
  check guards the branch while review guards the decisions.
- Pin the reference host card: llama.cpp b12066 by source commit and whole-release
  asset digest, the Q4_K_M weights by Hugging Face revision, size and sha256, the
  preserved settings, and the serve command with `-hf` replaced by an explicit
  `-m` path so a repository selector cannot stand in for the pinned file.
- Run the pinned configuration: b12066 from its verified asset, Q4_K_M from its
  verified file, serving `127.0.0.1:8001` with the preserved flags, answering a
  request, and recording the allocation the server reports beside the footprint
  the process actually holds.
- Publish Getting Started as the site's third page: five numbered steps from the
  recorded walk, the pinned digests, the two macOS failures and an occupied port
  named where they happen, and a closing section that says the worker is not
  published yet. A drift check fails when the page and the reference card
  disagree about a pin.
- Retire the backlog entry asking for the site check to be required on `main`:
  the ruleset now requires a pull request and the default-suite check, so the
  condition it named is met and the format says to delete rather than archive.
  Reopen the accessibility-statement entry, whose condition this page meets.
- Split phase 5 into four stacked cycles, P5.1 to P5.4: resolution and records
  proved with fixtures, workspace preparation, the Pi child, then its deadline.
- Bound each trial's Pi session with a deadline: the child runs in its own process
  group, a fired deadline kills the group, and the trial is recorded as `stopped`
  rather than failed — with no verdict, and no further trials started.
- Start each trial's Pi child in print mode: the prepared workspace as its working
  directory, closed stdin, a private agent directory, a shared session directory,
  explicit extensions in load order, and `session-ended` recorded with the
  trajectory and the model requests it really made.
- Prepare each trial's workspace from its fixture: base, variant overlay and
  deletions, the prompt written beside the tree rather than inside it, and
  `trial.json` at `prepared` — a status that cannot be mistaken for a result.
- Add `satyrn-pi eval`: worker, Pi, suite and server resolved and printed, a
  preflight health check that stops before any record exists, `job.json` and
  `run.json` under `runs/`, and the counting rules — proven with fixtures, no
  process and no socket. Pi resolves from the project's pinned 1.5.2 install.
