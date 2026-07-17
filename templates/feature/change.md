---
name: change
description: >
  Unified Change Record template for bugs and CRs.
  Created during /h:change workflow.
agent_contract:
  prerequisites:
    - id: PRE-001
      action: "Identify whether change is bug or CR."
  outputs:
    - id: OUT-001
      path: "CHG-NNN.md change record"
---
<!-- *** Maintained by AvonS/harness-eng, DON'T modify this, will be overwritten during next upgrade *** -->

# Change Record: CHG-[NNN]

**ID**: CHG-[NNN]
**Type**: [bug|CR]
**Status**: [active|verification-pending|resolved|archived|blocked]
**Created**: [YYYY-MM-DD]
**Ref**: [APPROVED|PENDING]

---

## Baseline
- **Revision**: [baseline_git_commit_hash]
- **Dirty worktree**:
  - [path]
- **Observed behavior**: [What is currently happening]
- **Reproduction / Current behavior**: [Steps to reproduce or current state]
- **Affected flow / boundary**: [e.g., database-auth]

---

## Request
- **Expected behavior**: [What should happen]
- **Desired delta**: [For CRs: the requested enhancement]

---

## Analysis & Decisions
- **Root cause**: [For bugs: analysis of root cause]
- **Affected boundaries**:
  - [boundary]
- **Risk level**: [S|M|L]
- **Technical Decisions**:
  - id: DEC-[NNN]
    decision: [decision_text]
    rationale: [rationale_text]
- **Assumptions**:
  - [assumption_text]
- **Relevant prior decisions**:
  - id: DEC-[XYZ]
    ref: [path_or_link_to_past_slice_spec_or_design]

---

## Acceptance Criteria
- **Functional**:
  - [ ] [verifiable_acceptance_criterium_1]
- **Invariants**:
  - [ ] [invariant_criterium_1]

---

## Implementation
- **Changed files**:
  - [path]
- **Commits**:
  - [commit_hash]

---

## Evidence
- **Verification commands**:
  - [command]
- **Result**: [pending|pass|fail]
- **Recorded at**: [ISO_timestamp]
- **Log path**: [path_to_log]
