"""The eval CLI.

It resolves, prints, gates and records, in that order, and it does nothing else.
Every fact it would otherwise learn from the machine arrives as a probe, so the
default test suite can exercise the whole command without a process or a socket.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
from pathlib import Path
from typing import Sequence

from . import __version__
from . import session
from .records import (
    aggregate_requests,
    job_id,
    job_path,
    read_trials,
    write_job,
    write_run,
)
from .resolve import ResolutionError, resolve_pi, resolve_suite, resolve_worker
from .trial import write_trial
from .workspace import PROMPT_NAME, WorkspaceError, prepare

CLI_VERSION = __version__
DEFAULT_BASE_URL = "http://127.0.0.1:8001/v1"
DEFAULT_MODEL = "Mellum2.1-12B-A2.5B-Thinking"
DEFAULT_DEADLINE_SECONDS = 300.0
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
    evaluate.add_argument(
        "--deadline",
        type=float,
        default=DEFAULT_DEADLINE_SECONDS,
        help="seconds one Pi session may run before its process group is killed",
    )
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
    if not math.isfinite(args.deadline) or args.deadline <= 0:
        return _fail(f"--deadline must be positive seconds, not {args.deadline:g}")

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

    identifier = job_id(probes.now())
    path = job_path(Path(runs_root), suite, identifier)
    extension = (Path(worker.path) / worker.entry).resolve()

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
            "extensions": [str(extension)],
            "deadline_seconds": args.deadline,
            "started_at": identifier.rsplit("-", 1)[0],
        },
    )

    sessions = path / "sessions"
    failures = 0
    stopped = 0
    for index, task in enumerate(suite.tasks, start=1):
        trial = path / f"trial-{index:02d}"
        session_id = f"{identifier}-trial-{index:02d}"
        write_trial(
            trial,
            {
                "task": task["id"],
                "status": "prepared",
                "model": DEFAULT_MODEL,
                "worker": str(worker.path),
                "worker_version": worker.version,
                "pi_version": pi.version,
            },
        )
        try:
            workspace = prepare(task, suite_root / f"suite-{suite.name}", trial)
        except WorkspaceError as error:
            return _fail(str(error))

        write_trial(trial, {"status": "running", "session_id": session_id})
        agent_dir = trial / "agent"
        session.write_agent_profile(agent_dir, base_url=args.base_url, model=DEFAULT_MODEL)
        outcome = session.run_session(
            binary=pi.path,
            trial=trial,
            workspace=workspace,
            prompt=(trial / PROMPT_NAME).read_text().strip(),
            session_id=session_id,
            session_dir=sessions,
            agent_dir=agent_dir,
            extensions=[extension],
            model=DEFAULT_MODEL,
            base_env=probes.base_env,
            spawn=probes.spawn,
            clock=probes.monotonic,
            deadline=args.deadline,
        )
        record: dict[str, object] = {
            "status": "stopped" if outcome.stopped else "session-ended",
            "exit_status": outcome.exit_status,
            "elapsed_seconds": outcome.elapsed_seconds,
            "model_requests": outcome.model_requests,
            "trajectory": session.TRAJECTORY_NAME if outcome.trajectory else None,
        }
        if outcome.stopped:
            record["stopped_by"] = "deadline"
        write_trial(trial, record)
        if outcome.stopped:
            stopped += 1
            print(
                f"{trial.name} stopped after {args.deadline:g}s; no further trials started",
                file=sys.stderr,
            )
            break
        if outcome.exit_status != 0:
            failures += 1
            print(f"{trial.name}: Pi exited with status {outcome.exit_status}", file=sys.stderr)
            if outcome.stderr.strip():
                print(outcome.stderr.strip()[-400:], file=sys.stderr)

    records = read_trials(path)
    requests = aggregate_requests(records)
    elapsed = round(probes.monotonic() - started, 3)
    exit_status = OK if failures == 0 and stopped == 0 else STOPPED
    write_run(
        path,
        {
            "status": "stopped" if stopped else "session-ended",
            "trials": len(records),
            "failures": failures,
            "stopped": stopped,
            "model_requests": requests,
            "elapsed_seconds": elapsed,
            "counts_source": "sessions",
            "exit_status": exit_status,
        },
    )

    print(f"worker   {worker.version} {worker.path} ({worker.source})")
    print(f"pi       {pi.version} ({'verified' if pi.verified else 'unverified'}, {pi.source})")
    print(f"suite    {suite.name} {suite.version}, {len(suite.tasks)} tasks")
    print(f"server   {args.base_url}")
    print(
        f"sessions {len(records) - stopped} ended, {failures} failed, {stopped} stopped, "
        f"{requests} model requests"
    )
    print(f"records  {path}")
    return exit_status


def installed_worker() -> Path | None:
    """The worker an installed npm package would supply. P8 makes this real."""
    for candidate in sorted(Path("node_modules").glob("@*/*")):
        manifest = candidate / "package.json"
        if not manifest.is_file():
            continue
        try:
            data = json.loads(manifest.read_text())
        except json.JSONDecodeError:
            continue
        if isinstance(data.get("satyrn"), dict) and data["satyrn"].get("worker"):
            return candidate
    return None


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


def kill_group(pid: int) -> None:
    """Kill the group the child leads.

    `start_new_session=True` makes the child a session and group leader, so its
    pid *is* the group id. Looking the group up with `getpgid` would fail on the
    very race this guards: a child that has just been reaped has no pgid, while
    its descendants may still be running.
    """
    import signal

    try:
        os.killpg(pid, signal.SIGKILL)
    except ProcessLookupError:
        pass


class RealProcess:
    """The one place a child is started. Its own session group is P5.4's to kill."""

    def __init__(self, argv, cwd: Path, env) -> None:
        import subprocess

        self._process = subprocess.Popen(
            list(argv),
            cwd=str(cwd),
            env=dict(env),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            start_new_session=True,
        )

    def communicate(self, timeout: float | None = None) -> tuple[str, str]:
        """Wait, translating the child's timeout into the boundary's own signal."""
        import subprocess

        try:
            return self._process.communicate(timeout=timeout)
        except subprocess.TimeoutExpired as error:
            raise session.TimedOut() from error

    def kill_group(self) -> None:
        """Kill everything the child started, not only the child."""
        kill_group(self._process.pid)

    @property
    def exit_status(self) -> int:
        return int(self._process.returncode)


class RealProbes:
    """The probes a real run uses. Each one is still just an attribute."""

    def __init__(self, cwd: Path) -> None:
        import os
        import shutil
        from datetime import datetime, timezone

        self.installed_worker = installed_worker
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
        self.spawn = RealProcess
        self.base_env = dict(os.environ)


def run() -> int:
    """The console entry: real probes, the repository root, the working directory."""
    cwd = Path.cwd()
    return main(sys.argv[1:], probes=RealProbes(cwd), runs_root=cwd / "runs", cwd=cwd)
