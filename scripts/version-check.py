#!/usr/bin/env python3
"""
version-check.py — Check for new harness-eng versions.

Usage: python3 scripts/version-check.py [repo] [harness_dir]

Default: python3 scripts/version-check.py AvonS/harness-eng .harness-eng

Checks GitHub releases for latest version, caches for 24 hours,
compares with local version, outputs result.
"""

import os
import re
import subprocess
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

REPO = sys.argv[1] if len(sys.argv) > 1 else "AvonS/harness-eng"
HARNESS_DIR = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(".harness-eng")
CACHE_FILE = HARNESS_DIR / ".version-cache"
VERSION_FILE = HARNESS_DIR / "VERSION"
CACHE_TTL = 86400  # 24 hours in seconds

GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
RED = "\033[0;31m"
CYAN = "\033[0;36m"
NC = "\033[0m"


def get_local_version() -> str:
    """Read local version from VERSION file or git tag."""
    if VERSION_FILE.is_file():
        return VERSION_FILE.read_text(encoding="utf-8").strip()
    try:
        result = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return "unknown"


def get_cached_version() -> Optional[str]:
    """Read cached version if still within TTL and VERSION hasn't been updated."""
    if not CACHE_FILE.is_file():
        return None

    lines = CACHE_FILE.read_text(encoding="utf-8").strip().splitlines()
    if len(lines) < 2:
        return None

    cached_date_str = lines[0].strip()
    cached_version = lines[1].strip()

    try:
        cached_date = datetime.fromisoformat(cached_date_str)
        now = datetime.now(timezone.utc)
        age = (now - cached_date).total_seconds()

        # Invalidate if VERSION file modified after cache
        if VERSION_FILE.is_file():
            version_mtime = os.path.getmtime(VERSION_FILE)
            version_mod_time = datetime.fromtimestamp(version_mtime, tz=timezone.utc)
            if version_mod_time > cached_date:
                return None

        if age < CACHE_TTL:
            return cached_version
    except (ValueError, OSError):
        return None

    return None


def fetch_latest_version() -> Optional[str]:
    """Fetch latest version from GitHub releases."""
    latest_version: Optional[str] = None

    # Try GitHub CLI first
    try:
        result = subprocess.run(
            [
                "gh", "release", "list",
                "--repo", REPO,
                "--limit", "1",
                "--json", "tagName",
                "--jq", ".[0].tagName",
            ],
            capture_output=True,
            text=True,
            timeout=15,
        )
        if result.returncode == 0 and result.stdout.strip():
            latest_version = result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # Fallback: GitHub API via HTTP
    if not latest_version:
        api_url = f"https://api.github.com/repos/{REPO}/releases/latest"
        try:
            req = urllib.request.Request(
                api_url,
                headers={"User-Agent": "harness-eng/version-check", "Accept": "application/vnd.github.v3+json"},
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                import json
                data = json.loads(resp.read().decode("utf-8"))
                latest_version = data.get("tag_name", "")
        except (urllib.error.URLError, json.JSONDecodeError, OSError):
            pass

    # Fallback: scrape HTML releases page
    if not latest_version:
        releases_url = f"https://github.com/{REPO}/releases"
        try:
            req = urllib.request.Request(
                releases_url,
                headers={"User-Agent": "harness-eng/version-check"},
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                html = resp.read().decode("utf-8", errors="replace")
                match = re.search(r'/releases/tag/(v[0-9]+\.[0-9]+\.[0-9]+)', html)
                if match:
                    latest_version = match.group(1)
        except (urllib.error.URLError, OSError):
            pass

    # Update cache if we got a version
    if latest_version:
        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        CACHE_FILE.write_text(f"{now_str}\n{latest_version}\n", encoding="utf-8")
        return latest_version

    return None


def compare_versions(current: str, latest: str) -> str:
    """Compare two semver strings. Returns UP-TO-DATE, PATCH, MINOR, MAJOR, or UNKNOWN."""
    def parse(v: str) -> Optional[tuple]:
        v = v.lstrip("v")
        parts = v.split(".")
        try:
            return tuple(int(p) for p in parts)
        except ValueError:
            return None

    curr = parse(current)
    lat = parse(latest)

    # If either version is not valid semver, we can't compare
    if curr is None or lat is None:
        return "UNKNOWN"

    if lat[0] > curr[0]:
        return "MAJOR"
    if lat[0] < curr[0]:
        return "UP-TO-DATE"
    if lat[1] > curr[1]:
        return "MINOR"
    if lat[1] < curr[1]:
        return "UP-TO-DATE"
    if lat[2] > curr[2]:
        return "PATCH"
    return "UP-TO-DATE"


def main():
    local_version = get_local_version()

    # Dogfood mode: if this script is running inside the canonical source repo,
    # it will find AGENTS.md and templates/ at the repository root.
    # Skip remote comparison — we are the upstream, not a downstream consumer.
    repo_root = Path(__file__).resolve().parent.parent
    if (repo_root / "AGENTS.md").is_file() and (repo_root / "templates").is_dir():
        print(f"{GREEN}✅ VERSION_CHECK:DOGFOOD{NC} — {local_version} (canonical source repo)")
        sys.exit(0)

    # Try cache first
    latest_version = get_cached_version()

    # Fetch if cache miss
    if not latest_version:
        latest_version = fetch_latest_version()

    # Handle fetch failure
    if not latest_version:
        print(f"{YELLOW}⚠️  VERSION_CHECK:UNAVAILABLE{NC} — Could not fetch latest version")
        print(f"   Using local version: {local_version}")
        sys.exit(0)

    # Compare versions
    comparison = compare_versions(local_version, latest_version)

    if comparison == "UP-TO-DATE":
        print(f"{GREEN}✅ VERSION_CHECK:UP-TO-DATE{NC} — {local_version}")
    elif comparison == "UNKNOWN":
        print(f"{YELLOW}⚠️  VERSION_CHECK:UNKNOWN{NC} — Local version '{local_version}' is not valid semver")
        print(f"   Latest version: {latest_version}")
        print(f"   Run upgrade to fix: Read the harness rules from https://github.com/{REPO} and upgrade")
    else:
        release_url = f"https://github.com/{REPO}/releases/tag/{latest_version}"
        print(
            f"{YELLOW}⚠️  VERSION_CHECK:BEHIND{NC} — "
            f"New version of harness-eng ({REPO}) available: {latest_version} (current: {local_version})"
        )
        print(f"   Release notes: {release_url}")
        print(
            f"   Run: Read the harness rules from https://github.com/{REPO} "
            f"and upgrade this project's .harness-eng to the latest version."
        )


if __name__ == "__main__":
    main()
