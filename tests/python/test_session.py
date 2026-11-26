"""The Pi child's argv, environment, profile and artifact. No process is started."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from satyrn_pi import session

WORKER = Path("/w/worker.ts")
RECORDER = Path("/w/recorder.ts")


def argv(**overrides):
    values = dict(
        binary=Path("/p/pi"),
        prompt="Do the thing.",
        session_id="job-01",
        session_dir=Path("/j/sessions"),
        extensions=[WORKER],
        model="Mellum2.1-12B-A2.5B-Thinking",
    )
    values.update(overrides)
    return session.session_argv(**values)


def test_the_child_runs_in_print_mode() -> None:
    assert "--print" in argv()
    assert "-p" not in argv()


def test_the_prompt_is_last_and_fenced_from_options() -> None:
    built = argv(prompt="-- not an option")
    assert built[-2:] == ["--", "-- not an option"]


def test_the_argv_carries_the_session_id_and_the_shared_directory() -> None:
    built = argv()
    assert built[built.index("--session-id") + 1] == "job-01"
    assert built[built.index("--session-dir") + 1] == "/j/sessions"


def test_extensions_load_in_the_order_given() -> None:
    built = argv(extensions=[WORKER, RECORDER])
    positions = [index for index, item in enumerate(built) if item in ("-e", "--extension")]
    loaded = [built[index + 1] for index in positions]
    assert loaded == ["/w/worker.ts", "/w/recorder.ts"]


def test_discovery_is_off_so_the_list_is_the_whole_list() -> None:
    assert "--no-extensions" in argv()


def test_the_pinned_model_is_named_explicitly() -> None:
    built = argv(model="Mellum2.1-12B-A2.5B-Thinking")
    assert built[built.index("--provider") + 1] == session.PROVIDER
    assert built[built.index("--model") + 1] == "Mellum2.1-12B-A2.5B-Thinking"


def test_the_environment_points_at_the_private_agent_directory() -> None:
    base = {"PATH": "/bin", "HOME": "/home/someone"}
    env = session.session_env(base, agent_dir=Path("/t/agent"))
    assert env["PI_CODING_AGENT_DIR"] == "/t/agent"
    assert env["PATH"] == "/bin"


def test_the_callers_environment_is_not_mutated() -> None:
    base = {"PATH": "/bin"}
    session.session_env(base, agent_dir=Path("/t/agent"))
    assert base == {"PATH": "/bin"}


def test_the_profile_points_at_the_checked_server_and_model(tmp_path: Path) -> None:
    session.write_agent_profile(
        tmp_path / "agent",
        base_url="http://127.0.0.1:8001/v1",
        model="Mellum2.1-12B-A2.5B-Thinking",
    )
    models = json.loads((tmp_path / "agent" / "models.json").read_text())
    provider = models["providers"][session.PROVIDER]
    assert provider["baseUrl"] == "http://127.0.0.1:8001/v1"
    assert provider["api"] == "openai-completions"
    assert [model["id"] for model in provider["models"]] == [
        "Mellum2.1-12B-A2.5B-Thinking"
    ]


def test_the_profile_pins_the_sampling_the_host_card_records(tmp_path: Path) -> None:
    session.write_agent_profile(
        tmp_path / "agent", base_url="http://host/v1", model="m"
    )
    models = json.loads((tmp_path / "agent" / "models.json").read_text())
    model = models["providers"][session.PROVIDER]["models"][0]
    assert model["samplingParams"] == {
        "temperature": 1.0,
        "top_p": 0.95,
        "top_k": 20,
    }
    assert model["contextWindow"] == 50000
    assert model["maxTokens"] == 16384


def test_the_profile_makes_the_model_the_default(tmp_path: Path) -> None:
    session.write_agent_profile(
        tmp_path / "agent", base_url="http://host/v1", model="m"
    )
    settings = json.loads((tmp_path / "agent" / "settings.json").read_text())
    assert settings["defaultProvider"] == session.PROVIDER
    assert settings["defaultModel"] == "m"


class Handle:
    """A spawned child, as `run_session` sees one."""

    def __init__(
        self,
        returncode: int = 0,
        writes: Path | None = None,
        stdout: str = "",
        outlives_the_deadline: bool = False,
    ) -> None:
        self.exit_status = returncode
        self._writes = writes
        self._stdout = stdout
        self._outlives = outlives_the_deadline
        self.killed = 0
        self.calls: list[tuple] = []

    def communicate(self, timeout: float | None = None) -> tuple[str, str]:
        self.calls.append(("communicate", timeout))
        if self._outlives:
            self._outlives = False
            raise session.TimedOut()
        if self._writes is not None:
            self._writes.parent.mkdir(parents=True, exist_ok=True)
            self._writes.write_text(
                "\n".join(
                    [
                        json.dumps({"type": "session", "id": "job-01"}),
                        json.dumps({"type": "message", "message": {"role": "user"}}),
                        json.dumps({"type": "message", "message": {"role": "assistant"}}),
                        json.dumps({"type": "message", "message": {"role": "toolResult"}}),
                        json.dumps({"type": "message", "message": {"role": "assistant"}}),
                    ]
                )
                + "\n"
            )
        return self._stdout, ""

    def kill_group(self) -> None:
        self.killed += 1
        self.exit_status = -9


def run(tmp_path: Path, handle: Handle, **overrides):
    spawned: list[tuple] = []
    ticks = [10.0, 12.5]

    def spawn(argv, cwd, env):
        spawned.append((argv, cwd, env))
        return handle

    values = dict(
        binary=Path("/p/pi"),
        trial=tmp_path,
        workspace=tmp_path / "workspace",
        prompt="Do the thing.",
        session_id="job-01",
        session_dir=tmp_path / "sessions",
        agent_dir=tmp_path / "agent",
        extensions=[WORKER],
        model="m",
        base_env={"PATH": "/bin"},
        spawn=spawn,
        clock=lambda: ticks.pop(0),
        deadline=300.0,
    )
    values.update(overrides)
    return session.run_session(**values), spawned


def test_the_child_starts_in_the_workspace_with_its_environment(tmp_path: Path) -> None:
    _, spawned = run(tmp_path, Handle())
    argv, cwd, env = spawned[0]
    assert cwd == tmp_path / "workspace"
    assert env["PI_CODING_AGENT_DIR"] == str(tmp_path / "agent")
    assert argv[0] == "/p/pi"


def test_the_outcome_carries_the_exit_status_and_the_clock(tmp_path: Path) -> None:
    outcome, _ = run(tmp_path, Handle(returncode=3))
    assert outcome.exit_status == 3
    assert outcome.elapsed_seconds == 2.5


def test_the_session_artifact_is_copied_beside_the_trial(tmp_path: Path) -> None:
    artifact = tmp_path / "sessions" / "--t--" / "2026-11-26T10-00-00Z_job-01.jsonl"
    outcome, _ = run(tmp_path, Handle(writes=artifact))
    assert outcome.trajectory == tmp_path / "trajectory.jsonl"
    assert outcome.trajectory.is_file()


def test_requests_are_counted_from_the_artifact_not_the_output(tmp_path: Path) -> None:
    artifact = tmp_path / "sessions" / "--t--" / "stamp_job-01.jsonl"
    outcome, _ = run(tmp_path, Handle(writes=artifact, stdout="999\n"))
    assert outcome.model_requests == 2


def test_an_absent_artifact_is_reported_not_invented(tmp_path: Path) -> None:
    outcome, _ = run(tmp_path, Handle())
    assert outcome.trajectory is None
    assert outcome.model_requests == 0


def test_a_bad_line_does_not_hide_the_good_ones(tmp_path: Path) -> None:
    artifact = tmp_path / "sessions" / "stamp_job-01.jsonl"
    artifact.parent.mkdir(parents=True)
    artifact.write_text(
        "{not json\n" + json.dumps({"type": "message", "message": {"role": "assistant"}}) + "\n"
    )
    assert session.count_requests(artifact) == 1


def test_the_stderr_tail_comes_back_for_a_failure(tmp_path: Path) -> None:
    class Failing(Handle):
        def communicate(self, timeout=None):
            return "", "boom\n"

    outcome, _ = run(tmp_path, Failing(returncode=1))
    assert "boom" in outcome.stderr


@pytest.mark.parametrize("extension", [WORKER, RECORDER])
def test_every_extension_reaches_the_child(tmp_path: Path, extension: Path) -> None:
    _, spawned = run(tmp_path, Handle(), extensions=[extension])
    assert str(extension) in spawned[0][0]


@pytest.mark.parametrize("line", ["null", "[]", "7", '"text"', "true"])
def test_a_valid_json_non_object_does_not_stop_the_count(tmp_path: Path, line: str) -> None:
    artifact = tmp_path / "sessions" / "stamp_job-01.jsonl"
    artifact.parent.mkdir(parents=True)
    artifact.write_text(
        line + "\n" + json.dumps({"type": "message", "message": {"role": "assistant"}}) + "\n"
    )
    assert session.count_requests(artifact) == 1


def test_the_deadline_reaches_the_child(tmp_path: Path) -> None:
    handle = Handle()
    run(tmp_path, handle, deadline=12.5)
    assert handle.calls == [("communicate", 12.5)]


def test_a_fired_deadline_kills_the_group_and_reaps_the_child(tmp_path: Path) -> None:
    handle = Handle(outlives_the_deadline=True)
    outcome, _ = run(tmp_path, handle)
    assert outcome.stopped is True
    assert handle.killed == 1
    assert outcome.exit_status == -9
    assert handle.calls == [("communicate", 300.0), ("communicate", None)]


def test_a_clean_run_is_not_stopped(tmp_path: Path) -> None:
    outcome, _ = run(tmp_path, Handle())
    assert outcome.stopped is False


def test_a_stopped_span_is_measured_from_the_same_start(tmp_path: Path) -> None:
    outcome, _ = run(tmp_path, Handle(outlives_the_deadline=True))
    assert outcome.elapsed_seconds == 2.5
