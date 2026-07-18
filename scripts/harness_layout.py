#!/usr/bin/env python3
"""Canonical harness filesystem discovery and validation."""

import json
import os
from pathlib import Path


def active_artifacts(harness: Path, filename: str) -> list[Path]:
    results = list(harness.glob(f"specs/active/*/{filename}"))
    results.extend(harness.glob(f"phases/active/*/features/*/{filename}"))
    return sorted(results)


def active_feature_dirs(harness: Path) -> list[Path]:
    dirs = [path.parent for path in active_artifacts(harness, "spec.md")]
    dirs.extend([path.parent for path in active_artifacts(harness, "spec.yaml")])
    return sorted(list(set(dirs)))


def archived_item_count(harness: Path) -> int:
    specs = harness / "specs" / "done"
    phases = harness / "phases" / "archive"
    return sum(1 for root in (specs, phases) if root.is_dir() for path in root.iterdir() if path.is_dir())


def validate_layout(project: Path, manifest: dict) -> list[str]:
    errors: list[str] = []
    for relative in manifest["required_directories"]:
        if not (project / relative).is_dir():
            errors.append(f"missing directory: {relative}")
    for relative in manifest["required_files"]:
        if not (project / relative).is_file():
            errors.append(f"missing file: {relative}")
    for relative, target in manifest["required_symlinks"].items():
        path = project / relative
        if not path.is_symlink() or os.readlink(path) != target:
            errors.append(f"invalid symlink: {relative} -> {target}")
    for relative in manifest["misplaced_paths"]:
        if (project / relative).exists():
            errors.append(f"misplaced path: {relative}")
    legacy = list((project / ".harness-eng" / "phases").glob("*/features/active"))
    errors.extend(f"legacy phase path: {path.relative_to(project)}" for path in legacy)
    return errors


def load_manifest(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))
