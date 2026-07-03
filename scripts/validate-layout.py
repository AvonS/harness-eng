#!/usr/bin/env python3
import argparse
from pathlib import Path
from harness_layout import load_manifest, validate_layout


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("project", nargs="?", default=".")
    parser.add_argument("--manifest", default=".harness-eng/templates/init-layout.json")
    args = parser.parse_args()
    errors = validate_layout(Path(args.project), load_manifest(Path(args.manifest)))
    for error in errors:
        print(error)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
