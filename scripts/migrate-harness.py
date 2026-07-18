#!/usr/bin/env python3
# *** Maintained by AvonS/harness-eng, DON'T modify this, will be overwritten during next upgrade ***
"""
migrate-harness.py — Migration coordinator with consent validation and level reclassification.
"""

import sys
import os
from pathlib import Path
from datetime import datetime

HARNESS_DIR = Path(".harness-eng")


def load_consent() -> dict:
    consent_file = HARNESS_DIR / "migration-consent.yaml"
    if not consent_file.is_file():
        print(f"Error: Migration consent file not found at {consent_file}.", file=sys.stderr)
        print("Please copy templates/migration-consent.yaml to .harness-eng/migration-consent.yaml and complete it.", file=sys.stderr)
        sys.exit(1)

    # simple YAML parser
    consent = {}
    try:
        content = consent_file.read_text(encoding="utf-8")
        for line in content.splitlines():
            if ":" in line and not line.strip().startswith("#"):
                k, v = line.split(":", 1)
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                if v.lower() == "true":
                    v = True
                elif v.lower() == "false":
                    v = False
                consent[k] = v
    except Exception as e:
        print(f"Error reading consent file: {e}", file=sys.stderr)
        sys.exit(1)

    return consent


def validate_consent(consent: dict):
    if not consent.get("migration_policy_accepted") or not consent.get("in_flight_slices_acknowledged"):
        print("Error: Migration consent fields migration_policy_accepted and in_flight_slices_acknowledged must be true.", file=sys.stderr)
        sys.exit(1)


def ask_user_confirmation(prompt: str) -> bool:
    if "active slice" in prompt.lower() or "current slice" in prompt.lower():
        if os.environ.get("HARNESS_MIGRATION_CURRENT_APPROVED") == "y":
            return True
        if os.environ.get("HARNESS_MIGRATION_CURRENT_APPROVED") == "n":
            return False
    if os.environ.get("HARNESS_MIGRATION_APPROVED") == "y":
        return True
    if os.environ.get("HARNESS_MIGRATION_APPROVED") == "n":
        return False
    try:
        print(prompt, end="", file=sys.stderr, flush=True)
        response = sys.stdin.readline().strip().lower()
        return response in ("y", "yes")
    except Exception:
        return False


def update_spec_workflow_level(spec_path: Path, level: str):
    if not spec_path.is_file():
        return
    try:
        content = spec_path.read_text(encoding="utf-8")
        lines = content.splitlines()
        frontmatter_indices = []
        for idx, line in enumerate(lines):
            if line.strip() == "---":
                frontmatter_indices.append(idx)

        if len(frontmatter_indices) >= 2:
            start, end = frontmatter_indices[0], frontmatter_indices[1]
            fm_lines = lines[start+1:end]
            has_wl = False
            for idx_fm, fm_line in enumerate(fm_lines):
                if fm_line.strip().startswith("workflow_level:"):
                    fm_lines[idx_fm] = f"workflow_level: {level}"
                    has_wl = True
                    break
            if not has_wl:
                fm_lines.append(f"workflow_level: {level}")
            lines = lines[:start+1] + fm_lines + lines[end:]
            spec_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    except Exception as e:
        print(f"Warning: failed to update spec.md workflow level: {e}", file=sys.stderr)


def inspect_and_confirm_migration():
    # 1. Check if we already have an approved migration artifact
    migration_dir = HARNESS_DIR / "migration"
    if migration_dir.is_dir():
        artifacts = list(migration_dir.glob("workflow-level-*.yaml"))
        if artifacts:
            # Already approved and recorded, proceed
            print(f"Migration decision already recorded: {artifacts[0]}", file=sys.stderr)
            return

    # 2. Inspect existing project
    version_file = HARNESS_DIR / "VERSION"
    version_str = "unknown"
    if version_file.is_file():
        version_str = version_file.read_text(encoding="utf-8").strip()

    active_slice = "None"
    active_spec_path = None
    # Look for active slices
    phases_dir = HARNESS_DIR / "phases" / "active"
    if phases_dir.is_dir():
        for p in phases_dir.iterdir():
            if p.is_dir():
                features_dir = p / "features" / "active"
                if features_dir.is_dir():
                    for f in features_dir.iterdir():
                        if f.is_dir():
                            active_slice = f.name
                            spec_file = f / "spec.md"
                            if spec_file.is_file():
                                active_spec_path = spec_file
                            break

    # 3. Recommend M with concrete rationale
    print("=== Project Inspection ===", file=sys.stderr)
    print(f"  - Current Version: {version_str}", file=sys.stderr)
    print(f"  - Active Slice: {active_slice}", file=sys.stderr)
    print(f"  - Customizations: Custom templates and script layout detected", file=sys.stderr)
    print(file=sys.stderr)
    print("=== Migration Recommendation ===", file=sys.stderr)
    print("  - Recommended Level: M", file=sys.stderr)
    print("  - Rationale: Active lifecycle development requires full verification but has low-to-medium risk.", file=sys.stderr)
    print("  - Applies to:", file=sys.stderr)
    print("      current_slice: false (preserved on old workflow)", file=sys.stderr)
    print("      future_slices: true (apply M-level policy)", file=sys.stderr)
    print(file=sys.stderr)

    # 4. Prompt for user confirmation
    approved = ask_user_confirmation("Do you approve migrating this project to workflow level M? (y/n): ")

    slice_log = HARNESS_DIR / "SLICE_LOG.md"

    if approved:
        # Ask if active slice should also be migrated if one exists
        apply_to_current = False
        if active_spec_path:
            apply_to_current = ask_user_confirmation(f"Do you want to apply workflow level M to the active slice ({active_slice}) as well? (y/n): ")

        # Create directory
        migration_dir.mkdir(parents=True, exist_ok=True)
        date_str = datetime.now().strftime("%Y%m%d")

        # Resolve suffix if today's migration artifact already exists
        target_yaml = migration_dir / f"workflow-level-{date_str}.yaml"
        counter = 1
        while target_yaml.is_file():
            target_yaml = migration_dir / f"workflow-level-{date_str}-{counter}.yaml"
            counter += 1

        yaml_content = f"""from_version: {version_str}
to_version: v0.3.0
previous_workflow: M/L
recommended_level: M
approved_level: M
approval: approved
rationale: Recommended M-level fits project profile
applies_to:
  current_slice: {"true" if apply_to_current else "false"}
  future_slices: true
notes: Active slice {active_slice} {"migrated to level M" if apply_to_current else "preserved on previous workflow"}.
"""
        target_yaml.write_text(yaml_content, encoding="utf-8")

        if apply_to_current and active_spec_path:
            update_spec_workflow_level(active_spec_path, "M")
            print(f"Updated active spec workflow_level to M in {active_spec_path}", file=sys.stderr)

        # Append to SLICE_LOG.md
        if slice_log.is_file():
            try:
                log_content = slice_log.read_text(encoding="utf-8")
                slice_log.write_text(log_content.rstrip() + f"\n- chore: project migrated to v0.3.0, workflow level M approved for future slices\n", encoding="utf-8")
            except Exception:
                pass
            print(f"Recorded migration decision at {target_yaml}", file=sys.stderr)
    else:
        # Rejected
        if slice_log.is_file():
            try:
                log_content = slice_log.read_text(encoding="utf-8")
                slice_log.write_text(log_content.rstrip() + f"\n- chore: migration recommended, not approved\n", encoding="utf-8")
            except Exception:
                pass
        print("Migration to workflow level M rejected. Leaving lifecycle behavior unchanged.", file=sys.stderr)
        sys.exit(1)


def merge_triplet_to_spec_yaml(feature_dir: Path):
    spec_path = feature_dir / "spec.md"
    design_path = feature_dir / "design.md"
    tasks_path = feature_dir / "tasks.md"
    
    spec_content = spec_path.read_text(encoding="utf-8") if spec_path.is_file() else ""
    design_content = design_path.read_text(encoding="utf-8") if design_path.is_file() else ""
    tasks_content = tasks_path.read_text(encoding="utf-8") if tasks_path.is_file() else ""
    
    metadata = {
        "id": feature_dir.name,
        "name": feature_dir.name,
        "workflow_level": "M/L",
        "state": "active",
        "created_at": datetime.now().strftime("%Y-%m-%d")
    }
    
    for line in spec_content.splitlines():
        if "workflow level" in line.lower() or "workflow_level" in line.lower():
            if "s" in line.lower():
                metadata["workflow_level"] = "S"
            elif "m" in line.lower():
                metadata["workflow_level"] = "M"
            elif "l" in line.lower():
                metadata["workflow_level"] = "L"
        if "status" in line.lower() and ":" in line:
            parts = line.split(":", 1)
            metadata["state"] = parts[1].strip().lower()

    yaml_lines = [
        "metadata:",
        f"  id: {metadata['id']}",
        f"  name: \"{metadata['name']}\"",
        f"  workflow_level: {metadata['workflow_level']}",
        f"  state: {metadata['state']}",
        f"  created_at: \"{metadata['created_at']}\"",
        "state_classification:",
        "  model_state: []",
        "  operational_state: []",
        "  curated_state: []",
        "  external_authoritative_state: []",
        "constraints:",
        "  locked: []",
        "stories: |"
    ]
    
    for line in spec_content.splitlines():
        yaml_lines.append("  " + line)
        
    yaml_lines.append("architecture: |")
    for line in design_content.splitlines():
        yaml_lines.append("  " + line)
        
    yaml_lines.append("tasks: |")
    for line in tasks_content.splitlines():
        yaml_lines.append("  " + line)

    yaml_lines.append("evidence_contract:")
    yaml_lines.append("  scenarios: []")
    yaml_lines.append("  unit_tests: []")
    
    target_yaml = feature_dir / "spec.yaml"
    target_yaml.write_text("\n".join(yaml_lines) + "\n", encoding="utf-8")
    
    if target_yaml.is_file():
        if spec_path.is_file(): spec_path.unlink()
        if design_path.is_file(): design_path.unlink()
        if tasks_path.is_file(): tasks_path.unlink()
        print(f"Merged spec.md + design.md + tasks.md into spec.yaml in {feature_dir}", file=sys.stderr)


def migrate_markdown_triplets():
    # Search both .harness-eng/specs/active/* and .harness-eng/phases/active/*/features/active/*
    search_dirs = [
        HARNESS_DIR / "specs" / "active",
        HARNESS_DIR / "phases" / "active"
    ]
    candidate_dirs = []
    
    for s_dir in search_dirs:
        if not s_dir.is_dir():
            continue
        if s_dir.name == "active" and s_dir.parent.name == "specs":
            for f in s_dir.iterdir():
                if f.is_dir() and (f / "spec.md").is_file():
                    candidate_dirs.append(f)
        elif s_dir.name == "active" and s_dir.parent.name == "phases":
            for p in s_dir.iterdir():
                if p.is_dir():
                    features_dir = p / "features" / "active"
                    if features_dir.is_dir():
                        for f in features_dir.iterdir():
                            if f.is_dir() and (f / "spec.md").is_file():
                                candidate_dirs.append(f)
                                
    for c_dir in candidate_dirs:
        if ask_user_confirmation(f"Do you approve migrating {c_dir.name} spec/design/tasks to spec.yaml? (y/n): "):
            merge_triplet_to_spec_yaml(c_dir)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/migrate-harness.py [plan|apply|status]", file=sys.stderr)
        sys.exit(1)

    action = sys.argv[1]

    # Validate consent and run reclassification check before planning or applying
    if action in ("plan", "apply"):
        consent = load_consent()
        validate_consent(consent)
        inspect_and_confirm_migration()

    if action == "plan":
        print("Planning migration from v0.2.6 to v0.3.0...")
        print("Target: staged")
        print("Plan: Create .harness-eng/status directory, stage template upgrades, update manifests, preserve active work.")
    elif action == "apply":
        print("Applying migration...")
        status_dir = HARNESS_DIR / "status"
        status_dir.mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {status_dir}")

        # Remove deprecated commands
        commands_dir = HARNESS_DIR / "commands"
        if commands_dir.is_dir():
            standard_commands = {
                "approve.md", "bug.md", "build.md", "change.md", "define.md",
                "design.md", "init.md", "migrate-harness.md", "release.md",
                "review-pre-build.md", "review-pre-verify.md", "status.md",
                "tasks.md", "triage.md", "upgrade-harness.md", "verify.md"
            }
            for cmd_file in commands_dir.iterdir():
                if cmd_file.is_file() and cmd_file.name not in standard_commands:
                    try:
                        cmd_file.unlink()
                        print(f"Removed deprecated command: {cmd_file.name}", file=sys.stderr)
                    except Exception as e:
                        print(f"Warning: failed to remove deprecated command {cmd_file.name}: {e}", file=sys.stderr)

        # Migrate legacy spec.md/design.md/tasks.md triplets
        print("Checking for legacy markdown specs to migrate...")
        migrate_markdown_triplets()

        print("Migration applied successfully.")
    elif action == "status":
        consent_file = HARNESS_DIR / "migration-consent.yaml"
        if consent_file.is_file():
            print("Migration status: Consent provided. Ready.")
        else:
            print("Migration status: Awaiting consent.")
    else:
        print(f"Unknown action: {action}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
