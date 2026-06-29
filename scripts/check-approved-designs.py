#!/usr/bin/env python3
import sys
from pathlib import Path

HARNESS_DIR = Path(sys.argv[1] if len(sys.argv) > 1 else ".harness-eng")
approved_count = 0

GREEN, RED, NC = '\033[0;32m', '\033[0;31m', '\033[0m'

def check_file(p):
    global approved_count
    if "Ref: APPROVED" in p.read_text(errors='replace'):
        print(f"{GREEN}✅ APPROVED{NC}: {p}")
        approved_count += 1

for p in HARNESS_DIR.glob("phases/*/features/active/*/design.md"): check_file(p)
for p in HARNESS_DIR.glob("phase-*/features/active/*/design.md"): check_file(p)
for p in HARNESS_DIR.glob("specs/active/*/design.md"): check_file(p)

print()
if approved_count > 0:
    print(f"{GREEN}✅ Found {approved_count} approved design(s) — build can proceed{NC}")
    sys.exit(0)
else:
    print(f"{RED}❌ No approved designs found — build cannot proceed{NC}")
    print("   Run /h:approve to approve design(s) first")
    sys.exit(1)
