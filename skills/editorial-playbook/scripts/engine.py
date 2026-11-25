#!/usr/bin/env python3
"""Load and verify the pinned public writing core. No telemetry or execution."""

import hashlib
import json
from pathlib import Path, PurePosixPath
import re
from urllib.error import HTTPError
from urllib.request import HTTPRedirectHandler, Request, build_opener


SKILL_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LOCK = SKILL_ROOT / "references" / "engine-lock.json"
REPOSITORY = "CopernicusP/evidence-to-article"
CORE_PREFIX = "skills/evidence-to-article/"
REQUIRED_FILES = {
    "LICENSE",
    CORE_PREFIX + "SKILL.md",
    CORE_PREFIX + "references/authorial-voice.md",
    CORE_PREFIX + "references/channels.md",
    CORE_PREFIX + "references/editorial-decisions.md",
    CORE_PREFIX + "references/manifest-contract.md",
    CORE_PREFIX + "references/style-cards.md",
    CORE_PREFIX + "scripts/build_outputs.py",
    CORE_PREFIX + "scripts/check_run.py",
}
MAX_FILE_BYTES = 2 * 1024 * 1024


def digest(data):
    return hashlib.sha256(data).hexdigest()


def relative_parts(value):
    """Accept portable relative paths without traversal or alternate separators."""
    if (not isinstance(value, str) or not value or "\\" in value or ":" in value
            or "\x00" in value):
        raise ValueError("Path must be a nonempty portable relative path")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in ("", ".", "..") for part in value.split("/")):
        raise ValueError("Path must not be absolute or contain dot/traversal components")
    return path.parts


def safe_relative_path(root, relative):
    """Resolve a path beneath root, rejecting existing symlink components."""
    root = Path(root)
    if root.is_symlink():
        raise ValueError("Root must not be a symbolic link")
    root = root.resolve()
    current = root
    for part in relative_parts(relative):
        current = current / part
        if current.is_symlink():
            raise ValueError("Symbolic links are not permitted: " + relative)
    resolved = current.resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError("Path escapes its root: " + relative) from exc
    return resolved


def validate_lock(lock):
    if not isinstance(lock, dict) or type(lock.get("schema_version")) is not int or lock["schema_version"] != 1:
        raise ValueError("Unsupported dependency lock schema")
    if lock.get("name") != "evidence-to-article" or lock.get("repository") != REPOSITORY:
        raise ValueError("Dependency lock must identify the public Evidence to Article repository")
    if not isinstance(lock.get("version"), str) or not re.fullmatch(r"\d+\.\d+\.\d+", lock["version"]):
        raise ValueError("Dependency version must be a semantic version")
    if not isinstance(lock.get("commit"), str) or not re.fullmatch(r"[0-9a-f]{40}", lock["commit"]):
        raise ValueError("Dependency commit must be a full lowercase commit SHA")
    files = lock.get("files")
    if not isinstance(files, dict) or set(files) != REQUIRED_FILES:
        raise ValueError("Dependency lock must contain exactly the supported core files")
    for path, expected in files.items():
        relative_parts(path)
        if not isinstance(expected, str) or not re.fullmatch(r"[0-9a-f]{64}", expected):
            raise ValueError("Invalid locked SHA-256 for " + path)
    return lock


def load_lock(path=None):
    path = Path(path) if path is not None else DEFAULT_LOCK
    if path.is_symlink():
        raise ValueError("Dependency lock must not be a symbolic link")
    lock = json.loads(path.read_text(encoding="utf-8"))
    return validate_lock(lock)


def verify_engine(engine_root, lock, allow_extra=False):
    """Verify every required file; raise ValueError/OSError for any mismatch."""
    validate_lock(lock)
    root = Path(engine_root)
    if root.is_symlink() or not root.is_dir():
        raise ValueError("Dependency root must be a real directory")
    if not allow_extra:
        allowed_dirs = {str(parent) for relative in lock["files"]
                        for parent in PurePosixPath(relative).parents if str(parent) != "."}
        for path in root.rglob("*"):
            relative = path.relative_to(root).as_posix()
            if path.is_symlink():
                raise ValueError("Unexpected symbolic link in dependency: " + relative)
            if path.is_dir() and relative not in allowed_dirs:
                raise ValueError("Unexpected directory in dependency: " + relative)
            if not path.is_dir() and relative not in lock["files"]:
                raise ValueError("Unexpected file in dependency: " + relative)
    for relative, expected in lock["files"].items():
        path = safe_relative_path(root, relative)
        if not path.is_file() or path.stat().st_size > MAX_FILE_BYTES:
            raise ValueError("Missing or oversized dependency file: " + relative)
        if digest(path.read_bytes()) != expected:
            raise ValueError("Dependency hash mismatch: " + relative)
    return {
        "name": lock["name"], "version": lock["version"],
        "commit": lock["commit"], "verified_files": len(lock["files"]),
        "integrity_verified": True, "semantic_verification_performed": False,
    }


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise HTTPError(req.full_url, code, "Redirect refused for pinned dependency", headers, fp)


def fetch_or_copy_engine(destination, lock, source=None, offline=False):
    """Materialize a verified core, using an explicit local cache or pinned HTTPS."""
    validate_lock(lock)
    destination = Path(destination)
    if destination.is_symlink():
        raise ValueError("Dependency destination must not be a symbolic link")
    if destination.exists() and (not destination.is_dir() or any(destination.iterdir())):
        raise ValueError("Dependency destination must be absent or empty")
    if source is not None:
        source = Path(source)
        # A full checkout may contain README, tests and Git metadata. Copy only
        # locked files; never execute or preserve arbitrary cache extras.
        verify_engine(source, lock, allow_extra=True)
    elif offline:
        raise ValueError("Offline setup requires --engine-source with the locked repository files")
    destination.mkdir(parents=True, exist_ok=True)
    opener = build_opener(_NoRedirect())
    for relative, expected in lock["files"].items():
        if source is not None:
            data = safe_relative_path(source, relative).read_bytes()
        else:
            url = "https://raw.githubusercontent.com/{}/{}/{}".format(REPOSITORY, lock["commit"], relative)
            req = Request(url, headers={"User-Agent": "editorial-playbook/0.3.1"})
            with opener.open(req, timeout=15) as response:
                if response.geturl() != url:
                    raise ValueError("Dependency response URL differs from the locked URL")
                data = response.read(MAX_FILE_BYTES + 1)
        if len(data) > MAX_FILE_BYTES or digest(data) != expected:
            raise ValueError("Downloaded/copied dependency hash or size mismatch: " + relative)
        target = safe_relative_path(destination, relative)
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("xb") as stream:
            stream.write(data)
    return verify_engine(destination, lock)
