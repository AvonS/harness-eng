---
name: tasks
description: >
  Granular task list for workflow commands.
  All tasks are ✅ Built — reverse-engineered from existing source.
  Organized by user story and design component mapping.
---

# Tasks: Workflow Commands (F001)

**Input**: spec.md (10 user stories) + design.md (pipeline architecture, 14 commands)
**Ref**: PENDING

---

## Format: `[ID] [P?] [Story] Description → Design Component`

- **[P]**: Can run in parallel (independent files)
- **[Story]**: User story this task belongs to
- **→**: Mapped design component from design.md

---

## Story 1 — Project Initialization (P1)

**Goal**: A single init command scaffolds the entire harness structure.
**Independent test**: Run init on empty dir — verify all expected files and symlinks.
**Design components**: Init command, scaffolding pipeline

- [x] **T001** [US1] `commands/init.md` — project scaffolding with 3 re-init choices → Init command, entry point

---

## Story 2 — Feature Definition and Design (P1)

**Goal**: Structured specs and technical designs before any code.
**Independent test**: Run define then design — verify spec.md + design.md produced.
**Design components**: Define command, Design command

- [x] **T002** [US2] `commands/define.md` — feature spec from BRD, questions, phase grouping → Define command
- [x] **T003** [US2] `commands/design.md` — architecture, interfaces, file layout with skill references and constitution check → Design command

---

## Story 3 — Human Design Approval (P1)

**Goal**: Gate 1 — human controls what gets built.
**Independent test**: Run approve — verify `**Ref**: APPROVED` written only after human confirmation.
**Design components**: Approve command, Gate Keeper persona, Ref marker chain

- [x] **T004** [US3] `commands/approve.md` — presents design summary, waits for human, writes Ref: APPROVED → Approve command, Gatekeeper persona

---

## Story 4 — Task Breakdown and TDD Implementation (P1)

**Goal**: Granular tasks, TDD loop, 3-fail escalation.
**Independent test**: Run tasks then build — verify commits, tests, format.
**Design components**: Tasks command, Build command, TDD loop, Developer persona

- [x] **T005** [US4] `commands/tasks.md` — ordered task breakdown with deps and file scope → Tasks command
- [x] **T006** [US4] `commands/build.md` — TDD loop with test-fail-implement-pass-commit per task → Build command, TDD loop, Developer persona

---

## Story 5 — Pre-Build Gap Analysis (P1)

**Goal**: Automated BRD→spec→design alignment check before implementation.
**Independent test**: Run review-pre-build — verify 6 categories, PASS/CONDITIONAL/FAIL.
**Design components**: Review pre-build command, Sr Tech Lead persona, 5-document review

- [x] **T007** [US5] `commands/review-pre-build.md` — pre-build gap analysis, 6 check categories, verdict routing → Review pre-build, Sr Tech Lead

---

## Story 6 — Post-Build Review (P1)

**Goal**: Gate 2 — automated comparison of implementation against design.
**Independent test**: Run review-pre-verify — verify story/file/test coverage.
**Design components**: Review pre-verify command, Sr Tech Lead persona, design-vs-code comparison

- [x] **T008** [US6] `commands/review-pre-verify.md` — post-build review, compares implementation vs design line by file → Review pre-verify, Sr Tech Lead

---

## Story 7 — Test Execution and Verification (P1)

**Goal**: Run tests, check acceptance criteria, produce verification report.
**Independent test**: Run verify — verify all tests pass and verification.md produced.
**Design components**: Verify command, verification output artifact

- [x] **T009** [US7] `commands/verify.md` — run test suite, check acceptance criteria, produce verification.md → Verify command

---

## Story 8 — Release Workflow (P1)

**Goal**: Gate 3 — structured release with human approval, PR, archive.
**Independent test**: Run release — verify PR, archive, Release Ref marker.
**Design components**: Release command, Gatekeeper persona, release pipeline

- [x] **T010** [US8] `commands/release.md` — release workflow, PR creation, feature archive, marker chain → Release command, Gatekeeper persona

---

## Story 9 — Project Status and Health (P2)

**Goal**: Operational visibility and compliance checking.
**Independent test**: Run status then health — verify both produce readable reports.
**Design components**: Status command, Health command

- [x] **T011** [P][US9] `commands/status.md` — version, active features, phase progress, SLICE_LOG freshness → Status command
- [x] **T012** [P][US9] `commands/health.md` — 10 compliance checks across CRITICAL/HIGH/MEDIUM → Health command

---

## Story 10 — Bug and Request Triage (P2)

**Goal**: Classify incoming issues and route to correct workflow.
**Independent test**: Submit bug — verify triage classifies and routes to bug workflow.
**Design components**: Triage command, Bug command

- [x] **T013** [US10] `commands/triage.md` — classify issue as Bug/CR/Feature/Deferred → Triage command
- [x] **T014** [US10] `commands/bug.md` — shortened bug fix workflow: regression test first, fix, verify → Bug command

---

## Design Component Coverage

| Design Component | Tasks Covered By |
|---|---|
| Init command (entry point) | T001 |
| Define command | T002 |
| Design command | T003 |
| Approve command | T004 |
| Tasks command | T005 |
| Build command + TDD loop | T006 |
| Review pre-build | T007 |
| Review pre-verify | T008 |
| Verify command | T009 |
| Release command + pipeline | T010 |
| Status command | T011 |
| Health command | T012 |
| Triage command | T013 |
| Bug command | T014 |
| Gate Keeper persona | T004, T010 |
| Sr Tech Lead persona | T007, T008 |
| Developer persona | T006 |
| Ref marker chain | T004, T010 |
| PR + archive pipeline | T010 |

---

## Execution Strategy

All tasks are ✅ Built — these are reverse-engineered. The task structure traces existing files to spec stories and design components for review and maintenance.

## Validation Checklist

- [x] All tasks have [ID] and file paths
- [x] Parallel tasks marked with [P]
- [x] Story labels [US1]–[US10] for traceability
- [x] Every task maps to a user story
- [x] Every user story has all needed tasks
- [x] Design component coverage mapped
