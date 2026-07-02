# Release Notes

## v0.2.0 - Phase 2 Versioned Migration

**Date**: 2026-07-02
**Status**: Unreleased

### Changes

- Introduced `Foundry` lineage identity model via `manifest.json`.
- Implemented a file-based versioned migration engine (`migrate-harness.py`) with Backup Manager and Migration Lock to ensure state safety during upgrades.
- Refactored legacy detection into a simplified catch-all for pre-Foundry projects.
- Updated `upgrade-harness.md` to properly orchestrate pre-upgrade staging, migrations, and canonical file replacement.
- Updated `init.md` to establish the new identity structure automatically on bootstrap.
- Added Testing Level prompts and design template integrations for scaled verification.
## v0.1.2 - Project Release Policies

**Date**: 2026-07-02
**Status**: Released

### Changes

- Added a project-specific `release_policy` to the canonical constitution template.
- Added `local_merge` and `pull_request` release strategies.
- Preserved explicit Human Gate 2 approval for both strategies.
- Required publication checks for the target branch and release tag.
- Corrected release-gate parsing for canonical `**Release Ref**: PENDING` fields.
- Added regression coverage for release policy consumption and release-reference parsing.

## v0.1.1 - Phase 1 Gap Closure

**Date**: 2026-07-02
**Status**: Released

### Changes

- Reconciled canonical inventory and logical role documentation.
- Added deterministic skill selection with preservation of project-owned edits.
- Added bounded failure tracking and scoped `BLOCKED.md` recovery.
- Added material-scenario traceability through tasks, review, and verification.
- Added fail-closed project sensor execution.
- Replaced universal TDD/BDD mandates with proportionate Evidence Contracts fixed at Gate 1.
- Isolated product E2E tests from live dogfood state.

## v0.0.1 - Phase 0 Foundation

**Date**: 2026-06-30
**Status**: Released

### Changes

- Established canonical workflow commands, templates, agent roles, gates, scripts, hooks, and documentation.
