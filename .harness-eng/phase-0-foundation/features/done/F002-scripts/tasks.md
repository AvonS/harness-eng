---
name: tasks
description: >
  Granular task list for enforcement scripts.
  All tasks are ✅ Built — reverse-engineered from existing source.
  Organized by user story and design quadrant.
---

# Tasks: Enforcement Scripts (F002)

**Input**: spec.md (7 user stories) + design.md (gate/status/validation/release quadrants)
**Ref**: PENDING

---

## Format: `[ID] [P?] [Story] Description → Design Component`

---

## Story 1 — Gate Enforcement (P1)

**Goal**: Pre-flight scripts block commands when conditions aren't met.
**Independent test**: Run against mixed APPROVED/PENDING designs — exits non-zero.
**Design components**: Gate Scripts quadrant

- [x] **T001** [US1] `scripts/check-approved-designs.sh` — grep for Ref: APPROVED in all designs, phase + specs → Gate Scripts

---

## Story 2 — Status Dashboard (P1)

**Goal**: Quick project health overview from file structure.
**Independent test**: Run in harness project — produces structured report.
**Design components**: Status Scripts quadrant

- [x] **T002** [P][US2] `scripts/harness-status.py` — Python status dashboard, file existence + validity → Status Scripts
- [x] **T003** [P][US2] `scripts/harness-status.sh` — shell variant of status dashboard → Status Scripts
- [x] **T004** [P][US2] `scripts/harness-status-server.py` — HTTP server for visual dashboard → Status Scripts

---

## Story 3 — Version Check (P1)

**Goal**: Detect outdated harness versions.
**Independent test**: Run against known version — detects outdated vs current.
**Design components**: Gate Scripts (version-specific)

- [x] **T005** [P][US3] `scripts/version-check.py` — Python version comparison against GitHub releases → Gate Scripts
- [x] **T006** [P][US3] `scripts/version-check.sh` — shell variant of version check → Gate Scripts

---

## Story 4 — Sanity Checks (P1)

**Goal**: Verify basic project structure before workflow commands.
**Independent test**: Run in valid vs invalid project — correct exit codes.
**Design components**: Gate Scripts (sanity-specific)

- [x] **T007** [P][US4] `scripts/harness-check.py` — Python sanity checks (files, structure) → Gate Scripts
- [x] **T008** [P][US4] `scripts/harness-check.sh` — shell variant of sanity checks → Gate Scripts

---

## Story 5 — Slice Log Validation (P2)

**Goal**: Ensure SLICE_LOG.md follows required format.
**Independent test**: Run against valid and invalid SLICE_LOG.
**Design components**: Validation Scripts quadrant

- [x] **T009** [P][US5] `scripts/check-slice-log.sh` — validate entire SLICE_LOG format → Validation Scripts
- [x] **T010** [P][US5] `scripts/check-slice-log-entry.sh` — validate single entry format → Validation Scripts

---

## Story 6 — Release Notes Generation (P2)

**Goal**: Generate changelog from git history.
**Independent test**: Run in repo with commits — produces markdown changelog.
**Design components**: Release Scripts quadrant

- [x] **T011** [US6] `scripts/generate-release-notes.sh` — changelog from git log grouped by type → Release Scripts

---

## Story 7 — Release Logging (P2)

**Goal**: Record release events with version, date, notes.
**Independent test**: Run with version arg — creates release record.
**Design components**: Release Scripts quadrant

- [x] **T012** [US7] `scripts/log-release.sh` — append release record with version, date, summary → Release Scripts

---

## Design Quadrant Coverage

| Design Quadrant | Tasks Covered By |
|---|---|
| Gate Scripts | T001, T005, T006, T007, T008 |
| Status Scripts | T002, T003, T004 |
| Validation Scripts | T009, T010 |
| Release Scripts | T011, T012 |

---

## Execution Strategy

All tasks are ✅ Built — reverse-engineered from existing scripts/. The task structure maps each script to its spec story and design quadrant for review and maintenance.

## Validation Checklist

- [x] All tasks have [ID] and file paths
- [x] Parallel tasks marked with [P]
- [x] Story labels [US1]–[US7] for traceability
- [x] Every task maps to a user story
- [x] Design quadrant coverage mapped
