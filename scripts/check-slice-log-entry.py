#!/usr/bin/env python3
import sys
from pathlib import Path

if len(sys.argv) < 2:
    print("Usage: python3 scripts/check-slice-log-entry.py <step> [harness_dir]")
    sys.exit(1)

STEP = sys.argv[1]
HARNESS_DIR = Path(sys.argv[2] if len(sys.argv) > 2 else ".harness-eng")
SLICE_LOG = HARNESS_DIR / "SLICE_LOG.md"
GREEN, RED, NC = '\033[0;32m', '\033[0;31m', '\033[0m'

if not SLICE_LOG.is_file():
    print(f"{RED}❌ FAIL{NC}: {SLICE_LOG} not found")
    sys.exit(1)

if STEP.lower() in SLICE_LOG.read_text(errors='replace').lower():
    print(f"{GREEN}✅ PASS{NC}: SLICE_LOG has entry for: {STEP}")
    sys.exit(0)
else:
    print(f"{RED}❌ FAIL{NC}: SLICE_LOG missing entry for: {STEP}")
    print("   Run the previous step first to create an entry")
    sys.exit(1)
