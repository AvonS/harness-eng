#!/usr/bin/env python3
# *** Maintained by AvonS/harness-eng, DON'T modify this, will be overwritten during next upgrade ***
"""
harness-status.py — Show current workflow state.

Usage: python3 scripts/harness-status.py [--json]

Default: Colored human-readable output.
--json:   Structured JSON blob with all status fields.
"""

import json
from dataclasses import dataclass
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from harness_layout import active_artifacts, archived_item_count, active_feature_dirs

HARNESS_DIR = Path(".harness-eng")

# ANSI colors
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
RED = "\033[0;31m"
CYAN = "\033[0;36m"
NC = "\033[0m"

JSON_MODE = "--json" in sys.argv
PLAIN_MODE = "--plain" in sys.argv

if PLAIN_MODE:
    GREEN = ""
    YELLOW = ""
    RED = ""
    CYAN = ""
    NC = ""

@dataclass
class StatusSnapshot:
    steps: list[dict]
    slice_log: dict
    version: dict
    build_times: dict | None
    skill_install_log: dict | None
    blocked_features: list[str]
    deferred_items: dict
    handover: dict
    next_step: str


def eprint(*args, **kwargs):
    """Print to stderr (used for non-JSON messages in JSON mode)."""
    print(*args, file=sys.stderr, **kwargs)


def find_active(filename: str) -> list[Path]:
    """Find files in active CR/bug items and active phase features."""
    return active_artifacts(HARNESS_DIR, filename)


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
    return archived_item_count(HARNESS_DIR)


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
        blocked = find_blocked_features()
        steps.append(
            {
                "step": "build",
                "status": "pending" if blocked else ("done" if remaining == 0 else "pending"),
                "label": "Build",
                "message": "Blocked by BLOCKED.md"
                if blocked
                else ("All tasks complete" if remaining == 0 else f"{remaining} tasks remaining"),
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

    if find_blocked_features():
        return "resolve BLOCKED.md"
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


def get_skill_install_log() -> dict | None:
    log_path = HARNESS_DIR / "skill-install.json"
    if not log_path.is_file():
        return None
    try:
        return json.loads(log_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def find_blocked_features() -> list[Path]:
    return find_active("BLOCKED.md")


def count_deferred_items() -> dict:
    """Count deferred items by status across active features."""
    counts = {"open": 0, "resolved": 0, "superseded": 0, "promoted-to-blocker": 0}
    for f in find_active("deferred.md"):
        content = f.read_text(encoding="utf-8", errors="replace")
        for line in content.splitlines():
            if line.startswith("|") and not line.startswith("|--"):
                cells = [c.strip() for c in line.split("|")]
                if len(cells) >= 7:
                    status = cells[6].lower()
                    if status in counts:
                        counts[status] += 1
    return counts


def load_plan() -> dict:
    plan_file = HARNESS_DIR / "plan.yaml"
    if not plan_file.is_file():
        return {"phases": []}
    phases = []
    try:
        content = plan_file.read_text(encoding="utf-8")
        current_phase = None
        current_slice = None
        for line in content.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            indent = len(line) - len(line.lstrip())
            if stripped.startswith("- id:"):
                item_id = stripped.split(":", 1)[1].strip().strip('"').strip("'")
                if indent == 2:
                    if current_phase:
                        phases.append(current_phase)
                    current_phase = {"id": item_id, "slices": []}
                    current_slice = None
                elif indent == 6:
                    current_slice = {"id": item_id, "status": "pending", "name": "", "resolution": ""}
                    if current_phase:
                        current_phase["slices"].append(current_slice)
            elif stripped.startswith("name:"):
                val = stripped.split(":", 1)[1].strip().strip('"').strip("'")
                if indent == 4 and current_phase:
                    current_phase["name"] = val
                elif indent == 8 and current_slice:
                    current_slice["name"] = val
            elif stripped.startswith("status:"):
                val = stripped.split(":", 1)[1].strip().strip('"').strip("'")
                if indent == 4 and current_phase:
                    current_phase["status"] = val
                elif indent == 8 and current_slice:
                    current_slice["status"] = val
            elif stripped.startswith("resolution:"):
                val = stripped.split(":", 1)[1].strip().strip('"').strip("'")
                if indent == 8 and current_slice:
                    current_slice["resolution"] = val
        if current_phase:
            phases.append(current_phase)
    except Exception as e:
        eprint(f"Warning: failed to parse plan.yaml: {e}")
    return {"phases": phases}


def get_evidence_freshness(slice_id: str) -> str:
    active_dirs = active_feature_dirs(HARNESS_DIR)
    for d in active_dirs:
        if d.name == slice_id or d.name.startswith(slice_id + "-"):
            slice_yaml = d / "verify" / "slice.yaml"
            if slice_yaml.is_file():
                try:
                    content = slice_yaml.read_text(encoding="utf-8")
                    recorded_at = None
                    config_h = None
                    env_h = None
                    for line in content.splitlines():
                        if "recorded_at:" in line:
                            recorded_at = line.split(":", 1)[1].strip().strip('"').strip("'")
                        elif "config_hash:" in line:
                            config_h = line.split(":", 1)[1].strip().strip('"').strip("'")
                        elif "environment_hash:" in line:
                            env_h = line.split(":", 1)[1].strip().strip('"').strip("'")
                    
                    age_str = "unknown age"
                    is_stale = False
                    if recorded_at:
                        try:
                            # Parse UTC timestamp
                            dt = datetime.fromisoformat(recorded_at.replace("Z", "+00:00"))
                            delta = datetime.now(timezone.utc) - dt
                            age_days = delta.days
                            if age_days == 0:
                                age_str = "today"
                            else:
                                age_str = f"{age_days}d ago"
                            if age_days >= 1:
                                is_stale = True
                        except Exception:
                            pass
                    
                    curr_config_h = get_config_hash()
                    curr_env_h = get_environment_hash()
                    if config_h != curr_config_h or env_h != curr_env_h:
                        is_stale = True
                        
                    status_lbl = "stale" if is_stale else "fresh"
                    return f"({status_lbl}, {age_str})"
                except Exception:
                    pass
    return ""


def format_human(snapshot: StatusSnapshot):
    """Print human-readable colored output matching the original .sh format."""
    print(f"{CYAN}=== harness-eng Workflow Status ==={NC}")
    print()

    for s in snapshot.steps:
        if s["status"] == "done":
            icon = f"{GREEN}✅{NC}"
        elif s["status"] == "pending":
            icon = f"{YELLOW}⏳{NC}"
        else:
            icon = f"{RED}❌{NC}"
        print(f"{icon} {s['label'].lower():8} — {s['message']}")

    blocked = snapshot.blocked_features
    if blocked:
        print()
        print(f"{RED}⛔ BLOCKED{NC} — {blocked[0]}")

    # Plan Phases
    plan_data = load_plan()
    show_all = "--all" in sys.argv
    print()
    print(f"{CYAN}=== Plan Phases ==={NC}")
    for p in plan_data.get("phases", []):
        if p["status"] == "active" or show_all:
            status_icon = "🟢" if p["status"] == "active" else ("⚪" if p["status"] == "pending" else "🔵")
            print(f" {status_icon} {p['name']} ({p['status']})")
            for s in p.get("slices", []):
                slice_icon = "  ⏳" if s["status"] == "active" else ("  ⚪" if s["status"] == "pending" else "  ✅")
                freshness = ""
                if s["status"] == "active":
                    freshness = get_evidence_freshness(s["id"])
                    if freshness:
                        freshness = " " + freshness
                print(f"{slice_icon} {s['id']}: {s['name']} [{s['status']}]{freshness}")

    # Build times
    build_data = snapshot.build_times
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
    if snapshot.slice_log["status"] == "fresh":
        print(f"{GREEN}✅ Fresh{NC} — last entry {snapshot.slice_log['age_days']} days ago")
    elif snapshot.slice_log["status"] == "stale":
        print(f"{YELLOW}⚠️  Stale{NC} — last entry {snapshot.slice_log['age_days']} days ago")
    elif snapshot.slice_log["status"] == "no_date":
        print(f"{YELLOW}⚠️  No date found{NC}")
    elif snapshot.slice_log["status"] == "not_found":
        print(f"{RED}❌ Not found{NC}")
    else:
        print(f"{YELLOW}⚠️  Unknown{NC}")

    # Version
    print()
    print(f"{CYAN}=== Version ==={NC}")
    if snapshot.version["status"] == "up_to_date":
        v = snapshot.version.get("local_version", "?")
        print(f"{GREEN}✅ VERSION_CHECK:UP-TO-DATE{NC} — {v}")
    elif snapshot.version["status"] == "dogfood":
        v = snapshot.version.get("local_version", "?")
        print(f"{GREEN}✅ VERSION_CHECK:DOGFOOD{NC} — {v} (canonical source repo)")
    elif snapshot.version["status"] == "behind":
        raw = snapshot.version.get("raw_output", "")
        print(f"{YELLOW}{raw}{NC}" if raw else f"{YELLOW}⚠️  Update available{NC}")
    elif snapshot.version["status"] == "unavailable":
        print(f"{YELLOW}⚠️  VERSION_CHECK:UNAVAILABLE{NC} — Could not fetch latest version")
    elif snapshot.version["status"] == "unknown_version":
        raw = snapshot.version.get("raw_output", "")
        print(f"{YELLOW}{raw}{NC}" if raw else f"{YELLOW}⚠️  Version format unknown{NC}")
    else:
        print(f"{YELLOW}⚠️  Version check not available{NC}")

    skill_log = snapshot.skill_install_log
    if skill_log is not None:
        print()
        print(f"{CYAN}=== Skill Install Log ==={NC}")
        print(f"{GREEN}✅ {len(skill_log)} skill install record(s){NC}")

    # Next step
    print()
    print(f"{CYAN}=== Next Step ==={NC}")
    print(f"→ Run: {snapshot.next_step}")

    # Deferred items
    deferred = snapshot.deferred_items
    if any(v > 0 for v in deferred.values()):
        print()
        print(f"{CYAN}=== Deferred Items ==={NC}")
        if deferred["open"] > 0:
            print(f"{YELLOW}   Open: {deferred['open']}{NC}")
        if deferred["promoted-to-blocker"] > 0:
            print(f"{RED}   Promoted to blocker: {deferred['promoted-to-blocker']}{NC}")
        if deferred["resolved"] > 0:
            print(f"{GREEN}   Resolved: {deferred['resolved']}{NC}")
        if deferred["superseded"] > 0:
            print(f"   Superseded: {deferred['superseded']}")


def to_yaml(data) -> str:
    if isinstance(data, dict):
        lines = []
        for k, v in data.items():
            if isinstance(v, (str, int, bool)) or v is None:
                val_str = "" if v is None else str(v)
                if ":" in val_str or "#" in val_str or "\n" in val_str or v == "":
                    val_str = f'"{val_str}"'
                lines.append(f"{k}: {val_str}")
            elif isinstance(v, list):
                if not v:
                    lines.append(f"{k}: []")
                else:
                    lines.append(f"{k}:")
                    for item in v:
                        if isinstance(item, dict):
                            lines.append(f"  - " + to_yaml(item).replace("\n", "\n    ").strip())
                        else:
                            val_str = str(item)
                            if ":" in val_str or "#" in val_str or "\n" in val_str or item == "":
                                val_str = f'"{val_str}"'
                            lines.append(f"  - {val_str}")
        return "\n".join(lines)
    return ""


def parse_markdown_metadata(content: str) -> dict:
    meta = {}
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            frontmatter = parts[1]
            for line in frontmatter.splitlines():
                if ":" in line:
                    key, val = line.split(":", 1)
                    meta[key.strip()] = val.strip().strip('"').strip("'")
    return meta


def extract_decisions(content: str, ref_file: str = "") -> list[dict]:
    decisions = []
    lines = content.splitlines()
    in_section = False
    for line in lines:
        if line.startswith("## Technical Decisions") or line.startswith("## Research & Technical Decisions"):
            in_section = True
            continue
        if in_section:
            if line.startswith("##") or line.startswith("---"):
                in_section = False
                continue
            if line.startswith("|") and "DEC-" in line:
                cells = [c.strip() for c in line.split("|")[1:-1]]
                if len(cells) >= 3 and cells[0].startswith("DEC-"):
                    decisions.append({
                        "id": cells[0],
                        "decision": cells[1],
                        "rationale": cells[2],
                        "ref": ref_file
                    })
    return decisions


def extract_assumptions(content: str) -> list[str]:
    assumptions = []
    lines = content.splitlines()
    in_section = False
    for line in lines:
        if line.startswith("## Assumptions"):
            in_section = True
            continue
        if in_section:
            if line.startswith("##") or line.startswith("---"):
                in_section = False
                continue
            if line.strip().startswith("-"):
                assumptions.append(line.strip().lstrip("-").strip())
    return assumptions


def regenerate_handover(steps: list[dict]) -> dict:
    """Scan authoritative artifacts and write `.harness-eng/handover.yaml`."""
    current_slice = ""
    workflow_level = "M/L"
    completed_tasks = []
    decisions = []
    assumptions = []
    evidence = []
    blockers = []
    
    specs = find_active("spec.md")
    if specs:
        spec_path = specs[0]
        current_slice = spec_path.parent.name
        try:
            content = spec_path.read_text(encoding="utf-8", errors="replace")
            meta = parse_markdown_metadata(content)
            workflow_level = meta.get("workflow_level", "M/L")
            decisions.extend(extract_decisions(content, ref_file="spec.md"))
            assumptions.extend(extract_assumptions(content))
        except Exception:
            pass
            
    designs = find_active("design.md")
    if designs:
        try:
            content = designs[0].read_text(encoding="utf-8", errors="replace")
            decisions.extend(extract_decisions(content, ref_file="design.md"))
        except Exception:
            pass

    tasks = find_active("tasks.md")
    if tasks:
        try:
            content = tasks[0].read_text(encoding="utf-8", errors="replace")
            for line in content.splitlines():
                if line.startswith("- [x]") or line.startswith("- [X]"):
                    parts = line.split(" ", 2)
                    if len(parts) >= 3:
                        completed_tasks.append(parts[2].strip())
        except Exception:
            pass

    blocked_files = find_blocked_features()
    for f in blocked_files:
        try:
            lines = f.read_text(encoding="utf-8", errors="replace").splitlines()
            for line in lines:
                if line.strip().startswith("-"):
                    blockers.append(line.strip().lstrip("-").strip())
        except Exception:
            pass

    verifications = find_active("verification.md")
    if verifications:
        try:
            content = verifications[0].read_text(encoding="utf-8", errors="replace")
            for line in content.splitlines():
                if line.startswith("|") and ("PASS" in line or "FAIL" in line) and not line.startswith("|--"):
                    cells = [c.strip() for c in line.split("|")[1:-1]]
                    if len(cells) >= 2:
                        evidence.append({"name": cells[0], "status": cells[1]})
        except Exception:
            pass

    state = "defined"
    step_map = {s["step"]: s for s in steps}
    if blocked_files:
        state = "blocked"
    elif step_map.get("verify", {}).get("status") == "done":
        state = "verified"
    elif step_map.get("build", {}).get("status") == "done":
        state = "verification-pending"
    elif step_map.get("tasks", {}).get("status") == "done":
        state = "building"
        
    next_action = determine_next_step(steps)

    handover_data = {
        "state": state,
        "current_slice": current_slice,
        "workflow_level": workflow_level,
        "completed": completed_tasks,
        "decisions": [{"id": d["id"], "ref": d["ref"]} for d in decisions],
        "assumptions": assumptions,
        "evidence": [e["name"] for e in evidence],
        "blockers": blockers,
        "next_action": next_action
    }

    try:
        yaml_content = "# Generated derived handover view. Do not edit directly.\n" + to_yaml(handover_data)
        (HARNESS_DIR / "handover.yaml").write_text(yaml_content, encoding="utf-8")
    except Exception as e:
        eprint(f"Error: failed to write handover.yaml: {e}")
        sys.exit(1)

    return handover_data


import html

def format_html(snapshot: StatusSnapshot):
    """Generate a premium, self-contained HTML status page."""
    steps = snapshot.steps
    slice_log = snapshot.slice_log
    version = snapshot.version
    next_step = snapshot.next_step
    deferred = snapshot.deferred_items
    handover = snapshot.handover
    step_rows = ""
    for s in steps:
        if s["status"] == "done":
            status_class = "status-done"
            status_symbol = "&#10003;"
        elif s["status"] == "pending":
            status_class = "status-pending"
            status_symbol = "&#9203;"
        else:
            status_class = "status-not-started"
            status_symbol = "&#10007;"
        
        step_rows += f"""
        <div class="step-card {status_class}">
            <div class="step-icon">{status_symbol}</div>
            <div class="step-details">
                <span class="step-label">{html.escape(s['label'])}</span>
                <span class="step-message">{html.escape(s['message'])}</span>
            </div>
        </div>
        """

    decisions_list = ""
    for d in handover.get("decisions", []):
        decisions_list += f"<li><strong>{html.escape(d.get('id', ''))}</strong> (ref: {html.escape(d.get('ref', ''))})</li>"
    if not decisions_list:
        decisions_list = "<li>No decisions recorded</li>"

    completed_list = ""
    for c in handover.get("completed", []):
        completed_list += f"<li>&#10003; {html.escape(c)}</li>"
    if not completed_list:
        completed_list = "<li>No tasks completed</li>"

    blockers_list = ""
    for b in handover.get("blockers", []):
        blockers_list += f"<li class='blocker-item'>&#9940; {html.escape(b)}</li>"
    if not blockers_list:
        blockers_list = "<li>No active blockers</li>"

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>harness-eng status</title>
    <style>
        body {{
            background-color: #0f172a;
            color: #f8fafc;
            font-family: 'Inter', -apple-system, sans-serif;
            margin: 0;
            padding: 2rem;
            display: flex;
            justify-content: center;
        }}
        .container {{
            max-width: 1000px;
            width: 100%;
        }}
        header {{
            margin-bottom: 2rem;
            border-bottom: 1px solid #334155;
            padding-bottom: 1rem;
        }}
        h1 {{
            color: #38bdf8;
            font-size: 2.25rem;
            margin: 0;
        }}
        .meta {{
            color: #94a3b8;
            font-size: 0.875rem;
            margin-top: 0.5rem;
        }}
        .grid {{
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 2rem;
        }}
        @media (max-width: 768px) {{
            .grid {{
                grid-template-columns: 1fr;
            }}
        }}
        .card {{
            background: #1e293b;
            border-radius: 8px;
            border: 1px solid #334155;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }}
        h2 {{
            color: #38bdf8;
            margin-top: 0;
            font-size: 1.25rem;
            border-bottom: 1px solid #334155;
            padding-bottom: 0.5rem;
        }}
        .step-card {{
            display: flex;
            align-items: center;
            padding: 0.75rem;
            border-radius: 6px;
            margin-bottom: 0.5rem;
            border-left: 4px solid transparent;
        }}
        .status-done {{
            background: #14532d;
            border-left-color: #22c55e;
        }}
        .status-pending {{
            background: #78350f;
            border-left-color: #eab308;
        }}
        .status-not-started {{
            background: #450a0a;
            border-left-color: #ef4444;
        }}
        .step-icon {{
            font-size: 1.25rem;
            margin-right: 1rem;
            width: 24px;
            text-align: center;
        }}
        .step-details {{
            display: flex;
            flex-direction: column;
        }}
        .step-label {{
            font-weight: bold;
            font-size: 1rem;
        }}
        .step-message {{
            font-size: 0.875rem;
            color: #cbd5e1;
        }}
        .badge {{
            display: inline-block;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: bold;
            text-transform: uppercase;
        }}
        .badge-info {{ background-color: #0369a1; color: #e0f2fe; }}
        .badge-warning {{ background-color: #78350f; color: #fef9c3; }}
        .badge-success {{ background-color: #14532d; color: #dcfce7; }}
        ul {{
            padding-left: 1.25rem;
            margin: 0;
        }}
        li {{
            margin-bottom: 0.5rem;
            color: #cbd5e1;
        }}
        .blocker-item {{
            color: #f87171;
            font-weight: bold;
        }}
        .next-step-box {{
            background: #0369a1;
            border-radius: 6px;
            padding: 1rem;
            font-weight: bold;
            color: #e0f2fe;
            margin-top: 1rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>harness-eng status</h1>
            <div class="meta">
                Generated at: {datetime.now(timezone.utc).isoformat()} |
                Harness Version: {html.escape(version.get('local_version', 'v0.3.0'))} |
                Workflow Level: <span class="badge badge-info">{html.escape(handover.get('workflow_level', 'M/L'))}</span>
            </div>
        </header>
        
        <div class="grid">
            <div class="main-column">
                <div class="card">
                    <h2>Workflow Steps</h2>
                    {step_rows}
                </div>
                
                <div class="card">
                    <h2>Active Slice & Handover State</h2>
                    <p><strong>Current Slice:</strong> {html.escape(handover.get('current_slice', 'None'))}</p>
                    <p><strong>Lifecycle State:</strong> <span class="badge badge-info">{html.escape(handover.get('state', 'unknown'))}</span></p>
                    
                    <h3>Completed Tasks / Stories</h3>
                    <ul>
                        {completed_list}
                    </ul>
                    
                    <h3>Technical Decisions</h3>
                    <ul>
                        {decisions_list}
                    </ul>
                </div>
            </div>
            
            <div class="sidebar">
                <div class="card">
                    <h2>Next Action</h2>
                    <div class="next-step-box">
                        → {html.escape(next_step)}
                    </div>
                </div>

                <div class="card">
                    <h2>Active Blockers</h2>
                    <ul>
                        {blockers_list}
                    </ul>
                </div>
                
                <div class="card">
                    <h2>Deferred Items</h2>
                    <p><strong>Open:</strong> {deferred.get('open', 0)}</p>
                    <p><strong>Resolved:</strong> {deferred.get('resolved', 0)}</p>
                    <p><strong>Promoted to Blocker:</strong> {deferred.get('promoted-to-blocker', 0)}</p>
                </div>

                <div class="card">
                    <h2>SLICE_LOG Status</h2>
                    <p>Status: <span class="badge {'badge-success' if slice_log['status'] == 'fresh' else 'badge-warning'}">{html.escape(slice_log['status'])}</span></p>
                    {f"<p>Age: {slice_log['age_days']} days ago</p>" if slice_log.get('age_days') is not None else ""}
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""
    try:
        html_dir = HARNESS_DIR / "status"
        html_dir.mkdir(parents=True, exist_ok=True)
        (html_dir / "index.html").write_text(html_content, encoding="utf-8")
    except Exception as e:
        eprint(f"Warning: failed to write status HTML: {e}")


def format_json(snapshot: StatusSnapshot):
    """Output structured JSON with all status information."""
    output = {
        "workflow_steps": snapshot.steps,
        "slice_log": snapshot.slice_log,
        "version": snapshot.version,
        "build_times": snapshot.build_times,
        "skill_install_log": snapshot.skill_install_log,
        "blocked_features": snapshot.blocked_features,
        "deferred_items": snapshot.deferred_items,
        "handover": snapshot.handover,
        "next_step": snapshot.next_step,
    }
    print(json.dumps(output, indent=2, default=str))


def get_environment_hash() -> str:
    import hashlib
    lockfiles = [
        "package-lock.json", "go.sum", "Cargo.lock", "poetry.lock",
        "Gemfile.lock", "mix.lock", "composer.lock", "requirements.txt"
    ]
    for lf in lockfiles:
        path = Path(lf)
        if path.is_file():
            try:
                return hashlib.sha256(path.read_bytes()).hexdigest()
            except Exception:
                pass
    fallback_str = f"{sys.version}_{sys.platform}"
    return hashlib.sha256(fallback_str.encode("utf-8")).hexdigest()


def get_config_hash() -> str:
    import hashlib
    content = b""
    constitution_file = HARNESS_DIR / "CONSTITUTION.md"
    if constitution_file.is_file():
        try:
            content += constitution_file.read_bytes()
        except Exception:
            pass
            
    spec_yamls = active_artifacts(HARNESS_DIR, "spec.yaml")
    if spec_yamls:
        try:
            content += spec_yamls[0].read_bytes()
        except Exception:
            pass
    else:
        spec_mds = active_artifacts(HARNESS_DIR, "spec.md")
        if spec_mds:
            try:
                content += spec_mds[0].read_bytes()
            except Exception:
                pass
                
    return hashlib.sha256(content).hexdigest()


def ensure_compiled_policy():
    project_yaml = HARNESS_DIR / "project.yaml"
    config_h = get_config_hash()
    env_h = get_environment_hash()
    
    project_name = "harness-eng"
    tech_stack = []
    
    tech_file = HARNESS_DIR / "technology.yaml"
    if tech_file.is_file():
        try:
            for line in tech_file.read_text(encoding="utf-8").splitlines():
                if "-" in line and not line.strip().startswith("#"):
                    tech_stack.append(line.split("-", 1)[1].strip())
        except Exception:
            pass
    if not tech_stack:
        tech_stack = ["Python", "Git"]
        
    yaml_content = f"""project_name: "{project_name}"
locked_constraints: []
constitution_hash: "{config_h}"
config_hash: "{config_h}"
environment_hash: "{env_h}"
workflow_default: "M/L"
technology_stack:
"""
    for tech in tech_stack:
        yaml_content += f"  - \"{tech}\"\n"
        
    project_yaml.write_text(yaml_content, encoding="utf-8")


def ensure_plan():
    plan_yaml = HARNESS_DIR / "plan.yaml"
    if not plan_yaml.is_file():
        phases = []
        phases_file = HARNESS_DIR / "PHASES.md"
        if phases_file.is_file():
            content = phases_file.read_text(encoding="utf-8")
            current_phase = None
            for line in content.splitlines():
                if line.startswith("# Phase") or line.startswith("## Phase"):
                    phase_name = line.lstrip("#").strip()
                    current_phase = {
                        "id": f"PHASE-{len(phases)+1:02d}",
                        "name": phase_name,
                        "status": "pending",
                        "slices": []
                    }
                    phases.append(current_phase)
                elif line.strip().startswith("-") and current_phase is not None:
                    slice_name = line.strip().lstrip("-").strip()
                    current_phase["slices"].append({
                        "id": f"F{len(phases)}0{len(current_phase['slices'])+1}",
                        "name": slice_name,
                        "status": "pending",
                        "resolution": "summary"
                    })
        
        if not phases:
            phases = [{
                "id": "PHASE-01",
                "name": "Phase 1: Foundation",
                "status": "active",
                "slices": []
            }]
            
        active_dirs = active_feature_dirs(HARNESS_DIR)
        for d in active_dirs:
            found = False
            for p in phases:
                for s in p["slices"]:
                    if s["id"] == d.name:
                        s["status"] = "active"
                        s["resolution"] = "detailed"
                        p["status"] = "active"
                        found = True
                        break
            if not found:
                phases[0]["slices"].append({
                    "id": d.name,
                    "name": d.name,
                    "status": "active",
                    "resolution": "detailed"
                })
                phases[0]["status"] = "active"
                
        yaml_lines = ["phases:"]
        for p in phases:
            yaml_lines.append(f"  - id: {p['id']}")
            yaml_lines.append(f"    name: \"{p['name']}\"")
            yaml_lines.append(f"    status: {p['status']}")
            if not p["slices"]:
                yaml_lines.append("    slices: []")
            else:
                yaml_lines.append("    slices:")
                for s in p["slices"]:
                    yaml_lines.append(f"      - id: {s['id']}")
                    yaml_lines.append(f"        name: \"{s['name']}\"")
                    yaml_lines.append(f"        status: {s['status']}")
                    yaml_lines.append(f"        resolution: {s['resolution']}")
                    
        plan_yaml.write_text("\n".join(yaml_lines) + "\n", encoding="utf-8")
        eprint(f"Generated {plan_yaml}")


def main():
    ensure_compiled_policy()
    ensure_plan()
    steps = get_step_statuses()
    slice_log = check_slice_log_freshness()
    version = check_version()
    
    if "--regenerate" in sys.argv:
        regenerate_handover(steps)
        if len(sys.argv) == 2 or (len(sys.argv) == 3 and "--json" in sys.argv):
            sys.exit(0)

    # Load existing handover.yaml if it exists
    handover = {}
    handover_file = HARNESS_DIR / "handover.yaml"
    if handover_file.is_file():
        try:
            content = handover_file.read_text(encoding="utf-8")
            lines = content.splitlines()
            current_key = None
            for line in lines:
                if ":" in line and not line.strip().startswith("-"):
                    k, v = line.split(":", 1)
                    k = k.strip()
                    v = v.strip().strip('"').strip("'")
                    if v == "[]" or v == "":
                        handover[k] = []
                    else:
                        handover[k] = v
                elif line.strip().startswith("-"):
                    val = line.strip().lstrip("-").strip().strip('"').strip("'")
                    if current_key and isinstance(handover.get(current_key), list):
                        handover[current_key].append(val)
                if not line.strip().startswith("-") and ":" in line:
                    current_key = line.split(":", 1)[0].strip()
                    
            # Parse decisions list of dicts
            decisions = []
            current_decision = None
            for line in lines:
                if line.strip().startswith("- id:"):
                    if current_decision:
                        decisions.append(current_decision)
                    current_decision = {"id": line.split(":", 1)[1].strip().strip('"').strip("'")}
                elif line.strip().startswith("ref:") and current_decision:
                    current_decision["ref"] = line.split(":", 1)[1].strip().strip('"').strip("'")
            if current_decision:
                decisions.append(current_decision)
            handover["decisions"] = decisions

            # completed list
            completed = []
            in_completed = False
            for line in lines:
                if line.startswith("completed:"):
                    in_completed = True
                elif in_completed:
                    if line.startswith("  - ") and not ":" in line:
                        completed.append(line.split("-", 1)[1].strip().strip('"').strip("'"))
                    elif line.strip() != "" and not line.startswith("  - "):
                        in_completed = False
            handover["completed"] = completed

            # assumptions list
            assumptions = []
            in_assumptions = False
            for line in lines:
                if line.startswith("assumptions:"):
                    in_assumptions = True
                elif in_assumptions:
                    if line.startswith("  - ") and not ":" in line:
                        assumptions.append(line.split("-", 1)[1].strip().strip('"').strip("'"))
                    elif line.strip() != "" and not line.startswith("  - "):
                        in_assumptions = False
            handover["assumptions"] = assumptions

            # blockers list
            blockers = []
            in_blockers = False
            for line in lines:
                if line.startswith("blockers:"):
                    in_blockers = True
                elif in_blockers:
                    if line.startswith("  - ") and not ":" in line:
                        blockers.append(line.split("-", 1)[1].strip().strip('"').strip("'"))
                    elif line.strip() != "" and not line.startswith("  - "):
                        in_blockers = False
            handover["blockers"] = blockers

        except Exception as e:
            eprint(f"Warning: failed to parse handover.yaml: {e}")

    if not handover:
        handover = {
            "state": "pending",
            "current_slice": "None",
            "workflow_level": "M/L",
            "completed": [],
            "decisions": [],
            "assumptions": [],
            "evidence": [],
            "blockers": [],
            "next_action": determine_next_step(steps)
        }

    snapshot = StatusSnapshot(
        steps=steps,
        slice_log=slice_log,
        version=version,
        build_times=get_build_times(),
        skill_install_log=get_skill_install_log(),
        blocked_features=[str(p) for p in find_blocked_features()],
        deferred_items=count_deferred_items(),
        handover=handover,
        next_step=determine_next_step(steps)
    )

    if "--json" in sys.argv:
        format_json(snapshot)
    elif "--html" in sys.argv:
        format_html(snapshot)
        print(f"HTML status written to .harness-eng/status/index.html")
    else:
        format_human(snapshot)
        
        print()
        print(f"{CYAN}=== Handover View (handover.yaml) ==={NC}")
        print(f"   State: {handover.get('state')}")
        print(f"   Workflow Level: {handover.get('workflow_level')}")
        print(f"   Current Slice: {handover.get('current_slice')}")
        print(f"   Decisions Count: {len(handover.get('decisions', []))}")


if __name__ == "__main__":
    main()
