---
name: spec
description: >
  Feature specification with Given/When/Then stories.
  Created during /h:define phase.
  Stories must be testable and prioritized.
agent_contract:
  prerequisites:
    - id: PRE-001
      action: "Confirm BRD.md and ARCHITECTURE.md exist."
      on_failure: "STOP: Cannot write spec without project context."
  actions:
    - id: ACT-001
      action: "Write Given/When/Then stories with P1/P2/P3 priorities."
    - id: ACT-002
      action: "Include NEEDS INPUT and MUST INPUT markers where required."
  must_do:
    - id: MUST-001
      action: "Every story must use testable Given/When/Then format."
  must_not_do:
    - id: NEVER-001
      action: "Do not leave MUST INPUT markers unfilled."
  outputs:
    - id: OUT-001
      path: "spec.md with prioritized testable stories"
---

# Spec Template: [FEATURE_NAME]

**Feature**: [FEATURE_NAME]
**Created**: [DATE]
**Status**: Draft
**Ref**: [APPROVED|PENDING]

**Input**: [DESCRIPTION_OF_FEATURE]

---

## User Stories

### Story 1 — [STORY_TITLE] (Priority: P1)

[Describe this user journey in plain language]

**Why this priority**: [Value and reasoning]
**Independent test**: [How to verify this story alone]

**Acceptance Scenarios**:

1. **Given** [initial state], **When** [action], **Then** [expected outcome]
2. **Given** [initial state], **When** [action], **Then** [expected outcome]

---

### Story 2 — [STORY_TITLE] (Priority: P2)

[Describe this user journey]

**Why this priority**: [Value]
**Independent test**: [How to verify]

**Acceptance Scenarios**:

1. **Given** [initial state], **When** [action], **Then** [expected outcome]

---

[Add more stories as needed]

---

## Edge Cases

- What happens when [boundary condition]?
- How does system handle [error scenario]?

---

## Functional Requirements

- **FR-001**: System MUST [specific capability]
- **FR-002**: System MUST [specific capability]
- **FR-003**: Users MUST be able to [key interaction]

*Mark unclear requirements:*
- **FR-004**: System MUST [capability] [NEEDS CLARIFICATION: <what's unclear>]

---

## Success Criteria

| # | Criterion | Measurable? |
|---|-----------|-------------|
| SC-001 | [metric, e.g., "Users complete checkout in under 3 minutes"] | ✅ |
| SC-002 | [metric] | ✅ |

---

## Key Entities

- **[ENTITY_1]**: [What it represents, key attributes]
- **[ENTITY_2]**: [What it represents, relationships]

---

## Assumptions

- [Assumption about users, environment, dependencies]
- [Assumption about scope boundaries]

---

## Out of Scope

- [What this feature explicitly does NOT solve]

---

## Validation Checklist

> *Run this checklist before finalizing the spec.*

**Content Quality:**
- [ ] No implementation details (languages, frameworks, APIs)
- [ ] Focused on user value and business needs
- [ ] Written for non-technical stakeholders
- [ ] All mandatory sections completed

**Requirement Completeness:**
- [ ] No [NEEDS CLARIFICATION] markers remain
- [ ] Requirements are testable and unambiguous
- [ ] Success criteria are measurable
- [ ] Success criteria are technology-agnostic
- [ ] All acceptance scenarios use Given/When/Then
- [ ] Edge cases identified
- [ ] Scope clearly bounded

**Feature Readiness:**
- [ ] All stories have acceptance criteria
- [ ] Stories cover primary user flows
- [ ] Feature meets measurable success criteria
- [ ] No implementation details in spec
