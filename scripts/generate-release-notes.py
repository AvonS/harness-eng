#!/usr/bin/env python3
# *** Maintained by AvonS/harness-eng, DON'T modify this, will be overwritten during next upgrade ***
import sys
import re
import datetime
import os
from pathlib import Path

HARNESS_DIR = Path(sys.argv[1] if len(sys.argv) > 1 else ".harness-eng")
SLICE_LOG = HARNESS_DIR / "SLICE_LOG.md"
OUTPUT = Path("RELEASE-NOTES.md")

if not SLICE_LOG.is_file():
    tag = os.environ.get("GITHUB_REF", "").replace("refs/tags/", "")
    print(f"Warning: {SLICE_LOG} not found — generating minimal release notes")
    OUTPUT.write_text(f"# Release {tag}\n\n**Date**: {datetime.date.today()}\n\n## What's New\n\nSee [CHANGELOG](CHANGELOG.md) for full details.\n")
    print(f"Release notes written to {OUTPUT}")
    sys.exit(0)

content = SLICE_LOG.read_text(errors='replace')
blocks = re.split(r'^## ', content, flags=re.MULTILINE)[1:]
if not blocks:
    print(f"Error: No entries found in {SLICE_LOG}")
    sys.exit(1)

latest = blocks[0]
lines = latest.splitlines()
title = lines[0].split(" — ")[-1] if " — " in lines[0] else lines[0]
date_match = re.search(r'(\d{4}-\d{2}-\d{2})', lines[0])
date = date_match.group(1) if date_match else "Unknown"

status, what_done, decisions = "", [], []
mode = None
for line in lines[1:]:
    if line.startswith("**Status:**"): status = line.replace("**Status:**", "").strip()
    elif line.startswith("**What was done:**"): mode = "what"
    elif line.startswith("**Key decisions:**"): mode = "decisions"
    elif line.startswith("**"): mode = None
    elif line.strip() and mode == "what": what_done.append(line.lstrip("- "))
    elif line.strip() and mode == "decisions": decisions.append(line.lstrip("- "))

out = f"# {title}\n\n**Date**: {date}\n**Status**: {status}\n\n## What's New\n\n"
out += "\n".join(f"- {item}" for item in what_done) + "\n\n## Key Decisions\n\n"
out += "\n".join(f"- {item}" for item in decisions) + "\n\n## Changes\n\nSee [CHANGELOG](CHANGELOG.md) for full details.\n"

OUTPUT.write_text(out)
print(f"Release notes written to {OUTPUT}")
