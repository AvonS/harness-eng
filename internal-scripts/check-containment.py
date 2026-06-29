#!/usr/bin/env python3
import os
import sys
import subprocess
from pathlib import Path

repo_root = sys.argv[1] if len(sys.argv) > 1 else None
if not repo_root:
    try:
        repo_root = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip()
    except:
        repo_root = os.getcwd()
repo_root = Path(repo_root).resolve()

RED, GREEN, NC = '\033[0;31m', '\033[0;32m', '\033[0m'
failures = 0
checked = 0

for root, dirs, files in os.walk(repo_root):
    if '.git' in root: continue
    for f in files:
        p = Path(root) / f
        if p.is_symlink():
            checked += 1
            target = p.resolve()
            if not target.exists():
                print(f"{RED}✗ BROKEN{NC}: {p} → {os.readlink(p)} (target does not exist)")
                failures += 1
            elif not str(target).startswith(str(repo_root)):
                print(f"{RED}✗ EXTERNAL{NC}: {p} → {os.readlink(p)} (resolves to: {target})")
                failures += 1

if failures > 0:
    print(f"\n{RED}FAIL{NC}: {failures} of {checked} symlink(s) resolve outside the repository.")
    sys.exit(1)
else:
    print(f"{GREEN}PASS{NC}: All {checked} symlink(s) resolve within {repo_root}")
    sys.exit(0)
