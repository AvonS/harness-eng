---
name: tasks
description: >
  Granular task list for git hooks.
  All tasks are ✅ Built — reverse-engineered from existing source.
  Organized by user story and hook lifecycle stages.
---

# Tasks: Git Hooks (F005)

**Input**: spec.md (3 user stories) + design.md (pre-commit hook lifecycle, commit flow diagram)
**Ref**: PENDING

---

## Format: `[ID] [P?] [Story] Description → Design Component`

---

## Story 1 — Commit Message Validation (P1)

**Goal**: Pre-commit hook validates commit message format before allowing commit.
**Independent test**: Commit with bad format — rejected with error explaining expected format.
**Design components**: Pre-commit hook → commit validation flow → regex matching

- [x] **T001** [US1] `hooks/pre-commit` — commit message validation: regex match `type(ID): description`, reject with error on mismatch, skip merge commits → Commit validation flow

**Acceptance criteria covered**:
- AC1: `feat(42): add login` → allowed
- AC2: `fixed stuff` → rejected with format error
- AC3: `FEAT(42): add login` → rejected (case-sensitive)
- AC4: `fix(1): ` (empty desc) → rejected

---

## Story 2 — Pre-Commit Harness Checks (P2)

**Goal**: Hook runs basic harness integrity checks before allowing commit.
**Independent test**: Stage malformed SLICE_LOG — commit blocked.
**Design components**: Pre-commit hook → harness integrity flow

- [x] **T002** [US2] `hooks/pre-commit` (extended) — harness checks: validate SLICE_LOG format if modified, check required files not deleted → Harness integrity flow

**Acceptance criteria covered**:
- AC1: Malformed SLICE_LOG staged → commit rejected with format error
- AC2: Required harness file deleted → commit rejected
- AC3: All checks pass → commit allowed

---

## Story 3 — Hook Installation (P2)

**Goal**: Init command installs pre-commit hook automatically.
**Independent test**: Fresh clone — init installs `.git/hooks/pre-commit`.
**Design components**: Hook installation flow (copy/symlink from source)

- [x] **T003** [US3] Hook installation via init — `commands/init.md` copies/symlinks `hooks/pre-commit` to `.git/hooks/pre-commit` → Hook installation flow

**Acceptance criteria covered**:
- AC1: Fresh clone → init installs `.git/hooks/pre-commit`
- AC2: Outdated hook → `--force` overwrites

---

## Hook Lifecycle Coverage

| Stage | Tasks Covered By |
|---|---|
| Source | T001, T002 (`hooks/pre-commit`) |
| Installation | T003 (init command) |
| Pre-commit execution | T001 (validation), T002 (checks) |
| Human override | `git commit --no-verify` (standard git, not a task) |

---

## Execution Strategy

All tasks are ✅ Built — reverse-engineered from existing hooks/. The same source file (`hooks/pre-commit`) serves multiple stories via its two responsibilities: format validation + harness checks.

## Validation Checklist

- [x] All tasks have [ID] and file paths
- [x] Story labels [US1]–[US3] for traceability
- [x] Every task maps to a user story
- [x] Acceptance criteria referenced per task
- [x] Hook lifecycle coverage mapped
