#!/usr/bin/env python3
# *** Maintained by AvonS/harness-eng, DON'T modify this, will be overwritten during next upgrade ***
"""
Persistent blocked-state helpers.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass(frozen=True)
class FailureScope:
    work_item_id: str
    check_name: str


@dataclass
class FailureState:
    scope: FailureScope
    attempts: int
    first_failure: str
    latest_failure: str
    latest_evidence: str


def _state_path(scope: FailureScope, state_root: Path) -> Path:
    safe = f"{scope.work_item_id}__{scope.check_name}.json"
    return state_root / safe


def load_failure_state(scope: FailureScope, state_root: Path) -> FailureState | None:
    path = _state_path(scope, state_root)
    if not path.is_file():
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    return FailureState(
        scope=scope,
        attempts=payload["attempts"],
        first_failure=payload["first_failure"],
        latest_failure=payload["latest_failure"],
        latest_evidence=payload["latest_evidence"],
    )


def record_failure(scope: FailureScope, state_root: Path, evidence: str) -> FailureState:
    state_root.mkdir(parents=True, exist_ok=True)
    state = load_failure_state(scope, state_root)
    if state is None:
        state = FailureState(scope, 1, evidence, evidence, evidence)
    else:
        state.attempts += 1
        state.latest_failure = evidence
        state.latest_evidence = evidence
    _state_path(scope, state_root).write_text(
        json.dumps(asdict(state) | {"scope": asdict(state.scope)}, indent=2),
        encoding="utf-8",
    )
    return state


def should_block(state: FailureState) -> bool:
    return state.attempts >= 3


def write_blocked_markdown(feature_dir: Path, state: FailureState, resume_command: str) -> Path:
    blocked = feature_dir / "BLOCKED.md"
    blocked.write_text(
        "\n".join(
            [
                "# BLOCKED",
                "",
                f"- Work item: {state.scope.work_item_id}",
                f"- Failing check: {state.scope.check_name}",
                f"- First observed failure: {state.first_failure}",
                f"- Latest failure: {state.latest_failure}",
                f"- Latest evidence: {state.latest_evidence}",
                f"- Attempts: {state.attempts}",
                f"- Resume command: {resume_command}",
            ]
        ),
        encoding="utf-8",
    )
    return blocked


def clear_failure_state(scope: FailureScope, state_root: Path, feature_dir: Path | None = None) -> None:
    path = _state_path(scope, state_root)
    if path.is_file():
        path.unlink()
    if feature_dir is not None and not any(state_root.glob("*.json")):
        blocked = feature_dir / "BLOCKED.md"
        if blocked.is_file():
            blocked.unlink()


def is_blocked(feature_dir: Path) -> bool:
    return (feature_dir / "BLOCKED.md").is_file()
