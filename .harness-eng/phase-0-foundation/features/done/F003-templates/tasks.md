---
name: tasks
description: >
  Granular task list for document templates.
  All tasks are ✅ Built — reverse-engineered from existing source.
  Organized by user story and template group.
---

# Tasks: Document Templates (F003)

**Input**: spec.md (7 user stories) + design.md (4 template groups, template→doc mapping)
**Ref**: PENDING

---

## Format: `[ID] [P?] [Story] Description → Design Component`

---

## Story 1 — Feature Spec Template (P1)

**Goal**: Consistent spec structure with Given/When/Then stories.
**Independent test**: Open template and verify all required sections present.
**Design components**: Feature Templates group

- [x] **T001** [US1] `templates/feature/spec.md` — spec template with User Stories, Acceptance Scenarios, FRs, SCs, Entities → Feature Templates

---

## Story 2 — Feature Design Template (P1)

**Goal**: Consistent architecture design with component maps, interfaces, constitution check.
**Independent test**: Open template and verify Ref marker, all design sections.
**Design components**: Feature Templates group

- [x] **T002** [US2] `templates/feature/design.md` — design template with Summary, Context, Constitution Check, Architecture, Research, Confidence → Feature Templates

---

## Story 3 — Feature Tasks Template (P1)

**Goal**: Consistent task breakdown with dependencies and status tracking.
**Independent test**: Open template and verify task ID, deps, status markers.
**Design components**: Feature Templates group

- [x] **T003** [US3] `templates/feature/tasks.md` — tasks template with phases, stories, deps, checkpoints → Feature Templates

---

## Story 4 — Big-Picture Templates (P1)

**Goal**: Consistent project-wide documents (CONSTITUTION, BRD, ARCHITECTURE).
**Independent test**: Open each and verify required sections.
**Design components**: Big-Picture Templates group

- [x] **T004** [P][US4] `templates/big-picture/CONSTITUTION.md` — project rules template with SST Golden Rules, Core Principles, Gates, Personas → Big-Picture
- [x] **T005** [P][US4] `templates/big-picture/BRD.md` — business requirements template with Problem, Users, Features, Workflow → Big-Picture
- [x] **T006** [P][US4] `templates/big-picture/ARCHITECTURE.md` — system design template with Contract Architecture, Templates, Gates, Flows → Big-Picture

---

## Story 5 — Phase Templates (P2)

**Goal**: Consistent phase definitions with feature list and exit criteria.
**Independent test**: Open template and verify phase structure.
**Design components**: Phase/Status Templates group

- [x] **T007** [P][US5] `templates/phase/PHASE.md` — phase definition template with features, exit criteria → Phase/Status
- [x] **T008** [P][US5] `templates/PHASES.md` — phase index template → Phase/Status
- [x] **T009** [P][US5] `templates/status/STATUS.md` — status dashboard template → Phase/Status

---

## Story 6 — SLICE_LOG Template (P2)

**Goal**: Consistent build narrative format.
**Independent test**: Open template — verify date|type|message format.
**Design components**: Root Templates group

- [x] **T010** [US6] `templates/SLICE_LOG.md` — log template with date|type|message format, parseable by check-slice-log → Root Templates

---

## Story 7 — Sanity Check Script Template (P2)

**Goal**: Deployable sanity-check skeleton for project root.
**Independent test**: Run generated script — verifies harness project structure.
**Design components**: Root Templates group

- [x] **T011** [US7] `templates/sanity-check.sh` — bash skeleton checking .harness-eng/, AGENTS.md, commands/, CONSTITUTION.md → Root Templates (deployed to scripts/)

---

## Template Group Coverage

| Template Group | Tasks Covered By |
|---|---|
| Feature Templates | T001, T002, T003 |
| Big-Picture Templates | T004, T005, T006 |
| Phase/Status Templates | T007, T008, T009 |
| Root Templates | T010, T011 |

---

## Execution Strategy

All tasks are ✅ Built — reverse-engineered from existing templates/. The task structure maps each template to its spec story and template group for review and maintenance.

## Validation Checklist

- [x] All tasks have [ID] and file paths
- [x] Parallel tasks marked with [P]
- [x] Story labels [US1]–[US7] for traceability
- [x] Every task maps to a user story
- [x] Template group coverage mapped
