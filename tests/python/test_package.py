"""Package skeleton smoke tests. No model, no network, no subprocess."""

import tomllib
from pathlib import Path

import satyrn_pi

PYPROJECT = Path(__file__).resolve().parents[2] / "pyproject.toml"


def test_version_is_a_string() -> None:
    assert isinstance(satyrn_pi.__version__, str)
    assert satyrn_pi.__version__


def test_version_matches_pyproject() -> None:
    with PYPROJECT.open("rb") as handle:
        project = tomllib.load(handle)["project"]
    assert satyrn_pi.__version__ == project["version"]
    assert project["name"] == "satyrn-pi"
