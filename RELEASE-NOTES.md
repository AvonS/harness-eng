# Release Notes

## v0.2.6 - Blocker-Only Workflow Loopbacks

**Date**: 2026-07-15
**Status**: Released

### Changes

- Added deferred ledger template (`deferred.md`) with table schema, destinations, statuses, and archival instructions.
- Updated design template with Primary Functional Flow section and S/M/L evidence matrix.
- Updated spec template with Testing Level field and Functional Evidence section.
- Updated triage, design, define, review-pre-build, tasks, build, review-pre-verify, verify, and release commands for blocker/deferred classification and S/M/L evidence policy.
- Updated sr-architect, sr-tech-lead, gatekeeper, and developer agents with blocker predicate and deferred reconciliation constraints.
- Updated `harness-status.py` to scan and display deferred item counts.
- Added 8 new E2E tests covering editorial amendment, blocker loopback, deferred at release, promotion, and S/M/L level policy.
- Updated AGENTS.md routing rules and gate descriptions for the blocker/deferred model.

---

## v0.2.5 - Canonical Delegation and Phase Layout

**Date**: 2026-07-03
**Status**: Released

### Changes

- Added bounded, path-based delegation contracts to every subagent command.
- Added progressive skill evidence to both independent review gates.
- Standardized phase state under `phases/active` and `phases/archive` with self-contained feature folders.
- Added schema-3 migration from the legacy nested feature lifecycle layout.
- Added a canonical init-layout manifest, validation, and S-level real-runtime smoke policy.

## v0.2.4 - Initialization Scope Enforcement

**Date**: 2026-07-03
**Status**: Released

### Changes

- **Fix**: Bound `/h:init` clarification answers to bootstrap context and prohibited automatic implementation.
- **Feature**: Added deterministic initialization write-boundary validation and state-based Manager routing.
- **Fix**: Made `/h:health` lifecycle-aware and aligned sanity skill checks with progressive external skill installation.

## v0.2.3 - Ponytail UI Design & Migration Fixes

**Date**: 2026-07-03
**Status**: Released

### Changes

- **Feature**: Enforced UI design patterns from `design-registry.yaml` into the design template and review gates to mandate the Ponytail YAGNI Framework (CR-304).
- **Feature**: Added explicit `SLICE_LOG` appending and post-upgrade health check validation to the `/h:upgrade-harness` workflow.
- **Fix**: Resolved `UnboundLocalError` in `version-check.py` and corrected `catalog.json` path resolution in `migrate-harness.py`.
- **Fix**: Added explicit bootstrap instruction for the migration engine in `upgrade-harness.md` for legacy (v0.0.x) upgrades.

## v0.2.2 - Post-Phase 2 Hotfixes

**Date**: 2026-07-02
**Status**: Released

### Changes

- **Fix**: Corrected `ROOT` path resolution in `sanity-check.sh` to prevent `HARNESS_DIR` from resolving to `.harness-eng/.harness-eng` in managed projects.
- **Fix**: Added `VERSION` to the `fetch_and_replace_from_canonical` block in `upgrade-harness.md` so managed projects sync their framework version correctly.
- **Feature**: Added `shadcn-svelte` and `web.dev-patterns` to `design-registry.yaml` to support Svelte/Tailwind architectures and Chrome Developers best practices.
- **Feature**: Split `design-registry.yaml` into a canonical template and local project overrides to resolve confusion and merge collisions.


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
