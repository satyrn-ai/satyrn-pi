"""Workspace preparation: a workspace directory and a prompt beside it.

The prompt belongs to the trial record, not to the agent's workspace: a file
inside the tree is one the agent can read, and one grading would have to ignore.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from satyrn_pi.workspace import WorkspaceError, prepare

SUITE = Path(__file__).parent / "fixtures" / "eval" / "suite-basic"


def task(identifier: str) -> dict:
    data = json.loads((SUITE / "suite.json").read_text())
    return next(t for t in data["tasks"] if t["id"] == identifier)


def test_base_files_land_in_the_workspace(tmp_path: Path) -> None:
    workspace = prepare(task("task-03"), SUITE, tmp_path / "trial-01")
    assert (workspace / "app.py").read_text().startswith("try:")


def test_the_overlay_replaces_a_base_file(tmp_path: Path) -> None:
    workspace = prepare(task("task-01"), SUITE, tmp_path / "trial-01")
    written = (workspace / "app.py").read_text()
    assert written.startswith('"""Arithmetic helpers."""')
    assert written.count("def add") == 1


def test_deletions_remove_a_base_file(tmp_path: Path) -> None:
    workspace = prepare(task("task-02"), SUITE, tmp_path / "trial-01")
    assert not (workspace / "a.py").exists()
    assert (workspace / "b.py").read_text() == "subtotal = 2\n"


def test_the_prompt_sits_beside_the_workspace_not_inside_it(tmp_path: Path) -> None:
    trial = tmp_path / "trial-01"
    workspace = prepare(task("task-01"), SUITE, trial)
    assert (trial / "prompt.txt").read_text().strip() == "Add a docstring to the module."
    assert workspace == trial / "workspace"
    assert not (workspace / "prompt.txt").exists()


def test_a_missing_fixture_stops_with_a_named_task(tmp_path: Path) -> None:
    with pytest.raises(WorkspaceError) as raised:
        prepare({"id": "task-99", "fixture": "fixtures/task-99"}, SUITE, tmp_path / "t")
    assert "task-99" in str(raised.value)


def test_a_task_without_instructions_stops(tmp_path: Path) -> None:
    with pytest.raises(WorkspaceError):
        prepare({"id": "task-01", "fixture": "fixtures/task-01"}, SUITE, tmp_path / "t")


def test_preparing_twice_does_not_leave_the_first_attempt_behind(tmp_path: Path) -> None:
    trial = tmp_path / "trial-01"
    prepare(task("task-01"), SUITE, trial)
    stale = trial / "workspace" / "leftover.py"
    stale.write_text("stale\n")
    prepare(task("task-01"), SUITE, trial)
    assert not stale.exists()
