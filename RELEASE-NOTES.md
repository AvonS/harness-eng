# Release v0.1.0 — Phase 1 Gap Closure

**Date**: 2026-07-02
**Status**: Release Candidate
**Version**: v0.1.0

## What's New

- **Canonical Reconciliation**: Phase 1 reconciles the documented workflow with the current repository shape, including logical-role terminology, dynamic inventory checks, and dogfood script separation.
- **Deterministic Skill Selection**: `/h:init` and `/h:upgrade-harness` now have a real skill-selection CLI, preview selected skills, record install baselines, and preserve locally modified skills without blocking upstream updates to unchanged ones.
- **Bounded Failure Contract**: `harness-check.py` now counts failed command attempts, creates scoped `BLOCKED.md` files on the third failure, and clears the scoped failure state after recovery.
- **BDD Traceability Enforcement**: scenario IDs, task linkage, and evidence checks are now enforced programmatically during `review-pre-verify` and `verify`.
- **Project Sensor Contract**: `technology.yaml` defines repo-owned sensors, and required hooks now fail closed on command failure, timeout, missing command, or missing required sensor configuration.
- **Isolated Integration Tests**: both `tests/e2e_workflow_test.sh` and `tests/test_sanity_discovery.py` now run in temporary project roots instead of mutating live harness state.
- **Proportionate Evidence Contracts**: design approval now fixes the minimum convincing evidence for each change. TDD, BDD, integration, UI, and other test techniques are selected by behavior, risk, and reversibility instead of being universally required.

## Key Decisions

- Used install-log digests to distinguish unchanged installed skills from project-modified skills.
- Kept traceability and sensor enforcement in the gate layer so missing evidence or missing required sensors stop the workflow mechanically.
- Preserved the file-edition boundary by keeping optional Pi-harness capabilities out of the Phase 1 implementation.
- Made evidence scope a Gate 1 decision so pre-verify can enforce agreed proof without repeatedly inventing new test categories. Only defects, design gaps, or newly exposed security/scope assumptions may expand it.

## Verification Snapshot

- Product implementation commit: `e640db6`
- Full Python suite: `python3 -m unittest discover -v tests`
- Happy-path sanity: `bash scripts/sanity-check.sh`
- Workflow E2E: `bash tests/e2e_workflow_test.sh`

## Release Gate

- Pending Human Gate 2 through `/h:release`
