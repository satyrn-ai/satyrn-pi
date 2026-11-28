import hashlib, json
from pathlib import Path

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
