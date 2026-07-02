#!/usr/bin/env python3
# *** Maintained by AvonS/harness-eng, DON'T modify this, will be overwritten during next upgrade ***
"""
Scenario traceability helpers.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Scenario:
    scenario_id: str
    source_requirement: str
    provenance: str
    given: str
    when: str
    then: str
    evidence_strategy: str


@dataclass(frozen=True)
class ScenarioCoverage:
    scenario_id: str
    task_ids: list[str]
    evidence_paths: list[Path]
    status: str


def parse_scenarios(spec_path: Path) -> list[Scenario]:
    content = spec_path.read_text(encoding="utf-8")
    scenarios: list[Scenario] = []
    for block in re.findall(r"```yaml\n(.*?)\n```", content, flags=re.S):
        fields: dict[str, str] = {}
        for line in block.splitlines():
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip()
        if {"scenario_id", "source_requirement", "provenance", "given", "when", "then", "evidence_strategy"}.issubset(fields):
            scenarios.append(
                Scenario(
                    scenario_id=fields["scenario_id"],
                    source_requirement=fields["source_requirement"],
                    provenance=fields["provenance"],
                    given=fields["given"],
                    when=fields["when"],
                    then=fields["then"],
                    evidence_strategy=fields["evidence_strategy"],
                )
            )
    return scenarios


def parse_task_links(tasks_path: Path) -> dict[str, list[str]]:
    content = tasks_path.read_text(encoding="utf-8")
    links: dict[str, list[str]] = {}
    for line in content.splitlines():
        m = re.search(r"(SCN-\d+(?:-\d+)?)", line)
        if m:
            links.setdefault(m.group(1), []).append(line.strip())
    return links


def resolve_evidence(feature_root: Path, scenario_id: str) -> list[Path]:
    matches: list[Path] = []
    for path in feature_root.rglob("*"):
        if not path.is_file():
            continue
        if "tests" not in path.parts and path.name not in {"verification.md", "review-pre-verify.md", "review-pre-build.md"}:
            continue
        try:
            if scenario_id in path.read_text(encoding="utf-8"):
                matches.append(path)
        except UnicodeDecodeError:
            continue
    return matches


def validate_traceability(
    scenarios: list[Scenario], task_links: dict[str, list[str]], feature_root: Path, require_evidence: bool = True
) -> list[ScenarioCoverage]:
    coverage: list[ScenarioCoverage] = []
    for scenario in scenarios:
        evidence = resolve_evidence(feature_root, scenario.scenario_id)
        tasks = [item for item in task_links.get(scenario.scenario_id, [])]
        has_evidence = bool(evidence) or not require_evidence
        status = "PASS" if tasks and has_evidence else "FAIL"
        coverage.append(
            ScenarioCoverage(
                scenario_id=scenario.scenario_id,
                task_ids=tasks,
                evidence_paths=evidence,
                status=status,
            )
        )
    return coverage


def render_traceability_table(coverage: list[ScenarioCoverage]) -> str:
    lines = ["| Scenario | Tasks | Evidence | Status |", "|---|---|---|---|"]
    for item in coverage:
        tasks = ", ".join(item.task_ids) if item.task_ids else "—"
        evidence = ", ".join(str(p) for p in item.evidence_paths) if item.evidence_paths else "—"
        lines.append(f"| {item.scenario_id} | {tasks} | {evidence} | {item.status} |")
    return "\n".join(lines)
