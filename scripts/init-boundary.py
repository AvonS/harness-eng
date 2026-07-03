#!/usr/bin/env python3
"""Capture and validate the filesystem write boundary for /h:init."""

import argparse
import hashlib
import json
import os
from pathlib import Path


IGNORED_PARTS = {".git", "__pycache__"}
ALLOWED_PREFIXES = (".harness-eng/",)
ALLOWED_ROOTS = {
    ".clinerules",
    ".cursorrules",
    "AGENTS.md",
    "ARCHITECTURE.md",
    "BRD.md",
    "CLAUDE.md",
    "claude.md",
    "technology.yaml",
    "VERSION",
    "version.txt",
}


def digest(path: Path) -> str:
    if path.is_symlink():
        return "symlink:" + os.readlink(path)
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot(root: Path, excluded: set[str] | None = None) -> dict[str, str]:
    excluded = excluded or set()
    files: dict[str, str] = {}
    for path in root.rglob("*"):
        relative = path.relative_to(root).as_posix()
        if relative in excluded or any(part in IGNORED_PARTS for part in path.relative_to(root).parts):
            continue
        if path.is_file() or path.is_symlink():
            files[relative] = digest(path)
    return files


def is_allowed(relative: str) -> bool:
    return relative in ALLOWED_ROOTS or relative.startswith(ALLOWED_PREFIXES)


def changed_outside_boundary(before: dict[str, str], after: dict[str, str]) -> list[str]:
    changed = {path for path in before.keys() | after.keys() if before.get(path) != after.get(path)}
    return sorted(path for path in changed if not is_allowed(path))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("snapshot", "check"))
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path)
    parser.add_argument("--baseline", type=Path)
    args = parser.parse_args()

    root = args.root.resolve()
    if args.action == "snapshot":
        if args.output is None:
            parser.error("snapshot requires --output")
        excluded = {args.output.resolve().relative_to(root).as_posix()}
        args.output.write_text(json.dumps(snapshot(root, excluded), indent=2, sort_keys=True) + "\n")
        return 0

    if args.baseline is None:
        parser.error("check requires --baseline")
    baseline_path = args.baseline.resolve()
    before = json.loads(baseline_path.read_text())
    excluded = {baseline_path.relative_to(root).as_posix()}
    violations = changed_outside_boundary(before, snapshot(root, excluded))
    if violations:
        print("Initialization changed paths outside its write boundary:")
        for path in violations:
            print(f"- {path}")
        return 1
    print("Initialization write boundary: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
