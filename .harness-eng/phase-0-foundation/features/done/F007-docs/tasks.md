---
name: tasks
description: >
  Granular task list for user-facing documentation.
  All tasks are ✅ Built — reverse-engineered from existing source.
  Organized by user story and document audience.
---

# Tasks: User-Facing Documentation (F007)

**Input**: spec.md (4 user stories) + design.md (document quadrant, reader journey map)
**Ref**: PENDING

---

## Format: `[ID] [P?] [Story] Description → Design Component`

---

## Story 1 — Business Requirements Understanding (P1)

**Goal**: New developers understand why harness-eng exists and the 3-gate workflow.
**Independent test**: After reading, developer can explain workflow and gates in own words.
**Design components**: BRD → Business stakeholders quadrant

- [x] **T001** [US1] `docs/BRD-harness.md` — Business Requirements Document: problem statement, solution overview, 11-step workflow, 3 gates (design approval, sr tech lead review, release approval) → BRD quadrant

**Acceptance criteria covered**:
- AC1: Developer reads BRD → can describe problem and 3 gates
- AC2: Developer can name 11 commands in order and 3 gates

---

## Story 2 — Quick Command Reference (P1)

**Goal**: Mid-session lookup for command trigger, purpose, gate.
**Independent test**: Developer finds command in < 10 seconds.
**Design components**: Command Reference → Developers mid-session quadrant

- [x] **T002** [US2] `docs/COMMAND-REFERENCE.md` — Quick reference table: all 14 commands with trigger, purpose, gate type (human/auto), persona, output artifact → Command Reference quadrant

**Acceptance criteria covered**:
- AC1: Developer finds review-pre-verify in < 3 sec
- AC2: Developer scans gate column → sees which commands need human

---

## Story 3 — End-User Onboarding (P2)

**Goal**: New team member completes first full workflow cycle without help.
**Independent test**: Follow guide from init to release — success.
**Design components**: User Guide → New team members quadrant

- [x] **T003** [US3] `docs/user-guide.md` — Step-by-step walkthrough from init → define → design → approve → tasks → build → verify → release, with troubleshooting section → User Guide quadrant

**Acceptance criteria covered**:
- AC1: New member completes full workflow following the guide
- AC2: Troubleshooting section helps identify blocked gates

---

## Story 4 — Architecture Review (P2)

**Goal**: Architects understand design rationale, trade-offs, rejected alternatives.
**Independent test**: Architect can list 3 decisions with rationale.
**Design components**: Architecture Review → Architects/Maintainers quadrant

- [x] **T004** [US4] `docs/architectural-review-2026-06-15.md` — Design decisions, trade-offs, rejected alternatives, dated filename for versioning → Architecture Review quadrant

**Acceptance criteria covered**:
- AC1: Architect reads review → understands 3-gate workflow rationale
- AC2: Architect sees trade-offs before proposing changes

---

## Document Quadrant Coverage

| Quadrant | Audience | Document | Tasks Covered By |
|---|---|---|---|
| BRD | Stakeholders, new devs | docs/BRD-harness.md | T001 |
| Command Reference | Developers mid-session | docs/COMMAND-REFERENCE.md | T002 |
| User Guide | New team members | docs/user-guide.md | T003 |
| Architecture Review | Architects, maintainers | docs/architectural-review-*.md | T004 |

---

## Document Relationship Coverage

| Relationship | Tasks Covered By |
|---|---|
| BRD → User Guide (why → how) | T001 → T003 |
| User Guide → Command Reference (during session) | T003, T002 |
| User Guide → Architecture Review (deep rationale) | T003, T004 |

---

## Execution Strategy

All tasks are ✅ Built — reverse-engineered from existing docs/. The task structure maps each document to its spec story, audience quadrant, and reader journey for review and maintenance.

## Validation Checklist

- [x] All tasks have [ID] and file paths
- [x] Story labels [US1]–[US4] for traceability
- [x] Every task maps to a user story
- [x] Document quadrant coverage mapped
- [x] Document relationship mapped
- [x] Acceptance criteria referenced per task
