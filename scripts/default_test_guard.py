"""Python side of the default-test tripwire.

Parses the default Python tests with `ast` and reports process or network
imports and calls. It reports; it never edits.
"""
import ast
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load_rules(path=None):
    rules_path = Path(path) if path else HERE / "default-test-rules.json"
    return json.loads(rules_path.read_text())


def _add(findings, path, node, message):
    findings.append(
        {
            "path": str(path),
            "rule": "default-test",
            "line": getattr(node, "lineno", 0),
            "message": message,
        }
    )


def scan_source(path, text, rules):
    findings = []
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return findings
    os_modules = {"os"}
    os_functions = set()
    calls = set()
    for call in rules["pythonCalls"]:
        module, name = call.split(".", 1)
        calls.add(name)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                if root in rules["pythonModules"]:
                    _add(findings, path, node, f"default tests must not import {alias.name}")
                if root == "os":
                    os_modules.add(alias.asname or alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = (node.module or "").split(".")[0]
            if module in rules["pythonModules"]:
                _add(findings, path, node, f"default tests must not import {module}")
            if module == "os":
                for alias in node.names:
                    if alias.name in calls:
                        os_functions.add(alias.asname or alias.name)
                        _add(findings, path, node, f"default tests must not call os.{alias.name}")
        elif isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
                if func.value.id in os_modules and func.attr in calls:
                    _add(findings, path, node, f"default tests must not call {func.value.id}.{func.attr}")
            elif isinstance(func, ast.Name) and func.id in os_functions:
                _add(findings, path, node, f"default tests must not call {func.id}")
    return findings


def collect_python_tests(root):
    base = Path(root) / "tests" / "python"
    return sorted(str(path) for path in base.rglob("*.py")) if base.exists() else []
