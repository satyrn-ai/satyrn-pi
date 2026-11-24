"""Resolve the worker, Pi and suite before a job exists.

Every probe arrives as an argument. Nothing here reads the environment, dials a
socket or starts a process, so a caller that forgets a probe gets a TypeError
rather than a network call.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, Mapping


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
    """A small subset of npm semver: ^, ~, >= and an exact version."""
    spec = text.strip()
    if spec.startswith("^"):
        low = parse_version(spec[1:])
        high = (low[0] + 1, 0, 0)
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


def _manifest(directory: Path) -> Mapping[str, object]:
    manifest = directory / "package.json"
    if not manifest.is_file():
        raise ResolutionError(f"no package.json in {directory}")
    try:
        return json.loads(manifest.read_text())
    except json.JSONDecodeError as error:
        raise ResolutionError(f"{manifest} is not valid JSON: {error}") from error


def _worker_from(directory: Path, source: str) -> Worker:
    manifest = _manifest(directory)
    satyrn = manifest.get("satyrn")
    if not isinstance(satyrn, Mapping) or not isinstance(satyrn.get("worker"), str):
        raise ResolutionError(f"{directory} declares no satyrn.worker entry")
    version = manifest.get("version")
    if not isinstance(version, str):
        raise ResolutionError(f"{directory} declares no version")
    return Worker(
        path=directory, version=version, entry=str(satyrn["worker"]), source=source
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
    return _worker_from(found, "installed")


def resolve_pi(
    *,
    candidates: Iterable[Path],
    version_of: Callable[[Path], str],
    peer_range: str,
    target: str = "1.5.2",
    exists: Callable[[Path], bool] = lambda path: path.is_file(),
) -> Pi:
    """The first existing candidate wins. In range but not the target is unverified.

    `exists` is injectable so tests need no files on disk, and so a caller can pass
    candidates in order without pre-filtering them.
    """
    tried: list[str] = []
    for candidate in candidates:
        if not exists(candidate):
            tried.append(f"{candidate} (absent)")
            continue
        version = version_of(candidate)
        if not satisfies(version, peer_range):
            tried.append(f"{candidate} ({version}, outside {peer_range})")
            continue
        source = "project" if "node_modules" in candidate.parts else "path"
        return Pi(
            path=candidate,
            version=version,
            verified=satisfies(version, target) or version == target,
            source=source,
        )
    detail = "; ".join(tried) if tried else "no candidates"
    raise ResolutionError(f"no usable Pi (required {peer_range}): {detail}")


def resolve_suite(name: str, root: Path) -> Suite:
    directory = root / f"suite-{name}"
    manifest = directory / "suite.json"
    if not manifest.is_file():
        raise ResolutionError(f"no suite {name!r} under {root}")
    data = json.loads(manifest.read_text())
    tasks = data.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        raise ResolutionError(f"{manifest} declares no tasks")
    return Suite(name=str(data["name"]), version=str(data["version"]), tasks=tuple(tasks))
