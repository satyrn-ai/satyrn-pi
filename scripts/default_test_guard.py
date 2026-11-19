"""Python side of the default-test tripwire.

Reads the shared rule table and reports process or network usage in the default
Python tests. It reports; it never edits.
"""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load_rules(path=None):
    rules_path = Path(path) if path else HERE / "default-test-rules.json"
    return json.loads(rules_path.read_text())


def _strip_comment(line):
    return line.split("#", 1)[0]


IMPORT = re.compile(r"^\s*import\s+(.+)$")
FROM = re.compile(r"^\s*from\s+([A-Za-z0-9_.]+)\s+import\s+(.+)$")


def scan_source(path, text, rules):
    findings = []
    for number, raw in enumerate(text.splitlines(), start=1):
        line = _strip_comment(raw)
        modules = []
        from_names = []
        direct = IMPORT.match(line)
        if direct:
            modules = [part.strip().split(".")[0] for part in direct.group(1).split(",")]
        source = FROM.match(line)
        if source:
            modules = [source.group(1).split(".")[0]]
            from_names = [name.strip() for name in source.group(2).split(",")]
        for module in modules:
            if module in rules["pythonModules"]:
                findings.append(
                    {
                        "path": str(path),
                        "rule": "default-test",
                        "line": number,
                        "message": f"default tests must not import {module}",
                    }
                )
        for call in rules["pythonCalls"]:
            module, name = call.split(".", 1)
            if source and module in modules and name in from_names:
                findings.append(
                    {
                        "path": str(path),
                        "rule": "default-test",
                        "line": number,
                        "message": f"default tests must not call {call}",
                    }
                )
            if f"{call}(" in line:
                findings.append(
                    {
                        "path": str(path),
                        "rule": "default-test",
                        "line": number,
                        "message": f"default tests must not call {call}",
                    }
                )
    return findings


def collect_python_tests(root):
    base = Path(root) / "tests" / "python"
    return sorted(str(path) for path in base.rglob("*.py")) if base.exists() else []
