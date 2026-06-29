---
name: spec
description: >
  Feature specification for the workflow command system.
  Each command is a step-by-step instruction set for the agent
  with pre-flight checks, execution steps, and gate enforcement.
---

# Spec: Workflow Commands

**Feature**: F001 — Workflow Commands
**Created**: 2026-06-22
**Status**: Draft
**Ref**: PENDING

**Input**: 14 markdown command files at `commands/` that define the harness-eng workflow. Each command has YAML frontmatter, pre-flight bash blocks, step-by-step instructions, and constraints sections.

---

## User Stories

### Story 1 — Project Initialization (Priority: P1)

As a developer starting a new project, I want to run a single init command that scaffolds the entire harness structure so I can begin feature work immediately.

**Why this priority**: Without init, there is no project foundation. All other commands depend on it.
**Independent test**: Run init on an empty directory — verify all expected files and symlinks are created.

**Acceptance Scenarios**:

1. **Given** an empty project directory with a template repo, **When** I run `/h:init`, **Then** `.harness-eng/CONSTITUTION.md`, `BRD.md`, `ARCHITECTURE.md`, `technology.yaml`, and `VERSION` are created
2. **Given** a project that already has `.harness-eng/`, **When** I run `/h:init`, **Then** I am offered 3 choices: upgrade, re-init (with backup), or cancel
3. **Given** a greenfield project with no source documents, **When** init runs, **Then** the agent asks template-driven questions grouped by document (BRD, ARCHITECTURE, CONSTITUTION, tools)

---

### Story 2 — Feature Definition and Design (Priority: P1)

As a developer, I want to define features using structured specs and create technical designs so I know WHAT to build and HOW before writing code.

**Why this priority**: Spec and design are the contracts the agent builds against. Without them, drift is guaranteed.
**Independent test**: Run define then design — verify spec.md and design.md are produced with all required sections.

**Acceptance Scenarios**:

1. **Given** an approved BRD, **When** I run `/h:define`, **Then** the agent reads the BRD and architecture, asks clarifying questions, and produces a spec.md with Given/When/Then stories
2. **Given** a BRD with 5+ requirements, **When** I run `/h:define`, **Then** the agent organizes features into phases and presents the phase plan for approval
3. **Given** an approved spec.md, **When** I run `/h:design`, **Then** the agent produces a design.md with component map, data flow, interfaces, file layout, verification criteria, and constitution check
4. **Given** a design that references third-party SDKs, **When** the agent creates the design, **Then** it fetches and reads official documentation to verify correct API usage

---

### Story 3 — Human Design Approval (Priority: P1)

As a project owner, I want to review and approve designs before any code is written so I control what gets built.

**Why this priority**: This is Gate 1 — the primary human control point. No code should be written without approved design.
**Independent test**: Run approve — verify `**Ref**: APPROVED` is written to design.md only after explicit human confirmation.

**Acceptance Scenarios**:

1. **Given** a design.md with `**Ref**: PENDING`, **When** I run `/h:approve`, **Then** the agent presents the design summary and waits for my explicit decision
2. **Given** I confirm approval, **When** the agent writes the marker, **Then** `**Ref**: APPROVED` replaces `**Ref**: PENDING` in design.md
3. **Given** a design with `**Ref**: PENDING`, **When** build is attempted, **Then** the pre-flight check in build.md greps for REF marker and blocks execution

---

### Story 4 — Task Breakdown and Implementation (Priority: P1)

As a developer, I want the agent to break an approved design into granular tasks and implement them one at a time using TDD so each unit is small, testable, and traceable.

**Why this priority**: Task granularity and TDD are the core quality mechanisms. Without them, the agent generates large untestable code blocks.
**Independent test**: Run tasks then build — verify each task produces a commit, tests exist, and commits follow `type(ID): description`.

**Acceptance Scenarios**:

1. **Given** an approved design.md, **When** I run `/h:tasks`, **Then** the agent produces tasks.md with ordered tasks, each with description, dependencies, and file scope
2. **Given** tasks.md, **When** I run `/h:build`, **Then** the agent processes one task at a time: write test, confirm fail, implement, confirm pass, commit
3. **Given** a task fails 3 consecutive fix attempts, **When** the agent tries to continue, **Then** it stops, writes a BLOCKED section, and escalates to the human

---

### Story 5 — Pre-Build Gap Analysis (Priority: P1)

As a project owner, I want an automated check that validates BRD → spec → design alignment before any code is written so gaps are caught early.

**Why this priority**: Catches missing requirements, misaligned designs, and untestable stories before implementation waste occurs.
**Independent test**: Run review-pre-build — verify the report checks all 6 categories and produces PASS/CONDITIONAL/FAIL.

**Acceptance Scenarios**:

1. **Given** a completed design and tasks.md, **When** review-pre-build runs, **Then** it checks: BRD coverage, spec completeness, design alignment, tech compliance, skill compliance, and testability
2. **Given** critical gaps are found, **When** the review completes, **Then** the verdict is FAIL and build is blocked
3. **Given** the verdict is FAIL, **When** the agent reports, **Then** specific fixes with file paths and line numbers are given

---

### Story 6 — Post-Build Review (Priority: P1)

As a project owner, I want an automated Sr Tech Lead review that compares the implementation against the design so gaps between spec and code are caught.

**Why this priority**: This is Gate 2 — the automated quality gate. Ensures the implementation matches the approved design.
**Independent test**: Run review-pre-verify — verify it checks every story, file, and test against the design.

**Acceptance Scenarios**:

1. **Given** completed build with all tasks committed, **When** review-pre-verify runs, **Then** the agent compares implementation against design and spec line by file
2. **Given** gaps are found, **When** the review completes with FAIL, **Then** the agent routes back to build for fixes
3. **Given** no critical gaps, **When** the review completes with PASS, **Then** the agent proceeds to verify

---

### Story 7 — Test Execution and Verification (Priority: P1)

As a project owner, I want tests to run and acceptance criteria to be checked before release so I know the feature works.

**Why this priority**: Without verification, there is no evidence the feature is complete and working.
**Independent test**: Run verify — verify all tests pass and a verification.md report is produced.

**Acceptance Scenarios**:

1. **Given** a completed build with passing review, **When** I run `/h:verify`, **Then** the agent runs the full test suite and checks acceptance criteria against spec.md
2. **Given** all tests pass and criteria are met, **When** verification completes, **Then** verification.md is produced with status PASS
3. **Given** some tests fail, **When** verification completes, **Then** verification.md is produced with status FAIL and details

---

### Story 8 — Release Workflow (Priority: P1)

As a project owner, I want to approve and ship completed features through a structured release process so nothing ships without my explicit approval.

**Why this priority**: This is Gate 3 — the final human control point. Prevents unapproved code from reaching production.
**Independent test**: Run release — verify PR is created, feature is archived, and Release Ref marker is set.

**Acceptance Scenarios**:

1. **Given** a passing verification.md, **When** I run `/h:release`, **Then** the agent checks for `**Release Ref**: APPROVED` and stops if missing
2. **Given** I confirm release approval, **When** the agent writes the marker and creates a PR, **Then** the PR includes verification evidence in the body
3. **Given** the PR is merged, **When** cleanup runs, **Then** the feature branch is deleted, the feature is archived, and SLICE_LOG is updated

---

### Story 9 — Project Status and Health (Priority: P2)

As a project owner, I want to check project status and harness compliance so I know what's happening and whether the agent is following rules.

**Why this priority**: Status and health are operational visibility — important but not blocking feature delivery.
**Independent test**: Run status then health — verify both produce readable reports.

**Acceptance Scenarios**:

1. **Given** an active project, **When** I run `/h:status`, **Then** the agent shows version, active features, phase progress, SLICE_LOG freshness, and actionable next step
2. **Given** the agent may have skipped rules, **When** I run `/h:health`, **Then** the agent runs 10 compliance checks across CRITICAL, HIGH, and MEDIUM severities
3. **Given** a CRITICAL violation is found, **When** health check completes, **Then** the agent uses strong language and provides clear remediation steps

---

### Story 10 — Bug and Request Triage (Priority: P2)

As a project owner, I want incoming issues classified and routed correctly so bugs get fast-tracked and features follow the full workflow.

**Why this priority**: Triage prevents incorrect workflow routing. Bugs need shortened paths; features need full gates.
**Independent test**: Submit a bug description — verify triage classifies it and routes to the bug workflow.

**Acceptance Scenarios**:

1. **Given** an incoming issue, **When** triage runs, **Then** it classifies as Bug/CR/Feature/Deferred with rationale
2. **Given** a bug is classified, **When** the bug workflow runs, **Then** it follows a shortened path: regression test first, fix, verify
3. **Given** a feature is classified, **When** the feature workflow runs, **Then** it follows the full 11-step workflow

---

## Edge Cases

- What happens when init is run on a project that already has `.harness-eng/`? (3 choices: upgrade / re-init with backup / cancel)
- What happens when build is called but no approved design exists? (pre-flight grep blocks execution)
- What happens when verify finds critical test failures? (verification.md shows FAIL, release gate blocks)
- What happens when the Sr Tech Lead review keeps finding gaps? (3-fix-attempt limit → BLOCKED escalation)
- What happens when a bug is reported during an active phase vs after release? (branch from phase branch vs from main)
- What happens when `version.txt` exists at project root? (init symlinks `.harness-eng/VERSION` to it)
- What happens when the agent runs a command without first reading CONSTITUTION.md? (health check catches it as CRITICAL)

---

## Functional Requirements

- **FR-001**: Every command MUST have YAML frontmatter with `name`, `description`, and trigger phrases
- **FR-002**: Every command MUST include pre-flight checks that call scripts and block on failure
- **FR-003**: Gate commands (approve, release) MUST present evidence to human and wait for explicit decision
- **FR-004**: Build command MUST enforce TDD: test first, confirm fail, implement, confirm pass, commit
- **FR-005**: Build command MUST stop after 3 failed fix attempts and escalate to human
- **FR-006**: Review commands MUST compare documents (BRD→spec→design or design→code) and produce PASS/CONDITIONAL/FAIL verdict
- **FR-007**: Init command MUST detect existing `.harness-eng/` and offer 3 choices before proceeding
- **FR-008**: Init command MUST create symlinks for product source (commands, scripts, hooks, skills, feature templates) and copies for project-specific files
- **FR-009**: Status command MUST show version, active features, phase progress, SLICE_LOG freshness
- **FR-010**: Health command MUST run all 10 compliance checks every time

---

## Success Criteria

| # | Criterion | Measurable? |
|---|-----------|-------------|
| SC-001 | All 14 commands exist and are callable via their trigger phrases | ✅ |
| SC-002 | Each command produces the documented output artifacts | ✅ |
| SC-003 | Gate commands correctly block when markers are missing | ✅ |
| SC-004 | Build enforces TDD for every task | ✅ |
| SC-005 | Review commands produce correct verdicts based on gap analysis | ✅ |
| SC-006 | Init handles greenfield, brownfield, and re-init correctly | ✅ |
| SC-007 | Status and health produce readable reports without errors | ✅ |

---

## Key Entities

- **Command**: A markdown file with YAML frontmatter, steps, and constraints that instructs the agent on a specific workflow action
- **Pre-flight**: A bash block at the start of a command that runs scripts and exits if conditions aren't met
- **Gate Marker**: A cross-document reference string (`**Ref**: APPROVED`, `**Release Ref**: APPROVED`) that blocks workflow progression
- **TDD Loop**: The test-fail-implement-pass-commit cycle for each task in build
- **Verdict**: The output of a review command: PASS, CONDITIONAL, or FAIL

---

## Assumptions

- The agent has file read/write access to the project directory
- The agent can execute bash commands (for pre-flight checks and scripts)
- Python 3 and common shell utilities are available on the system
- Git is available for branch management and commit tracking
- The agent follows the instruction ordering in each command file

---

## Out of Scope

- A GUI or web interface for the workflow (file-based only)
- Automatic enforcement of agent behavior beyond bash-level gates
- Integration with external project management tools (Jira, Trello)
- Runtime monitoring or alerting beyond the status dashboard

---

## Validation Checklist

**Content Quality:**
- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

**Requirement Completeness:**
- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] Success criteria are technology-agnostic
- [x] All acceptance scenarios use Given/When/Then
- [x] Edge cases identified
- [x] Scope clearly bounded

**Feature Readiness:**
- [x] All stories have acceptance criteria
- [x] Stories cover primary user flows
- [x] Feature meets measurable success criteria
- [x] No implementation details in spec
