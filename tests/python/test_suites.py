import hashlib, json, pathlib
from pathlib import Path

import pytest

from satyrn_pi.suite_data import SuiteDataError, load_suite_data

SUITES = Path(__file__).resolve().parents[2] / "src" / "satyrn_pi" / "suites"
NAMES = ("easy", "medium", "hard")


def test_the_manifest_matches_the_copied_tree():
    for name in NAMES:
        root, source = SUITES / f"suite-{name}", SUITES / f"suite-{name}" / "source"
        copied = json.loads((root / "SOURCES.json").read_text())["copied"]
        on_disk = {str(p.relative_to(source)) for p in source.rglob("*") if p.is_file()}
        assert set(copied) == on_disk, name
        for relative, digest in copied.items():
            assert hashlib.sha256((source / relative).read_bytes()).hexdigest() == digest


def test_the_instruction_is_the_prompts_joined():
    for name in NAMES:
        root = SUITES / f"suite-{name}"
        manifest = json.loads((root / "suite.json").read_text())
        task = manifest["tasks"][0]
        prompts = [
            path.read_text().strip()
            for path in sorted((root / "source" / "prompts").glob("*.md"))
        ]
        assert task["instructions"] == "\n\n".join(prompts), name
        assert task["fixture"] == "source", name
        assert task["verification"].strip(), name


def test_the_prompt_mode_is_joined():
    for name in NAMES:
        manifest = json.loads((SUITES / f"suite-{name}" / "suite.json").read_text())
        assert manifest["promptMode"] == "joined", name
        assert manifest["version"] == "1", name


def build(tmp_path, *, copied=("base/app.py", "expected.json"),
          expected=("grader_tests/t.py::test_a",), graders=(), stray=None,
          duplicate=False):
    root = tmp_path / "suite-x"
    for relative in copied:
        target = root / "source" / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("x")
    if stray:
        (root / "source" / stray).parent.mkdir(parents=True, exist_ok=True)
        (root / "source" / stray).write_text("x")
    for module in graders:
        (root / "graders").mkdir(parents=True, exist_ok=True)
        (root / "graders" / module).write_text("x")
    ids = list(expected) + (list(expected) if duplicate else [])
    (root / "source" / "expected.json").write_text(json.dumps(ids))
    (root / "SOURCES.json").write_text(json.dumps({
        "repository": "andrevanzuydam/mellum-worker", "commit": "c", "hash": "sha256",
        "copied": {relative: "0" * 64 for relative in copied},
        "reference": {"grader/t.py": "0" * 64}, "authored": ["suite.json"],
    }))
    (root / "suite.json").write_text("{}")
    return root


def test_a_stray_file_in_the_copy_is_refused(tmp_path):
    with pytest.raises(SuiteDataError, match="stray"):
        load_suite_data(build(tmp_path, stray="base/extra.py"))


def test_a_missing_copied_file_is_refused(tmp_path):
    root = build(tmp_path)
    (root / "source" / "base" / "app.py").unlink()
    with pytest.raises(SuiteDataError, match="missing"):
        load_suite_data(root)


def test_a_duplicated_expected_id_is_refused(tmp_path):
    with pytest.raises(SuiteDataError, match="duplicate"):
        load_suite_data(build(tmp_path, duplicate=True))


def test_an_id_outside_the_prefix_is_refused(tmp_path):
    with pytest.raises(SuiteDataError, match="grader_tests/"):
        load_suite_data(build(tmp_path, expected=("test.py::test_a",)))


def test_an_expected_module_absent_from_graders_is_refused(tmp_path):
    with pytest.raises(SuiteDataError, match=r"t\.py"):
        load_suite_data(build(tmp_path, graders=("other.py",)))


def test_a_suite_without_a_copy_is_refused(tmp_path):
    (tmp_path / "suite-x").mkdir()
    with pytest.raises(SuiteDataError, match="source"):
        load_suite_data(tmp_path / "suite-x")


def test_a_reference_entry_needs_no_local_file(tmp_path):
    data = load_suite_data(build(tmp_path))
    assert data.provenance.reference == ("grader/t.py",)
    assert data.graders is None


def test_the_pinned_suites_load():
    for name in NAMES:
        data = load_suite_data(SUITES / f"suite-{name}")
        assert data.graders is None
        assert data.expected
        assert all(one.startswith("grader_tests/") for one in data.expected)


def _suite_manifest(root, name="x"):
    root.mkdir(parents=True, exist_ok=True)
    (root / "suite.json").write_text(json.dumps({
        "name": name, "version": "1",
        "tasks": [{"id": "t", "instructions": "do it", "fixture": "source",
                   "verification": "it works"}],
    }))
    return root


def test_a_suite_whose_manifest_disagrees_is_refused_by_resolve():
    from satyrn_pi.resolve import ResolutionError, resolve_suite
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        root = pathlib.Path(tmp)
        suite = _suite_manifest(root / "suite-x")
        (suite / "source").mkdir()
        (suite / "source" / "a.py").write_text("x")
        with pytest.raises(ResolutionError, match="SOURCES.json"):
            resolve_suite("x", root)


def test_a_fixture_shaped_suite_still_resolves_without_data():
    from satyrn_pi.resolve import resolve_suite
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        root = pathlib.Path(tmp)
        _suite_manifest(root / "suite-x")
        suite = resolve_suite("x", root)
        assert suite.data is None
