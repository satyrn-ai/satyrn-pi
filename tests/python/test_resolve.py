"""Resolution of worker, Pi and suite. No process, no socket, no network."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from satyrn_pi.resolve import (
    Pi,
    ResolutionError,
    Suite,
    Worker,
    resolve_pi,
    resolve_suite,
    resolve_worker,
    satisfies,
)

FIXTURES = Path(__file__).parent / "fixtures" / "eval"


def test_explicit_worker_wins_over_the_installed_one() -> None:
    resolved = resolve_worker(FIXTURES / "worker-stub", lambda: FIXTURES / "worker-other")
    assert resolved.source == "explicit"
    assert resolved.path == FIXTURES / "worker-stub"
    assert resolved.version == "0.0.1"


def test_installed_worker_is_used_when_none_is_given() -> None:
    resolved = resolve_worker(None, lambda: FIXTURES / "worker-stub")
    assert resolved.source == "installed"
    assert resolved.version == "0.0.1"


def test_nothing_resolving_names_both_attempts() -> None:
    with pytest.raises(ResolutionError) as raised:
        resolve_worker(None, lambda: None)
    assert "explicit" in str(raised.value)
    assert "installed" in str(raised.value)


def test_a_directory_without_a_manifest_is_not_a_worker() -> None:
    with pytest.raises(ResolutionError):
        resolve_worker(FIXTURES / "suite-basic", lambda: None)


def test_worker_reads_the_manifest_rather_than_the_directory_name() -> None:
    resolved = resolve_worker(None, lambda: FIXTURES / "worker-other")
    assert resolved.version == "0.0.2"
    assert resolved.entry == "./other.ts"


def test_a_suite_holds_tasks_and_no_results() -> None:
    suite = resolve_suite("basic", FIXTURES)
    assert isinstance(suite, Suite)
    assert suite.version == "0.0.1"
    assert [task["id"] for task in suite.tasks] == ["task-01", "task-02", "task-03"]
    for task in suite.tasks:
        assert set(task) == {"id", "instructions", "fixture", "verification"}


def test_an_unknown_suite_names_what_it_looked_for() -> None:
    with pytest.raises(ResolutionError) as raised:
        resolve_suite("missing", FIXTURES)
    assert "missing" in str(raised.value)


def test_the_project_binary_wins_over_path() -> None:
    calls: list[Path] = []

    def version_of(path: Path) -> str:
        calls.append(path)
        return "1.5.2" if path == Path("/p/node_modules/.bin/pi") else "1.7.0"

    resolved = resolve_pi(
        candidates=[("project", Path("/p/node_modules/.bin/pi")), ("path", Path("/usr/bin/pi"))],
        version_of=version_of,
        peer_range="^1.1.0",
        target="1.5.2",
        exists=lambda _: True,
    )
    assert resolved.source == "project"
    assert resolved.verified is True
    assert calls == [Path("/p/node_modules/.bin/pi")]


def test_a_path_binary_is_used_only_when_the_project_has_none() -> None:
    resolved = resolve_pi(
        candidates=[("path", Path("/usr/bin/pi"))],
        version_of=lambda path: "1.4.0",
        peer_range="^1.1.0",
        target="1.5.2",
        exists=lambda _: True,
    )
    assert resolved.source == "path"
    assert resolved.verified is False


def test_the_target_is_verified_and_the_floor_is_not() -> None:
    def resolve(version: str) -> Pi:
        return resolve_pi(
            candidates=[("project", Path("/p/pi"))],
            version_of=lambda _: version,
            peer_range="^1.1.0",
            exists=lambda _: True,
        )

    target = resolve("1.5.2")
    floor = resolve("1.1.0")
    assert isinstance(target, Pi) and target.verified is True
    assert floor.verified is False


@pytest.mark.parametrize("version", ["1.0.0", "2.0.0"])
def test_an_out_of_range_version_stops(version: str) -> None:
    with pytest.raises(ResolutionError):
        resolve_pi(
            candidates=[("project", Path("/p/pi"))],
            version_of=lambda _: version,
            peer_range="^1.1.0",
            exists=lambda _: True,
        )


def test_a_version_inside_the_range_but_past_the_target_runs_unverified() -> None:
    resolved = resolve_pi(
        candidates=[("project", Path("/p/pi"))],
        version_of=lambda _: "1.7.0",
        peer_range="^1.1.0",
        exists=lambda _: True,
    )
    assert resolved.verified is False


def test_no_pi_at_all_stops() -> None:
    with pytest.raises(ResolutionError):
        resolve_pi(candidates=[], version_of=lambda _: "1.5.2", peer_range="^1.1.0")


def test_an_absent_candidate_is_skipped_not_used() -> None:
    resolved = resolve_pi(
        candidates=[("project", Path("/missing/pi")), ("path", Path("/p/pi"))],
        version_of=lambda _: "1.5.2",
        peer_range="^1.1.0",
        exists=lambda path: str(path) == "/p/pi",
    )
    assert resolved.path == Path("/p/pi")


@pytest.mark.parametrize(
    ("version", "range_", "expected"),
    [
        ("1.5.2", "^1.1.0", True),
        ("1.0.0", "^1.1.0", False),
        ("2.0.0", "^1.1.0", False),
        ("1.2.9", "~1.2.0", True),
        ("1.3.0", "~1.2.0", False),
        ("1.1.0", ">=1.1.0", True),
        ("1.0.9", ">=1.1.0", False),
        ("1.5.2", "1.5.2", True),
        ("1.5.1", "1.5.2", False),
        ("1.7.0", "^1.1.0", True),
    ],
)
def test_range_parsing(version: str, range_: str, expected: bool) -> None:
    assert satisfies(version, range_) is expected


def test_the_worker_does_not_carry_results() -> None:
    resolved: Worker = resolve_worker(None, lambda: FIXTURES / "worker-stub")
    assert not hasattr(resolved, "model_requests")


def test_the_manifest_is_json_not_a_guess() -> None:
    manifest = json.loads((FIXTURES / "worker-stub" / "package.json").read_text())
    assert manifest["satyrn"]["worker"].endswith(".ts")


def test_a_suite_that_names_itself_differently_is_refused(tmp_path: Path) -> None:
    root = tmp_path / "suites"
    (root / "suite-basic").mkdir(parents=True)
    (root / "suite-basic" / "suite.json").write_text(
        json.dumps({"name": "other", "version": "0.0.1", "tasks": [
            {"id": "t", "instructions": "i", "fixture": "f", "verification": "v"}]})
    )
    with pytest.raises(ResolutionError) as raised:
        resolve_suite("basic", root)
    assert "other" in str(raised.value)


def test_a_task_missing_a_field_fails_before_any_job_exists(tmp_path: Path) -> None:
    root = tmp_path / "suites"
    (root / "suite-basic").mkdir(parents=True)
    (root / "suite-basic" / "suite.json").write_text(
        json.dumps({"name": "basic", "version": "0.0.1", "tasks": [{"id": "t"}]})
    )
    with pytest.raises(ResolutionError) as raised:
        resolve_suite("basic", root)
    assert "instructions" in str(raised.value)


def test_malformed_suite_json_is_a_resolution_error(tmp_path: Path) -> None:
    root = tmp_path / "suites"
    (root / "suite-basic").mkdir(parents=True)
    (root / "suite-basic" / "suite.json").write_text("{not json")
    with pytest.raises(ResolutionError):
        resolve_suite("basic", root)


def test_a_zero_major_caret_follows_npm(tmp_path: Path) -> None:
    assert satisfies("0.1.0", "^0.1.0") is True
    assert satisfies("0.9.0", "^0.1.0") is False
    assert satisfies("0.0.1", "^0.0.1") is True
    assert satisfies("0.0.2", "^0.0.1") is False


def test_a_worker_whose_entry_is_missing_is_not_a_worker(tmp_path: Path) -> None:
    (tmp_path / "package.json").write_text(
        json.dumps(
            {
                "name": "@satyrn-pi/gone",
                "version": "0.0.1",
                "satyrn": {"worker": "./gone.ts"},
            }
        )
    )
    with pytest.raises(ResolutionError) as raised:
        resolve_worker(tmp_path, lambda: None)
    assert "gone.ts" in str(raised.value)


def test_the_stub_suite_is_one_task_for_an_end_to_end_run() -> None:
    suite = resolve_suite("stub", FIXTURES)
    assert [task["id"] for task in suite.tasks] == ["task-stub"]
    assert suite.tasks[0]["fixture"] == "fixtures/task-stub"


@pytest.mark.parametrize("entry", ["../outside.ts", "/etc/passwd"])
def test_a_worker_entry_outside_the_directory_is_refused(
    tmp_path: Path, entry: str
) -> None:
    (tmp_path / "outside.ts").write_text("export default function () {}\n")
    worker = tmp_path / "worker"
    worker.mkdir()
    (worker / "package.json").write_text(
        json.dumps({"name": "w", "version": "0.0.1", "satyrn": {"worker": entry}})
    )
    with pytest.raises(ResolutionError):
        resolve_worker(worker, lambda: None)
