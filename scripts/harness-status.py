#!/usr/bin/env python3
# *** Maintained by AvonS/harness-eng, DON'T modify this, will be overwritten during next upgrade ***
"""
harness-status.py — Show current workflow state.

Usage: python3 scripts/harness-status.py [--json]

Default: Colored human-readable output.
--json:   Structured JSON blob with all status fields.
"""

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

HARNESS_DIR = Path(".harness-eng")

# ANSI colors
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
RED = "\033[0;31m"
CYAN = "\033[0;36m"
NC = "\033[0m"

JSON_MODE = "--json" in sys.argv


def eprint(*args, **kwargs):
    """Print to stderr (used for non-JSON messages in JSON mode)."""
    print(*args, file=sys.stderr, **kwargs)


def find_active(filename: str) -> list[Path]:
    """Find files matching filename in specs/active/ or phases/*/features/active/."""
    results: list[Path] = []
    spec_glob = f"specs/active/*/{filename}"
    phase_glob = f"phases/*/features/active/*/{filename}"
    results.extend(HARNESS_DIR.glob(spec_glob))
    results.extend(HARNESS_DIR.glob(phase_glob))
    return results


def count_files(filename: str) -> int:
    return len(find_active(filename))


def has_approval() -> bool:
    for f in find_active("design.md"):
        content = f.read_text(encoding="utf-8", errors="replace")
        if "Ref" in content and "APPROVED" in content:
            return True
    return False


def count_incomplete_tasks() -> int:
    total = 0
    for f in find_active("tasks.md"):
        content = f.read_text(encoding="utf-8", errors="replace")
        for line in content.splitlines():
            if line.startswith("- [ ]"):
                total += 1
    return total


def count_completed_tasks() -> int:
    total = 0
    for f in find_active("tasks.md"):
        content = f.read_text(encoding="utf-8", errors="replace")
        for line in content.splitlines():
            if line.startswith("- [x]") or line.startswith("- [X]"):
                total += 1
    return total


def verification_passed() -> bool:
    for f in find_active("verification.md"):
        content = f.read_text(encoding="utf-8", errors="replace")
        if "All passing" in content or "✅" in content:
            return True
    return False


def count_archived() -> int:
    count = 0
    archive_dir = HARNESS_DIR / "specs" / "archive"
    if archive_dir.is_dir():
        count += len([d for d in archive_dir.iterdir() if d.is_dir()])
    phases_dir = HARNESS_DIR / "phases"
    if phases_dir.is_dir():
        for phase_dir in phases_dir.iterdir():
            features_archive = phase_dir / "features" / "archive"
            if features_archive.is_dir():
                count += len([d for d in features_archive.iterdir() if d.is_dir()])
    return count


def check_slice_log_freshness() -> dict:
    """Check SLICE_LOG freshness. Returns dict with status and details."""
    result = {"section": "slice_log", "status": "unknown", "age_days": None}

    slice_log = HARNESS_DIR / "SLICE_LOG.md"
    if not slice_log.is_file():
        result["status"] = "not_found"
        return result

    content = slice_log.read_text(encoding="utf-8", errors="replace")
    dates = re.findall(r"## (\d{4}-\d{2}-\d{2})", content)
    if not dates:
        # Fallback to any date if no headers found
        dates = re.findall(r"\d{4}-\d{2}-\d{2}", content)
        if not dates:
            result["status"] = "no_date"
            return result
        last_date_str = dates[-1]
    else:
        last_date_str = dates[0]
    try:
        last_date = datetime.strptime(last_date_str, "%Y-%m-%d").replace(
            tzinfo=timezone.utc
        )
        now = datetime.now(timezone.utc)
        age_days = (now - last_date).days
        result["age_days"] = age_days
        if age_days <= 7:
            result["status"] = "fresh"
        else:
            result["status"] = "stale"
    except ValueError:
        result["status"] = "no_date"

    return result


def check_version() -> dict:
    """Run version check script. Returns dict with status."""
    result = {"section": "version", "status": "unknown", "local_version": None}

    version_file = HARNESS_DIR / "VERSION"
    if version_file.is_file():
        result["local_version"] = version_file.read_text(encoding="utf-8").strip()

    # Try running version-check.py first, then .sh fallback
    candidates = [
        ("python3", ["scripts/version-check.py"]),
        ("bash", ["scripts/version-check.sh"]),
        ("bash", [str(HARNESS_DIR / "scripts" / "version-check.sh")]),
    ]
    for runner, args in candidates:
        script_path = Path(args[0])
        if script_path.is_file():
            import subprocess

            try:
                proc = subprocess.run(
                    [runner, str(script_path)],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                output = (proc.stdout + proc.stderr).strip()
                if "UP-TO-DATE" in output:
                    result["status"] = "up_to_date"
                elif "DOGFOOD" in output:
                    result["status"] = "dogfood"
                elif "BEHIND" in output:
                    result["status"] = "behind"
                elif "UNAVAILABLE" in output:
                    result["status"] = "unavailable"
                elif "UNKNOWN" in output:
                    result["status"] = "unknown_version"
                result["raw_output"] = output
                break
            except (FileNotFoundError, subprocess.TimeoutExpired):
                continue

    return result


def get_step_statuses() -> list[dict]:
    """Evaluate each workflow step and return structured results."""
    steps = []

    # init
    init_ok = (
        (HARNESS_DIR / "CONSTITUTION.md").is_file()
        and (HARNESS_DIR / "BRD.md").is_file()
    )
    steps.append(
        {
            "step": "init",
            "status": "done" if init_ok else "not_started",
            "label": "Init",
            "message": "Constitution, BRD, Architecture created"
            if init_ok
            else "Not started",
        }
    )

    # define
    spec_count = count_files("spec.md")
    steps.append(
        {
            "step": "define",
            "status": "done" if spec_count > 0 else "not_started",
            "label": "Define",
            "message": f"{spec_count} spec(s) created" if spec_count > 0 else "No specs yet",
        }
    )

    # design
    design_count = count_files("design.md")
    if design_count > 0:
        approved = has_approval()
        steps.append(
            {
                "step": "design",
                "status": "done" if approved else "pending",
                "label": "Design",
                "message": "Approved" if approved else "Pending approval",
            }
        )
    else:
        steps.append(
            {
                "step": "design",
                "status": "not_started",
                "label": "Design",
                "message": "No design yet",
            }
        )

    # approve
    if design_count > 0:
        approved = has_approval()
        steps.append(
            {
                "step": "approve",
                "status": "done" if approved else "pending",
                "label": "Approve",
                "message": "Design approved" if approved else "Waiting for human review",
            }
        )
    else:
        steps.append(
            {
                "step": "approve",
                "status": "not_started",
                "label": "Approve",
                "message": "No design to approve",
            }
        )

    # tasks
    tasks_count = count_files("tasks.md")
    if tasks_count > 0:
        remaining = count_incomplete_tasks()
        completed = count_completed_tasks()
        total = remaining + completed
        steps.append(
            {
                "step": "tasks",
                "status": "done",
                "label": "Tasks",
                "message": f"{completed}/{total} tasks complete",
                "total_tasks": total,
                "completed_tasks": completed,
                "remaining_tasks": remaining,
            }
        )
    else:
        steps.append(
            {
                "step": "tasks",
                "status": "not_started",
                "label": "Tasks",
                "message": "No tasks yet",
            }
        )

    # build
    if tasks_count > 0:
        remaining = count_incomplete_tasks()
        steps.append(
            {
                "step": "build",
                "status": "done" if remaining == 0 else "pending",
                "label": "Build",
                "message": "All tasks complete"
                if remaining == 0
                else f"{remaining} tasks remaining",
                "remaining_tasks": remaining,
            }
        )
    else:
        steps.append(
            {
                "step": "build",
                "status": "not_started",
                "label": "Build",
                "message": "No tasks to build",
            }
        )

    # verify
    verify_count = count_files("verification.md")
    if verify_count > 0:
        passed = verification_passed()
        steps.append(
            {
                "step": "verify",
                "status": "done" if passed else "pending",
                "label": "Verify",
                "message": "All criteria passing"
                if passed
                else "Verification pending or has failures",
            }
        )
    else:
        steps.append(
            {
                "step": "verify",
                "status": "not_started",
                "label": "Verify",
                "message": "No verification yet",
            }
        )

    # release-approve
    if verify_count > 0:
        approved_release = False
        for f in find_active("verification.md"):
            content = f.read_text(encoding="utf-8", errors="replace")
            for line in content.splitlines():
                if "Release Ref" in line and "APPROVED" in line:
                    approved_release = True
                    break
            if approved_release:
                break
        steps.append(
            {
                "step": "release-approve",
                "status": "done" if approved_release else "pending",
                "label": "Release Approve",
                "message": "Approved"
                if approved_release
                else "Pending human approval",
            }
        )
    else:
        steps.append(
            {
                "step": "release-approve",
                "status": "not_started",
                "label": "Release Approve",
                "message": "Verify first",
            }
        )

    # release
    archived = count_archived()
    steps.append(
        {
            "step": "release",
            "status": "done" if archived > 0 else "not_started",
            "label": "Release",
            "message": f"{archived} feature(s) released",
            "archived_count": archived,
        }
    )

    return steps


def determine_next_step(steps: list[dict]) -> str:
    """Determine the recommended next action."""
    step_map = {s["step"]: s for s in steps}

    if step_map["init"]["status"] != "done":
        return "init"
    if step_map["define"]["status"] != "done":
        return "define"
    if step_map["design"]["status"] == "not_started":
        return "design"
    if step_map["approve"]["status"] == "pending":
        return "approve (human review needed)"
    if step_map["tasks"]["status"] == "not_started":
        return "tasks"
    if step_map["build"]["status"] == "pending":
        return "build (tasks remaining)"
    if step_map["verify"]["status"] == "not_started":
        return "verify"
    if step_map.get("release-approve", {}).get("status") == "pending":
        return "release-approve (human approval needed)"
    return "release"


def format_duration(seconds: int) -> str:
    """Format seconds into human-readable duration."""
    if seconds < 0:
        return "0s"
    minutes = seconds // 60
    secs = seconds % 60
    if minutes > 0:
        return f"{minutes}m {secs:02d}s"
    return f"{secs}s"


def get_build_times() -> dict | None:
    """Read build-log.json and return build timing data, or None if absent."""
    build_log = HARNESS_DIR / "build-log.json"
    if not build_log.is_file():
        return None
    try:
        return json.loads(build_log.read_text())
    except (json.JSONDecodeError, OSError):
        return None


def format_human(steps: list[dict], slice_log: dict, version: dict):
    """Print human-readable colored output matching the original .sh format."""
    print(f"{CYAN}=== harness-eng Workflow Status ==={NC}")
    print()

    for s in steps:
        if s["status"] == "done":
            icon = f"{GREEN}✅{NC}"
        elif s["status"] == "pending":
            icon = f"{YELLOW}⏳{NC}"
        else:
            icon = f"{RED}❌{NC}"
        print(f"{icon} {s['label'].lower():8} — {s['message']}")

    # Build times
    build_data = get_build_times()
    if build_data:
        print()
        print(f"{CYAN}=== Build Times ==={NC}")
        for story in build_data.get("stories", []):
            duration = format_duration(story.get("duration_seconds", 0))
            print(f"   {story.get('id', '?')}: {duration}")
        total = format_duration(build_data.get("total_duration_seconds", 0))
        print(f"{GREEN}   Total: {total}{NC}")

    # SLICE_LOG
    print()
    print(f"{CYAN}=== SLICE_LOG ==={NC}")
    if slice_log["status"] == "fresh":
        print(f"{GREEN}✅ Fresh{NC} — last entry {slice_log['age_days']} days ago")
    elif slice_log["status"] == "stale":
        print(f"{YELLOW}⚠️  Stale{NC} — last entry {slice_log['age_days']} days ago")
    elif slice_log["status"] == "no_date":
        print(f"{YELLOW}⚠️  No date found{NC}")
    elif slice_log["status"] == "not_found":
        print(f"{RED}❌ Not found{NC}")
    else:
        print(f"{YELLOW}⚠️  Unknown{NC}")

    # Version
    print()
    print(f"{CYAN}=== Version ==={NC}")
    if version["status"] == "up_to_date":
        v = version.get("local_version", "?")
        print(f"{GREEN}✅ VERSION_CHECK:UP-TO-DATE{NC} — {v}")
    elif version["status"] == "dogfood":
        v = version.get("local_version", "?")
        print(f"{GREEN}✅ VERSION_CHECK:DOGFOOD{NC} — {v} (canonical source repo)")
    elif version["status"] == "behind":
        raw = version.get("raw_output", "")
        # Extract the version from raw output
        print(f"{YELLOW}{raw}{NC}" if raw else f"{YELLOW}⚠️  Update available{NC}")
    elif version["status"] == "unavailable":
        print(f"{YELLOW}⚠️  VERSION_CHECK:UNAVAILABLE{NC} — Could not fetch latest version")
    elif version["status"] == "unknown_version":
        raw = version.get("raw_output", "")
        print(f"{YELLOW}{raw}{NC}" if raw else f"{YELLOW}⚠️  Version format unknown{NC}")
    else:
        print(f"{YELLOW}⚠️  Version check not available{NC}")

    # Next step
    print()
    print(f"{CYAN}=== Next Step ==={NC}")
    print(f"→ Run: {determine_next_step(steps)}")


def format_json(steps: list[dict], slice_log: dict, version: dict):
    """Output structured JSON with all status information."""
    output = {
        "workflow_steps": steps,
        "slice_log": slice_log,
        "version": version,
        "build_times": get_build_times(),
        "next_step": determine_next_step(steps),
    }
    print(json.dumps(output, indent=2, default=str))


def main():
    steps = get_step_statuses()
    slice_log = check_slice_log_freshness()
    version = check_version()

    if JSON_MODE:
        format_json(steps, slice_log, version)
    else:
        format_human(steps, slice_log, version)


if __name__ == "__main__":
    main()
