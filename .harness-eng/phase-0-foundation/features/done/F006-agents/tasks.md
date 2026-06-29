---
name: tasks
description: >
  Granular task list for agent definitions.
  All tasks are ✅ Built — reverse-engineered from existing source.
  Organized by user story and persona pipeline stages.
---

# Tasks: Agent Definitions (F006)

**Input**: spec.md (4 user stories) + design.md (persona pipeline, gate ownership table)
**Ref**: PENDING

---

## Format: `[ID] [P?] [Story] Description → Design Component`

---

## Story 1 — Persona-Specific Instructions (P1)

**Goal**: Each persona has agent.md defining commands, mode, gates, output.
**Independent test**: Read each agent.md — verify sections for Commands, Mode, Gates, Output.
**Design components**: 4 persona directories → Persona Pipeline

- [x] **T001** [US1] `agents/collaborator/agent.md` — Collaborator persona: commands (define, design), mode (ask/challenge), gates (spec complete) → Collaborator pipeline stage
- [x] **T002** [US1] `agents/developer/agent.md` — Developer persona: commands (tasks, build), mode (Jr Programmer), gates (design approved), TDD → Developer pipeline stage
- [x] **T003** [US1] `agents/sr-tech-lead/agent.md` — Sr Tech Lead persona: commands (review-pre-build, review-pre-verify), mode (reviewer), gates (code ≥ design) → Sr Tech Lead pipeline stage
- [x] **T004** [US1] `agents/gatekeeper/agent.md` — Gatekeeper persona: commands (approve, release), mode (gatekeeper), gates (human confirmation required) → Gatekeeper pipeline stage

---

## Story 2 — Gate Assignment (P1)

**Goal**: Each persona owns specific gates in the workflow.
**Independent test**: Map persona → gate → verify gate referenced in agent.md.
**Design components**: Gate ownership table

- [x] **T005** [US2] Collaborator owns "spec complete" gate — verify spec has all sections before handoff → Gate: Spec Complete
- [x] **T006** [US2] Developer owns "design approved" gate — calls check-approved-designs.sh before build → Gate: Design Approved
- [x] **T007** [US2] Sr Tech Lead owns "code ≥ design" and "skill compliance" gates — review compares against design and skills → Gate: Code ≥ Design + Skill Compliance
- [x] **T008** [US2] Gatekeeper owns "human approved" gates — approve and release commands require human confirmation → Gate: Human Approval (design + release)

---

## Story 3 — Output Artifact Handoff (P2)

**Goal**: Each persona produces artifacts consumed by next persona.
**Independent test**: Trace artifact chain spec→design→tasks→code→verification.
**Design components**: Artifact handoff chain

- [x] **T009** [US3] Collaborator → Developer handoff — spec.md + design.md → tasks.md + implementation → Artifact chain: spec → design → tasks
- [x] **T010** [US3] Developer → Sr Tech Lead handoff — implementation code + tests → review report → Artifact chain: code → review
- [x] **T011** [US3] Sr Tech Lead → Gatekeeper handoff — review report → verification.md → release PR → Artifact chain: review → verification → release

---

## Story 4 — Mode Switching (P2)

**Goal**: Single agent switches personas as workflow progresses.
**Independent test**: Full workflow — agent changes behavior per command.
**Design components**: Persona switching via command frontmatter

- [x] **T012** [US4] Persona switching documented — CONSTITUTION.md and ARCHITECTURE.md define how agent switches persona per command via YAML frontmatter `agent:` field → Mode switching flow

---

## Persona Pipeline Coverage

| Pipeline Stage | Persona | Tasks Covered By | Gate |
|---|---|---|---|
| Requirements + Design | Collaborator | T001, T005, T009 | Spec complete |
| Implementation | Developer | T002, T006, T010 | Design approved |
| Review | Sr Tech Lead | T003, T007, T009 | Code ≥ design + skills |
| Approve + Release | Gatekeeper | T004, T008, T011 | Human approval |

---

## Execution Strategy

All tasks are ✅ Built — reverse-engineered from existing agents/. The task structure maps each persona to its spec story, gate responsibility, and artifact handoff for review and maintenance.

## Validation Checklist

- [x] All tasks have [ID] and file paths
- [x] Story labels [US1]–[US4] for traceability
- [x] Every task maps to a user story
- [x] Persona pipeline coverage mapped
- [x] Gate ownership mapped per persona
- [x] Artifact handoff chain documented
