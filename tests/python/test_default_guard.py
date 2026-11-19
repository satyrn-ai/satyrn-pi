"""Python side of the default-test tripwire.

Forbidden examples are assembled from parts so this file never contains a
matching pattern when the guard scans its own tree.
"""
import importlib.util
import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
GUARD = REPO / "scripts" / "default_test_guard.py"
SUB = "sub" + "process"
SOCKET = "sock" + "et"
OS_IMPORT = "from os import " + "system"
OS_CALL = "os." + "system("


def load_guard():
    assert GUARD.exists(), "scripts/default_test_guard.py is missing"
    spec = importlib.util.spec_from_file_location("default_test_guard", GUARD)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def rules():
    return json.loads((REPO / "scripts" / "default-test-rules.json").read_text())


def test_the_guard_exposes_scan_source():
    guard = load_guard()
    assert callable(guard.scan_source)
    assert callable(guard.collect_python_tests)


def test_forbidden_imports_and_calls_fail(tmp_path):
    guard = load_guard()
    cases = [
        f"import {SUB}\n",
        f"import {SOCKET}\n",
        f"{OS_IMPORT}\n",
        f"{OS_CALL}'x')\n",
    ]
    for i, text in enumerate(cases):
        path = tmp_path / f"bad_{i}.py"
        path.write_text(text)
        assert guard.scan_source(str(path), text, rules()), text


def test_allowed_imports_pass(tmp_path):
    guard = load_guard()
    text = "import json\nimport pathlib\n"
    path = tmp_path / "ok.py"
    path.write_text(text)
    assert guard.scan_source(str(path), text, rules()) == []


def test_comments_do_not_trip_the_guard(tmp_path):
    guard = load_guard()
    text = f"# import {SUB}\n# {OS_CALL}'x')\n"
    path = tmp_path / "comment.py"
    path.write_text(text)
    assert guard.scan_source(str(path), text, rules()) == []


def test_the_python_tests_pass_the_tripwire():
    guard = load_guard()
    files = guard.collect_python_tests(REPO)
    assert files, "no Python tests found"
    findings = []
    for file in files:
        findings.extend(guard.scan_source(file, Path(file).read_text(), rules()))
    assert findings == []
