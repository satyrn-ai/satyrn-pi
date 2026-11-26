"""Write the records a job leaves behind.

`job.json` is written once, before anything runs; `run.json` last, so a directory
holding both is a finished job and a directory holding only the first is a job that
never got there. Filesystem only: no clock beyond the one passed in.
"""

from __future__ import annotations

import json
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Mapping

from .resolve import Suite


def job_id(moment: datetime) -> str:
    """A sortable UTC stamp plus a short suffix, so concurrent runs cannot collide."""
    stamp = moment.astimezone(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")
    return f"{stamp}-{secrets.token_hex(3)}"


def job_path(runs: Path, suite: Suite, identifier: str) -> Path:
    day = identifier.split("T", 1)[0]
    return Path(runs) / f"{day}-{suite.name}" / identifier


def load_trials(directory: Path) -> list[Mapping[str, object]]:
    return [
        json.loads(path.read_text())
        for path in sorted(Path(directory).glob("*.json"))
    ]


def aggregate_requests(trials: Iterable[Mapping[str, object]]) -> int:
    """Model requests add up. Elapsed seconds do not, and never call this for them."""
    return sum(int(trial["model_requests"]) for trial in trials)


def _write(path: Path, name: str, payload: Mapping[str, object]) -> None:
    path.mkdir(parents=True, exist_ok=True)
    target = path / name
    temporary = target.with_suffix(f"{target.suffix}.tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    temporary.replace(target)


def write_job(path: Path, job: Mapping[str, object]) -> None:
    _write(path, "job.json", job)


def write_run(path: Path, run: Mapping[str, object]) -> None:
    _write(path, "run.json", run)
