#!/usr/bin/env python3
"""Create or repair this host's ignored Python 3.12 research environment."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.python_env import (  # noqa: E402
    REQUIRED_DISTRIBUTIONS,
    REQUIRED_MODULES,
    REQUIREMENTS_FILE,
    execution_host,
    environment_dir,
    venv_python,
)


class BootstrapFailure(RuntimeError):
    def __init__(self, diagnosis: str, attempts: list[str]):
        super().__init__(diagnosis)
        self.diagnosis = diagnosis
        self.attempts = attempts


def _run(
    argv: list[str],
    *,
    cwd: Path = ROOT,
    env: dict[str, str] | None = None,
    timeout: int = 180,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        argv, cwd=cwd, env=env, text=True, capture_output=True,
        timeout=timeout, check=False,
    )


def _short_result(result: subprocess.CompletedProcess[str]) -> str:
    message = (result.stderr or result.stdout).strip()
    return message[-900:] if message else f"exit {result.returncode}"


def _version(executable: str | Path) -> tuple[int, int, int] | None:
    try:
        result = _run([
            str(executable), "-c",
            "import json,sys; print(json.dumps(list(sys.version_info[:3])))",
        ], timeout=20)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    try:
        major, minor, patch = json.loads(result.stdout.strip())
        return int(major), int(minor), int(patch)
    except (ValueError, TypeError, json.JSONDecodeError):
        return None


def find_interpreter(requested: str | None = None) -> tuple[str, tuple[int, int, int], list[str]]:
    """Find an installed Python 3.12 belonging to the active OS environment."""
    host = execution_host()
    attempts: list[str] = []
    candidates: list[str] = []
    if requested:
        candidates.append(requested)
    if sys.version_info[:2] == (3, 12):
        candidates.append(sys.executable)
    if host == "windows":
        launcher = shutil.which("py")
        if launcher:
            try:
                result = _run([launcher, "-3.12", "-c", "import sys; print(sys.executable)"])
                if result.returncode == 0 and result.stdout.strip():
                    candidates.append(result.stdout.strip().splitlines()[-1])
                else:
                    attempts.append(f"Windows Python launcher: {_short_result(result)}")
            except (OSError, subprocess.TimeoutExpired) as exc:
                attempts.append(f"Windows Python launcher: {type(exc).__name__}")
        candidates.extend(filter(None, (shutil.which("python3.12"), shutil.which("python"))))
    else:
        candidates.extend(filter(None, (shutil.which("python3.12"), shutil.which("python3"))))

    seen: set[str] = set()
    for candidate in candidates:
        normalized = os.path.normcase(os.path.abspath(candidate))
        if normalized in seen:
            continue
        seen.add(normalized)
        detected = _version(candidate)
        attempts.append(f"{candidate}: {detected or 'unusable'}")
        if detected and detected[:2] == (3, 12):
            return candidate, detected, attempts
    raise BootstrapFailure(
        f"No usable Python 3.12 interpreter was found for the {host} execution host. "
        "Install Python 3.12 for this host, then rerun the bootstrap.",
        attempts,
    )


def _module_check(executable: str | Path, module: str) -> bool:
    try:
        result = _run([str(executable), "-c", f"import {module}"] , timeout=20)
    except (OSError, subprocess.TimeoutExpired):
        return False
    return result.returncode == 0


def _repair_venv_prerequisite(base_python: str, attempts: list[str]) -> None:
    if _module_check(base_python, "venv"):
        return
    host = execution_host()
    apt = shutil.which("apt-get")
    if host in {"wsl", "linux"} and apt:
        command: list[str] | None = None
        if hasattr(os, "geteuid") and os.geteuid() == 0:
            command = [apt, "install", "-y", "python3.12-venv"]
        elif shutil.which("sudo"):
            command = [shutil.which("sudo") or "sudo", "-n", apt, "install", "-y", "python3.12-venv"]
        if command:
            try:
                result = _run(command, timeout=300)
                attempts.append(f"venv package repair: {_short_result(result)}")
            except (OSError, subprocess.TimeoutExpired) as exc:
                attempts.append(f"venv package repair: {type(exc).__name__}")
            if _module_check(base_python, "venv"):
                return
    raise BootstrapFailure(
        f"Python 3.12 is installed, but its venv module is unavailable on {host}. "
        "The bootstrap attempted the host package-manager repair; install the matching "
        "Python 3.12 venv package or make it available locally, then rerun.",
        attempts,
    )


def _site_packages(env_dir: Path, host: str) -> Path:
    if host == "windows":
        return env_dir / "Lib" / "site-packages"
    candidates = sorted((env_dir / "lib").glob("python3.12*/site-packages"))
    if candidates:
        return candidates[0]
    return env_dir / "lib" / "python3.12" / "site-packages"


def _cached_pip_wheel(base_python: str, root: Path, attempts: list[str]) -> Path | None:
    pip_version = next((v for k, v in REQUIRED_DISTRIBUTIONS.items() if k.casefold() == "pip"), None)
    if not pip_version:
        raise BootstrapFailure("requirements.txt must pin pip so an environment can be repaired", attempts)

    local_wheels = root / ".local" / "python-bootstrap" / "wheels"
    local_wheels.mkdir(parents=True, exist_ok=True)
    expected_name = f"pip-{pip_version}-py3-none-any.whl"
    for candidate in [*local_wheels.glob("pip-*.whl"), *Path.home().glob(".cache/pip/wheels/*/*/*/pip-*.whl")]:
        if candidate.name == expected_name:
            return candidate

    try:
        result = _run([
            base_python, "-c",
            "import ensurepip,pathlib; p=pathlib.Path(ensurepip.__file__).parent/'_bundled'; "
            "print(next(iter(p.glob('pip-*.whl')),''))",
        ], timeout=20)
        bundled = Path(result.stdout.strip()) if result.returncode == 0 and result.stdout.strip() else None
        if bundled and bundled.name == expected_name and bundled.is_file():
            return bundled
        attempts.append(f"ensurepip bundled wheel: {bundled.name if bundled else 'not available'}")
    except (OSError, subprocess.TimeoutExpired) as exc:
        attempts.append(f"ensurepip bundled wheel: {type(exc).__name__}")

    apt = shutil.which("apt-get")
    if apt:
        try:
            result = _run([apt, "download", "python3-pip-whl"], cwd=local_wheels, timeout=180)
            attempts.append(f"local apt pip-wheel download: {_short_result(result)}")
            if result.returncode == 0:
                dpkg_deb = shutil.which("dpkg-deb")
                if dpkg_deb:
                    extracted = root / ".local" / "python-bootstrap" / "apt-extracted"
                    extracted.mkdir(parents=True, exist_ok=True)
                    for package in local_wheels.glob("python3-pip-whl_*.deb"):
                        unpacked = _run([dpkg_deb, "-x", str(package), str(extracted)], timeout=120)
                        if unpacked.returncode != 0:
                            attempts.append(f"apt wheel extraction: {_short_result(unpacked)}")
                    for candidate in extracted.rglob(expected_name):
                        destination = local_wheels / expected_name
                        if candidate.resolve() != destination.resolve():
                            shutil.copy2(candidate, destination)
                        return destination
        except (OSError, subprocess.TimeoutExpired) as exc:
            attempts.append(f"local apt pip-wheel repair: {type(exc).__name__}")

    # The pip bootstrap wheel is itself pinned by requirements.txt. Verify
    # its digest from PyPI metadata before using the wheel on an ensurepip-free host.
    metadata_url = f"https://pypi.org/pypi/pip/{pip_version}/json"
    try:
        with urllib.request.urlopen(metadata_url, timeout=20) as response:
            metadata = json.load(response)
        asset = next(
            item for item in metadata["urls"]
            if item.get("filename") == expected_name and item.get("packagetype") == "bdist_wheel"
        )
        destination = local_wheels / expected_name
        with urllib.request.urlopen(asset["url"], timeout=45) as response:
            data = response.read()
        digest = hashlib.sha256(data).hexdigest()
        if digest != asset["digests"]["sha256"]:
            raise ValueError("downloaded pip wheel did not match the PyPI SHA-256")
        destination.write_bytes(data)
        attempts.append(f"verified pip bootstrap wheel: pip=={pip_version}, sha256={digest}")
        return destination
    except (OSError, urllib.error.URLError, StopIteration, KeyError, ValueError, json.JSONDecodeError) as exc:
        attempts.append(f"pinned PyPI pip-wheel repair: {type(exc).__name__}: {exc}")
    return None


def _seed_pip(env_python: Path, env_dir: Path, base_python: str, host: str, root: Path, attempts: list[str]) -> None:
    try:
        result = _run([str(env_python), "-m", "ensurepip", "--upgrade"], timeout=90)
        attempts.append(f"ensurepip repair: {_short_result(result)}")
        if result.returncode == 0 and _module_check(env_python, "pip"):
            return
    except (OSError, subprocess.TimeoutExpired) as exc:
        attempts.append(f"ensurepip repair: {type(exc).__name__}")

    wheel = _cached_pip_wheel(base_python, root, attempts)
    if wheel is None:
        pip_version = next((v for k, v in REQUIRED_DISTRIBUTIONS.items() if k.casefold() == "pip"), "pinned")
        raise BootstrapFailure(
            f"Python 3.12 can create an environment, but pip is absent and no verified "
            f"pip=={pip_version} wheel could be obtained from the local package cache, apt, or PyPI. "
            "The environment was preserved for retry; restore package-network access and rerun.",
            attempts,
        )
    site = _site_packages(env_dir, host)
    site.mkdir(parents=True, exist_ok=True)
    try:
        with zipfile.ZipFile(wheel) as archive:
            archive.extractall(site)
    except (OSError, zipfile.BadZipFile) as exc:
        raise BootstrapFailure(f"Could not seed pip from {wheel.name}: {type(exc).__name__}", attempts) from exc
    if not _module_check(env_python, "pip"):
        raise BootstrapFailure("The verified pip wheel was extracted, but the environment still cannot import pip.", attempts)


def _probe_env(env_python: Path, env_dir: Path) -> dict[str, object]:
    code = r'''
import importlib, importlib.metadata, importlib.util, json, sys
required = json.loads(sys.argv[1])
modules = json.loads(sys.argv[2])
versions = {}
imports = {}
for name in required:
    try: versions[name] = importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError: versions[name] = None
for name, module in modules.items():
    try: importlib.import_module(module); imports[name] = True
    except Exception: imports[name] = False
print(json.dumps({"python": list(sys.version_info[:3]), "prefix": sys.prefix,
                  "pip": importlib.util.find_spec("pip") is not None,
                  "versions": versions, "imports": imports}))
'''
    result = _run([
        str(env_python), "-c", code,
        json.dumps(REQUIRED_DISTRIBUTIONS), json.dumps(REQUIRED_MODULES),
    ], timeout=40)
    if result.returncode != 0:
        raise BootstrapFailure(f"Environment validation could not run: {_short_result(result)}", [])
    try:
        report = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise BootstrapFailure("Environment validation returned malformed output.", []) from exc
    expected_prefix = str(env_dir.resolve())
    if tuple(report.get("python", ())[:2]) != (3, 12):
        report["failures"] = ["python is not 3.12"]
    elif Path(str(report.get("prefix", ""))).resolve() != Path(expected_prefix):
        report["failures"] = ["interpreter prefix does not match the persistent environment"]
    else:
        failures = []
        if not report.get("pip"):
            failures.append("pip is missing")
        for name, expected in REQUIRED_DISTRIBUTIONS.items():
            if report.get("versions", {}).get(name) != expected:
                failures.append(f"{name}=={expected} required; found {report.get('versions', {}).get(name) or 'missing'}")
        for name, imported in report.get("imports", {}).items():
            if not imported:
                failures.append(f"required module for {name} cannot be imported")
        report["failures"] = failures
    return report


def _quarantine(env_dir: Path) -> Path:
    quarantine = env_dir.parent / "quarantine"
    quarantine.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    destination = quarantine / f"{env_dir.name}-{stamp}"
    suffix = 1
    while destination.exists():
        destination = quarantine / f"{env_dir.name}-{stamp}-{suffix}"
        suffix += 1
    env_dir.rename(destination)
    return destination


def _requirements_hash() -> str:
    digest = hashlib.sha256()
    digest.update(REQUIREMENTS_FILE.name.encode("utf-8"))
    digest.update(REQUIREMENTS_FILE.read_bytes())
    return digest.hexdigest()


def bootstrap(
    *,
    root: Path = ROOT,
    requested_python: str | None = None,
    requested_env_dir: Path | None = None,
) -> dict[str, object]:
    host = execution_host()
    env_dir = requested_env_dir.resolve() if requested_env_dir else environment_dir(root, host)
    local_root = (root / ".local").resolve()
    if env_dir != local_root and local_root not in env_dir.parents:
        raise BootstrapFailure("The persistent environment must be stored under the ignored .local directory.", [])
    if env_dir == local_root:
        raise BootstrapFailure("Place the environment in a child directory of the ignored .local directory.", [])

    base_python, base_version, attempts = find_interpreter(requested_python)
    _repair_venv_prerequisite(base_python, attempts)
    env_dir.parent.mkdir(parents=True, exist_ok=True)
    target_python = venv_python(root, host=host, environment_path=env_dir)
    action = "created"
    create_environment = True

    if env_dir.exists():
        if target_python.is_file():
            try:
                existing = _probe_env(target_python, env_dir)
            except BootstrapFailure as exc:
                attempts.append(f"existing environment probe: {exc}")
                existing = {}
            if existing and not existing.get("failures"):
                return {
                    "ok": True,
                    "action": "reused",
                    "host": host,
                    "python_version": ".".join(map(str, existing["python"])),
                    "environment_path": str(env_dir),
                    "python_executable": str(target_python),
                    "pinned_distributions": existing["versions"],
                    "requirements_sha256": _requirements_hash(),
                    "native_windows_preferred_for_game_connected_research": host != "windows",
                    "attempts": attempts,
                }
            if existing.get("python") and tuple(existing["python"][:2]) == (3, 12) and Path(str(existing.get("prefix"))).resolve() == env_dir:
                action = "repaired"
                create_environment = False
            else:
                preserved = _quarantine(env_dir)
                attempts.append(f"preserved unusable environment at {preserved}")
                action = "created"
        else:
            preserved = _quarantine(env_dir)
            attempts.append(f"preserved incomplete environment at {preserved}")
            action = "created"

    env_dir.parent.mkdir(parents=True, exist_ok=True)
    if create_environment:
        ensurepip_ready = _run([base_python, "-m", "ensurepip", "--version"], timeout=20).returncode == 0
        create_args = [base_python, "-m", "venv"]
        if not ensurepip_ready:
            create_args.append("--without-pip")
        create_args.append(str(env_dir))
        try:
            created = _run(create_args, timeout=120)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise BootstrapFailure(f"Could not create the persistent Python environment: {type(exc).__name__}.", attempts) from exc
        if created.returncode != 0:
            raise BootstrapFailure(f"Python venv creation failed: {_short_result(created)}", attempts)
    if not target_python.is_file():
        raise BootstrapFailure("Python reported successful venv creation, but its interpreter is missing.", attempts)

    if not _module_check(target_python, "pip"):
        _seed_pip(target_python, env_dir, base_python, host, root, attempts)

    before = _probe_env(target_python, env_dir)
    if before.get("failures"):
        pip_cache = root / ".local" / "python-bootstrap" / "pip-cache"
        pip_cache.mkdir(parents=True, exist_ok=True)
        pip_env = os.environ.copy()
        pip_env["PIP_CACHE_DIR"] = str(pip_cache)
        pip_install = _run([
            str(target_python), "-m", "pip", "install",
            "--disable-pip-version-check", "--retries", "1", "--timeout", "20",
            "--requirement", str(REQUIREMENTS_FILE),
        ], env=pip_env, timeout=600)
        attempts.append(f"pinned requirements install: {_short_result(pip_install)}")
        if pip_install.returncode != 0:
            raise BootstrapFailure(
                "Pinned dependency installation failed after creating or repairing the environment. "
                "The environment is left in place for an idempotent retry; inspect the install diagnosis.",
                attempts,
            )

    check = _run([str(target_python), "-m", "pip", "check"], timeout=60)
    if check.returncode != 0:
        raise BootstrapFailure(f"Pinned environment dependency check failed: {_short_result(check)}", attempts)
    report = _probe_env(target_python, env_dir)
    if report.get("failures"):
        raise BootstrapFailure("Environment verification failed: " + "; ".join(report["failures"]), attempts)

    manifest = {
        "schema_version": 1,
        "host": host,
        "base_python": base_python,
        "base_python_version": ".".join(map(str, base_version)),
        "environment_path": str(env_dir),
        "python_executable": str(target_python),
        "python_version": ".".join(map(str, report["python"])),
        "pinned_distributions": report["versions"],
        "requirements_sha256": _requirements_hash(),
        "validation": "pass",
    }
    (env_dir / ".harness-bootstrap.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return {
        "ok": True,
        "action": action,
        "host": host,
        "python_version": manifest["python_version"],
        "environment_path": str(env_dir),
        "python_executable": str(target_python),
        "pinned_distributions": report["versions"],
        "requirements_sha256": manifest["requirements_sha256"],
        "native_windows_preferred_for_game_connected_research": host != "windows",
        "attempts": attempts,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--python", help="use this installed Python 3.12 interpreter")
    parser.add_argument("--env-dir", type=Path, help="disposable test override; must be under .local")
    args = parser.parse_args(argv)
    try:
        report = bootstrap(requested_python=args.python, requested_env_dir=args.env_dir)
    except BootstrapFailure as exc:
        print(json.dumps({
            "ok": False,
            "host": execution_host(),
            "diagnosis": exc.diagnosis,
            "attempts": exc.attempts,
        }, indent=2), file=sys.stderr)
        return 1
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        print(json.dumps({
            "ok": False,
            "host": execution_host(),
            "diagnosis": f"{type(exc).__name__}: {exc}",
        }, indent=2), file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
