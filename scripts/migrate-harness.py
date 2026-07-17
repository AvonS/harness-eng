#!/usr/bin/env python3
# *** Maintained by AvonS/harness-eng, DON'T modify this, will be overwritten during next upgrade ***
"""
migrate-harness.py — Migration coordinator with consent validation.
"""

import sys
import os
from pathlib import Path

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


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/migrate-harness.py [plan|apply|status]", file=sys.stderr)
        sys.exit(1)

    action = sys.argv[1]

    # Validate consent before planning or applying
    if action in ("plan", "apply"):
        consent = load_consent()
        validate_consent(consent)

    if action == "plan":
        print("Planning migration from v0.2.6 to v0.3.0...")
        print("Target: staged")
        print("Plan: Create .harness-eng/status directory, stage template upgrades, update manifests.")
    elif action == "apply":
        print("Applying migration...")
        status_dir = HARNESS_DIR / "status"
        status_dir.mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {status_dir}")
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
