# Backlog

Deferred work lives here. Each entry says what was deferred and the condition
that reopens it; an entry without a meaningful reopen condition is deleted, not
kept. An empty backlog is valid — do not invent entries to fill this file.

## Entry format

### Short title

- **Area:** the cycle or phase it belongs to
- **Deferred:** what was deferred, and why it is not in the current cycle
- **Reopen when:** the observable condition that brings it back
- **Links:** the plan, research note or issue that carries the detail

## Entries

### Accessibility statement for the site

- **Area:** the documentation site
- **Deferred:** the source site's footer links an accessibility statement. This
  site's footer carries only the copyright, and a link to a page that does not
  exist is worse than no link. The adopted stylesheet's contrast, focus and
  reduced-motion behaviour still apply.
- **Reopen when:** the site has more than the home page and the glossary, or a
  reader or reviewer asks for a statement.
- **Links:** [P3.1 spec](docs/superpowers/specs/2026-11-19-p3.1-site-identity-design.md)
- **Reopened 2026-11-24:** Getting Started makes the site three pages, which is
  the condition above. The statement is unclaimed work rather than backlog, and it
  belongs to whoever next touches the site's chrome.

### Read the version of a globally installed Pi

- **Area:** the eval CLI, from P5.1 and P5.3
- **Deferred:** Pi resolves from the project's pinned `node_modules/.bin/pi` first
  and from `PATH` only when that is absent. The `PATH` fallback reads the version
  from a `package.json` beside the binary; a global install (Volta, Homebrew, npm
  `-g`) is a link whose manifest is not necessarily an ancestor, so the fallback
  stops with `cannot tell ...'s version without running it` instead of guessing.
  `npm ci` is the supported path, and a live run from a worktree without it
  demonstrated the stop rather than a false version.
- **Reopen when:** someone runs eval from a checkout without `npm ci`, or a cycle
  makes the global install a supported entry point — P7.1's run settings or P9.1's
  installer walkthrough.
- **Links:** [P5.3 plan](docs/superpowers/plans/2026-11-24-p5.3-pi-child.md),
  `version_beside` in `src/satyrn_pi/cli.py`
