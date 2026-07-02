#!/usr/bin/env python3
# *** Maintained by AvonS/harness-eng, DON'T modify this, will be overwritten during next upgrade ***
"""
Project sensor runner.
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass(frozen=True)
class Sensor:
    sensor_id: str
    command: str
    required_before: list[str]
    timeout_seconds: int
    evidence_label: str


@dataclass(frozen=True)
class SensorResult:
    sensor_id: str
    command: str
    exit_code: int
    started_at: str
    finished_at: str
    evidence_path: Path


class SensorExecutionError(RuntimeError):
    pass


class SensorConfigurationError(RuntimeError):
    pass


def load_sensors(config_path: Path) -> list[Sensor]:
    sensors: list[Sensor] = []
    if not config_path.is_file():
        return sensors
    current: dict[str, str] = {}
    for line in config_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        normalized = line.lstrip()
        if normalized.startswith("- id:"):
            if current:
                sensors.append(
                    Sensor(
                        sensor_id=current["id"],
                        command=current["command"],
                        required_before=current.get("required_before", "").split(",")
                        if current.get("required_before")
                        else [],
                        timeout_seconds=int(current.get("timeout", "60")),
                        evidence_label=current.get("evidence", ""),
                    )
                )
            current = {"id": normalized.split(":", 1)[1].strip()}
        elif ":" in normalized and current:
            key, value = normalized.split(":", 1)
            current[key.strip()] = value.strip()
    if current:
        sensors.append(
            Sensor(
                sensor_id=current["id"],
                command=current["command"],
                required_before=current.get("required_before", "").split(",")
                if current.get("required_before")
                else [],
                timeout_seconds=int(current.get("timeout", "60")),
                evidence_label=current.get("evidence", ""),
            )
        )
    return sensors


def select_sensors(sensors: list[Sensor], hook: str) -> list[Sensor]:
    return [sensor for sensor in sensors if hook in [item.strip() for item in sensor.required_before]]


def run_sensor(sensor: Sensor, workdir: Path, evidence_root: Path) -> SensorResult:
    evidence_root.mkdir(parents=True, exist_ok=True)
    started = datetime.now(timezone.utc).isoformat()
    try:
        proc = subprocess.run(
            sensor.command,
            shell=True,
            cwd=workdir,
            capture_output=True,
            text=True,
            timeout=sensor.timeout_seconds,
            check=False,
        )
    except FileNotFoundError as exc:
        raise SensorExecutionError(f"missing command: {sensor.command}") from exc
    except subprocess.TimeoutExpired as exc:
        raise SensorExecutionError(f"timeout: {sensor.command}") from exc
    finished = datetime.now(timezone.utc).isoformat()
    evidence_path = evidence_root / f"{sensor.sensor_id}.json"
    evidence_path.write_text(
        json.dumps(
            {
                "sensor_id": sensor.sensor_id,
                "command": sensor.command,
                "stdout": proc.stdout,
                "stderr": proc.stderr,
                "exit_code": proc.returncode,
                "started_at": started,
                "finished_at": finished,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    result = SensorResult(sensor.sensor_id, sensor.command, proc.returncode, started, finished, evidence_path)
    if proc.returncode != 0:
        raise SensorExecutionError(f"failed: {sensor.command}")
    return result


def capture_sensor_evidence(result: SensorResult) -> None:
    result.evidence_path.touch(exist_ok=True)


def run_sensors_for_hook(config_path: Path, hook: str, workdir: Path, evidence_root: Path) -> list[SensorResult]:
    selected = select_sensors(load_sensors(config_path), hook)
    if not selected:
        raise SensorConfigurationError(f"no sensors configured for required hook: {hook}")
    results: list[SensorResult] = []
    for sensor in selected:
        results.append(run_sensor(sensor, workdir, evidence_root))
    return results


def render_sensor_table(results: list[SensorResult]) -> str:
    lines = ["| Sensor | Command | Exit | Evidence |", "|---|---|---|---|"]
    for result in results:
        lines.append(
            f"| {result.sensor_id} | {result.command} | {result.exit_code} | {result.evidence_path} |"
        )
    return "\n".join(lines)
