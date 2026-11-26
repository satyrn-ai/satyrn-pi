"""Resolve the worker, Pi and suite before a job exists.

Every probe arrives as an argument. Nothing here reads the environment, dials a
socket or starts a process, so a caller that forgets a probe gets a TypeError
rather than a network call.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, Mapping, Sequence

TASK_FIELDS = ("id", "instructions", "fixture", "verification")


class ResolutionError(RuntimeError):
    """An input could not be resolved, or would need a guess to resolve."""


@dataclass(frozen=True)
class Worker:
    path: Path
    version: str
    entry: str
    source: str


@dataclass(frozen=True)
class Pi:
    path: Path
    version: str
    verified: bool
    source: str


@dataclass(frozen=True)
class Suite:
    name: str
    version: str
    tasks: tuple[Mapping[str, str], ...]


def parse_version(text: str) -> tuple[int, int, int]:
    parts = text.strip().split(".")
    if len(parts) != 3 or not all(part.isdigit() for part in parts):
        raise ResolutionError(f"not a version: {text!r}")
    major, minor, patch = (int(part) for part in parts)
    return major, minor, patch


def parse_range(text: str) -> Callable[[tuple[int, int, int]], bool]:
    """The subset of npm semver this repository needs: ^, ~, >= and an exact version.

    Caret and tilde follow npm's rules for a zero major version, where the first
    non-zero component is the one that may not change.
    """
    spec = text.strip()
    if spec.startswith("^"):
        low = parse_version(spec[1:])
        if low[0] > 0:
            high = (low[0] + 1, 0, 0)
        elif low[1] > 0:
            high = (0, low[1] + 1, 0)
        else:
            high = (0, 0, low[2] + 1)
        return lambda version: low <= version < high
    if spec.startswith("~"):
        low = parse_version(spec[1:])
        high = (low[0], low[1] + 1, 0)
        return lambda version: low <= version < high
    if spec.startswith(">="):
        low = parse_version(spec[2:])
        return lambda version: version >= low
    exact = parse_version(spec)
    return lambda version: version == exact


def satisfies(version: str, declared: str) -> bool:
    return parse_range(declared)(parse_version(version))


def _read_json(path: Path, what: str) -> Mapping[str, object]:
    if not path.is_file():
        raise ResolutionError(f"no {what} at {path}")
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as error:
        raise ResolutionError(f"{path} is not valid JSON: {error}") from error
    if not isinstance(data, Mapping):
        raise ResolutionError(f"{path} must be a JSON object")
    return data


def _required_text(manifest: Mapping[str, object], field: str, path: Path) -> str:
    value = manifest.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ResolutionError(f"{path} needs a {field} string")
    return value


def _worker_from(directory: Path, source: str) -> Worker:
    path = Path(directory) / "package.json"
    manifest = _read_json(path, "worker manifest")
    satyrn = manifest.get("satyrn")
    if not isinstance(satyrn, Mapping):
        raise ResolutionError(f"{path} declares no satyrn block")
    entry = satyrn.get("worker")
    if not isinstance(entry, str) or not entry.strip():
        raise ResolutionError(f"{path} declares no satyrn.worker entry")
    root = Path(directory).resolve()
    candidate = (root / entry).resolve()
    if root not in candidate.parents or not candidate.is_file():
        raise ResolutionError(f"{path} names {entry}, which is not in the directory")
    return Worker(
        path=Path(directory),
        version=_required_text(manifest, "version", path),
        entry=entry,
        source=source,
    )


def resolve_worker(
    explicit: Path | None, installed: Callable[[], Path | None]
) -> Worker:
    """An explicit path wins; the installed package is the fallback, not a tiebreak."""
    if explicit is not None:
        return _worker_from(explicit, "explicit")
    found = installed()
    if found is None:
        raise ResolutionError(
            "no worker: nothing explicit (--worker) and nothing installed resolved"
        )
    return _worker_from(Path(found), "installed")


def resolve_pi(
    *,
    candidates: Sequence[tuple[str, Path]],
    version_of: Callable[[Path], str],
    peer_range: str,
    target: str = "1.5.2",
    exists: Callable[[Path], bool] = lambda path: path.is_file(),
) -> Pi:
    """Candidates are (source, path) in priority order; provenance comes with them.

    A version inside the declared range runs; only the target is verified.
    """
    tried: list[str] = []
    for source, candidate in candidates:
        if not exists(candidate):
            tried.append(f"{candidate} (absent)")
            continue
        version = version_of(candidate)
        if not satisfies(version, peer_range):
            tried.append(f"{candidate} ({version}, outside {peer_range})")
            continue
        return Pi(
            path=Path(candidate),
            version=version,
            verified=version == target,
            source=source,
        )
    detail = "; ".join(tried) if tried else "no candidates"
    raise ResolutionError(f"no usable Pi (required {peer_range}): {detail}")


def resolve_suite(name: str, root: Path) -> Suite:
    """Validate the whole suite here: a task that fails later fails after a job exists."""
    path = Path(root) / f"suite-{name}" / "suite.json"
    manifest = _read_json(path, "suite manifest")
    declared = _required_text(manifest, "name", path)
    if declared != name:
        raise ResolutionError(f"{path} names itself {declared!r}, not {name!r}")
    version = _required_text(manifest, "version", path)
    tasks = manifest.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        raise ResolutionError(f"{path} declares no tasks")
    validated: list[Mapping[str, str]] = []
    for index, task in enumerate(tasks, start=1):
        if not isinstance(task, Mapping):
            raise ResolutionError(f"{path} task {index} is not an object")
        for field in TASK_FIELDS:
            if not isinstance(task.get(field), str) or not task[field].strip():
                raise ResolutionError(f"{path} task {index} needs a {field} string")
        validated.append({field: task[field] for field in TASK_FIELDS})
    return Suite(name=declared, version=version, tasks=tuple(validated))
