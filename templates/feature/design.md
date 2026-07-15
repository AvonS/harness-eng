---
name: design
description: >
  Technical architecture design for a feature.
  Created after spec.md is approved.
  Must include **Ref**: PENDING for gate tracking.
agent_contract:
  prerequisites:
    - id: PRE-001
      action: "Confirm spec.md exists and is approved."
      on_failure: "STOP: Cannot design without approved spec."
  actions:
    - id: ACT-001
      action: "Fill all sections from spec.md stories and architecture constraints."
    - id: ACT-002
      action: "Include **Ref**: PENDING marker at top."
  must_do:
    - id: MUST-001
      action: "Document data flow, interfaces, file layout, and verification criteria."
    - id: MUST-002
      action: "Define a proportionate Evidence Contract for the change."
    - id: MUST-003
      action: "Set the Testing Level (S/M/L) in the header. The Developer will read this field to determine the depth of tests to implement."
    - id: MUST-004
      action: "Name one primary happy-path functional flow or justify inspection as stronger and cheaper."
    - id: MUST-005
      action: "Select S/M/L from risk and boundary depth. Never require test count or coverage as gate criteria."
  must_not_do:
    - id: NEVER-001
      action: "Do not finalize without **Ref**: PENDING marker."
  outputs:
    - id: OUT-001
      path: "design.md with Ref: PENDING"
---
<!-- *** Maintained by AvonS/harness-eng, DON'T modify this, will be overwritten during next upgrade *** -->


# Design Template: [FEATURE_NAME]

**Branch**: `[BRANCH_NAME]`
**Date**: [DATE]
**Spec**: [link to spec.md]
**Ref**: [APPROVED|PENDING|REJECTED]
**Approved by**: [Human|Agent]
**Approved date**: [YYYY-MM-DD]
**Testing Level**: [S|M|L]

**Input**: Feature specification from `specs/[FEATURE]/spec.md`

---

## Summary

[Extract from spec: primary requirement + technical approach]

---

## Primary Functional Flow

> Name the single happy-path functional flow that proves the feature works. If inspection (static analysis, manual review, documentation verification) is stronger and cheaper than functional testing, justify that choice explicitly.

**Primary flow**: [Describe the one happy-path functional flow, e.g., "User submits form -> backend validates -> database persists -> confirmation displayed"]

**Justification (if inspection)**: [Only if no functional flow: explain why inspection provides stronger evidence at lower cost]

---

## Technical Context

**Language/Version**: [LANGUAGE_VERSION] or NEEDS CLARIFICATION

**Primary Dependencies**: [DEPENDENCIES] or NEEDS CLARIFICATION

**Storage**: [STORAGE] or N/A

**Testing**: [TEST_FRAMEWORK] or NEEDS CLARIFICATION

**Target Platform**: [PLATFORM] or NEEDS CLARIFICATION

**Performance Goals**: [GOALS] or NEEDS CLARIFICATION

---

## Constitution Check

> *GATE: Must pass before implementation. Re-check after design.*

| Rule | Status | Notes |
|------|--------|-------|
| [PRINCIPLE_1_NAME] | ✅ PASS / ❌ FAIL | [if fail, explain] |
| [PRINCIPLE_2_NAME] | ✅ PASS / ❌ FAIL | [if fail, explain] |
| [PRINCIPLE_3_NAME] | ✅ PASS / ❌ FAIL | [if fail, explain] |

**If any gate FAILS:** Document in Complexity Tracking section below.

---

## Architecture

### Component Map

```
<visual representation of components>
```

| Component | Responsibility | Depends On |
|-----------|---------------|------------|
| [COMPONENT] | [WHAT IT DOES] | [DEPENDENCIES] |

### Data Flow

[How data moves through the system]

### Interfaces

```[LANGUAGE]
// Function signatures, API endpoints, type definitions
[INTERFACE_DEFINITIONS]
```

---

## File Layout

**New Files:**
- [PATH] — [purpose]

**Modified Files:**
- [PATH] — [what changes]

---

## UI Design

[Describe UI architecture, components, and layout mapping from registry]

---

## Evidence Contract

**Change classification**: [documentation / configuration / pure logic / stateful behavior / integration boundary / UI / security-sensitive]
**Risk and reversibility**: [LOW / MEDIUM / HIGH] — [reason]

### S/M/L Evidence Matrix

| Level | Primary evidence | Integration depth | Failure/recovery evidence |
|-------|-----------------|-------------------|--------------------------|
| Level S | One happy-path functional check, or cheapest deterministic inspection | None (unit or below) | None required |
| Level M | Happy path + important failure path + every affected material boundary | Integration across affected boundaries | Failure at each boundary |
| Level L | Full E2E functional flow | End-to-end across all critical paths | Critical failure/recovery, regression, operational sanity |

**Selected level**: [S|M|L] — [reason from risk and boundary depth]

### Evidence Table

| Requirement or Risk | Required Evidence | Evidence Level | Why Sufficient |
|---------------------|-------------------|----------------|----------------|
| [behavior/risk] | [inspection, static check, unit test, integration test, browser check, scenario, other] | [level] | [reason] |

**Explicitly not required:**
- [Test or technique that adds no decision value for this change, with reason]

### Universal Policy

- Test count and coverage are not gate criteria. Evidence is evaluated by decision value, not quantity.
- Placeholder, self-fulfilling, or duplicate tests are not evidence.
- When a reviewer names extra evidence beyond the contract, they must cite concrete risk.

**Completion rule:** All required evidence passes and the existing regression suite has no failures. Testing techniques not listed above are not release requirements unless implementation exposes a security risk, scope change, or false design assumption.

---

## Research

> *Technical decisions with rationale.*

| Decision | Rationale | Alternatives Rejected |
|----------|-----------|----------------------|
| [DECISION] | [WHY] | [WHAT ELSE AND WHY NOT] |

---

## Complexity Tracking

> *Fill ONLY if Constitution Check has violations that must be justified.*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [VIOLATION] | [NEED] | [WHY SIMPLER NOT ENOUGH] |

---

## Design Confidence

| Claim | Confidence | Source |
|-------|-----------|--------|
| [CLAIM] | VERIFIED / INFERRED / ASSUMED | [SOURCE] |

**Review priority:** ASSUMED needs confirmation. INFERRED needs validation. VERIFIED needs sanity check.

---

## Self-Challenge

> *Before human review, argue against your own design.*

**What is the strongest reason this design might be wrong?**
[HONEST_ASSESSMENT]

**What assumption am I making that I haven't stated?**
[UNSTATED_ASSUMPTION]

**What would need to be true for this to fail?**
[FAILURE_CONDITIONS]

---

## Validation Checklist

> *Run this checklist before presenting for approval.*

**Architecture:**
- [ ] Component map is complete
- [ ] Data flow is documented
- [ ] Interfaces are defined (signatures, not implementations)
- [ ] File layout specifies new vs modified files

**Constitution:**
- [ ] All constitution rules checked
- [ ] Violations documented with justification
- [ ] Complexity tracking filled (if violations exist)

**Research:**
- [ ] All NEEDS CLARIFICATION items resolved
- [ ] Technical decisions documented with rationale
- [ ] Alternatives considered and rejected

**Quality:**
- [ ] Evidence Contract is proportionate to change risk and reversibility
- [ ] Required and unnecessary evidence are explicit
- [ ] Primary functional flow named (or inspection justified)
- [ ] Testing level (S/M/L) selected and documented
- [ ] Design confidence tags filled (VERIFIED/INFERRED/ASSUMED)
- [ ] Self-challenge completed
- [ ] No implementation code (design only)
