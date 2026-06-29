# Architecture Document
# Project: harness-eng
# Date: 2026-06-22
# Status: Complete

---

## System Overview

harness-eng is a file-based convention — no runtime, no server, no API keys. The system consists of markdown templates that constrain agent behavior, shell/python scripts for status checking, and a folder structure that acts as a state machine. It forces a 2-Human-Gate Autonomous Loop through strict persona separation.

---

## Component Map

```text
AGENTS.md ──────────────────→ .harness-eng/
(project root,               ├── CONSTITUTION.md (rules + persona definitions)
 self-contained)             ├── BRD.md (requirements)
                               ├── ARCHITECTURE.md (design)
                               ├── technology.yaml (config)
                               ├── commands/ (workflow steps)
                               ├── skills/ (language rules)
                               ├── scripts/ (status tools)
                               └── phases/
                                   └── <phase>/
                                       ├── PHASE.md
                                       └── features/active/
                                           └── <feature>/
                                               ├── spec.md
                                               ├── design.md
                                               ├── tasks.md
                                               └── verification.md
```

| Component | Responsibility | Depends On |
|-----------|---------------|------------|
| `commands/` | 11-step workflow instructions | — |
| `templates/` | Document templates with placeholders | — |
| `scripts/` | Status, check, version utilities | Python 3.8+ |
| `phases/` | Multi-feature phase organization | — |
| `CONSTITUTION.md` | Project rules, principles, persona definitions, gates | — |
| `BRD.md` | Business requirements | — |
| `technology.yaml` | Toolchain, test/lint commands | — |

---

## Workflow

```text
init → define → design → review-pre-build → approve → tasks → build → review-pre-verify → verify → release
```

| Step | Command | Persona | Output | Gate |
|------|---------|---------|--------|------|
| 1 | `/h:init` | Manager | Constitution, BRD, architecture | — |
| 2 | `/h:define` | Collaborator | Feature spec.md | — |
| 3 | `/h:design` | Collaborator | Design document | — |
| 4 | `/h:review-pre-build`| Sr Architect | Pre-build gap analysis | ✅ Agent |
| 5 | `/h:approve` | Collaborator | Approved design | ✅ Human |
| 6 | `/h:tasks` | Developer | Task list | — |
| 7 | `/h:build` | Jr Programmer | Committed code + tests | — |
| 8 | `/h:review-pre-verify`| Sr Tech Lead | Review report | ✅ Agent |
| 9 | `/h:verify` | Gatekeeper | Verification report | — |
| 10 | `/h:release` | Gatekeeper | Merged PR, archived feature | ✅ Human |

*(Note: `/h:triage`, `/h:bug`, `/h:status`, `/h:health`, `/h:upgrade-harness` run orthogonally to the main feature loop)*

---

## 7-Persona Architecture

### 1. Manager (Main Thread)
- **Role**: Silent background orchestrator. Runs `/h:init`, `/h:status`, `/h:health`, `/h:upgrade-harness`.
- **Constraint**: Never writes feature code or specs. Only routes subagents and maintains state machine.

### 2. Collaborator
- **Role**: Front-line agent. Runs `/h:triage`, `/h:bug`, `/h:define`, `/h:design`, `/h:approve`.
- **Constraint**: Explores the problem space, clarifies ambiguities, talks to the user.

### 3. Sr Architect
- **Role**: Pre-build auditor. Runs `/h:review-pre-build`.
- **Constraint**: Validates `design.md` against the `BRD.md` before the human ever sees it.

### 4. Developer
- **Role**: Task planner. Runs `/h:tasks`.
- **Constraint**: Breaks the design into bite-sized, deterministic steps.

### 5. Jr Programmer
- **Role**: Executor. Runs `/h:build`.
- **Constraint**: Follows TDD strictly, implements one task at a time, never improvises.

### 6. Sr Tech Lead
- **Role**: Pre-verify auditor. Runs `/h:review-pre-verify`.
- **Constraint**: Reviews the code with fresh eyes to ensure it matches the original design without gaps.

### 7. Gatekeeper
- **Role**: Quality assurance. Runs `/h:verify`, `/h:release`.
- **Constraint**: Runs the tests, writes the verification report, and handles the release process with the human.

---

## Four Gates

| Gate | Trigger | Checker | Escalation |
|------|---------|---------|------------|
| **1. Sr Architect Review** (agent)| After `design.md` created | Sr Architect compares design vs BRD | PASS → proceed to human; FAIL → back to design |
| **2. Design Approval** (human) | After pre-build review passes | Human reviews design | Request changes → redesign; Approve → proceed to tasks |
| **3. Sr Tech Lead Review** (agent)| Auto-triggered after build | Sr Tech Lead compares design vs code | PASS → verify; FAIL → back to build (fix only) |
| **4. Release Approval** (human) | After `verification.md` filled | Human reviews verification report | Approve → merge and release; Reject → fix and re-verify |
