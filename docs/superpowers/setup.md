# Superpowers setup and revision

Contributors develop this port with the Superpowers skills. This record fixes
the revision those skills come from, how they reach a contributor's Pi, and how
a later upgrade is decided and reviewed.

## Revision

- Source: `github.com/obra/superpowers`
- Pinned commit: `bb92a77741419a4ab5f06e711a283343f1ada0c3`
- Description: `v7.0.0`, 2026-10-09
- Installed as the Pi git package `git:github.com/obra/superpowers@bb92a77741419a4ab5f06e711a283343f1ada0c3`

This is the revision that drove P1.1 and P1.2. It is pinned rather than
floating: Pi reconciles a git package to its configured ref and later updates
do not move it.

## How the skills reach Pi

`npm run setup` runs `npm ci`, `uv sync`, then `pi install` with the pinned
source. Pi clones the package under its config directory
(`~/.pi/agent/git/github.com/obra/superpowers`, or under
`$PI_CODING_AGENT_DIR` when set), discovers the package's `skills/` directories
at startup, and advertises each skill's name and description to the agent. Full
instructions load only when a task matches, or when a contributor invokes
`/skill:<name>`.

## Side effects and consent

The install writes to **user-level** Pi configuration, which other projects on
the same machine share. Setup therefore inspects the existing entry first:

- no Superpowers entry: install at the pinned commit;
- the same pinned commit: report it as already configured and install nothing;
- a different ref, or an unpinned entry: refuse, print the current and
  requested refs, and require an explicit `npm run setup -- --yes` to change it.

Setup never rewrites a different existing ref silently.

## Upgrade policy

Adopting a different Superpowers revision is a named, reviewed decision. It
records the new commit and description, the skills and repository contracts the
change affects, and the evidence limits of that adoption. Fetching newer
upstream code does not by itself replace this pin or bypass the SDD workflow.

## Subject worker

These are contributor skills. The measured subject worker loads none of them by
default, and this setup does not add Superpowers to the product's runtime.
