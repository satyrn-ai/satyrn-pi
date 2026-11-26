"""The trial record, replaced at each boundary.

A trial that never reached a final status stays a status, not a failure: partial
is a state the record can hold honestly, and it never looks complete.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Mapping

STATUSES = ("prepared", "running", "session-ended", "graded", "stopped")
FINAL = ("graded", "stopped")
RESULT_FIELDS = ("verdict", "score")
RESULT_STATUS = "graded"


def write_trial(trial: Path, update: Mapping[str, object]) -> None:
    """Merge `update` into `trial.json`, refusing a status outside the closed set."""
    trial = Path(trial)
    trial.mkdir(parents=True, exist_ok=True)
    target = trial / "trial.json"
    existing: dict[str, object] = {}
    if target.is_file():
        existing = json.loads(target.read_text())
    merged = {**existing, **update}
    status = merged.get("status")
    if status not in STATUSES:
        raise ValueError(f"unknown trial status: {status!r}")
    if status != RESULT_STATUS:
        leaked = [field for field in RESULT_FIELDS if field in merged]
        if leaked:
            raise ValueError(
                f"a trial at {status!r} cannot carry {', '.join(leaked)}"
            )
    temporary = target.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(merged, indent=2, sort_keys=True) + "\n")
    temporary.replace(target)
