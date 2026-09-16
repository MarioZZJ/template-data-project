#!/usr/bin/env python3
"""Portable single-job research runtime. Task state and dependencies stay in Multica."""
from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import plistlib
import re
import shutil
import signal
import socket
import subprocess
import sys
import tarfile
import tempfile
import time
import uuid
import venv

SCHEMA = "research-run/v1"


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".write-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


@contextlib.contextmanager
def locked(path, timeout=60):
    """OS-backed lock, automatically released on crash; portable stdlib only."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+b") as handle:
        if handle.tell() == 0:
            handle.write(b"0")
            handle.flush()
        until = time.monotonic() + timeout
        while True:
            try:
                if os.name == "nt":
                    import msvcrt
                    handle.seek(0)
                    msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except (OSError, BlockingIOError):
                if time.monotonic() >= until:
                    raise RuntimeError(f"Another operation holds {path.name}; retry after it finishes")
                time.sleep(0.05)
        try:
            yield
        finally:
            if os.name == "nt":
                import msvcrt
                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.flock(handle, fcntl.LOCK_UN)


def call(argv, cwd=None, env=None):
    result = subprocess.run(argv, cwd=cwd, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode:
        # Commands can contain private configuration: do not echo argv or stderr.
        raise RuntimeError(f"{Path(str(argv[0])).name} failed (exit {result.returncode}); inspect the local environment")
    return result.stdout.strip()


def git(repo, *args):
    return call(["git", "-C", str(repo), *args])


def repository(path):
    return Path(git(Path(path).resolve(), "rev-parse", "--show-toplevel")).resolve()


def origin_identity(repo):
    try:
        remote = git(repo, "remote", "get-url", "origin")
    except RuntimeError:
        return None
    # Strip authentication/query fragments; normalize common SSH and HTTPS spellings.
    from urllib.parse import urlsplit, unquote
    if "://" in remote:
        parsed = urlsplit(remote)
        if parsed.scheme == "file":
            identity = "local:" + str(Path(unquote(parsed.path)).resolve())
        else:
            host = (parsed.hostname or "").lower()
            default_port = {"ssh": 22, "https": 443, "http": 80}.get(parsed.scheme)
            if parsed.port is not None and parsed.port != default_port:
                host += ":" + str(parsed.port)
            identity = host + "/" + parsed.path.strip("/")
    elif re.match(r"^[^/]+@[^:]+:", remote):
        identity = remote.split("@", 1)[1].replace(":", "/", 1)
    else:
        local = Path(remote).expanduser()
        identity = "local:" + str((local if local.is_absolute() else repo / local).resolve())
    return identity.removesuffix(".git").rstrip("/")


def valid_name(name):
    if not name or name in {".", ".."} or not re.fullmatch(r"[\w][\w.-]*", name, re.UNICODE):
        raise ValueError("Project name must be a readable directory name without separators")
    return name


def common_dir(repo):
    raw = Path(git(repo, "rev-parse", "--git-common-dir"))
    return str((repo / raw).resolve()) if not raw.is_absolute() else str(raw.resolve())


def locate(args, create=False):
    repo = repository(args.repo)
    home = Path(args.assets_home).expanduser().resolve()
    origin = origin_identity(repo)
    common = common_dir(repo)
    with locked(home / ".projects.lock"):
        registry_path = home / "projects.json"
        registry = read_json(registry_path) if registry_path.exists() else {"schema": "research-projects/v1", "projects": []}
        matches = [p for p in registry["projects"] if (origin and origin in p["origins"]) or common in p["git_common_dirs"]]
        if len(matches) > 1:
            raise RuntimeError("Origin and checkout map to different projects; resolve projects.json explicitly")
        if matches:
            entry = matches[0]
            if create:
                if args.project_name and args.project_name != entry["name"]:
                    raise ValueError("Project is already mapped; renaming does not move assets automatically")
                if args.asset_root and str(Path(args.asset_root).expanduser().resolve()) != entry["asset_root"]:
                    raise ValueError("Existing asset mapping differs; migrate explicitly before changing it")
                if origin and origin not in entry["origins"]:
                    entry["origins"].append(origin)
                if common not in entry["git_common_dirs"]:
                    entry["git_common_dirs"].append(common)
                atomic_json(registry_path, registry)
            return repo, Path(entry["asset_root"]), entry
        if not create:
            raise RuntimeError("Project has not been initialized; run setup first")
        name = valid_name(args.project_name or (origin.rsplit("/", 1)[-1] if origin else ""))
        if any(p["name"] == name for p in registry["projects"]):
            raise ValueError("A different origin already uses this name; choose --project-name with a readable alias")
        root = Path(args.asset_root).expanduser().resolve() if args.asset_root else home / name
        if any(Path(p["asset_root"]).resolve() == root for p in registry["projects"]):
            raise ValueError("Asset root already belongs to another project")
        if root.exists() and any(root.iterdir()):
            raise ValueError("Unregistered asset root is not empty; inspect and register it explicitly")
        for directory in ("inputs", "envs", "runs", "deliveries"):
            (root / directory).mkdir(parents=True, exist_ok=True)
        entry = {"name": name, "origins": [origin] if origin else [], "git_common_dirs": [common], "asset_root": str(root), "created_at": now()}
        registry["projects"].append(entry)
        atomic_json(registry_path, registry)
        return repo, root, entry


def digest(path):
    sha = hashlib.sha256()
    with Path(path).open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            sha.update(chunk)
    return sha.hexdigest()


def dependency_key(repo, stdlib, extras):
    sha = hashlib.sha256()
    sha.update(json.dumps([sys.version_info[:2], sys.platform, stdlib, sorted(extras)]).encode())
    if not stdlib:
        for name in ("pyproject.toml", "uv.lock"):
            path = repo / name
            if not path.is_file():
                raise ValueError(f"{name} is required; use --stdlib only for dependency-free demonstrations")
            content = path.read_bytes()
            # Local/editable dependencies can preserve references to a disappearing worktree.
            if name == "uv.lock" and re.search(rb"(?:editable|directory)\s*=\s*[\"'](?!\.[\"'])", content):
                raise ValueError("Local path dependencies need a separately fixed source; external worktree references are unsupported")
            if name == "pyproject.toml" and re.search(rb"\b(?:path|workspace)\s*=", content):
                raise ValueError("Local path/workspace dependencies need a separately fixed source")
            sha.update(name.encode() + content)
    return sha.hexdigest()[:20]


def python_in(env):
    return env / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def prepare_env(repo, root, stdlib=False, extras=()):
    key = dependency_key(repo, stdlib, extras)
    env = root / "envs" / key
    with locked(root / "envs" / (key + ".lock"), timeout=300):
        ready = env / ".research-ready.json"
        if ready.exists() and python_in(env).is_file():
            return env
        if stdlib:
            venv.EnvBuilder(with_pip=False).create(env)
        else:
            uv = shutil.which("uv")
            if not uv:
                raise RuntimeError("uv is required; install it and retry setup")
            variables = os.environ.copy()
            variables["UV_PROJECT_ENVIRONMENT"] = str(env)
            argv = [uv, "sync", "--frozen", "--no-editable", "--project", str(repo)]
            for extra in extras:
                argv.extend(["--extra", extra])
            call(argv, env=variables)
        if not python_in(env).is_file():
            raise RuntimeError("Stable environment has no Python interpreter")
        atomic_json(ready, {"dependency_key": key, "stdlib": stdlib, "extras": list(extras), "created_at": now()})
    return env


def platform_supervisor():
    if sys.platform.startswith("linux"):
        return "systemd"
    if sys.platform == "darwin":
        return "launchd"
    if os.name == "nt":
        return "windows"
    raise RuntimeError("No supported persistent supervisor on this platform")


def supervisor_available(kind):
    command = {"systemd": "systemd-run", "launchd": "launchctl", "windows": "powershell.exe"}[kind]
    if not shutil.which(command):
        return False
    if kind == "systemd":
        result = subprocess.run(["systemctl", "--user", "show-environment"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return result.returncode == 0
    return True


def setup(args):
    repo, root, _ = locate(args, create=True)
    env = prepare_env(repo, root, args.stdlib, args.extra)
    atomic_json(root / "environment.json", {"stdlib": args.stdlib, "extras": args.extra, "environment_dir": str(env)})
    supervisor = platform_supervisor()
    return {"asset_root": str(root), "environment_dir": str(env), "supervisor": supervisor, "supervisor_available": supervisor_available(supervisor), "note": "Native platform availability is not an end-to-end run test"}


def snapshot(repo, commit, destination):
    with tempfile.TemporaryFile() as archive:
        proc = subprocess.run(["git", "-C", str(repo), "archive", "--format=tar", commit], stdout=archive, stderr=subprocess.PIPE)
        if proc.returncode:
            raise RuntimeError("Could not create committed code snapshot")
        archive.seek(0)
        with tarfile.open(fileobj=archive) as source:
            # Only regular files/directories and internal relative symlinks, never devices/hardlinks.
            members = source.getmembers()
            base = destination.resolve()
            for member in members:
                target = (base / member.name).resolve()
                if not target.is_relative_to(base) or not (member.isfile() or member.isdir() or member.issym()):
                    raise ValueError("Unsafe path or unsupported file type in Git snapshot")
                if member.issym() and (Path(member.linkname).is_absolute() or not (target.parent / member.linkname).resolve().is_relative_to(base)):
                    raise ValueError("Snapshot symlinks must remain inside the fixed code tree")
            # extractall(filter=...) is not available in Python 3.10; members were validated above.
            if hasattr(tarfile, "data_filter"):
                source.extractall(base, members=members, filter="data")
            else:
                source.extractall(base, members=members)


def parse_deadline(value):
    if not value:
        return None
    parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("Deadline must include a UTC offset or Z")
    return parsed


def inputs_for(root, specs):
    inputs = []
    for spec in specs:
        if "=" not in spec:
            raise ValueError("--input requires NAME=PATH")
        name, raw = spec.split("=", 1)
        valid_name(name)
        path = Path(raw).expanduser().resolve()
        if not path.is_file():
            raise ValueError("Each fixed input must be a file; use an explicit manifest for a dataset directory")
        if not path.is_relative_to(root / "inputs") and not path.is_relative_to(root / "runs"):
            raise ValueError("Inputs must be fixed files under project inputs/ or an earlier run/")
        if any(item["name"] == name for item in inputs):
            raise ValueError("Input names must be unique")
        inputs.append({"name": name, "path": str(path), "sha256": digest(path), "size": path.stat().st_size})
    return inputs


def psquote(text):
    return "'" + str(text).replace("'", "''") + "'"


def launch(record, record_path):
    kind = record["supervisor"]["kind"]
    identifier = record["supervisor"]["id"]
    argv = [str(python_in(Path(record["environment_dir"]))), str(record_path.parent / "runtime.py"), "_worker", str(record_path)]
    if kind == "systemd":
        call(["systemd-run", "--user", "--unit", identifier, "--collect", "--property=Type=exec", "--property=Restart=no", "--property=KillMode=control-group", *argv])
    elif kind == "launchd":
        plist = record_path.parent / "supervisor.plist"
        with plist.open("wb") as handle:
            plistlib.dump({"Label": identifier, "ProgramArguments": argv, "RunAtLoad": True, "KeepAlive": False, "WorkingDirectory": str(record_path.parent), "StandardOutPath": str(record_path.parent / "logs/supervisor.stdout.log"), "StandardErrorPath": str(record_path.parent / "logs/supervisor.stderr.log")}, handle)
        call(["launchctl", "bootstrap", f"gui/{os.getuid()}", str(plist)])
    elif kind == "windows":
        # Register an on-demand task (no future trigger that could repeat paid work).
        arguments = subprocess.list2cmdline(argv[1:])
        script = "$ErrorActionPreference='Stop'; " + f"$action=New-ScheduledTaskAction -Execute {psquote(argv[0])} -Argument {psquote(arguments)} -WorkingDirectory {psquote(record_path.parent)}; " + "$settings=New-ScheduledTaskSettingsSet -ExecutionTimeLimit ([TimeSpan]::Zero) -MultipleInstances IgnoreNew; " + f"Register-ScheduledTask -TaskName {psquote(identifier)} -Action $action -Settings $settings | Out-Null; Start-ScheduledTask -TaskName {psquote(identifier)}"
        call(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", script])
    else:
        raise ValueError("Unknown supervisor")


def run(args):
    repo, root, _ = locate(args)
    command = list(args.command)
    if command and command[0] == "--":
        command.pop(0)
    if not command:
        raise ValueError("run requires a command after --")
    if git(repo, "status", "--porcelain", "--untracked-files=all"):
        raise ValueError("Commit the intended changes and resolve unrelated dirty files before run; the runtime never commits automatically")
    if git(repo, "ls-files", "--stage").find("160000 ") >= 0:
        raise ValueError("Submodules must have an explicit fixed snapshot strategy before long jobs")
    if any(str(repo) in argument for argument in command):
        raise ValueError("Command references the disposable checkout; use paths relative to the fixed code snapshot")
    config = read_json(root / "environment.json")
    commit = git(repo, "rev-parse", "HEAD")
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ-") + uuid.uuid4().hex[:12]
    directory = root / "runs" / run_id
    for name in ("code", "data", "outputs", "logs"):
        (directory / name).mkdir(parents=True)
    snapshot(repo, commit, directory / "code")
    env = prepare_env(directory / "code", root, config["stdlib"], config["extras"])
    deadline = parse_deadline(args.deadline)
    if deadline and deadline <= dt.datetime.now(dt.timezone.utc):
        raise ValueError("Deadline is already in the past")
    if args.attempt_limit < 1:
        raise ValueError("Attempt limit must be positive")
    budgets = json.loads(args.budget_json) if args.budget_json else {}
    if not isinstance(budgets, dict):
        raise ValueError("Budget metadata must be an object")
    if args.issue_id:
        uuid.UUID(args.issue_id)
    kind = "foreground" if args.foreground else platform_supervisor()
    if kind != "foreground" and not supervisor_available(kind):
        raise RuntimeError("Native supervisor unavailable; fix it or use --foreground for synchronous diagnostics")
    record = {"schema": SCHEMA, "run_id": run_id, "issue_id": args.issue_id, "status": "prepared", "command": command, "code_commit": commit, "code_dir": str(directory / "code"), "environment_dir": str(env), "asset_root": str(root), "inputs": inputs_for(root, args.input), "artifacts": [], "checks": [], "created_at": now(), "started_at": None, "finished_at": None, "exit_code": None, "supervisor": {"kind": kind, "id": "research-" + run_id.lower()}, "deadline": args.deadline, "attempts": 0, "attempt_limit": args.attempt_limit, "budgets": budgets, "execution_host": socket.gethostname(), "execution_platform": sys.platform}
    record_path = directory / "run.json"
    shutil.copy2(Path(__file__).resolve(), directory / "runtime.py")
    record["runtime_sha256"] = digest(directory / "runtime.py")
    atomic_json(record_path, record)
    if args.foreground:
        worker(record_path)
    else:
        try:
            launch(record, record_path)
        except Exception:
            # A launch request may have reached the supervisor. Never submit it again automatically.
            with locked(directory / ".state.lock"):
                latest = read_json(record_path)
                latest["launch_outcome"] = "unknown; inspect supervisor before any retry"
                atomic_json(record_path, latest)
            raise
    return read_json(record_path)


def dotenv(path, env):
    if not path.exists():
        return
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:]
        if "=" not in line:
            raise ValueError(f"Invalid .env assignment at line {number}")
        key, value = line.split("=", 1)
        key, value = key.strip(), value.strip()
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key):
            raise ValueError(f"Invalid .env key at line {number}")
        if value[:1] in ("'", '"'):
            if value[-1:] != value[:1] or len(value) < 2:
                raise ValueError(f"Invalid quoted .env value at line {number}")
            value = value[1:-1]
        env.setdefault(key, value)


def stop_process(process):
    if process.poll() is not None:
        return
    if os.name == "nt":
        subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        with contextlib.suppress(ProcessLookupError):
            os.killpg(process.pid, signal.SIGTERM)
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            with contextlib.suppress(ProcessLookupError):
                os.killpg(process.pid, signal.SIGKILL)
    process.wait()


def worker(record_path):
    record_path = Path(record_path).resolve()
    directory = record_path.parent
    with locked(directory / ".worker.lock", timeout=0):
        with locked(directory / ".state.lock"):
            record = read_json(record_path)
            # An OS restart or duplicate launch must not resubmit computation.
            if record["status"] != "prepared" or record["attempts"] != 0:
                return
            record.update(status="running", started_at=now(), worker_pid=os.getpid(), attempts=1)
            atomic_json(record_path, record)
        cancelled = [False]
        def on_signal(signum, frame):
            cancelled[0] = True
        for sig in (signal.SIGTERM, signal.SIGINT):
            signal.signal(sig, on_signal)
        process = None
        exit_code = 1
        failure = None
        state = "failed"
        try:
            env = os.environ.copy()
            dotenv(Path(record["asset_root"]) / ".env", env)
            # Task tokens expire at session exit and never belong to persistent research jobs.
            env.pop("MULTICA_TOKEN", None)
            stable_python = python_in(Path(record["environment_dir"]))
            env["PATH"] = str(stable_python.parent) + os.pathsep + env.get("PATH", "")
            env["VIRTUAL_ENV"] = record["environment_dir"]
            env["DATA_ROOT"] = str(Path(record["asset_root"]) / "inputs")
            env["RUN_DIR"] = str(directory)
            env["OUTPUT_ROOT"] = str(directory / "outputs")
            env["PYTHONUNBUFFERED"] = "1"
            env.pop("PYTHONPATH", None)
            for item in record["inputs"]:
                if digest(item["path"]) != item["sha256"]:
                    raise RuntimeError("Fixed input changed after submission")
            command = record["command"][:]
            if command[0] in ("python", "python3", "python.exe"):
                command[0] = str(stable_python)
            deadline = parse_deadline(record["deadline"])
            if cancelled[0] or (deadline and dt.datetime.now(dt.timezone.utc) >= deadline):
                failure = "cancelled" if cancelled[0] else "deadline_exceeded"
                state = "cancelled" if cancelled[0] else "failed"
                raise RuntimeError("Job expired before computation started")
            with (directory / "logs/stdout.log").open("ab") as out, (directory / "logs/stderr.log").open("ab") as err:
                options = {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP} if os.name == "nt" else {"start_new_session": True}
                process = subprocess.Popen(command, cwd=record["code_dir"], env=env, stdout=out, stderr=err, **options)
                with locked(directory / ".state.lock"):
                    record["process_pid"] = process.pid
                    atomic_json(record_path, record)
                while process.poll() is None:
                    if cancelled[0] or (deadline and dt.datetime.now(dt.timezone.utc) >= deadline):
                        failure = "cancelled" if cancelled[0] else "deadline_exceeded"
                        stop_process(process)
                        break
                    time.sleep(0.1)
                exit_code = process.returncode
            if failure:
                state = "cancelled" if cancelled[0] else "failed"
            else:
                state = "succeeded" if exit_code == 0 else "failed"
            changed = [item["name"] for item in record["inputs"] if not Path(item["path"]).is_file() or digest(item["path"]) != item["sha256"]]
            if changed:
                state, failure = "failed", "fixed_input_modified"
        except BaseException as exc:
            if process is not None:
                stop_process(process)
            # Any post-exit evidence failure invalidates a successful process exit.
            state = "cancelled" if cancelled[0] else "failed"
            # Do not include exception values, which may contain credentials or command arguments.
            failure = failure or "worker_error:" + type(exc).__name__
        finally:
            artifacts = []
            try:
                for path in sorted((directory / "outputs").rglob("*")):
                    if path.is_file() and not path.is_symlink():
                        artifacts.append({"path": str(path), "sha256": digest(path), "size": path.stat().st_size})
            except (OSError, ValueError) as exc:
                state = "failed"
                failure = "artifact_evidence_error:" + type(exc).__name__
            with locked(directory / ".state.lock"):
                record.update(status=state, exit_code=exit_code, finished_at=now(), artifacts=artifacts)
                if failure:
                    record["failure_reason"] = failure
                atomic_json(record_path, record)


def supervisor_active(record):
    kind, identifier = record["supervisor"]["kind"], record["supervisor"]["id"]
    if kind == "systemd":
        result = subprocess.run(["systemctl", "--user", "is-active", identifier], capture_output=True, text=True)
        if result.returncode == 0:
            return True
        return False if result.stdout.strip() in {"inactive", "failed", "unknown"} else None
    if kind == "launchd":
        result = subprocess.run(["launchctl", "print", f"gui/{os.getuid()}/{identifier}"], capture_output=True, text=True)
        if result.returncode:
            return False if "Could not find service" in result.stderr else None
        return "state = running" in result.stdout
    if kind == "windows":
        result = subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", f"(Get-ScheduledTask -TaskName {psquote(identifier)} -ErrorAction Stop).State"], capture_output=True, text=True)
        if result.returncode:
            return None
        return result.stdout.strip() in {"Running", "Queued"}
    pid = record.get("worker_pid")
    if not pid:
        return False
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def reconcile_run(record_path, grace_seconds=60):
    """Mark proven abandoned jobs failed; never restart a research command.

    Call explicitly from status --reconcile or an authorized local monitor.
    It is safe to import this function from the bridge on the execution host.
    """
    record_path = Path(record_path)
    initial = read_json(record_path)
    if initial["status"] not in {"prepared", "running"}:
        return initial
    if initial.get("execution_host") != socket.gethostname():
        return initial
    age = dt.datetime.now(dt.timezone.utc) - dt.datetime.fromisoformat(initial["created_at"])
    if age.total_seconds() < grace_seconds or supervisor_active(initial) is not False:
        return initial
    try:
        with locked(record_path.parent / ".worker.lock", timeout=0):
            with locked(record_path.parent / ".state.lock"):
                current = read_json(record_path)
                if current["status"] in {"prepared", "running"} and supervisor_active(current) is False:
                    current.update(status="failed", finished_at=now(), exit_code=None,
                                   failure_reason="supervisor_ended_without_result",
                                   recovery_evidence={"observed_at": now(), "supervisor_active": False, "worker_lock_free": True})
                    atomic_json(record_path, current)
                return current
    except RuntimeError:
        return read_json(record_path)  # A live worker still owns the job.


def run_record(root, run_id):
    valid_name(run_id)
    path = root / "runs" / run_id / "run.json"
    if not path.is_file():
        raise ValueError("Unknown run ID")
    return path


def status(args):
    repo, root, _ = locate(args)
    if args.dashboard_from:
        snapshot_data = read_json(args.dashboard_from)
        snapshot_data["source_url"] = snapshot_data.get("source_url") or snapshot_data.get("source")
        if not snapshot_data.get("source_url") or not snapshot_data.get("generated_at") or not isinstance(snapshot_data.get("issues"), list):
            raise ValueError("Dashboard input needs source_url, generated_at and issues from Multica")
        def cell(value):
            return str(value).replace("|", "\\|").replace("\n", " ")
        lines = ["# 项目进展快照", "", f"来源：{snapshot_data['source_url']}", f"生成时间：{snapshot_data['generated_at']}", "", "<!-- Generated from Multica. Do not maintain task state here. -->", "", "| 任务 | 状态 |", "|---|---|"]
        for item in snapshot_data["issues"]:
            lines.append(f"| [{cell(item['identifier'])} {cell(item['title'])}]({item['url']}) | {cell(item['status'])} |")
        target = Path(args.dashboard)
        if not target.is_absolute():
            target = repo / target
        for field, title in (("phases", "阶段"), ("decisions", "待决事项"), ("artifacts", "关键成果")):
            lines.extend(["", "## " + title, ""])
            items = snapshot_data.get(field)
            if not items:
                lines.append("快照未提供。")
            else:
                for item in items:
                    if isinstance(item, str):
                        lines.append("- " + cell(item))
                    else:
                        label = cell(item.get("title", item.get("name", item.get("path", "未命名"))))
                        link = item.get("url")
                        state = item.get("status")
                        lines.append("- " + (f"[{label}]({link})" if link else label) + ("：" + cell(state) if state else ""))
        begin, end = "<!-- BEGIN MULTICA STATUS -->", "<!-- END MULTICA STATUS -->"
        section = begin + "\n" + "\n".join(lines) + "\n" + end
        old = target.read_text(encoding="utf-8") if target.exists() else ""
        if (begin in old) != (end in old) or old.count(begin) > 1 or old.count(end) > 1:
            raise ValueError("Dashboard contains incomplete or duplicate generated-section markers")
        if begin in old:
            left, right = old.index(begin), old.index(end) + len(end)
            if right < left:
                raise ValueError("Dashboard markers are out of order")
            updated = old[:left] + section + old[right:]
        else:
            updated = old.rstrip() + ("\n\n" if old else "") + section + "\n"
        target.write_text(updated, encoding="utf-8")
    paths = [run_record(root, args.run_id)] if args.run_id else sorted((root / "runs").glob("*/run.json"))
    result = []
    for path in paths:
        record = reconcile_run(path) if args.reconcile else read_json(path)
        if record["status"] in {"running", "prepared"}:
            record["observed_supervisor_active"] = supervisor_active(record)
            if record["observed_supervisor_active"] is False:
                record["attention"] = "Supervisor is inactive without terminal evidence; inspect logs before resubmitting"
        result.append(record)
    return {"asset_root": str(root), "runs": result, "notification_note": "Notification receipt is maintained by the independent bridge"}


def write_delivery_once(path, value):
    """Publish a complete immutable JSON file without an overwrite window."""
    path = Path(path)
    with locked(path.parent / ".delivery.lock"):
        if path.exists():
            raise FileExistsError("Final delivery already exists; immutable records cannot be overwritten")
        atomic_json(path, value)


def finalize_delivery(args, root):
    if args.draft or args.artifact or args.check or args.run_id or args.research_impact or args.scope_complete or args.review_required:
        raise ValueError("Finalize uses the unchanged draft; do not supply new scope, artifacts or checks")
    if args.issue_revision is None or args.issue_revision < 0:
        raise ValueError("Finalize requires a non-negative --issue-revision")
    if not args.review_evidence:
        raise ValueError("Finalize requires the independent review comment UUID")
    uuid.UUID(args.review_evidence)
    draft_path = Path(args.finalize).expanduser().resolve()
    value = read_json(draft_path)
    identifier = valid_name(value.get("delivery_id", ""))
    expected = root / "deliveries" / (identifier + ".draft.json")
    if draft_path != expected.resolve():
        raise ValueError("Draft must be this project's canonical delivery draft")
    if value.get("schema") != "research-delivery/v1" or value.get("result") != "awaiting_review" or not value.get("scope_complete") or not value.get("review", {}).get("required"):
        raise ValueError("Not a complete delivery draft awaiting independent review")
    if value.get("issue_id") != args.issue_id:
        raise ValueError("Draft belongs to a different issue")
    if not value.get("checks") or any(item.get("ok") is not True for item in value["checks"]) or not value.get("artifacts"):
        raise ValueError("Draft is missing full-scope checks or artifacts")
    for item in value["artifacts"]:
        path = Path(item["path"]).resolve()
        if not path.is_relative_to(root / "runs") and not path.is_relative_to(root / "deliveries"):
            raise ValueError("Draft artifact is outside stable project assets")
        if not path.is_file() or digest(path) != item.get("sha256"):
            raise ValueError("Draft artifact changed after preparation; create and review a new draft")
    value.update(result="ready", issue_revision=args.issue_revision, finalized_at=now(), review={"required": True, "passed": True, "evidence": {"comment_id": args.review_evidence}})
    path = root / "deliveries" / (identifier + ".json")
    write_delivery_once(path, value)
    return {"delivery_path": str(path), "record": value, "next_action": "Post the final attachment through the active agent execution; the bridge verifies the reviewer and revision."}


def deliver(args):
    _, root, _ = locate(args)
    uuid.UUID(args.issue_id)
    if args.finalize:
        return finalize_delivery(args, root)
    if args.draft and (not args.review_required or args.issue_revision is not None or args.review_evidence):
        raise ValueError("--draft requires --review-required and cannot have revision or completed review evidence")
    if not args.scope_complete:
        raise ValueError("A ready delivery requires --scope-complete after checking the full task")
    if not args.check or not args.artifact or not args.research_impact:
        raise ValueError("A delivery requires artifacts, named completed checks and research impact")
    if args.review_required and not args.review_evidence and not args.draft:
        raise ValueError("Required independent review needs --draft followed by --finalize with --review-evidence")
    if args.run_id:
        record = read_json(run_record(root, args.run_id))
        if record["status"] != "succeeded" or not record.get("finished_at") or record.get("exit_code") != 0:
            raise ValueError("Run has not completed successfully; inspect evidence before delivery")
        if record.get("issue_id") != args.issue_id:
            raise ValueError("Run belongs to a different issue")
    identifier = "research-delivery-" + uuid.uuid4().hex
    artifact_directory = root / "deliveries" / identifier / "artifacts"
    artifacts = []
    for number, raw in enumerate(args.artifact):
        path = Path(raw).expanduser().resolve()
        if not path.is_file():
            raise ValueError("Delivery artifacts must be existing files")
        if path.name == ".env" or path.name.startswith(".env.") or ".multica" in path.parts:
            raise ValueError("Credential/configuration files cannot be delivery artifacts")
        source = path
        if not path.is_relative_to(root / "runs") and not path.is_relative_to(root / "deliveries"):
            artifact_directory.mkdir(parents=True, exist_ok=True)
            path = artifact_directory / (f"{number:03d}-" + source.name)
            shutil.copy2(source, path)
        artifacts.append({"path": str(path), "source_path": str(source), "sha256": digest(path), "size": path.stat().st_size})
    evidence = args.review_evidence
    if args.review_required and evidence:
        uuid.UUID(evidence)
        evidence = {"comment_id": evidence}
    value = {"schema": "research-delivery/v1", "delivery_id": identifier, "issue_id": args.issue_id, "run_id": args.run_id, "result": "awaiting_review" if args.draft else "ready", "scope_complete": True, "artifacts": artifacts, "checks": [{"name": name, "ok": True} for name in args.check], "research_impact": args.research_impact, "review": {"required": args.review_required, "passed": bool(args.review_evidence), "evidence": evidence}, "created_at": now()}
    if args.issue_revision is not None:
        if args.issue_revision < 0:
            raise ValueError("Issue revision must be non-negative")
        value["issue_revision"] = args.issue_revision
    path = root / "deliveries" / (identifier + (".draft.json" if args.draft else ".json"))
    write_delivery_once(path, value)
    return {"delivery_path": str(path), "record": value, "next_action": "Request independent review of this exact draft; do not submit it as ready." if args.draft else "Post through the active agent execution. The bridge independently verifies source identity, latest comment and issue revision."}


def export(args):
    repo, root, _ = locate(args)
    if not args.accepted_by.strip():
        raise ValueError("Export requires explicit acceptance evidence in --accepted-by")
    record = read_json(run_record(root, args.run_id))
    if record["status"] != "succeeded" or record.get("exit_code") != 0:
        raise ValueError("Only successfully completed runs can be selected for formal export")
    source = (Path(record["code_dir"]).parent / "outputs" / args.file).resolve()
    output_root = (Path(record["code_dir"]).parent / "outputs").resolve()
    if not source.is_relative_to(output_root) or not source.is_file():
        raise ValueError("Export must select an existing file inside this run's outputs")
    recorded = next((item for item in record["artifacts"] if Path(item["path"]).resolve() == source), None)
    if not recorded or digest(source) != recorded["sha256"]:
        raise ValueError("Artifact differs from the completed run evidence")
    filename = args.name or source.name
    if Path(filename).name != filename or filename in {".", ".."}:
        raise ValueError("Export name must be a filename")
    target = repo / "outputs" / args.kind / filename
    for candidate in (repo / "outputs", target.parent, target):
        if candidate.is_symlink():
            raise ValueError("Formal output paths must not contain symlinks")
    if not target.resolve().is_relative_to(repo / "outputs"):
        raise ValueError("Formal output escapes the repository outputs directory")
    with locked(root / ".export.lock"):
        index_path = repo / "outputs/provenance.json"
        if index_path.is_symlink():
            raise ValueError("Provenance index must not be a symlink")
        checkout_key = hashlib.sha256(str(repo).encode()).hexdigest()[:20]
        journal = root / "export-transactions" / (checkout_key + ".json")
        # If a prior process died mid-install, recover before any new export.
        if journal.exists():
            recover_export(journal, repo)
        index = read_json(index_path) if index_path.exists() else {"schema": "research-export/v1", "artifacts": []}
        if target.exists() and not args.replace:
            raise ValueError("Formal output already exists; review it and explicitly pass --replace")
        target.parent.mkdir(parents=True, exist_ok=True)
        relative = target.relative_to(repo).as_posix()
        evidence = {"path": relative, "sha256": recorded["sha256"], "source_run_id": record["run_id"], "source_artifact": str(source), "code_commit": record["code_commit"], "command": record["command"], "inputs": record["inputs"], "accepted_by": args.accepted_by, "exported_at": now()}
        previous = next((item for item in index["artifacts"] if item["path"] == relative), None)
        if previous:
            evidence["previous_versions"] = previous.get("previous_versions", []) + [{k: v for k, v in previous.items() if k != "previous_versions"}]
        index["artifacts"] = [item for item in index["artifacts"] if item["path"] != relative] + [evidence]
        token = uuid.uuid4().hex
        staged_target = target.parent / (".export-" + token + ".tmp")
        staged_index = index_path.parent / (".export-index-" + token + ".tmp")
        old_target = target.parent / (".export-old-" + token + ".tmp")
        old_index = index_path.parent / (".export-old-index-" + token + ".tmp")
        transaction = {"target": str(target), "index": str(index_path), "target_existed": target.exists(), "index_existed": index_path.exists(), "old_target": str(old_target), "old_index": str(old_index), "staged_target": str(staged_target), "staged_index": str(staged_index)}
        try:
            shutil.copy2(source, staged_target)
            if digest(staged_target) != recorded["sha256"]:
                raise ValueError("Artifact changed during export; staged copy is not the accepted artifact")
            atomic_json(staged_index, index)  # Fail before modifying either public file.
            if target.exists():
                shutil.copy2(target, old_target)
            if index_path.exists():
                shutil.copy2(index_path, old_index)
            atomic_json(journal, transaction)
            os.replace(staged_target, target)
            os.replace(staged_index, index_path)
            journal.unlink()  # Commit point; both public files now agree.
        except BaseException:
            if journal.exists():
                recover_export(journal, repo)
            raise
        finally:
            if not journal.exists():
                for temporary in (staged_target, staged_index, old_target, old_index):
                    temporary.unlink(missing_ok=True)
    return evidence


def recover_export(journal, repo):
    """Recover a two-file installation interrupted before its commit point."""
    transaction = read_json(journal)
    for field in ("target", "index", "old_target", "old_index", "staged_target", "staged_index"):
        path = Path(transaction[field])
        if path.is_symlink() or not path.resolve().is_relative_to(repo / "outputs"):
            raise ValueError("Export recovery path is outside repository outputs")
    for public, backup, existed in (("target", "old_target", "target_existed"), ("index", "old_index", "index_existed")):
        path, old = Path(transaction[public]), Path(transaction[backup])
        if transaction[existed]:
            # Copy the backup through a new temp file; retain backups until the journal clears.
            temporary = path.parent / (".export-restore-" + uuid.uuid4().hex + ".tmp")
            shutil.copy2(old, temporary)
            os.replace(temporary, path)
        else:
            path.unlink(missing_ok=True)
    Path(journal).unlink()
    for field in ("old_target", "old_index", "staged_target", "staged_index"):
        Path(transaction[field]).unlink(missing_ok=True)


def parser():
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--repo", default=".", help="Any path in the research Git checkout")
    result.add_argument("--assets-home", default=str(Path.home() / "ResearchAssets"), help="Visible registry directory (default: ~/ResearchAssets)")
    sub = result.add_subparsers(dest="action", required=True)
    p = sub.add_parser("setup", help="Map the project and prepare a stable dependency environment")
    p.add_argument("--project-name", help="Explicit readable alias; required when origin is absent")
    p.add_argument("--asset-root", help="Explicit asset root on a user-selected disk")
    p.add_argument("--stdlib", action="store_true", help="Dependency-free demonstration only; do not sync project dependencies")
    p.add_argument("--extra", action="append", default=[], help="Optional uv dependency extra (repeatable)")
    p = sub.add_parser("run", help="Submit one committed step to the native persistent supervisor")
    p.add_argument("--issue-id", help="Multica issue UUID; optional for local demonstrations")
    p.add_argument("--input", action="append", default=[], help="Fixed file NAME=PATH; use a manifest for a dataset")
    p.add_argument("--deadline", help="Absolute ISO timestamp with timezone; preserved across process restart")
    p.add_argument("--attempt-limit", type=int, default=1, help="Recorded limit; runtime never resubmits calculation automatically")
    p.add_argument("--budget-json", help="Resource budget metadata; cost enforcement belongs to the research command")
    p.add_argument("--foreground", action="store_true", help="Synchronous diagnostics; not a detached persistent job")
    p.add_argument("command", nargs=argparse.REMAINDER, help="Command argv after --; never put credentials in argv")
    p = sub.add_parser("status", help="Read real run evidence; optionally render an explicit Multica snapshot")
    p.add_argument("run_id", nargs="?")
    p.add_argument("--dashboard-from", help="Multica snapshot JSON: source_url, generated_at, issues")
    p.add_argument("--dashboard", default="DASHBOARD.md")
    p.add_argument("--reconcile", action="store_true", help="Record proven abandoned local jobs as failed; never restart computation")
    p = sub.add_parser("deliver", help="Prepare an immutable delivery; does not post or impersonate an agent")
    p.add_argument("--issue-id", required=True, help="Multica issue UUID")
    p.add_argument("--run-id")
    p.add_argument("--issue-revision", type=int, help="Expected revision immediately after posting this delivery; bridge verifies it")
    p.add_argument("--artifact", action="append", default=[], help="Existing artifact file; repeatable")
    p.add_argument("--check", action="append", default=[], help="Named check actually passed; repeatable")
    p.add_argument("--research-impact", help="Required when preparing a delivery or draft")
    group = p.add_mutually_exclusive_group()
    group.add_argument("--draft", action="store_true", help="Prepare immutable artifacts for independent review; not ready for closure")
    group.add_argument("--finalize", metavar="DRAFT", help="Finalize the unchanged reviewed draft once with revision and review comment UUID")
    p.add_argument("--scope-complete", action="store_true")
    p.add_argument("--review-required", action="store_true")
    p.add_argument("--review-evidence", default="")
    p = sub.add_parser("export", help="Select an accepted run artifact for Git-tracked paper output")
    p.add_argument("--run-id", required=True)
    p.add_argument("--file", required=True, help="Artifact path relative to run outputs/")
    p.add_argument("--kind", choices=["figures", "tables"], required=True)
    p.add_argument("--name", help="Destination filename")
    p.add_argument("--accepted-by", required=True, help="Reviewer or acceptance comment reference")
    p.add_argument("--replace", action="store_true", help="Explicitly replace an existing selected artifact")
    return result


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv and argv[0] == "_worker":
        worker(Path(argv[1]))
        return 0
    args = parser().parse_args(argv)
    try:
        result = globals()[args.action](args)
    except (ValueError, RuntimeError, OSError, KeyError) as error:
        print(f"research: {error}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
