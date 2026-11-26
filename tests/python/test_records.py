"""Job and run records. Filesystem reads and writes only."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

import pytest

from satyrn_pi.records import (
    aggregate_requests,
    job_id,
    job_path,
    read_trials,
    write_job,
    write_run,
)
from satyrn_pi.resolve import Suite

SUITE = Suite(name="basic", version="0.0.1", tasks=())


def write_trial(directory: Path, index: int, requests: int, elapsed: float) -> None:
    trial = directory / f"trial-{index:02d}"
    trial.mkdir(parents=True)
    (trial / "trial.json").write_text(
        json.dumps(
            {
                "task": f"task-{index:02d}",
                "status": "session-ended",
                "model_requests": requests,
                "elapsed_seconds": elapsed,
            }
        )
    )


def test_job_id_is_utc_fixed_width_and_unique(monkeypatch: pytest.MonkeyPatch) -> None:
    moment = datetime(2026, 11, 24, 14, 30, 5, tzinfo=timezone.utc)
    suffixes = iter(["aaaaaa", "bbbbbb"])
    monkeypatch.setattr("satyrn_pi.records.secrets.token_hex", lambda _: next(suffixes))
    first = job_id(moment)
    second = job_id(moment)
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{6}Z-[0-9a-f]{6}", first)
    assert first == "2026-11-24T143005Z-aaaaaa"
    assert second == "2026-11-24T143005Z-bbbbbb"


def test_job_path_nests_under_the_runs_tree(tmp_path: Path) -> None:
    path = job_path(tmp_path, SUITE, "2026-11-24T143005Z-abcdef")
    assert path == tmp_path / "2026-11-24-basic" / "2026-11-24T143005Z-abcdef"


def test_trials_are_read_from_the_job_the_run_wrote(tmp_path: Path) -> None:
    job = tmp_path / "job"
    write_trial(job, 1, 1, 0.5)
    write_trial(job, 2, 4, 2.0)
    write_trial(job, 3, 2, 1.0)
    trials = read_trials(job)
    assert [trial["task"] for trial in trials] == ["task-01", "task-02", "task-03"]
    assert all("model_requests" in trial for trial in trials)


def test_requests_aggregate_to_a_total_no_member_shares(tmp_path: Path) -> None:
    job = tmp_path / "job"
    write_trial(job, 1, 1, 0.5)
    write_trial(job, 2, 4, 2.0)
    write_trial(job, 3, 2, 1.0)
    trials = read_trials(job)
    total = aggregate_requests(trials)
    assert total == 7
    assert total not in {trial["model_requests"] for trial in trials}


def test_job_and_run_are_valid_json_with_the_resolved_facts(tmp_path: Path) -> None:
    path = job_path(tmp_path, SUITE, "2026-11-24T143005Z-abcdef")
    write_job(
        path,
        {
            "suite": "basic",
            "suite_version": "0.0.1",
            "cli_version": "0.1.0",
            "worker_path": "/w",
            "worker_version": "0.0.1",
            "pi_version": "1.5.2",
            "base_url": "http://127.0.0.1:8001/v1",
        },
    )
    written = json.loads((path / "job.json").read_text())
    assert written["suite_version"] == "0.0.1"
    assert written["base_url"].endswith("/v1")
    assert not (path / "run.json").exists()


def test_a_run_records_a_clock_that_is_not_the_trial_sum(tmp_path: Path) -> None:
    path = job_path(tmp_path, SUITE, "2026-11-24T143005Z-abcdef")
    write_trial(path, 1, 1, 4.5)
    write_trial(path, 2, 4, 2.0)
    write_trial(path, 3, 2, 1.25)
    trials = read_trials(path)
    trial_sum = sum(trial["elapsed_seconds"] for trial in trials)
    assert trial_sum == 7.75
    write_run(
        path,
        {
            "status": "session-ended",
            "model_requests": aggregate_requests(trials),
            "elapsed_seconds": 0.012,
            "exit_status": 0,
        },
    )
    written = json.loads((path / "run.json").read_text())
    assert written["model_requests"] == 7
    assert written["elapsed_seconds"] != trial_sum


def test_the_two_writes_do_not_depend_on_each_other(tmp_path: Path) -> None:
    path = job_path(tmp_path, SUITE, "2026-11-24T143005Z-abcdef")
    write_run(path, {"status": "resolved"})
    assert (path / "run.json").is_file()
    assert not (path / "job.json").exists()
    write_job(path, {"suite": "basic"})
    assert (path / "job.json").is_file()
