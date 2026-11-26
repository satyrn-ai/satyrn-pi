"""trial.json is written before anything runs and replaced at each boundary."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from satyrn_pi.trial import FINAL, STATUSES, write_trial


def test_a_prepared_trial_is_not_final(tmp_path: Path) -> None:
    write_trial(tmp_path, {"task": "task-01", "status": "prepared"})
    written = json.loads((tmp_path / "trial.json").read_text())
    assert written["status"] == "prepared"
    assert written["status"] not in FINAL


def test_a_prepared_trial_carries_no_verdict_and_no_score(tmp_path: Path) -> None:
    write_trial(tmp_path, {"task": "task-01", "status": "prepared"})
    written = json.loads((tmp_path / "trial.json").read_text())
    assert "verdict" not in written
    assert "score" not in written


def test_statuses_are_a_closed_set() -> None:
    assert STATUSES == ("prepared", "running", "session-ended", "graded", "stopped")


@pytest.mark.parametrize("status", ["invented", "done", "complete"])
def test_an_unknown_status_is_refused(tmp_path: Path, status: str) -> None:
    with pytest.raises(ValueError):
        write_trial(tmp_path, {"task": "task-01", "status": status})


def test_replacing_a_status_keeps_the_earlier_fields(tmp_path: Path) -> None:
    write_trial(tmp_path, {"task": "task-01", "status": "prepared", "worker": "fixture"})
    write_trial(tmp_path, {"status": "running"})
    written = json.loads((tmp_path / "trial.json").read_text())
    assert written["task"] == "task-01"
    assert written["worker"] == "fixture"
    assert written["status"] == "running"


def test_only_graded_and_stopped_are_final() -> None:
    assert FINAL == ("graded", "stopped")
    assert set(STATUSES) - set(FINAL) == {"prepared", "running", "session-ended"}


def test_a_trial_left_at_prepared_is_a_status_not_a_failure(tmp_path: Path) -> None:
    write_trial(tmp_path, {"task": "task-01", "status": "prepared"})
    written = json.loads((tmp_path / "trial.json").read_text())
    assert written["status"] != "failed"
    assert "failed" not in STATUSES


@pytest.mark.parametrize("status", ("prepared", "running", "session-ended"))
def test_a_non_final_trial_refuses_a_verdict_or_a_score(tmp_path: Path, status: str) -> None:
    with pytest.raises(ValueError):
        write_trial(tmp_path, {"task": "task-01", "status": status, "verdict": "pass"})
    with pytest.raises(ValueError):
        write_trial(tmp_path, {"task": "task-01", "status": status, "score": 1.0})
    assert not (tmp_path / "trial.json").exists()


def test_a_verdict_left_over_from_a_final_record_is_refused(tmp_path: Path) -> None:
    write_trial(tmp_path, {"task": "task-01", "status": "graded", "verdict": "pass", "score": 1.0})
    with pytest.raises(ValueError):
        write_trial(tmp_path, {"status": "prepared"})
