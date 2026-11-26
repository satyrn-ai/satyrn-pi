"""Start the Pi child for one trial and collect what it left behind.

Everything the machine would supply — the spawn callable, the environment and the
clock — arrives as an argument, so the default suite can exercise the whole child
boundary without starting a process. The real spawn lives in `cli.RealProbes`.
"""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Mapping, Sequence

PROVIDER = "satyrn"
TRAJECTORY_NAME = "trajectory.jsonl"
CONTEXT_WINDOW = 50000
MAX_TOKENS = 16384
SAMPLING = {"temperature": 1.0, "top_p": 0.95, "top_k": 20}


@dataclass(frozen=True)
class Outcome:
    """What a finished child leaves: its status, its clock and its artifact."""

    exit_status: int
    elapsed_seconds: float
    model_requests: int
    trajectory: Path | None
    stderr: str


def session_argv(
    *,
    binary: Path,
    prompt: str,
    session_id: str,
    session_dir: Path,
    extensions: Sequence[Path],
    model: str,
) -> list[str]:
    """Print mode, a fixed provider and model, explicit extensions, then the prompt.

    Discovery is off and every extension is named, so the list the job records is
    the list that loaded. The prompt arrives as an argument, never as a file the
    agent could read from its workspace.
    """
    argv = [
        str(binary),
        "--print",
        "--no-extensions",
        "--provider",
        PROVIDER,
        "--model",
        model,
        "--session-id",
        session_id,
        "--session-dir",
        str(session_dir),
    ]
    for extension in extensions:
        argv.extend(["--extension", str(extension)])
    argv.extend(["--", prompt])
    return argv


def session_env(base: Mapping[str, str], *, agent_dir: Path) -> dict[str, str]:
    """The caller's environment with only the agent directory replaced."""
    env = dict(base)
    env["PI_CODING_AGENT_DIR"] = str(agent_dir)
    return env


def write_agent_profile(directory: Path, *, base_url: str, model: str) -> None:
    """Give the child the server this job checked and the model it pinned.

    A private agent directory with nothing in it cannot reach a model; writing the
    provider here is what makes the directory private *and* usable. The sampling
    values are the ones the reference host card quotes.
    """
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    profile = {
        "providers": {
            PROVIDER: {
                "name": "Satyrn eval",
                "baseUrl": base_url,
                "api": "openai-completions",
                "apiKey": "not-needed",
                "models": [
                    {
                        "id": model,
                        "name": model,
                        "reasoning": True,
                        "input": ["text"],
                        "cost": {
                            "input": 0,
                            "output": 0,
                            "cacheRead": 0,
                            "cacheWrite": 0,
                        },
                        "contextWindow": CONTEXT_WINDOW,
                        "maxTokens": MAX_TOKENS,
                        "samplingParams": dict(SAMPLING),
                        "compat": {
                            "supportsDeveloperRole": False,
                            "supportsReasoningEffort": False,
                            "maxTokensField": "max_tokens",
                            "thinkingFormat": "qwen-chat-template",
                        },
                    }
                ],
            }
        }
    }
    settings = {"defaultProvider": PROVIDER, "defaultModel": model}
    (directory / "models.json").write_text(json.dumps(profile, indent=2) + "\n")
    (directory / "settings.json").write_text(json.dumps(settings, indent=2) + "\n")


def collect_trajectory(session_dir: Path, session_id: str, trial: Path) -> Path | None:
    """Copy the session file Pi named after this id, or say there is none."""
    matches = sorted(Path(session_dir).rglob(f"*_{session_id}.jsonl"))
    if not matches:
        return None
    target = Path(trial) / TRAJECTORY_NAME
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(matches[-1], target)
    return target


def count_requests(trajectory: Path) -> int:
    """One assistant message is one model response; tool results are not."""
    requests = 0
    for line in Path(trajectory).read_text().splitlines():
        if not line.strip():
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(entry, Mapping) or entry.get("type") != "message":
            continue
        message = entry.get("message")
        if isinstance(message, Mapping) and message.get("role") == "assistant":
            requests += 1
    return requests


def run_session(
    *,
    binary: Path,
    trial: Path,
    workspace: Path,
    prompt: str,
    session_id: str,
    session_dir: Path,
    agent_dir: Path,
    extensions: Sequence[Path],
    model: str,
    base_env: Mapping[str, str],
    spawn: Callable[[Sequence[str], Path, Mapping[str, str]], object],
    clock: Callable[[], float],
) -> Outcome:
    """Spawn one child, wait for it, and turn its remains into an `Outcome`.

    An interrupt kills the child's process group and reaps it before the
    exception continues, so no descendant outlives the run that started it.
    """
    argv = session_argv(
        binary=binary,
        prompt=prompt,
        session_id=session_id,
        session_dir=session_dir,
        extensions=extensions,
        model=model,
    )
    started = clock()
    handle = spawn(argv, Path(workspace), session_env(base_env, agent_dir=agent_dir))
    try:
        _, stderr = handle.communicate()
    except KeyboardInterrupt:
        handle.kill_group()
        handle.communicate()
        raise
    elapsed = round(clock() - started, 3)
    trajectory = collect_trajectory(session_dir, session_id, Path(trial))
    return Outcome(
        exit_status=int(handle.exit_status),
        elapsed_seconds=elapsed,
        model_requests=count_requests(trajectory) if trajectory else 0,
        trajectory=trajectory,
        stderr=stderr or "",
    )
