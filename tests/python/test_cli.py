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
from satyrn_pi.resolve import ResolutionError

FIXTURES = Path(__file__).parent / "fixtures" / "eval"
REPO = Path(__file__).resolve().parents[2]


@dataclass
class Probes:
    """What the CLI would otherwise learn from the machine. Tests supply fakes."""

    installed_worker: Callable[[], Path | None] = lambda: FIXTURES / "worker-stub"
    pi_candidates: list = field(default_factory=lambda: [("project", Path("/p/pi"))])
    version_of: Callable[[Path], str] = lambda _: "1.5.2"
    server_health: Callable[[str], bool] = lambda _: True
    server_models: Callable[[str], tuple[str, ...]] = lambda _: ("Mellum2.1-12B-A2.5B-Thinking",)
    suite_root: Path = FIXTURES
    now: Callable[[], datetime] = lambda: datetime(
        2026, 11, 24, 14, 30, 5, tzinfo=timezone.utc
    )
    exists: Callable[[Path], bool] = lambda _: True
    ticks: list[float] = field(default_factory=lambda: [100.0, 100.025])
    monotonic: Callable[[], float] = lambda: 0.0


def run(tmp_path, *argv, probes=None):
    probes = probes or Probes()
    ticks = list(probes.ticks)
    probes.monotonic = lambda: ticks.pop(0)
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
    assert summary["elapsed_seconds"] == 0.025
    assert summary["elapsed_seconds"] != sum(t["elapsed_seconds"] for t in trials)


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
    class Untouchable:
        def __getattr__(self, name):
            raise AssertionError(f"help touched probe {name!r}")

    code = cli.main(["eval", "--help"], probes=Untouchable(), runs_root=tmp_path / "runs", cwd=REPO)
    assert code == 0


def test_health_url_uses_the_origin_not_the_path() -> None:
    assert cli.health_url("http://127.0.0.1:8001/v1") == "http://127.0.0.1:8001/health"
    assert cli.health_url("https://host/api/v1") == "https://host/health"
    assert cli.health_url("http://host:9000/x/v1") == "http://host:9000/health"


@pytest.mark.parametrize("bad", ["ftp://host/v1", "not a url", "/v1", ""])
def test_health_url_refuses_a_non_http_base(bad: str) -> None:
    with pytest.raises(Exception):
        cli.health_url(bad)


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


def test_version_beside_reads_the_manifest(tmp_path: Path) -> None:
    package = tmp_path / "node_modules" / "@earendil-works" / "pi-coding-agent"
    (package / "dist" / "bundle").mkdir(parents=True)
    (package / "package.json").write_text(json.dumps({"version": "1.5.2"}))
    binary = package / "dist" / "bundle" / "cli.js"
    binary.write_text("#!/usr/bin/env node\n")
    assert cli.version_beside(binary) == "1.5.2"


def test_version_beside_without_a_manifest_is_a_resolution_error(tmp_path: Path) -> None:
    binary = tmp_path / "loose" / "pi"
    (tmp_path / "loose").mkdir()
    binary.write_text("x")
    from satyrn_pi.resolve import ResolutionError

    with pytest.raises(ResolutionError):
        cli.version_beside(binary)


def test_version_beside_with_malformed_json_is_a_resolution_error(tmp_path: Path) -> None:
    (tmp_path / "package.json").write_text("{not json")
    binary = tmp_path / "pi"
    binary.write_text("x")
    from satyrn_pi.resolve import ResolutionError

    with pytest.raises(ResolutionError):
        cli.version_beside(binary)


def test_a_server_without_the_pinned_alias_is_refused(tmp_path: Path) -> None:
    probes = Probes(server_models=lambda _: (
        "mellum2.1-12b-a2.5b-thinking-mlx",
        "qwen3.8-flash-next-oq4e-mtp",
    ))
    code, _, runs = run(tmp_path, "--suite", "basic", probes=probes)
    assert code == 2
    assert not runs.exists()


def test_the_refusal_names_what_the_server_actually_offers(tmp_path: Path, capsys) -> None:
    probes = Probes(server_models=lambda _: ("mellum2.1-12b-a2.5b-thinking-mlx",))
    run(tmp_path, "--suite", "basic", probes=probes)
    printed = capsys.readouterr().err
    assert "mellum2.1-12b-a2.5b-thinking-mlx" in printed
    assert cli.DEFAULT_MODEL in printed


def test_an_empty_model_list_is_refused(tmp_path: Path) -> None:
    code, _, runs = run(tmp_path, "--suite", "basic", probes=Probes(server_models=lambda _: ()))
    assert code == 2
    assert not runs.exists()


def test_the_pinned_alias_lets_the_run_through(tmp_path: Path) -> None:
    probes = Probes(server_models=lambda _: (cli.DEFAULT_MODEL,))
    code, _, _ = run(tmp_path, "--suite", "basic", probes=probes)
    assert code == 0


def test_an_unscoped_installed_worker_is_found(tmp_path: Path) -> None:
    worker = tmp_path / "node_modules" / "satyrn-pi"
    worker.mkdir(parents=True)
    (worker / "package.json").write_text(json.dumps({"satyrn": {"worker": "w.ts"}}))
    assert cli.installed_worker(tmp_path) == worker


def test_two_installed_workers_are_refused(tmp_path: Path) -> None:
    for name in ("satyrn-pi", "@satyrn/worker"):
        directory = tmp_path / "node_modules" / name
        directory.mkdir(parents=True)
        (directory / "package.json").write_text(json.dumps({"satyrn": {"worker": "w.ts"}}))
    with pytest.raises(ResolutionError, match="two installed workers"):
        cli.installed_worker(tmp_path)


def test_an_ambiguous_install_stops_before_a_job_directory(tmp_path: Path) -> None:
    def ambiguous():
        raise ResolutionError("two installed workers: a, b")

    probes = Probes(installed_worker=ambiguous)
    code, _, runs = run(tmp_path, "--suite", "basic", probes=probes)
    assert (code, runs.exists()) == (cli.STOPPED, False)


def test_the_resolution_is_printed_before_the_job_directory(tmp_path: Path, capsys) -> None:
    seen: list[str] = []
    probes = Probes()
    now = probes.now

    def capture() -> datetime:
        seen.append(capsys.readouterr().out)
        return now()

    probes.now = capture
    run(tmp_path, "--suite", "basic", probes=probes)
    assert all(word in seen[0] for word in ("worker", "pi", "suite", "server"))
