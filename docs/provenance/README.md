# Provenance: preserved source documents

The files here are **verbatim copies of the source repository's rules**, kept as
evidence for the port. They are not the rules of this repository.

- `mellum-worker-AGENTS.md` is `AGENTS.md` from
  `andrevanzuydam/mellum-worker` at the provenance pin `0e4a9b68`
  (2026-11-13), byte for byte.
- Its companion, the source process document, is preserved separately as
  [`../sdd.md`](../sdd.md). Both were copied unchanged; neither is edited here.

## What these files are for

1. **Evidence.** The port can quote exactly what the source said, rather than
   paraphrasing it from memory. The BRIEF's provenance section names these two
   documents as what "crosses verbatim".
2. **Input to P2.1.** Phase 2 creates this repository's root `AGENTS.md` as an
   *index* to the effective rules, maps the source wording and paths onto the
   port, and **re-earns their executable gates** (document caps, lifecycle
   checks, the default-test tripwire, import direction). Copying the prose is
   not proof that a gate exists.

## What these files are not

- **Not binding as written.** Source concepts such as Baseline Worker, `bare`,
  `arm`, `rung`, `ladder/`, `learn/glossary.md` and the OpenCode install path do
  not apply here. [`../rules-applicability.md`](../rules-applicability.md)
  states precedence, the source→port path mapping and the exclusions. Where the
  two disagree, the BRIEF's fixed decisions and that mapping govern.
- **Not edited.** Preserved originals stay byte-for-byte even when a later
  revision or a port decision makes part of them stale. A dated correction
  belongs in the document that supersedes them, not here.

## Related, but not preserved

[`../rules-applicability.md`](../rules-applicability.md) is the port's own
**transition record**: authored for this repository, dated, and expected to be
superseded when P2.1 installs the effective rules into the root `AGENTS.md`. It
is not a verbatim copy and does not live here for that reason; it carries the
precedence table and the source→port mappings that give the files above their
effective meaning.

## Verify a copy

From a checkout of this repository, with the source repository available:

```sh
git -C <mellum-worker-checkout> show 0e4a9b68:AGENTS.md \
  | diff - docs/provenance/mellum-worker-AGENTS.md
```

No output means the copy is intact. The same check applies to the staging
revision the repository was seeded from (`44bdbd61`).
