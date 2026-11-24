"""The eval CLI: resolve, print, gate, record. No process, no socket."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

import pytest

from satyrn_pi import cli
from satyrn_pi.records import aggregate_requests, load_trials

FIXTURES = Path(__file__).parent / "fixtures" / "eval"
REPO = Path(__file__).resolve().parents[2]


@dataclass
class Probes:
    """What the CLI would otherwise learn from the machine. Tests supply fakes."""

    installed_worker: Callable[[], Path | None] = lambda: FIXTURES / "worker-stub"
    pi_candidates: list[Path] = field(default_factory=lambda: [Path("/p/pi")])
    version_of: Callable[[Path], str] = lambda _: "1.5.2"
    server_health: Callable[[str], bool] = lambda _: True
    suite_root: Path = FIXTURES
    now: Callable[[], datetime] = lambda: datetime(
        2026, 11, 24, 14, 30, 5, tzinfo=timezone.utc
    )
    exists: Callable[[Path], bool] = lambda _: True
    calls: list[str] = field(default_factory=list)


def run(tmp_path, *argv, probes=None):
    probes = probes or Probes()
    runs = tmp_path / "runs"
    code = cli.main(["eval", *argv], probes=probes, runs_root=runs, cwd=REPO)
    return code, probes, runs


def only_job(runs: Path) -> Path:
    jobs = list(runs.glob("*-basic/*"))
    assert len(jobs) == 1
    return jobs[0]


def test_a_healthy_run_writes_job_and_run(tmp_path: Path) -> None:
    code, _, runs = run(tmp_path, "--suite", "basic")
    assert code == 0
    job = only_job(runs)
    assert (job / "job.json").is_file()
    assert (job / "run.json").is_file()


def test_the_printed_resolution_matches_the_record(tmp_path, capsys) -> None:
    code, _, runs = run(tmp_path, "--suite", "basic")
    assert code == 0
    job = json.loads((only_job(runs) / "job.json").read_text())
    printed = capsys.readouterr().out
    assert job["suite"] == "basic"
    assert job["suite_version"] in printed
    assert job["pi_version"] in printed
    assert job["worker_version"] in printed
    assert str(job["worker_path"]) in printed


def test_model_requests_are_summed_and_the_clock_is_not(tmp_path: Path) -> None:
    code, _, runs = run(tmp_path, "--suite", "basic")
    assert code == 0
    summary = json.loads((only_job(runs) / "run.json").read_text())
    trials = load_trials(FIXTURES / "trials")
    assert summary["model_requests"] == aggregate_requests(trials) == 10
    assert summary["elapsed_seconds"] < sum(t["elapsed_seconds"] for t in trials)


def test_an_unresolvable_worker_stops_without_a_run_directory(tmp_path: Path) -> None:
    code, _, runs = run(tmp_path, "--suite", "basic", probes=Probes(installed_worker=lambda: None))
    assert code == 2
    assert not runs.exists()


def test_an_out_of_range_pi_stops_without_a_run_directory(tmp_path: Path) -> None:
    code, _, runs = run(tmp_path, "--suite", "basic", probes=Probes(version_of=lambda _: "2.0.0"))
    assert code == 2
    assert not runs.exists()


def test_a_dead_server_stops_without_a_run_directory(tmp_path: Path) -> None:
    code, _, runs = run(tmp_path, "--suite", "basic", probes=Probes(server_health=lambda _: False))
    assert code == 2
    assert not runs.exists()


def test_an_unknown_suite_stops_without_a_run_directory(tmp_path: Path) -> None:
    code, _, runs = run(tmp_path, "--suite", "missing")
    assert code == 2
    assert not runs.exists()


def test_an_explicit_worker_is_recorded_as_explicit(tmp_path: Path) -> None:
    code, _, runs = run(tmp_path, "--suite", "basic", "--worker", str(FIXTURES / "worker-stub"))
    assert code == 0
    job = json.loads((only_job(runs) / "job.json").read_text())
    assert job["worker_source"] == "explicit"


def test_base_url_is_carried_into_the_record(tmp_path: Path) -> None:
    code, _, runs = run(tmp_path, "--suite", "basic", "--base-url", "http://127.0.0.1:9999/v1")
    assert code == 0
    job = json.loads((only_job(runs) / "job.json").read_text())
    assert job["base_url"] == "http://127.0.0.1:9999/v1"


def test_a_pi_that_runs_but_is_not_the_target_is_marked_unverified(tmp_path: Path) -> None:
    code, _, runs = run(tmp_path, "--suite", "basic", probes=Probes(version_of=lambda _: "1.1.0"))
    assert code == 0
    job = json.loads((only_job(runs) / "job.json").read_text())
    assert job["pi_verified"] is False


def test_help_needs_no_probe(tmp_path: Path) -> None:
    probes = Probes()
    code = cli.main(["eval", "--help"], probes=probes, runs_root=tmp_path / "runs", cwd=REPO)
    assert code == 0
    assert probes.calls == []


def test_the_health_probe_is_asked_about_the_base_url(tmp_path: Path) -> None:
    asked: list[str] = []
    probes = Probes(server_health=lambda url: asked.append(url) or True)
    run(tmp_path, "--suite", "basic", "--base-url", "http://127.0.0.1:8123/v1", probes=probes)
    assert asked == ["http://127.0.0.1:8123/v1"]


def test_the_cli_version_comes_from_the_package() -> None:
    import satyrn_pi

    assert cli.CLI_VERSION == satyrn_pi.__version__


def test_peer_range_is_read_from_the_manifest() -> None:
    manifest = json.loads((REPO / "package.json").read_text())
    assert cli.peer_range(REPO) == manifest["peerDependencies"]["@earendil-works/pi-coding-agent"]


def test_counts_say_they_came_from_fixtures(tmp_path: Path) -> None:
    code, _, runs = run(tmp_path, "--suite", "basic")
    assert code == 0
    summary = json.loads((only_job(runs) / "run.json").read_text())
    assert summary["counts_source"] == "fixtures"


def test_started_at_carries_the_stamp_not_its_first_field(tmp_path: Path) -> None:
    code, _, runs = run(tmp_path, "--suite", "basic")
    assert code == 0
    job = json.loads((only_job(runs) / "job.json").read_text())
    assert job["started_at"] == "2026-11-24T143005Z"
