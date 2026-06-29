---
name: tasks
description: >
  Granular task list for language skills.
  All tasks are ✅ Built — reverse-engineered from existing source.
  Organized by user story and language coverage.
---

# Tasks: Language Skills (F004)

**Input**: spec.md (5 user stories) + design.md (7 skills, design→review→code flow)
**Ref**: PENDING

---

## Format: `[ID] [P?] [Story] Description → Design Component`

---

## Story 1 — Language Convention Reference (P1)

**Goal**: Agent reads SKILL.md to learn project conventions before writing code.
**Independent test**: Write code in Go — verify it follows skill's test framework and formatting.
**Design components**: SKILL.md files → Skills Layer

- [x] **T001** [P][US1] `skills/go/SKILL.md` — Go conventions: test framework (testing), formatting (gofmt), error handling, libraries → Skills layer
- [x] **T002** [P][US1] `skills/python/SKILL.md` — Python conventions: test framework (pytest), type hints, imports, formatting → Skills layer
- [x] **T003** [P][US1] `skills/node/SKILL.md` — Node.js conventions: test framework, modules, npm, formatting → Skills layer
- [x] **T004** [P][US1] `skills/sql/SKILL.md` — SQL conventions: query style, naming conventions → Skills layer
- [x] **T005** [P][US1] `skills/datastar/SKILL.md` — Datastar framework conventions → Skills layer
- [x] **T006** [P][US1] `skills/oat/SKILL.md` — OAT (Opinionated API Tool) conventions → Skills layer

---

## Story 2 — Design Compliance Check (P1)

**Goal**: Design.md references relevant skills in Technical Context.
**Independent test**: Review design.md — must cite skills used.
**Design components**: Skills → Design Phase flow

- [x] **T007** [US2] Design command references skills — `commands/design.md` reads skills/ and includes in Technical Context → Skills → Design flow

---

## Story 3 — Review Compliance (P2)

**Goal**: Pre-verify review compares code against skill conventions.
**Independent test**: Write violating code — review must flag it.
**Design components**: Skills → Review Phase flow

- [x] **T008** [US3] Review command checks skills — `commands/review-pre-verify.md` compares code against skill conventions → Skills → Review flow

---

## Story 4 — Git Convention Enforcement (P2)

**Goal**: Commit messages follow skill conventions, enforced by pre-commit hook.
**Independent test**: Commit with bad format — hook rejects.
**Design components**: Git skill → Pre-commit hook

- [x] **T009** [US4] `skills/git/SKILL.md` — Git conventions: commit message format (type(ID): desc), branch naming, PR conventions → Skills layer
- [x] **T010** [US4] Pre-commit hook enforces git skill — `hooks/pre-commit` validates against git skill rules → Skills → Hooks flow

---

## Story 5 — New Language Onboarding (P2)

**Goal**: New language = new skill directory, no config changes.
**Independent test**: Create skills/rust/SKILL.md — status dashboard detects it.
**Design components**: Skill discovery mechanism

- [x] **T011** [US5] Skill discovery via directory listing — `ls skills/*/SKILL.md` lists all available skills → Discovery mechanism

---

## Language Coverage

| Language | Task | Required Sections (Test Framework, Formatting, Libraries, Error Handling, Conventions) |
|---|---|---|
| Go | T001 | ✅ Full coverage |
| Python | T002 | ✅ Full coverage |
| Node | T003 | ✅ Full coverage |
| SQL | T004 | ✅ Full coverage |
| Git | T009 | ✅ Full coverage |
| Datastar | T005 | ✅ Framework-specific |
| OAT | T006 | ✅ Framework-specific |

---

## Execution Strategy

All tasks are ✅ Built — reverse-engineered from existing skills/. The task structure maps each skill to its spec story and language coverage for review and maintenance.

## Validation Checklist

- [x] All tasks have [ID] and file paths
- [x] Parallel tasks marked with [P]
- [x] Story labels [US1]–[US5] for traceability
- [x] Every task maps to a user story
- [x] Language coverage mapped
