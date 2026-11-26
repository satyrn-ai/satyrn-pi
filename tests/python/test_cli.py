"""The eval CLI: resolve, print, gate, record. No process, no socket."""

from __future__ import annotations

import itertools
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Iterator

import pytest

from satyrn_pi import cli
from satyrn_pi.records import aggregate_requests, read_trials

FIXTURES = Path(__file__).parent / "fixtures" / "eval"
REPO = Path(__file__).resolve().parents[2]


class Handle:
    """A spawned child as the CLI's real spawn would return one."""

    def __init__(self, exit_status: int) -> None:
        self.exit_status = exit_status

    def communicate(self, timeout: float | None = None) -> tuple[str, str]:
        return "", ""


class FakeSpawn:
    """Writes a session artifact per child, so requests have a real source."""

    def __init__(self, requests: tuple[int, ...] = (1, 2, 3), exits: tuple[int, ...] = ()) -> None:
        self.requests: Iterator[int] = iter(requests)
        self.exits: Iterator[int] = iter(exits)
        self.calls: list[tuple[list[str], Path, dict]] = []

    def __call__(self, argv, cwd, env):
        argv = list(argv)
        self.calls.append((argv, Path(cwd), dict(env)))
        session_id = argv[argv.index("--session-id") + 1]
        session_dir = Path(argv[argv.index("--session-dir") + 1])
        artifact = session_dir / "--fixture--" / f"2026-11-26T10-00-00Z_{session_id}.jsonl"
        artifact.parent.mkdir(parents=True, exist_ok=True)
        lines = [json.dumps({"type": "message", "message": {"role": "user"}})]
        for _ in range(next(self.requests, 0)):
            lines.append(json.dumps({"type": "message", "message": {"role": "assistant"}}))
        artifact.write_text("\n".join(lines) + "\n")
        return Handle(next(self.exits, 0))


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
    ticks: list[float] = field(default_factory=list)
    monotonic: Callable[[], float] = lambda: 0.0
    spawn: Callable = field(default_factory=FakeSpawn)
    base_env: dict = field(default_factory=lambda: {"PATH": "/bin"})


def run(tmp_path, *argv, probes=None):
    probes = probes or Probes()
    ticks = list(probes.ticks)
    counter = itertools.count()
    probes.monotonic = (lambda: ticks.pop(0)) if ticks else (lambda: next(counter))
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
    probes = Probes(ticks=[100.0, 100.5, 101.0, 101.5, 102.0, 102.5, 103.0, 103.25])
    code, _, runs = run(tmp_path, "--suite", "basic", probes=probes)
    assert code == 0
    job = only_job(runs)
    summary = json.loads((job / "run.json").read_text())
    trials = read_trials(job)
    assert summary["model_requests"] == aggregate_requests(trials) == 6
    assert summary["model_requests"] not in {t["model_requests"] for t in trials}
    assert summary["elapsed_seconds"] == 3.25
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


def test_counts_say_they_came_from_sessions(tmp_path: Path) -> None:
    code, _, runs = run(tmp_path, "--suite", "basic")
    assert code == 0
    summary = json.loads((only_job(runs) / "run.json").read_text())
    assert summary["counts_source"] == "sessions"


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


def test_each_task_gets_a_trial_with_a_workspace_and_no_verdict(tmp_path: Path) -> None:
    code, _, runs = run(tmp_path, "--suite", "basic")
    assert code == 0
    job = only_job(runs)
    trials = sorted(path for path in job.glob("trial-*"))
    assert [trial.name for trial in trials] == ["trial-01", "trial-02", "trial-03"]
    for trial in trials:
        record = json.loads((trial / "trial.json").read_text())
        assert record["task"].startswith("task-")
        assert (trial / "prompt.txt").is_file()
        assert (trial / "workspace").is_dir()
        assert not (trial / "verdict.json").exists()
        assert "verdict" not in record
        assert "score" not in record


def test_the_run_says_its_sessions_ended(tmp_path: Path) -> None:
    code, _, runs = run(tmp_path, "--suite", "basic")
    summary = json.loads((only_job(runs) / "run.json").read_text())
    assert summary["status"] == "session-ended"
    assert summary["trials"] == 3


def test_each_trial_records_the_pinned_model(tmp_path: Path) -> None:
    code, _, runs = run(tmp_path, "--suite", "basic")
    assert code == 0
    job = only_job(runs)
    job_record = json.loads((job / "job.json").read_text())
    for trial in sorted(job.glob("trial-*")):
        record = json.loads((trial / "trial.json").read_text())
        assert record["model"] == job_record["model"]


def test_a_preparation_failure_leaves_the_trial_record_and_no_summary(tmp_path: Path) -> None:
    probes = Probes()
    probes.suite_root = tmp_path / "suites"
    (probes.suite_root / "suite-basic").mkdir(parents=True)
    (probes.suite_root / "suite-basic" / "suite.json").write_text(
        json.dumps({"name": "basic", "version": "0.0.1", "tasks": [
            {"id": "task-x", "instructions": "x", "fixture": "fixtures/task-x",
             "verification": "y"}]})
    )
    (probes.suite_root / "trials").mkdir()
    code, _, runs = run(tmp_path, "--suite", "basic", probes=probes)
    assert code == 2
    job = next(runs.glob("*-basic/*"))
    assert (job / "job.json").is_file()
    assert not (job / "run.json").exists()
    record = json.loads((job / "trial-01" / "trial.json").read_text())
    assert record["status"] == "prepared"


def test_each_trial_records_the_session_boundary(tmp_path: Path) -> None:
    code, _, runs = run(tmp_path, "--suite", "basic")
    assert code == 0
    job = only_job(runs)
    for trial in sorted(job.glob("trial-*")):
        record = json.loads((trial / "trial.json").read_text())
        assert record["status"] == "session-ended"
        assert record["exit_status"] == 0
        assert record["session_id"]
        assert record["model_requests"] >= 1
        assert (trial / "trajectory.jsonl").is_file()


def test_the_child_runs_in_the_workspace_with_a_private_profile(tmp_path: Path) -> None:
    code, probes, runs = run(tmp_path, "--suite", "basic")
    assert code == 0
    trial = only_job(runs) / "trial-01"
    argv, cwd, env = probes.spawn.calls[0]
    assert cwd == trial / "workspace"
    assert env["PI_CODING_AGENT_DIR"] == str(trial / "agent")
    profile = json.loads((trial / "agent" / "models.json").read_text())
    assert profile["providers"]["satyrn"]["baseUrl"] == cli.DEFAULT_BASE_URL
    assert argv[-1] == (trial / "prompt.txt").read_text().strip()


def test_the_job_records_the_extension_order(tmp_path: Path) -> None:
    code, _, runs = run(tmp_path, "--suite", "basic")
    assert code == 0
    job = json.loads((only_job(runs) / "job.json").read_text())
    assert job["extensions"] == [str((FIXTURES / "worker-stub" / "worker.ts").resolve())]


def test_a_running_trial_is_written_before_its_child_starts(tmp_path: Path) -> None:
    seen: list[str] = []
    probes = Probes()

    def spawn(argv, cwd, env):
        seen.append(json.loads((Path(cwd).parent / "trial.json").read_text())["status"])
        return FakeSpawn()(argv, cwd, env)

    probes.spawn = spawn
    code, _, _ = run(tmp_path, "--suite", "basic", probes=probes)
    assert code == 0
    assert seen == ["running", "running", "running"]


def test_a_failing_child_is_recorded_and_the_job_stops(tmp_path: Path) -> None:
    probes = Probes(spawn=FakeSpawn(exits=(0, 4, 0)))
    code, _, runs = run(tmp_path, "--suite", "basic", probes=probes)
    assert code == 2
    job = only_job(runs)
    failing = json.loads((job / "trial-02" / "trial.json").read_text())
    assert failing["status"] == "session-ended"
    assert failing["exit_status"] == 4
    summary = json.loads((job / "run.json").read_text())
    assert summary["status"] == "session-ended"
    assert summary["failures"] == 1
    assert summary["exit_status"] == 2


def test_a_missing_worker_entry_stops_before_a_job_directory(tmp_path: Path) -> None:
    worker = tmp_path / "worker"
    worker.mkdir()
    (worker / "package.json").write_text(
        json.dumps(
            {"name": "w", "version": "0.0.1", "satyrn": {"worker": "./gone.ts"}}
        )
    )
    code, _, runs = run(tmp_path, "--suite", "basic", "--worker", str(worker))
    assert code == 2
    assert not runs.exists()
