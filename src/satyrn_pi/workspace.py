"""Prepare a trial's workspace.

The workspace is a copy, never a reference: a task's base files, then its variant
overlay, then its deletions. Nothing here runs, spawns or reads the network — the
result is a directory on disk and a prompt beside it.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Mapping

PROMPT_NAME = "prompt.txt"
WORKSPACE_NAME = "workspace"


class WorkspaceError(RuntimeError):
    """A task's fixture is missing or incomplete."""


def _copy_tree(source: Path, destination: Path) -> None:
    for item in sorted(source.rglob("*")):
        if not item.is_file():
            continue
        target = destination / item.relative_to(source)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(item, target)


def _deletions(fixture: Path) -> list[str]:
    manifest = fixture / "deletions.txt"
    if not manifest.is_file():
        return []
    return [
        line.strip()
        for line in manifest.read_text().splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]


def prepare(task: Mapping[str, str], suite_root: Path, trial: Path) -> Path:
    """Build `trial/workspace` and write `trial/prompt.txt` beside it.

    Re-running replaces the workspace: a stale file from an earlier attempt would
    otherwise be graded as part of this one.
    """
    identifier = str(task.get("id", "<unidentified>"))
    relative = task.get("fixture")
    if not relative:
        raise WorkspaceError(f"task {identifier} declares no fixture")
    fixture = Path(suite_root) / relative
    base = fixture / "base"
    if not base.is_dir():
        raise WorkspaceError(f"task {identifier} has no base fixture at {base}")

    trial = Path(trial)
    destination = trial / WORKSPACE_NAME
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True)

    _copy_tree(base, destination)
    overlay = fixture / "overlay"
    if overlay.is_dir():
        _copy_tree(overlay, destination)
    for victim in _deletions(fixture):
        target = destination / victim
        if target.is_file():
            target.unlink()

    instructions = task.get("instructions")
    if not isinstance(instructions, str) or not instructions.strip():
        raise WorkspaceError(f"task {identifier} carries no instructions")
    (trial / PROMPT_NAME).write_text(instructions.strip() + "\n")
    return destination
