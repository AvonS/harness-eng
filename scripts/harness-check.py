#!/usr/bin/env python3
# *** Maintained by AvonS/harness-eng, DON'T modify this, will be overwritten during next upgrade ***
"""
harness-check.py — Validate prerequisites for each workflow step.

Usage: python3 scripts/harness-check.py <command> [--json]

Commands: init, triage, bug, define, design, review-pre-build, approve, tasks, build, review-pre-verify, verify, release
Exit: 0 = prerequisites met, 1 = prerequisites not met
"""

import json
import sys
from pathlib import Path

HARNESS_DIR = Path(".harness-eng")

RED = "[0;31m"
GREEN = "[0;32m"
YELLOW = "[1;33m"
NC = "[0m"

JSON_MODE = "--json" in sys.argv

def msg(*args, **kwargs):
    if JSON_MODE:
        print(*args, file=sys.stderr, **kwargs)
    else:
        print(*args, **kwargs)

def find_active(filename: str) -> list[Path]:
    results = []
    results.extend(HARNESS_DIR.glob(f"specs/active/*/{filename}"))
    results.extend(HARNESS_DIR.glob(f"phases/*/features/active/*/{filename}"))
    results.extend(HARNESS_DIR.glob(f"phase-*/features/active/*/{filename}"))
    return results

def count_incomplete_tasks() -> int:
    total = 0
    for f in find_active("tasks.md"):
        content = f.read_text(encoding="utf-8", errors="replace")
        for line in content.splitlines():
            if line.startswith("- [ ]"):
                total += 1
    return total

def check_active_file_approved(filename: str) -> bool:
    for f in find_active(filename):
        content = f.read_text(encoding="utf-8", errors="replace")
        if "Ref" in content and "APPROVED" in content:
            return True
    return False

results = []

def pass_msg(m: str):
    results.append({"type": "pass", "message": m})
    if not JSON_MODE:
        print(f"{GREEN}✅ PASS{NC}: {m}")

def fail_msg(m: str):
    results.append({"type": "fail", "message": m})
    if not JSON_MODE:
        print(f"{RED}❌ FAIL{NC}: {m}")

def warn_msg(m: str):
    results.append({"type": "warn", "message": m})
    if not JSON_MODE:
        print(f"{YELLOW}⚠️  WARN{NC}: {m}")

def info_msg(m: str):
    results.append({"type": "info", "message": m})
    if not JSON_MODE:
        print(f"   {m}")

def check_file(path: Path, description: str) -> bool:
    if path.is_dir() or path.is_file():
        pass_msg(description)
        return True
    else:
        fail_msg(f"{description} — not found: {path}")
        return False

def check_active_file(filename: str, description: str) -> bool:
    matches = find_active(filename)
    if matches:
        pass_msg(description)
        return True
    else:
        fail_msg(f"{description} — {filename} not found in any active feature")
        return False

def validate_init() -> int:
    errors = 0
    msg("=== Checking prerequisites for: init ===")
    pass_msg("Ready to run init")
    return errors

def validate_triage() -> int:
    errors = 0
    msg("=== Checking prerequisites for: triage ===")
    if not check_file(HARNESS_DIR, ".harness-eng/ exists"):
        errors += 1
    if errors == 0:
        pass_msg("Ready to triage")
    return errors

def validate_bug() -> int:
    errors = 0
    msg("=== Checking prerequisites for: bug ===")
    if not check_file(HARNESS_DIR, ".harness-eng/ exists"):
        errors += 1
    if errors == 0:
        pass_msg("Ready to run bug workflow")
    return errors

def validate_define() -> int:
    errors = 0
    msg("=== Checking prerequisites for: define ===")
    if not check_file(HARNESS_DIR / "CONSTITUTION.md", "Constitution exists"):
        errors += 1
    if not check_file(HARNESS_DIR / "BRD.md", "BRD exists"):
        errors += 1
    if errors == 0:
        pass_msg("Ready to run define")
    else:
        fail_msg("Run init first")
    return errors

def validate_design() -> int:
    errors = 0
    msg("=== Checking prerequisites for: design ===")
    if not check_active_file("spec.md", "Spec exists"):
        errors += 1
    if errors == 0:
        pass_msg("Ready to run design")
    else:
        fail_msg("Run define first to create spec")
    return errors

def validate_review_pre_build() -> int:
    errors = 0
    msg("=== Checking prerequisites for: review-pre-build ===")
    if not check_active_file("design.md", "Design exists"):
        errors += 1
    if not check_active_file("spec.md", "Spec exists"):
        errors += 1
    if not check_file(HARNESS_DIR / "BRD.md", "BRD exists"):
        errors += 1
    if errors == 0:
        pass_msg("Ready for Sr Architect review")
    else:
        fail_msg("Design and spec must exist")
    return errors

def validate_approve() -> int:
    errors = 0
    msg("=== Checking prerequisites for: approve ===")
    if not check_active_file("design.md", "Design exists"):
        errors += 1
    # Check if review-pre-build.md exists and is approved, but wait, this is only for standard loops
    # If it's a bug, it might skip review-pre-build. Let's just check if review-pre-build is approved OR if it's skipped.
    # Actually, we can check if it exists first. If it exists, it must be approved.
    rpb = find_active("review-pre-build.md")
    if rpb:
        if not check_active_file_approved("review-pre-build.md"):
            fail_msg("review-pre-build.md must be APPROVED before human approval")
            errors += 1
        else:
            pass_msg("Agent Gate 1 passed (review-pre-build)")
    if errors == 0:
        pass_msg("Ready for human review")
    return errors

def validate_tasks() -> int:
    errors = 0
    msg("=== Checking prerequisites for: tasks ===")
    if not check_active_file("design.md", "Design exists"):
        errors += 1
    if not check_active_file_approved("design.md"):
        fail_msg("Design not approved")
        errors += 1
    if not check_active_file("spec.md", "Spec exists"):
        errors += 1
    if errors == 0:
        pass_msg("Ready to create tasks")
    return errors

def validate_build() -> int:
    errors = 0
    msg("=== Checking prerequisites for: build ===")
    if not check_active_file("tasks.md", "Tasks exist"):
        errors += 1
    if not check_active_file_approved("design.md"):
        fail_msg("Design not approved")
        errors += 1
    if errors == 0:
        pass_msg("Ready to build")
    return errors

def validate_review_pre_verify() -> int:
    errors = 0
    msg("=== Checking prerequisites for: review-pre-verify ===")
    if not check_active_file_approved("design.md"):
        fail_msg("Design not approved")
        errors += 1
    if not check_active_file("spec.md", "Spec exists"):
        errors += 1
    remaining = count_incomplete_tasks()
    if remaining > 0:
        fail_msg(f"{remaining} tasks still incomplete")
        errors += 1
    if errors == 0:
        pass_msg("Ready for Sr Tech Lead review")
    return errors

def validate_verify() -> int:
    errors = 0
    msg("=== Checking prerequisites for: verify ===")
    if not check_active_file_approved("review-pre-verify.md"):
        fail_msg("review-pre-verify.md not approved (Agent Gate 2)")
        errors += 1
    remaining = count_incomplete_tasks()
    if remaining > 0:
        fail_msg(f"{remaining} tasks still incomplete")
        errors += 1
    if errors == 0:
        pass_msg("Ready to verify")
    return errors

def validate_release() -> int:
    errors = 0
    msg("=== Checking prerequisites for: release ===")
    if not check_active_file("verification.md", "Verification exists"):
        errors += 1
    release_pending = False
    for f in find_active("verification.md"):
        content = f.read_text(encoding="utf-8", errors="replace")
        if "Release Ref: PENDING" in content:
            release_pending = True
            break
    if release_pending:
        pass_msg("Verification is PENDING release approval")
    else:
        fail_msg("Verification not complete or not marked PENDING")
        errors += 1
    if errors == 0:
        pass_msg("Ready to release")
    return errors

def output_json(command: str, errors: int):
    status = "pass" if errors == 0 else "fail"
    message = "Ready to run" if errors == 0 else "Prerequisites not met"
    output = {
        "command": command,
        "status": status,
        "errors": errors,
        "message": message,
        "checks": results,
    }
    print(json.dumps(output, indent=2))

args = [a for a in sys.argv[1:] if a != "--json"]
COMMAND = args[0] if args else ""

errors = 0
match COMMAND:
    case "init": errors = validate_init()
    case "triage": errors = validate_triage()
    case "bug": errors = validate_bug()
    case "define": errors = validate_define()
    case "design": errors = validate_design()
    case "review-pre-build": errors = validate_review_pre_build()
    case "approve": errors = validate_approve()
    case "tasks": errors = validate_tasks()
    case "build": errors = validate_build()
    case "review-pre-verify": errors = validate_review_pre_verify()
    case "verify": errors = validate_verify()
    case "release": errors = validate_release()
    case _:
        msg(f"Usage: python3 {sys.argv[0]} <command> [--json]")
        sys.exit(1)

if JSON_MODE:
    output_json(COMMAND, errors)

sys.exit(0 if errors == 0 else 1)
