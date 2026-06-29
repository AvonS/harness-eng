# Design: F008 Backlog Cleanup & Python Standardization

## Architecture
This feature focuses on standardizing the internal scripting to Python and establishing robust end-to-end testing for the harness gates. 

## Python Migration
- `check-approved-designs.py`: Replaces the bash equivalent. Uses `Path.glob` to scan `specs/active/` and `phases/*/features/active/` for `design.md` containing `Ref: APPROVED`.
- `check-containment.py`: Validates that no code touches outside the designated project boundaries.
- `check-slice-log.py` / `check-slice-log-entry.py`: Validates the structure and presence of recent entries in `.harness-eng/SLICE_LOG.md`.
- `generate-release-notes.py`: Reads git history and `SLICE_LOG.md` to generate structured release notes.
- `log-release.py`: Handles appending release tags and timestamps to `SLICE_LOG.md`.

## E2E Testing
- `tests/e2e_workflow_test.sh`: 
  - Gate 1 Test: Mocks an unapproved design, attempts `/h:build` (via harness-check.py), approves it, attempts again (passes).
  - Gate 2 Test: Mocks completed tasks without `review-pre-verify.md`, attempts `/h:verify`, creates it, attempts again (passes).
  - Gate 3 Test: Mocks verification without `Release Ref: PENDING`, attempts `/h:release`, modifies it, attempts again (passes).

## BRD Updates
- Append a `System Events (Plugin Architecture)` section to `BRD.md`, defining lifecycle events (e.g., `pre-design`, `post-build`, `pre-verify`) that plugins will hook into.

**Ref**: PENDING
