---
name: design
description: >
  Technical architecture design for agent definitions.
  4 persona-specific agent.md files at agents/<persona>/agent.md
  that define behavior patterns, command ownership, gate
  responsibilities, and output artifacts for each role in the
  harness workflow. Personas form a sequential pipeline from
  requirements to release.
---

# Design: Agent Definitions

**Branch**: `main`
**Date**: 2026-06-22
**Spec**: `phases/phase-0-foundation/features/active/F006-agents/spec.md`
**Ref**: APPROVED
**Approved by**: PENDING
**Approved date**: PENDING

**Input**: Feature specification for agent definitions

---

## Summary

4 persona directories at `agents/<persona>/agent.md` that define how the agent behaves for each workflow phase. Personas form a linear pipeline: Collaborator (define/design) → Developer (tasks/build) → Sr Tech Lead (review) → Gatekeeper (approve/release). Each persona owns specific commands, operates in a defined mode, enforces specific gates, and produces specific output artifacts. A single agent session switches personas as the workflow progresses.

---

## Technical Context

**Language/Version**: Markdown (agent.md files)

**Primary Dependencies**: None (agent.md files are instructions, not code)

**Storage**: File-based at `agents/<persona>/agent.md`

**Testing**: Manual — verify agent behavior matches persona description when executing commands

**Target Platform**: Any AI agent that reads markdown and follows role instructions

**Performance Goals**: N/A

---

## Constitution Check

| Rule | Status | Notes |
|------|--------|-------|
| I. TDD Mandatory | ✅ PASS | Developer persona enforces TDD per task |
| II. Std Lib First | ✅ PASS | Skills define library choices — personas don't override |
| III. Verify Before Assuming | ✅ PASS | Every persona has a "verify gate before act" step |
| IV. Files Are Instructions | ✅ PASS | agent.md files ARE the instructions for persona behavior |
| V. Human in Control | ✅ PASS | Gatekeeper requires human; Sr Tech Lead is agent but reviewable |

---

## Architecture

### Component Map

```
┌─────────────────────────────────────────────────────────────────────────┐
│                       PERSONA PIPELINE                                   │
│                                                                         │
│  ┌────────────┐   ┌────────────┐   ┌────────────┐   ┌────────────┐   │
│  │ COLLABORATOR│   │ DEVELOPER  │   │SR TECH LEAD│   │ GATEKEEPER │   │
│  │             │   │            │   │            │   │            │   │
│  │ Mode: Ask   │   │ Mode: Do   │   │ Mode: Check│   │ Mode: Gate │   │
│  │             │   │            │   │            │   │            │   │
│  │ Commands:   │   │ Commands:  │   │ Commands:  │   │ Commands:  │   │
│  │ • define    │──▶│ • tasks    │──▶│ • review-  │──▶│ • approve  │──▶│
│  │ • design    │   │ • build    │   │   pre-build│   │ • release  │   │
│  │             │   │            │   │ • review-  │   │            │   │
│  │             │   │            │   │   pre-     │   │            │   │
│  │             │   │            │   │   verify   │   │            │   │
│  └────────────┘   └────────────┘   └────────────┘   └────────────┘   │
│         │                │                │                │          │
│         │ gate:          │ gate:          │ gate:          │ gate:    │
│         │ spec complete  │ design         │ code ≥ design  │ release  │
│         │                │ approved       │ skill compliant│ approved │
│         ▼                ▼                ▼                ▼          │
│  ┌────────────┐   ┌────────────┐   ┌────────────┐   ┌────────────┐   │
│  │ Output:    │   │ Output:    │   │ Output:    │   │ Output:    │   │
│  │ spec.md    │   │ impl code  │   │ review     │   │ release    │   │
│  │ design.md  │   │ tests      │   │ report     │   │ record     │   │
│  └────────────┘   └────────────┘   └────────────┘   └────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘

                     ┌──────────────────┐
                     │  AGENT SESSION    │
                     │  (single AI)      │
                     │                   │
                     │  Reads persona    │
                     │  agent.md for     │
                     │  current command  │
                     │                   │
                     │  Switches mode    │
                     │  at command       │
                     │  boundaries       │
                     └──────────────────┘
```

| Persona | Commands | Mode | Gate | Output |
|---------|----------|------|------|--------|
| Collaborator | define, design | Collaborative — ask questions, challenge assumptions, clarify requirements | Spec complete before handoff | spec.md, design.md |
| Developer | tasks, build | Jr Programmer — follow instructions, never improvise | Design approved before build | Implementation code, tests, tasks.md |
| Sr Tech Lead | review-pre-build, review-pre-verify | Reviewer — compare design vs code, check skill compliance | Code matches design, tests pass | Review report (PASS/CONDITIONAL/FAIL) |
| Gatekeeper | approve, release | Gatekeeper — require human confirmation, enforce marker chain | Human approved, all prior gates pass | Approval markers, release record |

### Data Flow

```
Workflow Handoff Chain:

  [Human] --input--> [Collaborator] --spec.md--> [Human approves]
  --approved spec--> [Developer] --tasks.md--> [Developer builds]
  --impl code--> [Sr Tech Lead reviews] --PASS--> [Gatekeeper]
  --verification.md--> [Human approves release] --> DONE

Persona Switching Logic:

  1. Agent receives command (e.g., "build it")
  2. Agent reads command frontmatter → identifies persona (Developer)
  3. Agent reads agents/developer/agent.md
  4. Agent follows persona's mode (Jr Programmer — no improvising)
  5. Agent enforces persona's gates (check approved designs)
  6. Agent executes command steps
  7. Agent produces persona's output artifact
  8. Agent presents result to user and suggests next command
  9. On next command, agent re-reads persona → may switch

Gate Ownership Detail:

  Gate                          Owned By        Mechanism
  ─────────────────────────────────────────────────────────
  Spec complete                 Collaborator    All sections filled
  Design approved               Developer       grep design.md for Ref: APPROVED
  Pre-build: design reviewed    Sr Tech Lead    review-pre-build report
  Pre-verify: code ≥ design     Sr Tech Lead    review-pre-verify report
  Human approval (design)       Gatekeeper      approve command
  Human approval (release)      Gatekeeper      release command
```

### Interfaces

```markdown
# agent.md structure (all 4 personas follow this):
---
name: <persona>
commands:
  - <command-1>
  - <command-2>
gate: <gate-description>
---

## Role
<persona description>

## Mode
<operating mode description>

## Gates
- <gate-1>: <enforcement mechanism>
- <gate-2>: <enforcement mechanism>

## Output
- <artifact-1>: <description>
- <artifact-2>: <description>
```

```bash
# Detection — how the agent determines current persona:
grep -A2 "name:" commands/<triggered_command>.md | head -4
# → agent: developer  (from command YAML frontmatter)

# Load — agent reads corresponding file:
cat agents/developer/agent.md
```

---

## File Layout

**New Files:** None — all 4 agent.md files exist.

**Modified Files:** None — agent definitions are stable.

---

## Research

| Decision | Rationale | Alternatives Rejected |
|----------|-----------|----------------------|
| 4 fixed personas | Matches the 4 workflow phases (define, build, review, release) | Single persona (no specialization), N dynamic personas (over-engineering) |
| Commands hand-picked per persona | Clean ownership — no ambiguity about who handles what | All personas handle all commands (no gate enforcement) |
| Agent reads persona per command | Allows single-session switching without restart | Fixed persona per session (can't switch mid-workflow) |
| agent.md in dedicated directory | Discoverable — `ls agents/` lists all personas | Embedded in command files (hard to find, duplicates across commands) |

---

## Complexity Tracking

N/A — No constitutional violations.

---

## Design Confidence

| Claim | Confidence | Source |
|-------|-----------|--------|
| All 4 agent.md files exist | VERIFIED | `ls agents/*/agent.md` |
| Each agent.md defines Commands | VERIFIED | grep for "commands" in each |
| Each agent.md defines Mode | VERIFIED | grep for "Mode" in each |
| Each agent.md defines Gates | VERIFIED | grep for "Gates" in each |
| Each agent.md defines Output | VERIFIED | grep for "Output" in each |
| Gatekeeper requires human confirmation | VERIFIED | approve.md and release.md pre-flight |

---

## Self-Challenge

**What is the strongest reason this design might be wrong?**
The persona pipeline is sequential and assumes linear progression (define → build → review → release). In practice, work may loop back (review → re-build → re-review), and the Sr Tech Lead persona doesn't have a "re-review" mode that handles incremental changes.

**What assumption am I making that I haven't stated?**
That the agent will reliably switch personas at command boundaries. If the agent caches persona state or ignores the persona instruction, it may behave as Developer during a review command.

**What would need to be true for this to fail?**
If the command YAML frontmatter doesn't specify which persona owns it, the agent has no way to know which agent.md to read. Currently, each command's frontmatter must include `agent: <persona>` mapping.

---

## Validation Checklist

**Architecture:**
- [x] Component map is complete
- [x] Data flow is documented
- [x] Interfaces are defined
- [x] File layout specifies new vs modified files

**Constitution:**
- [x] All constitution rules checked
- [x] Complexity tracking filled (if violations exist)

**Research:**
- [x] All NEEDS CLARIFICATION items resolved
- [x] Technical decisions documented with rationale
- [x] Alternatives considered and rejected

**Quality:**
- [x] Design confidence tags filled (VERIFIED/INFERRED/ASSUMED)
- [x] Self-challenge completed
- [x] No implementation code (design only)
