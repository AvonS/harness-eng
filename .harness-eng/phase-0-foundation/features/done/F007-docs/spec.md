---
name: spec
description: >
  Feature specification for user-facing documentation.
  4 documentation files that explain how to use and understand
  the harness-eng system: BRD (business requirements), command
  reference, user guide, and architecture review notes.
---

# Feature: User-Facing Documentation

**Feature**: F007 — User-Facing Documentation
**Status**: Complete (reverse-engineered)
**Ref**: PENDING

---

## User Stories

### Story 1 — Business Requirements Understanding (Priority: P1)

A new developer joins the project and needs to understand why harness-eng exists, what problems it solves, and how the 11-step workflow works at a business level. They read the BRD.

**Why this priority**: Without understanding the "why," developers can't make good decisions about when and how to use the harness.

**Independent test**: Give the BRD to a new developer — after reading, they can explain the workflow in their own words.

**Acceptance Scenarios**:

1. **Given** a developer unfamiliar with harness-eng, **When** they read `docs/BRD-harness.md`, **Then** they can describe the problem harness-eng solves (LLM code consistency/quality) and the 3 gates.
2. **Given** a developer who has read the BRD, **When** asked about the workflow, **Then** they can name the 11 commands in order and the 3 human/agent gates.

---

### Story 2 — Quick Command Reference (Priority: P1)

A developer is in the middle of a session and needs to quickly recall what command to run next, what it does, and what gate it requires. They open the command reference.

**Why this priority**: The full command files are detailed — a quick reference saves time during active work.

**Independent test**: Hand the command reference to a developer mid-session — they can find the right command in < 10 seconds.

**Acceptance Scenarios**:

1. **Given** a developer mid-session who needs to review pre-verify, **When** they open `docs/COMMAND-REFERENCE.md`, **Then** they find the `review-pre-verify` entry within 3 seconds and see its trigger, purpose, and gate.
2. **Given** a developer who wants to check if they need human approval, **When** they scan the gate column, **Then** they see which commands require human (approve, release) vs auto (review-pre-build, review-pre-verify).

---

### Story 3 — End-User Onboarding (Priority: P2)

A new team member needs a step-by-step guide to using the harness for their first task. They read the user guide from "what is this" through "I made my first release."

**Why this priority**: The BRD explains why, the command reference lists what — the user guide explains how (step by step).

**Independent test**: Give the user guide to a developer who has never used the harness — they complete a full workflow cycle without asking for help.

**Acceptance Scenarios**:

1. **Given** a new team member who has never used harness-eng, **When** they follow `docs/user-guide.md`, **Then** they complete a full workflow (init → define → design → approve → tasks → build → verify → release) successfully.
2. **Given** a user who encounters a blocked gate, **When** they read the troubleshooting section of the user guide, **Then** they can identify which gate is blocking and how to resolve it.

---

### Story 4 — Architecture Review (Priority: P2)

An architect or senior engineer needs to review the harness-eng architecture decisions. They read the architecture review document, which captures design decisions, trade-offs, and rationale.

**Why this priority**: Architecture decisions need a permanent record — not just what was decided, but why and what alternatives were rejected.

**Independent test**: An architect reads the review and can list 3 design decisions with their rationale and rejected alternatives.

**Acceptance Scenarios**:

1. **Given** an architect reviewing the harness, **When** they read `docs/architectural-review-2026-06-15.md`, **Then** they understand the 3-gate workflow design and the rationale for symlinked VERSION vs standalone.
2. **Given** an architect who wants to change the workflow, **When** they consult the architecture review, **Then** they see the trade-offs of the current design before proposing changes.

---

## Edge Cases

- What if the BRD and actual workflow diverge? Documentation must be updated when workflow changes — the BRD is not frozen.
- What if the user speaks a language other than English? Documentation is English-only for now.
- What if the command reference becomes stale? The reference must be regenerated when commands change.

## Functional Requirements

- **FR-001**: BRD MUST describe the problem, solution, 11-step workflow, and 3 gates.
- **FR-002**: Command reference MUST list every command with trigger, purpose, gate type, and output.
- **FR-003**: User guide MUST walk through a complete workflow cycle from init to release.
- **FR-004**: Documents MUST be versioned alongside the project source.
- **FR-005**: Documents MUST NOT contain implementation details that change frequently.

## Success Criteria

| # | Criterion | Measurable? |
|---|-----------|-------------|
| SC-001 | BRD covers problem, solution, workflow, gates | ✅ Section inspection |
| SC-002 | Command reference covers all 14 commands | ✅ grep for 14 command names |
| SC-003 | User guide covers full workflow cycle | ✅ Walk-through from init → release |
| SC-004 | Architecture review has dated filename for versioning | ✅ Filestamp in filename |

## Key Entities

- **BRD**: Business Requirements Document — high-level "why."
- **Command Reference**: Quick lookup of all commands and their properties.
- **User Guide**: Step-by-step onboarding tutorial.
- **Architecture Review**: Decision record with rationale and trade-offs.

## Assumptions

- Documentation is read by humans, not agents — written for human consumption.
- The workflow and commands evolve slowly — documentation is updated with each phase.
- New team members are the primary audience for the user guide and BRD.

## Out of Scope

- Multi-language documentation (English only).
- Video or interactive tutorials (static markdown only).
- API-level documentation (not a developer library — it's a workflow harness).

## Validation Checklist

**Content Quality:**
- [x] No implementation details
- [x] Focused on user value and business needs
- [ ] Written for non-technical stakeholders
- [x] All mandatory sections completed

**Requirement Completeness:**
- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] All acceptance scenarios use Given/When/Then
- [x] Edge cases identified
- [x] Scope clearly bounded

**Feature Readiness:**
- [x] All stories have acceptance criteria
- [x] Stories cover primary user flows
- [x] Feature meets measurable success criteria
- [x] No implementation details in spec
