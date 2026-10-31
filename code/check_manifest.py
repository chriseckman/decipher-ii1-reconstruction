"""Validate a clean public checkout against its complete file manifest.

The manifest does not hash itself. Only .git internals and Python bytecode
inside __pycache__ directories are excluded. In particular, .gitignore does
not exempt reader-created inputs or decoded outputs from this release check.
This verifies consistency, not an externally signed authenticity guarantee.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import sys


def check(root: Path) -> dict:
    root = root.resolve()
    manifest_path = root / "MANIFEST.json"
    if manifest_path.is_symlink():
        raise ValueError("MANIFEST.json must be a regular local file, not a symlink.")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("self_hash_included") is not False:
        raise ValueError("MANIFEST.json must declare self_hash_included: false.")
    entries = manifest.get("files")
    if not isinstance(entries, list):
        raise ValueError("MANIFEST.json must contain a files array.")
    expected = {}
    portable_names = set()
    for item in entries:
        name = item.get("path") if isinstance(item, dict) else None
        if (not isinstance(name, str) or not name or "\\" in name or ":" in name
                or name.startswith("/") or any(p in ("", ".", "..") for p in name.split("/"))
                or PurePosixPath(name).parts[0] == ".git" or name == "MANIFEST.json"):
            raise ValueError(f"Unsafe or excluded manifest path: {name!r}")
        if name.casefold() in portable_names:
            raise ValueError(f"Duplicate or case-colliding manifest path: {name}")
        if (type(item.get("bytes")) is not int or item["bytes"] < 0
                or not isinstance(item.get("sha256"), str)
                or re.fullmatch(r"[0-9a-f]{64}", item["sha256"]) is None):
            raise ValueError(f"Invalid size or SHA-256 for {name}")
        portable_names.add(name.casefold())
        expected[name] = item
    actual = set()
    ignored = 0
    for directory, dirs, files in os.walk(root, followlinks=False):
        base = Path(directory)
        if base == root and ".git" in dirs:
            dirs.remove(".git")
        for name in dirs:
            if (base / name).is_symlink():
                raise ValueError(f"Symlink directory is not a distributable file: {(base / name).relative_to(root).as_posix()}")
        for name in files:
            path = base / name
            relative = path.relative_to(root).as_posix()
            if relative in ("MANIFEST.json", ".git"):
                continue
            if path.is_symlink():
                raise ValueError(f"Symlink is not allowed: {relative}")
            if "__pycache__" in path.relative_to(root).parts[:-1] and path.suffix in (".pyc", ".pyo"):
                ignored += 1
                continue
            actual.add(relative)
    missing, extra = sorted(set(expected) - actual), sorted(actual - set(expected))
    if missing or extra:
        raise ValueError("File inventory mismatch. Missing: " + repr(missing) + "; unlisted: " + repr(extra)
                         + ". Run release checks from a pristine copy; local ciphertext and decoded output are not release files.")
    for name, item in expected.items():
        data = (root / name).read_bytes()
        if len(data) != item["bytes"] or hashlib.sha256(data).hexdigest() != item["sha256"]:
            raise ValueError(f"Size or SHA-256 mismatch: {name}")
    return {"result": "PASS", "payload_files": len(expected), "manifest_self_hash": "excluded",
            "ignored_python_bytecode_files": ignored, "scope": "Exact local inventory, sizes and SHA-256; not a signature."}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent,
                        help="Public checkout root (default: parent of this code directory)")
    args = parser.parse_args(argv)
    try:
        result = check(args.root)
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
