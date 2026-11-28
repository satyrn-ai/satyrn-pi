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
