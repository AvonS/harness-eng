---
name: tasks
description: >
  Granular task list for implementation.
  Created after design.md is approved.
  One task = one git commit.
agent_contract:
  prerequisites:
    - id: PRE-001
      action: "Confirm design.md has Ref: APPROVED."
      on_failure: "STOP: Cannot create tasks without approved design."
  actions:
    - id: ACT-001
      action: "Organize tasks by user story with explicit dependencies."
    - id: ACT-002
      action: "Mark parallel tasks with [P] and shared tasks with [SHARED]."
  must_do:
    - id: MUST-001
      action: "Each task must be under 30 minutes."
  must_not_do:
    - id: NEVER-001
      action: "Do not create tasks without approved design."
  outputs:
    - id: OUT-001
      path: "tasks.md with dependency ordering"
---
<!-- *** Maintained by AvonS/harness-eng, DON'T modify this, will be overwritten during next upgrade *** -->


# Tasks Template: [FEATURE_NAME]

**Input**: Design documents from `specs/[FEATURE]/`
**Ref**: [APPROVED|PENDING]

**Prerequisites**: design.md (approved), spec.md (user stories)

---

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this belongs to (US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: Project initialization

- [ ] T001 Create project structure per design
- [ ] T002 Initialize [language] with dependencies
- [ ] T003 [P] Configure linting and formatting

---

## Phase 2: Foundational

**Purpose**: Core infrastructure that BLOCKS all user stories

> ⚠️ No user story work can begin until this phase is complete

- [ ] T004 Setup database schema
- [ ] T005 [P] Implement authentication framework
- [ ] T006 [P] Setup API routing and middleware

**Checkpoint**: Foundation ready — user stories can begin

---

## Phase 3: Story 1 — [TITLE] (P1) 🎯 MVP

**Goal**: [What this story delivers]
**Independent Test**: [How to verify alone]

### Required Evidence

> Add only checks required by the approved Evidence Contract. For executable logic, put meaningful automated tests before implementation tasks.

- [ ] T007 [P] [US1] [required check from Evidence Contract]
- [ ] T008 [P] [US1] [additional required check, or remove]

### Implementation

- [ ] T009 [P] [US1] Create [Entity] model in src/models/
- [ ] T010 [US1] Implement [Service] in src/services/ (depends: T009)
- [ ] T011 [US1] Implement [Endpoint] in src/api/ (depends: T010)
- [ ] T012 [US1] Add validation and error handling
- [ ] T013 [US1] Add logging

**Checkpoint**: Story 1 fully functional and testable independently

---

## Phase 4: Story 2 — [TITLE] (P2)

**Goal**: [What this story delivers]
**Independent Test**: [How to verify alone]

### Tests

- [ ] T014 [P] [US2] Contract test in tests/contract/
- [ ] T015 [P] [US2] Integration test in tests/integration/

### Implementation

- [ ] T016 [P] [US2] Create [Entity] model
- [ ] T017 [US2] Implement [Service] (depends: T016)
- [ ] T018 [US2] Implement [Endpoint] (depends: T017)

**Checkpoint**: Stories 1 and 2 both work independently

---

## Phase 5: Polish

**Purpose**: Cross-cutting concerns

- [ ] T019 [P] Documentation updates
- [ ] T020 Code cleanup
- [ ] T021 Performance optimization
- [ ] T022 Run quickstart validation

---

## Dependencies & Execution Order

### Phase Dependencies
- **Setup**: No dependencies — start immediately
- **Foundational**: Depends on Setup — BLOCKS all stories
- **Stories**: Depend on Foundational — can run in parallel
- **Polish**: Depends on all desired stories

### Story Dependencies
- **US1 (P1)**: Start after Foundational — no other dependencies
- **US2 (P2)**: Start after Foundational — can run parallel with US1

### Parallel Opportunities
- All [P] tasks in Setup can run together
- All [P] tasks in Foundational can run together
- Once Foundational done, all stories can start in parallel
- Models within a story marked [P] can run together

---

## Implementation Strategy

### MVP First (Story 1 Only)
1. Setup → Foundational → Story 1 → STOP and validate → Deploy

### Incremental Delivery
1. Setup + Foundational → Foundation ready
2. Story 1 → Test → Deploy (MVP!)
3. Story 2 → Test → Deploy
4. Each story adds value without breaking previous

---

## Validation Checklist

> *Run before starting implementation.*

**Task Quality:**
- [ ] All tasks have [ID], file paths
- [ ] Parallel tasks marked with [P]
- [ ] Story labels [US1], [US2] for traceability
- [ ] Dependencies explicit (depends: T0XX)
- [ ] Checkpoints between phases

**Traceability:**
- [ ] Every task maps to a user story
- [ ] Every user story has all needed tasks
- [ ] Each story independently testable
- [ ] Setup and Foundational phases have no [Story] label
