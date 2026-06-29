#!/usr/bin/env python3
import sys
import re
import datetime
from pathlib import Path

HARNESS_DIR = Path(sys.argv[1] if len(sys.argv) > 1 else ".harness-eng")
MAX_AGE_DAYS = int(sys.argv[2]) if len(sys.argv) > 2 else 7
SLICE_LOG = HARNESS_DIR / "SLICE_LOG.md"

GREEN, YELLOW, RED, NC = '\033[0;32m', '\033[1;33m', '\033[0;31m', '\033[0m'

if not SLICE_LOG.is_file():
    print(f"{RED}❌ FAIL{NC}: {SLICE_LOG} not found")
    sys.exit(1)

print(f"{GREEN}✅ PASS{NC}: {SLICE_LOG} exists")
lines = SLICE_LOG.read_text(errors='replace').splitlines()
entries = [l for l in lines if l.startswith("## ")]
if not entries:
    print(f"{YELLOW}⚠️  WARN{NC}: No entries in SLICE_LOG")
    sys.exit(0)

print(f"{GREEN}✅ PASS{NC}: {len(entries)} entries found")
date_match = re.search(r"## (\d{4}-\d{2}-\d{2})", entries[0])
if not date_match:
    print(f"{YELLOW}⚠️  WARN{NC}: No date found in SLICE_LOG")
    sys.exit(0)

last_date = datetime.datetime.strptime(date_match.group(1), "%Y-%m-%d")
age_days = (datetime.datetime.now() - last_date).days

if age_days <= MAX_AGE_DAYS:
    print(f"{GREEN}✅ PASS{NC}: Last entry {age_days} days ago (within {MAX_AGE_DAYS} day limit)")
else:
    print(f"{YELLOW}⚠️  WARN{NC}: Last entry {age_days} days ago (exceeds {MAX_AGE_DAYS} day limit)")
    print("  Consider updating SLICE_LOG with recent progress")
