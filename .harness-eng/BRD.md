# Business Requirements Document
# Project: harness-eng
# Date: 2026-06-22
# Status: Draft
# Last Updated: 2026-06-22

---

## Executive Summary

harness-eng is a file-based development harness for AI coding assistants that provides structured workflows, smart templates, and quality gates for serious software development. It eliminates agent drift, context loss, and scope creep through a workflow with four gates (two human approval, two automated agent quality reviews).

**Target audience:** Serious programmers and teams building production systems.

**Core value:** Ensures agents follow a disciplined process with human oversight at critical points.

---

## Strategic Goal: Level 4 Agentic Engineering

Our ultimate target is to achieve **Level 4 (Product Owner: Spec-driven development)** as defined in the [Agentic Engineering framework](https://avons.github.io/notes/agentic-engineering/?v=1.1). 

At this level, the human stops thinking like a developer and starts thinking like a product owner. The human's job is to write a precise, unambiguous spec, debate it with the AI, set constraints, and approve the design. Then, the human steps away. The AI agent takes over, autonomously navigating the implementation loop (tasks → build → review → verify) until all tests pass. Hours later, the human returns only to verify the final result. 

Both the file-based harness and the future native plugin are explicitly designed to force this paradigm shift.

---

## Stakeholders

| Role | Name/Team | Interest |
|------|-----------|---------|
| Solo developer | — | Structured workflow without ceremony overhead |
| Small team | — | Parallel work with shared context |
| Enterprise team | — | Compliance, audit trails, quality gates |
| AI agent | — | Clear instructions, constrained templates, predictable workflow |

---

## Problems Being Solved

1. **Agent drift** — AI agents agree with users and build confident wrong answers
2. **Context loss** — agents forget decisions between sessions
3. **No quality gates** — code ships without architecture review
4. **Scope creep** — features grow beyond original intent
5. **Terminology drift** — same words mean different things across sessions
6. **Missing features** — agents silently drop requirements during spec creation
7. **Design drift** — implemented code diverges from approved design

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Workflow steps | 11 | init → review-pre-build → define → design → approve → tasks → build → review-pre-verify → verify → release |
| Quality gates | 4 | Approval Gate Human (2): Design, Release. Quality Gate Agent (2): Sr Architect pre-build, Sr Tech Lead pre-verify |
| Implicit gate chain | 4 documents | review-pre-build.md → design.md → review-pre-verify.md → verification.md (Ref markers) |
| Agent personas | 7 | Manager, Collaborator, Sr Architect, Developer, Jr Programmer, Sr Tech Lead, Gatekeeper |
| SST golden rules | 6 | Simple, Clear, Direct, Single Source of Truth, Testable, Trustworthy |
| Auto-loop | build→review→fix | Build triggers review; FAIL routes back; PASS auto-approves via sed |
| Foundation alignment | 1-time check | review-pre-build verifies BRD→source + phases→BRD at project inception |

---

## Design Decisions (Phase-0)

The following decisions were made during Phase-0 foundation work and gate analysis. They shape the canonical product source.

### Features (User Stories)

- **As a Human User**, I need two strict approval gates (design and release) so that I maintain ultimate control over the architecture and production code without having to micro-manage the implementation.
- **As a Manager persona**, I need to silently orchestrate the workflow in the background across loops so that the correct subagent is spawned and gates are respected.
- **As a Collaborator persona**, I need to be the front-line agent that triages bugs, drafts specs, clarifies ambiguities, and presents designs to the human for approval.
- **As a Sr Architect persona**, I need to audit the proposed design against the BRD and constitution so that I can catch architectural gaps before the human ever reviews it.
- **As a Developer persona**, I need to break the approved design down into granular tasks so that implementation is strictly ordered, traceable, and bite-sized.
- **As a Jr Programmer persona**, I need to execute tasks using Test-Driven Development (TDD) so that the code is built reliably and verified instantly.
- **As a Sr Tech Lead persona**, I need to review the implemented code against the original design so that I can automatically catch any divergence and route it back for fixes before verification.
- **As a Gatekeeper persona**, I need to run tests and fill out a verification report so that the human can confidently approve the release.
- **As a Human User**, I need to easily initialise the project (`/h:init`) on both greenfield and brownfield repositories so that the system auto-detects the state and bootstraps the harness seamlessly.
- **As a Human User**, I need to easily upgrade the harness (`/h:upgrade-harness`) so that I receive the newest templates and commands without losing my local rules.
- **As a Human User**, I need to submit bugs and change requests (`/h:bug`) so that the Collaborator can intelligently triage them (fix immediately, fold into active phase, or defer to backlog).

### System Scenarios

To ensure the harness acts as an intelligent file-based state machine (and later, a native plugin), it must auto-detect and handle the following scenarios:

**1. Project Initialisation (`/h:init`)**
- *Pure Greenfield*: No documents exist. The harness collaborates with the user to brainstorm and build the BRD and Architecture Docs (ADR) from scratch before generating Phase 0.
- *Prepped Greenfield*: The user has done their homework and placed a BRD and ADR in the root. The harness auto-detects them, parses them, and scaffolds the Phase 0 templates directly.
- *Brownfield*: An existing codebase exists with code and documentation. The harness reads the repository, extracts domain knowledge, infers the current state, and writes the baseline BRD and ADR retroactively.

**2. Harness Upgrades (`/h:upgrade-harness`)**
- *System Update*: A human triggers an upgrade. The Manager fetches the newest harness templates and commands, migrating the project safely without losing local constitution rules.

**3. Triage & Defect Management (`/h:triage` / `/h:bug`)**
- *Critical Bug*: A critical issue is reported. The Collaborator creates a `bugfix/` branch and rapidly bundles definition and design into a single step, producing both a spec and design with impact analysis before stopping for human approval (`/h:approve <bug-id>`).
- *WIP Phase Issue*: A change request (CR) is submitted that applies to the currently active phase. The Collaborator routes it into the active phase as an immediate CR.
- *Non-critical / Out-of-Scope*: A feature or non-critical bug is reported. The Collaborator adds it to the `.harness-eng/docs/backlog.md` and defers it.

**4. Phase Definition (`/h:define`)**
- *Backlog Grooming*: When starting a new phase, the Collaborator explicitly reads `.harness-eng/docs/backlog.md`. It brings relevant deferred items into the new phase's `spec.md` and explicitly marks them as closed in the backlog.

---

### Workflow Architecture
- **11-step workflow**: init → define → design → review-pre-build → approve → tasks → build → review-pre-verify → verify → release
- **7 agent personas**: Manager (silent orchestration), Collaborator (triage/define/design/approve), Sr Architect (review-pre-build), Developer (tasks), Jr Programmer (build), Sr Tech Lead (review-pre-verify), Gatekeeper (verify/release)
- **Agent definitions live in `agents/<name>/agent.md`** — canonical product source, referenced via `agent:` YAML frontmatter in commands
- **4 gates**: Design approval (human), Sr Architect pre-build review (agent), Sr Tech Lead pre-verify review (agent), Release approval (human)

### Auto-Loop (build → review → fix)
- Build auto-triggers Sr Tech Lead review (step 10 in build.md)
- Review routes FAIL/CONDITIONAL back to build for fixes
- Review auto-approves via `sed` on PASS (writes `**Ref**: APPROVED`)
- Scenario detection in build: initial / review_fix / verify_fix
- 3 fix attempts → BLOCKED → escalate to human

### Implicit Gate Chain
- Cross-document `**Ref**` markers: review-pre-build.md → design.md → review-pre-verify.md → verification.md
- Each gate blocks the next step via bash-level `grep` + `exit 1` checks
- No human needed for agent gate — auto-loop enforces without re-entry

### Hard Guardrails & STOP Conditions
- **Ref-Based Gates**: The system relies on hardcoded `**Ref**: APPROVED` markers injected into documents (`review-pre-build.md`, `design.md`, `review-pre-verify.md`, `verification.md`) to unlock the next phase.
- **Bash-Level STOP Conditions**: Prerequisites are enforced programmatically. If a gate is not met, the command triggers an explicit `exit 1` (STOP) condition, preventing the agent from hallucinating progress and forcing it to route back to the correct phase to fix the gap.
- **Constitution Enforcement**: A mandatory Constitution Check is baked directly into the templates, forcing agents to explicitly validate core constraints before proceeding.

### SST Golden Rules
- Universal rules placed in AGENTS.md (shipped to all projects)
- Also included in init-generated CONSTITUTION.md for each downstream project
- 6 categories: Simple, Clear, Direct, Single Source of Truth, Testable, Trustworthy
- YAML format for deterministic parsing by any LLM

### Foundation Alignment
- The harness ensures architectural alignment by validating proposed designs against the original Business Requirements Document (BRD) and project constitution.
- This validation occurs during the Pre-Design loop via the Sr Architect persona, catching architectural gaps before human review.

### Operational Commands
- `/h:health`: Provides compliance feedback by auditing agent adherence to the project constitution.
- `/h:status`: Displays dashboard data and the current state of the workflow and phases.
- `/h:upgrade-harness`: Safely pulls down the latest harness templates without overwriting local project rules.

---

## Constraints

- Language: Python (status server), Shell (scripts), Markdown (everything else)
- No runtime dependencies — file-based convention only
- Must work on macOS and Linux
- Must support any AI agent that can read/write files
- Python 3.8+ required for status server
- Agent-agnostic — rules work with any agent that reads files

---

## Out of Scope

- Vibe coding support
- Full agile ceremony (sprints, backlogs, velocity tracking)
- Project management features (Jira integration, burndown charts)
- Runtime tooling (CLI, server, API beyond status dashboard)
- Multi-language code generation

---

## System Events (Plugin Architecture Readiness)

To support the transition from a purely file-based harness to an extensible plugin-based system, the harness orchestrator MUST emit the following system events (hooks) that plugins can subscribe to:

- `pre-init` / `post-init`: Fired before/after the `/h:init` command scaffolds the repository.
- `pre-design` / `post-design`: Fired before/after the Collaborator generates `design.md`. Plugins can use this to inject mandatory security or compliance constraints.
- `pre-build` / `post-build`: Fired before/after the Jr Programmer executes TDD tasks. 
- `pre-verify` / `post-verify`: Fired around the Gatekeeper's testing phase.
- `on-gate-rejection`: Fired whenever a human or agent gate (e.g., `/h:review-pre-build` or `/h:approve`) returns a FAIL or REJECTED status.
- `on-release-approved`: Fired when the human explicitly approves a release, allowing plugins to trigger external deployments or CI pipelines.
