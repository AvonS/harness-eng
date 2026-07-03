#!/usr/bin/env python3
"""Validate execution classification and delegation fields."""
import sys
from pathlib import Path

FIELDS = ("capability", "outcome", "read_paths", "write_authority", "return_format", "max_response", "context_policy", "on_failure")

def validate(root: Path) -> list[str]:
    errors = []
    for path in sorted(root.glob("*.md")):
        text = path.read_text()
        enabled = "\nsubagent: true\n" in text
        if not enabled and "\nsubagent: false\n" not in text:
            errors.append(f"{path.name}: missing subagent classification")
        if enabled:
            block = text.split("\ndelegation:\n", 1)[1].split("\n\n", 1)[0] if "\ndelegation:\n" in text else ""
            for field in FIELDS:
                if f"  {field}:" not in block:
                    errors.append(f"{path.name}: missing delegation.{field}")
            if "inline complete files" not in block:
                errors.append(f"{path.name}: inline-file prohibition missing")
    return errors

if __name__ == "__main__":
    failures = validate(Path(sys.argv[1] if len(sys.argv) > 1 else "commands"))
    print("\n".join(failures))
    raise SystemExit(bool(failures))
