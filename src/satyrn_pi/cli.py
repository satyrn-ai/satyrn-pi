"""The eval CLI.

It resolves, prints, gates and records, in that order, and it does nothing else.
Every fact it would otherwise learn from the machine arrives as a probe, so the
default test suite can exercise the whole command without a process or a socket.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Sequence

from . import __version__
from .records import (
    aggregate_requests,
    job_id,
    job_path,
    load_trials,
    write_job,
    write_run,
)
from .resolve import ResolutionError, resolve_pi, resolve_suite, resolve_worker

CLI_VERSION = __version__
DEFAULT_BASE_URL = "http://127.0.0.1:8001/v1"
DEFAULT_MODEL = "Mellum2.1-12B-A2.5B-Thinking"
PEER_PACKAGE = "@earendil-works/pi-coding-agent"

OK = 0
STOPPED = 2


def peer_range(repo: Path) -> str:
    """The range this package promises an installer, read from the manifest."""
    manifest = json.loads((Path(repo) / "package.json").read_text())
    return manifest["peerDependencies"][PEER_PACKAGE]


def project_pi(repo: Path) -> Path:
    """The pinned install `npm ci` provides; absent until setup has run."""
    return Path(repo) / "node_modules" / ".bin" / "pi"


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="satyrn-pi", add_help=True)
    subcommands = parser.add_subparsers(dest="command")
    evaluate = subcommands.add_parser("eval", help="run a suite")
    evaluate.add_argument("--suite", required=True, help="suite name, e.g. basic")
    evaluate.add_argument("--worker", type=Path, default=None, help="explicit worker path")
    evaluate.add_argument("--base-url", default=DEFAULT_BASE_URL, help="OpenAI-compatible base")
    return parser


def _fail(message: str) -> int:
    print(f"satyrn-pi eval: {message}", file=sys.stderr)
    return STOPPED


def main(argv: Sequence[str], *, probes, runs_root: Path, cwd: Path) -> int:
    try:
        args = _parser().parse_args(list(argv))
    except SystemExit as exit_code:
        return int(exit_code.code or 0)

    if args.command != "eval":
        return _fail("no subcommand: expected eval")

    started = probes.monotonic()
    try:
        worker = resolve_worker(args.worker, probes.installed_worker)
        pi = resolve_pi(
            candidates=probes.pi_candidates,
            version_of=probes.version_of,
            peer_range=peer_range(cwd),
            exists=probes.exists,
        )
        suite_root = Path(probes.suite_root)
        suite = resolve_suite(args.suite, suite_root)
    except ResolutionError as error:
        return _fail(str(error))

    if not probes.server_health(args.base_url):
        return _fail(f"no server answered at {args.base_url}")

    offered = tuple(probes.server_models(args.base_url))
    if DEFAULT_MODEL not in offered:
        listed = ", ".join(offered) or "nothing"
        return _fail(
            f"the server at {args.base_url} does not serve {DEFAULT_MODEL} "
            f"(it lists: {listed}); this is not the pinned llama-server"
        )

    trials = load_trials(Path(probes.suite_root) / "trials")
    identifier = job_id(probes.now())
    path = job_path(Path(runs_root), suite, identifier)

    write_job(
        path,
        {
            "suite": suite.name,
            "suite_version": suite.version,
            "task_count": len(suite.tasks),
            "cli_version": CLI_VERSION,
            "repetition_count": 1,
            "worker_path": str(worker.path),
            "worker_entry": worker.entry,
            "worker_version": worker.version,
            "worker_source": worker.source,
            "pi_path": str(pi.path),
            "pi_version": pi.version,
            "pi_verified": pi.verified,
            "pi_source": pi.source,
            "model": DEFAULT_MODEL,
            "base_url": args.base_url,
            "started_at": identifier.rsplit("-", 1)[0],
        },
    )

    elapsed = round(probes.monotonic() - started, 3)
    write_run(
        path,
        {
            "status": "resolved",
            "model_requests": aggregate_requests(trials),
            "elapsed_seconds": elapsed,
            "counts_source": "fixtures",
            "exit_status": OK,
        },
    )

    print(f"worker   {worker.version} {worker.path} ({worker.source})")
    print(f"pi       {pi.version} ({'verified' if pi.verified else 'unverified'}, {pi.source})")
    print(f"suite    {suite.name} {suite.version}, {len(suite.tasks)} tasks")
    print(f"server   {args.base_url}")
    print(f"records  {path}")
    return OK


def installed_worker(cwd: Path) -> Path | None:
    """The worker an installed npm package would supply. P8 makes this real.

    The package's own name is unscoped, so it is checked first; scoped packages
    are the other shape an install can take. Two candidates would need a guess,
    so they stop the run instead of one being chosen by sort order.
    """
    root = Path(cwd) / "node_modules"
    candidates = [root / "satyrn-pi", *sorted(root.glob("@*/*"))]
    found = [
        candidate for candidate in candidates if _declares_worker(candidate / "package.json")
    ]
    if len(found) > 1:
        names = ", ".join(str(candidate) for candidate in found)
        raise ResolutionError(f"two installed workers: {names}; pass --worker")
    return found[0] if found else None


def _declares_worker(manifest: Path) -> bool:
    if not manifest.is_file():
        return False
    try:
        data = json.loads(manifest.read_text())
    except json.JSONDecodeError:
        return False
    if not isinstance(data, dict):
        return False
    satyrn = data.get("satyrn")
    return isinstance(satyrn, dict) and bool(satyrn.get("worker"))


def version_beside(binary: Path) -> str:
    """Read the version from the manifest the binary belongs to, without running it."""
    for parent in Path(binary).resolve().parents:
        manifest = parent / "package.json"
        if not manifest.is_file():
            continue
        try:
            version = json.loads(manifest.read_text()).get("version")
        except json.JSONDecodeError as error:
            raise ResolutionError(f"{manifest} is not valid JSON: {error}") from error
        if isinstance(version, str) and version.strip():
            return version
        raise ResolutionError(f"{manifest} declares no version")
    raise ResolutionError(f"cannot tell {binary}'s version without running it")


def health_url(base_url: str) -> str:
    """The health endpoint of the base URL's origin, whatever path it carries."""
    from urllib.parse import urlsplit

    parts = urlsplit(base_url)
    if parts.scheme not in ("http", "https") or not parts.netloc:
        raise ResolutionError(f"not an http(s) base URL: {base_url!r}")
    return f"{parts.scheme}://{parts.netloc}/health"


def server_models(base_url: str) -> tuple[str, ...]:
    """The model names a server offers, so a run cannot record one it never served."""
    import json as _json
    import urllib.error
    import urllib.request

    try:
        with urllib.request.urlopen(f"{base_url.rstrip('/')}/models", timeout=5) as response:
            payload = _json.loads(response.read())
    except (urllib.error.URLError, OSError, ValueError):
        return ()
    return tuple(
        entry.get("id", "") for entry in payload.get("data", []) if isinstance(entry, dict)
    )


def server_health(base_url: str) -> bool:
    """A real health check. The URL is built by `health_url`, tested without a socket."""
    import urllib.error
    import urllib.request

    try:
        with urllib.request.urlopen(health_url(base_url), timeout=5) as response:
            return response.status == 200
    except (urllib.error.URLError, OSError):
        return False


class RealProbes:
    """The probes a real run uses. Each one is still just an attribute."""

    def __init__(self, cwd: Path) -> None:
        import os
        import shutil
        from datetime import datetime, timezone

        self.installed_worker = lambda: installed_worker(cwd)
        path_pi = shutil.which("pi")
        self.pi_candidates = [("project", project_pi(cwd))]
        if path_pi:
            self.pi_candidates.append(("path", Path(path_pi)))
        self.version_of = version_beside
        self.server_health = server_health
        self.server_models = server_models
        self.suite_root = Path(
            os.environ.get("SATYRN_PI_SUITES", Path(__file__).parent / "suites")
        )
        self.now = lambda: datetime.now(timezone.utc)
        self.monotonic = time.monotonic
        self.exists = lambda path: Path(path).is_file()


def run() -> int:
    """The console entry: real probes, the repository root, the working directory."""
    cwd = Path.cwd()
    return main(sys.argv[1:], probes=RealProbes(cwd), runs_root=cwd / "runs", cwd=cwd)
