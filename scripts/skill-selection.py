#!/usr/bin/env python3
# *** Maintained by AvonS/harness-eng, DON'T modify this, will be overwritten during next upgrade ***
"""
Deterministic skill selection helpers for harness init and upgrade.
"""

from __future__ import annotations

import json
import hashlib
import argparse
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from shutil import copy2


@dataclass(frozen=True)
class SkillMatch:
    name: str
    source: str
    revision: str
    source_path: Path


@dataclass(frozen=True)
class SkillInstallRecord:
    name: str
    source: str
    revision: str
    installed_at: str
    destination: Path
    installed_digest: str
    action: str


DEFAULT_SKILL_ROOTS = [
    Path("skills"),
    Path(".harness-eng/skills"),
]


def detect_technology(root: Path) -> list[str]:
    tech: list[str] = []
    for name in ["technology.yaml", ".harness-eng/technology.yaml"]:
        path = root / name
        if path.is_file():
            for line in path.read_text(encoding="utf-8").splitlines():
                if ":" not in line:
                    continue
                key, value = line.split(":", 1)
                if key.strip() in {"skills", "technology", "stack"}:
                    tech.extend(
                        part.strip().lower()
                        for part in value.replace("[", "").replace("]", "").split(",")
                        if part.strip()
                    )
    return sorted(dict.fromkeys(tech))


def _skill_registry_root(root: Path) -> Path:
    for candidate in DEFAULT_SKILL_ROOTS:
        if (root / candidate).is_dir():
            return root / candidate
    return root / "skills"


def resolve_skills(technology_ids: list[str], root: Path) -> list[SkillMatch]:
    registry = _skill_registry_root(root)
    matches: list[SkillMatch] = []
    for tech in technology_ids:
        skill_dir = registry / tech
        skill_file = skill_dir / "SKILL.md"
        if skill_file.is_file():
            matches.append(
                SkillMatch(
                    name=tech,
                    source=str(skill_dir),
                    revision=_revision_for(skill_file),
                    source_path=skill_dir,
                )
            )
    return matches


def render_preview(matches: list[SkillMatch]) -> str:
    lines = ["Selected skills preview:"]
    for match in matches:
        lines.append(f"- {match.name} ({match.source})")
    return "\n".join(lines)


def install_skills(matches: list[SkillMatch], destination: Path, log_path: Path | None = None) -> list[SkillInstallRecord]:
    destination.mkdir(parents=True, exist_ok=True)
    previous_installs = load_install_log(log_path) if log_path is not None else {}
    records: list[SkillInstallRecord] = []
    for match in matches:
        target = destination / match.name
        target.mkdir(parents=True, exist_ok=True)
        target_file = target / "SKILL.md"
        source_file = match.source_path / "SKILL.md"
        action = "installed"
        installed_digest = _digest_file(source_file)
        if target_file.exists():
            previous = previous_installs.get(match.name)
            current_digest = _digest_file(target_file)
            if previous is None or current_digest != previous.get("installed_digest"):
                action = "preserved"
                installed_digest = previous.get("installed_digest", current_digest) if previous else current_digest
            else:
                copy2(source_file, target_file)
        else:
            copy2(source_file, target_file)
        records.append(
            SkillInstallRecord(
                name=match.name,
                source=match.source,
                revision=match.revision,
                installed_at=datetime.now(timezone.utc).isoformat(),
                destination=target,
                installed_digest=installed_digest,
                action=action,
            )
        )
    return records


def preserve_project_modifications(destination: Path, log_path: Path | None = None) -> list[Path]:
    preserved: list[Path] = []
    if not destination.is_dir():
        return preserved
    previous_installs = load_install_log(log_path) if log_path is not None else {}
    for skill_dir in destination.iterdir():
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.is_file():
            continue
        previous = previous_installs.get(skill_dir.name)
        if previous is None or _digest_file(skill_file) != previous.get("installed_digest"):
            preserved.append(skill_file)
    return preserved


def write_install_log(records: list[SkillInstallRecord], log_path: Path) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    payload = [asdict(record) | {"destination": str(record.destination)} for record in records]
    log_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def offline_failure_message() -> str:
    return (
        "Skill resolution requires a local registry or cache. "
        "Configure technology.yaml with local skills or provide a local fallback."
    )


def _revision_for(skill_file: Path) -> str:
    return str(int(skill_file.stat().st_mtime))


def _digest_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_install_log(log_path: Path | None) -> dict[str, dict[str, str]]:
    if log_path is None or not log_path.is_file():
        return {}
    payload = json.loads(log_path.read_text(encoding="utf-8"))
    return {entry["name"]: entry for entry in payload}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--destination", default=".harness-eng/skills")
    parser.add_argument("--log", default=".harness-eng/skill-install.json")
    parser.add_argument("--preview-only", action="store_true")
    args = parser.parse_args(argv)

    root = Path(args.root)
    destination = root / args.destination
    log_path = root / args.log
    technology_ids = detect_technology(root)
    if not technology_ids:
        print(offline_failure_message())
        return 1
    matches = resolve_skills(technology_ids, root)
    if not matches:
        print(offline_failure_message())
        return 1
    print(render_preview(matches))
    if args.preview_only:
        return 0
    records = install_skills(matches, destination, log_path)
    write_install_log(records, log_path)
    for record in records:
        print(f"{record.action}: {record.name} -> {record.destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
