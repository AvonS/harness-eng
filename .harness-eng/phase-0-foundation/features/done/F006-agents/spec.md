---
name: spec
description: >
  Feature specification for agent definitions.
  4 persona-specific agent instruction files that define
  the harness-eng agent roles: Collaborator (define, design),
  Developer (tasks, build), Sr Tech Lead (review-pre-build,
  review-pre-verify), and Gatekeeper (approve, release).
  Each agent file commands a persona, mode of operation,
  gate responsibilities, and output artifacts.
---

# Feature: Agent Definitions

**Feature**: F006 — Agent Definitions
**Status**: Complete (reverse-engineered)
**Ref**: PENDING

---

## User Stories

### Story 1 — Persona-Specific Instructions (Priority: P1)

The harness dispatches work to different agent personas. Each persona has its own agent.md file that tells the agent how to behave: what commands to handle, what mode to operate in, what gates to enforce, and what artifacts to produce.

**Why this priority**: Without persona-specific instructions, all agents behave identically — no specialist knowledge, no gate enforcement.

**Independent test**: Read each agent.md and verify it has sections for: Commands, Mode, Gates, Output, and Role Description.

**Acceptance Scenarios**:

1. **Given** the Collaborator persona (`agents/collaborator/agent.md`), **When** the agent is assigned to the define command, **Then** it operates in "Collaborator" mode — asking clarifying questions, challenging assumptions, interacting with the human.
2. **Given** the Developer persona (`agents/developer/agent.md`), **When** the agent is assigned to the build command, **Then** it operates in "Jr Programmer" mode — following instructions precisely, never improvising.
3. **Given** the Sr Tech Lead persona (`agents/sr-tech-lead/agent.md`), **When** the agent is assigned to review-pre-verify, **Then** it operates in "Reviewer" mode — comparing design vs code, checking compliance.
4. **Given** the Gatekeeper persona (`agents/gatekeeper/agent.md`), **When** the agent is assigned to the approve or release command, **Then** it requires explicit human confirmation before proceeding.

---

### Story 2 — Gate Assignment (Priority: P1)

Each persona is responsible for specific gates. Collaborator verifies spec completeness before handoff. Developer checks design approval before building. Sr Tech Lead gates pre-verify. Gatekeeper gates release.

**Why this priority**: Gates are meaningless without assigned responsibility. Each persona owns specific gates in the workflow.

**Independent test**: Map each persona to its gates and verify the gate is referenced in the persona's agent.md.

**Acceptance Scenarios**:

1. **Given** the Developer persona about to start build, **When** the agent checks design approval, **Then** it calls `check-approved-designs.sh` — if exit non-zero, it blocks (this is a gate owned by the Developer persona).
2. **Given** the Gatekeeper persona about to execute release, **When** the agent checks verification.md for **Release Ref**: APPROVED, **Then** it blocks if not approved (this is a gate owned by the Gatekeeper persona).

---

### Story 3 — Output Artifact Handoff (Priority: P2)

Each persona produces specific artifacts as output. Collaborator produces spec.md. Developer produces implementation code. Sr Tech Lead produces review reports. Gatekeeper produces release records. Artifacts flow between personas in sequence.

**Why this priority**: Clean handoff prevents dropped context. The output of one persona is the input of the next.

**Independent test**: Trace an artifact chain (e.g., spec.md → design.md → tasks.md → implementation → verification.md) and verify each persona produces its expected artifact.

**Acceptance Scenarios**:

1. **Given** the Collaborator completes a spec, **When** the human approves it, **Then** the handoff to the next persona (Designer or Developer) includes the spec.md as input.
2. **Given** the Developer completes a build task, **When** the Sr Tech Lead reviews it, **Then** the review references both the design.md and the implemented code.

---

### Story 4 — Mode Switching (Priority: P2)

A single agent may need to switch personas during a session. The agent reads the relevant agent.md to determine the current mode (Collaborator, Developer, Reviewer, Gatekeeper) and adjusts behavior accordingly.

**Why this priority**: A single AI session may span multiple workflow phases. The agent must know which hat to wear at each step.

**Independent test**: Simulate a full workflow session and verify the agent switches persona at each phase boundary.

**Acceptance Scenarios**:

1. **Given** the agent is in Developer mode during build, **When** the build completes and review-pre-verify begins, **Then** the agent switches to Sr Tech Lead mode without a new session.
2. **Given** the agent receives a command that belongs to a different persona, **When** it processes the command, **Then** it reads the new persona's agent.md before executing.

---

## Edge Cases

- What if two personas have conflicting instructions? The most recent command's persona takes precedence — no mixing.
- What if an agent.md is missing or malformed? The agent should use a default persona (Developer) and log a warning.
- What if the same agent is asked to both define and approve? Gatekeeper gate (human approval) prevents a single agent from both defining and releasing.

## Functional Requirements

- **FR-001**: Each agent.md MUST define: Role Description, Commands, Mode, Gates, Output Artifacts.
- **FR-002**: Personas MUST enforce their assigned gates before proceeding.
- **FR-003**: Gatekeeper persona MUST require explicit human confirmation for approve and release.
- **FR-004**: The agent MUST switch personas when the command changes.
- **FR-005**: Agent.md files MUST be discoverable by directory listing under `agents/`.

## Success Criteria

| # | Criterion | Measurable? |
|---|-----------|-------------|
| SC-001 | All 4 agent.md files exist | ✅ File existence |
| SC-002 | Each agent.md defines Commands, Mode, Gates, Output | ✅ grep for sections |
| SC-003 | Gatekeeper blocks release without human confirmation | ✅ Human confirmation required |
| SC-004 | Developer blocks build without approved design | ✅ Exit code from pre-flight |
| SC-005 | Sr Tech Lead review produces PASS/CONDITIONAL/FAIL | ✅ Review output format |

## Key Entities

- **Agent Persona**: A named role with specific commands, mode, gates, and output artifacts.
- **agent.md**: Per-persona instruction file telling the agent how to behave.
- **Gate Responsibility**: Which workflow gate a persona is responsible for enforcing.
- **Artifact Handoff**: The output of one persona becomes the input of the next.

## Assumptions

- The agent can read and follow multiple agent.md files in a single session.
- Persona switching is explicit — the agent reads a new agent.md when the command changes.
- The agent respects persona boundaries (Developer doesn't approve their own work).

## Out of Scope

- Dynamic persona creation (personas are predefined).
- Cross-persona conflict resolution (personas have distinct commands — no overlap).
- Authentication or identity management (personas are instruction files, not user accounts).

## Validation Checklist

**Content Quality:**
- [x] No implementation details
- [x] Focused on user value and business needs
- [ ] Written for non-technical stakeholders
- [x] All mandatory sections completed

**Requirement Completeness:**
- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] All acceptance scenarios use Given/When/Then
- [x] Edge cases identified
- [x] Scope clearly bounded

**Feature Readiness:**
- [x] All stories have acceptance criteria
- [x] Stories cover primary user flows
- [x] Feature meets measurable success criteria
- [x] No implementation details in spec
