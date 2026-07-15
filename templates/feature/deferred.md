---
name: deferred-ledger
description: >
  Deferred findings ledger. Appended to by review commands when findings
  do not satisfy the blocker predicate. Tracked alongside the feature
  through build, verify, and release.
agent_contract:
  prerequisites:
    - id: PRE-001
      action: "Confirm a feature folder exists under the active phase or specs/active."
      on_failure: "STOP: No active feature to attach deferred ledger."
  actions:
    - id: ACT-001
      action: "Append new findings with ID, Source, Finding, Rationale, Destination, Status, Resolution Evidence."
    - id: ACT-002
      action: "Assign sequential IDs: D-001, D-002, etc."
  must_do:
    - id: MUST-001
      action: "Use valid destinations: current-build, pre-verify, next-cr, backlog."
    - id: MUST-002
      action: "Use valid statuses: open, resolved, superseded, promoted-to-blocker."
    - id: MUST-003
      action: "Include resolution evidence when marking items resolved."
  must_not_do:
    - id: NEVER-001
      action: "Do not modify items already marked resolved or superseded."
    - id: NEVER-002
      action: "Do not use destinations or statuses outside the valid sets."
  outputs:
    - id: OUT-001
      path: "deferred.md appended to active feature folder"
---
<!-- *** Maintained by AvonS/harness-eng, DON'T modify this, will be overwritten during next upgrade *** -->


# Deferred Ledger: [FEATURE_NAME]

**Feature**: [FEATURE_NAME]
**Created**: [DATE]

---

## Deferred Findings

| ID | Source | Finding | Rationale | Destination | Status | Resolution Evidence |
|----|--------|---------|-----------|-------------|--------|---------------------|
| D-001 | [command] | [description] | [why deferred] | [destination] | [status] | [evidence or empty] |

---

## Destination Definitions

- **current-build**: Include in the current build as a `[DEFERRED]` task without expanding approved scope.
- **pre-verify**: Reconcile during review-pre-verify. Check whether the finding was addressed during build.
- **next-cr**: Address in the next change request or feature cycle.
- **backlog**: Parked indefinitely. No commitment to address.

## Status Definitions

- **open**: Finding is recorded and awaiting resolution at the designated destination.
- **resolved**: Finding has been addressed. Resolution evidence must be populated.
- **superseded**: Finding was overtaken by a later design decision or code change.
- **promoted-to-blocker**: Finding was re-evaluated and now satisfies the blocker predicate. Routes backward to the earliest affected command.

## Archival Instructions

When the feature is released (moved to `specs/done/` or `phases/archive/`), the deferred.md file is archived with the feature. Unresolved items carry forward as historical record. Items with status `promoted-to-blocker` must have been routed back before release.
