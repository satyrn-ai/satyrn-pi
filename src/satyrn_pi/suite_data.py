"""Validate a suite's copied tree, its provenance and its expected checks.

A suite is data before it is work: the copy must be the copy the manifest names, and the
expected checks must be checks the graders could actually run. Both are decided before a
job directory exists, so a broken suite costs a message rather than a run.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

SOURCES_NAME = "SOURCES.json"
SOURCE_DIR = "source"
GRADERS_DIR = "graders"
EXPECTED_NAME = "expected.json"
GRADER_PREFIX = "grader_tests/"
MANIFEST_KEYS = ("repository", "commit", "hash", "copied", "reference", "authored")


class SuiteDataError(ValueError):
    """A suite's data disagrees with its manifest or its graders."""


@dataclass(frozen=True)
class Provenance:
    """What came from the source, what was re-earned, what the port wrote."""

    copied: Mapping[str, str]
    reference: tuple[str, ...]
    authored: tuple[str, ...]


@dataclass(frozen=True)
class SuiteData:
    """The parts of a suite a job records before anything runs."""

    expected: tuple[str, ...]
    provenance: Provenance
    graders: Path | None


def _manifest(suite_dir: Path) -> dict:
    path = suite_dir / SOURCES_NAME
    if not path.is_file():
        raise SuiteDataError(f"{path} is missing")
    try:
        manifest = json.loads(path.read_text())
    except json.JSONDecodeError as error:
        raise SuiteDataError(f"{path} is not JSON: {error}") from error
    missing = [key for key in MANIFEST_KEYS if key not in manifest]
    if missing:
        raise SuiteDataError(f"{path} is missing {', '.join(missing)}")
    for key in ("copied", "reference"):
        if not isinstance(manifest[key], dict):
            raise SuiteDataError(f"{path} {key} is not an object")
    if not isinstance(manifest["authored"], list):
        raise SuiteDataError(f"{path} authored is not a list")
    return manifest


def _expected_ids(source: Path) -> tuple[str, ...]:
    path = source / EXPECTED_NAME
    if not path.is_file():
        return ()
    try:
        ids = json.loads(path.read_text())
    except json.JSONDecodeError as error:
        raise SuiteDataError(f"{path} is not JSON: {error}") from error
    if not isinstance(ids, list) or not all(isinstance(one, str) for one in ids):
        raise SuiteDataError(f"{path} is not a list of strings")
    seen: set[str] = set()
    duplicates: list[str] = []
    for identifier in ids:
        if identifier in seen:
            duplicates.append(identifier)
        seen.add(identifier)
    if duplicates:
        raise SuiteDataError(f"{path} has duplicate ids: {', '.join(duplicates)}")
    unprefixed = [one for one in ids if not one.startswith(GRADER_PREFIX)]
    if unprefixed:
        raise SuiteDataError(
            f"{path} has ids outside {GRADER_PREFIX}: {', '.join(unprefixed)}"
        )
    return tuple(ids)


def _module_of(identifier: str) -> str:
    return identifier[len(GRADER_PREFIX):].split("::", 1)[0]


def _check_graders(ids: tuple[str, ...], graders: Path | None) -> None:
    if graders is None or not ids:
        return
    available = {path.name for path in graders.iterdir() if path.is_file()}
    absent = sorted({_module_of(one) for one in ids} - available)
    if absent:
        raise SuiteDataError(
            f"{graders} has no module for expected ids: {', '.join(absent)}"
        )


def load_suite_data(suite_dir: Path) -> SuiteData:
    """Return the suite's checked data, or raise `SuiteDataError` naming what failed."""
    suite_dir = Path(suite_dir)
    source = suite_dir / SOURCE_DIR
    if not source.is_dir():
        raise SuiteDataError(f"{suite_dir} has no {SOURCE_DIR}/ tree")
    manifest = _manifest(suite_dir)
    copied = manifest["copied"]
    on_disk = {
        str(path.relative_to(source))
        for path in source.rglob("*")
        if path.is_file()
    }
    stray = sorted(on_disk - set(copied))
    if stray:
        raise SuiteDataError(f"{source} has files the manifest does not name: {', '.join(stray)}")
    missing = sorted(set(copied) - on_disk)
    if missing:
        raise SuiteDataError(f"{source} is missing files the manifest names: {', '.join(missing)}")
    ids = _expected_ids(source)
    graders_dir = suite_dir / GRADERS_DIR
    graders = graders_dir if graders_dir.is_dir() else None
    _check_graders(ids, graders)
    return SuiteData(
        expected=ids,
        provenance=Provenance(
            copied=dict(copied),
            reference=tuple(sorted(manifest["reference"])),
            authored=tuple(manifest["authored"]),
        ),
        graders=graders,
    )
