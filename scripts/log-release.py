#!/usr/bin/env python3
import sys
import datetime
from pathlib import Path

if len(sys.argv) < 3:
    print("Usage: python3 scripts/log-release.py <version> <summary> [harness_dir]")
    sys.exit(1)

VERSION, SUMMARY = sys.argv[1], sys.argv[2]
HARNESS_DIR = Path(sys.argv[3] if len(sys.argv) > 3 else ".harness-eng")
SLICE_LOG = HARNESS_DIR / "SLICE_LOG.md"

if not SLICE_LOG.is_file():
    print(f"Error: {SLICE_LOG} not found")
    sys.exit(1)

content = SLICE_LOG.read_text(errors='replace')
if f"Release {VERSION}" in content:
    print(f"Entry already exists for {VERSION} in SLICE_LOG")
    sys.exit(0)

date_str = datetime.date.today().isoformat()
entry = f"""## {date_str} — Release {VERSION}
**Status:** ✅ Done
**What was done:**
- {SUMMARY}

**Key decisions:**
- (none recorded)

**Build stats:**
- Version: {VERSION}

---
"""
lines = content.splitlines(keepends=True)
for i, line in enumerate(lines):
    if line.strip() == "---":
        lines.insert(i + 1, "\n" + entry)
        break
else:
    lines.append("\n" + entry)

SLICE_LOG.write_text("".join(lines))
print(f"✅ Logged release {VERSION} to SLICE_LOG.md")
