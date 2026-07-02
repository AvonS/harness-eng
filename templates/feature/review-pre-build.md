---
name: harness-review-pre-build
description: Template for pre-build BRD coverage check
agent_contract:
  prerequisites:
    - id: PRE-001
      action: "Confirm tasks.md, design.md, spec.md, BRD.md exist."
      on_failure: "STOP: Cannot review without prerequisite documents."
  actions:
    - id: ACT-001
      action: "Fill BRD coverage matrix, spec completeness, design alignment, and verdict."
    - id: ACT-002
      action: "Assess whether the Evidence Contract is sufficient and proportionate."
  must_do:
    - id: MUST-001
      action: "Include all 6 check categories (A-F) in report."
  must_not_do:
    - id: NEVER-001
      action: "Do not finalize without verdict (PASS/CONDITIONAL/FAIL)."
  outputs:
    - id: OUT-001
      path: "review-pre-build.md with verdict"
---
<!-- *** Maintained by AvonS/harness-eng, DON'T modify this, will be overwritten during next upgrade *** -->


# Pre-Build Review: <feature>

**Date**: <date>
**Feature**: <feature name>
**Ref**: PENDING

## BRD Coverage

| # | BRD Requirement | Spec Story | Status |
|---|-----------------|------------|--------|
| 1 | <requirement> | <story> | COVERED / MISSING |
| 2 | <requirement> | — | MISSING |

## Missing Requirements

<list any BRD requirements not covered by spec>

## Evidence Contract Review

| Risk or Requirement | Proposed Evidence | Sufficient? | Proportionate? | Required Change |
|---------------------|-------------------|-------------|----------------|-----------------|
| <item> | <evidence> | YES/NO | YES/NO | <change or none> |

Confirm both missing evidence and unnecessary test categories. Evidence scope must be settled before Human Gate 1.

## Verdict

- **PASS**: All BRD requirements covered
- **FAIL**: Missing requirements found — build blocked

## Action Required

<if FAIL: list requirements to add to spec.md>
