---
name: constitution-document
description: Big-picture template for the project constitution.

gates:
  - check: project purpose and core principles are defined
    on_fail: STOP, Cannot write constitution without purpose

actions:
  - Fill purpose, principles, gates, architecture rules, naming conventions, quality standards

outputs:
  - .harness-eng/CONSTITUTION.md

must_do:
  - SST Golden Rules and mandatory gates must be included verbatim

must_not_do:
  - Remove SST rules or mandatory gate definitions
---

# Constitution Template

**Version**: [CONSTITUTION_VERSION]
**Ratified**: [RATIFICATION_DATE]
**Last Amended**: [LAST_AMENDED_DATE]

---

## Comment Conventions

> *When generating this document, use these comment types:*

| Comment | Meaning | Gate impact |
|---------|---------|-------------|
| `<!-- NEEDS INPUT: -->` | Human may enhance this | Optional — gate passes |
| `<!-- MUST INPUT: -->` | Human must fill this | Required — gate fails if empty |
| `<!-- MISSED: -->` | Agent skipped, should have filled | Agent reviews |
| `<!-- CHECK AGENT: -->` | Agent may have filled incorrectly | Agent verifies |

---

## Project Purpose

> *What are we building and why? This grounds every decision.*

[ONE_SENTENCE_SUMMARY]

**Full requirements:** See `BRD.md`
**Domain context:** See `domain-ctx.txt` (if created)

---

## SST Golden Rules

> *Universal rules for every document. Hardcoded — do not modify.*

**Simple:** One concept per file. Every instruction is a single action verb. No conditional language.
**Clear:** Every step produces the same output regardless of LLM. No ambiguous terms. Every file path is explicit.
**Direct:** Tell the agent what TO DO, not what NOT to do. Gates use STOP with condition.
**Single Source of Truth:** Every rule exists in exactly one file. Agent definitions live in `agents/<name>/agent.md`.
**Testable:** Every document has a verification path. If you can't test it, remove the step.
**Trustworthy:** Never guess. Check file paths before referencing. After 3 failed attempts, STOP and escalate.

---

## Core Principles

### Harness Principles (Universal — Do Not Modify)

#### I. TDD Mandatory
Write tests first. Confirm failure. Implement. Pass. No feature is "done" without tests.

#### II. Std Lib First
Use standard library before adding dependencies. Justify every dependency addition.

#### III. Verify Before Assuming
Never assume a framework, library, or API feature exists without verifying. Check source, check docs, write a probe if uncertain.

#### IV. Files Are the Instructions
The harness works because the files are the instructions. The folder structure is the state machine.

#### V. Human in Control
The user owns the what and the why. The agent owns the how — within boundaries the user approved. Never self-approve.

### Project Principles (Must Be Filled — Project-Specific)

> *These principles are specific to THIS project. They define how the code should be structured, what patterns to use, and what constraints apply. Examples: "Game logic must be pure functions", "State transitions must be explicit", "UI layer must be separate from business logic".*

<!-- MUST INPUT: Add 2-5 project-specific principles -->

#### [PROJECT_PRINCIPLE_1_NAME]
[PROJECT_PRINCIPLE_1_DESCRIPTION]

#### [PROJECT_PRINCIPLE_2_NAME]
[PROJECT_PRINCIPLE_2_DESCRIPTION]

---

## Mandatory Gates

> *Three checkpoints that enforce quality. Never skip any gate.*

```yaml
gates:
  - name: "Design approval"
    type: human
    command: "/h:approve"
    blocks: "tasks, build"
    description: "Human reviews architecture before implementation"

  - name: "Sr Tech Lead review"
    type: agent
    command: "/h:review-pre-verify"
    blocks: "verify"
    description: "Agent compares design vs code, catches gaps"

  - name: "Release approval"
    type: human
    command: "/h:release"
    blocks: "merge"
    description: "Human approves final release"

must_not_do:
  - Skip any gate
  - Self-approve (agent cannot approve its own work)
  - Release without all gates passing
```

---

## 4-Persona Workflow

> *Universal personas. Hardcoded — do not modify.*

| Persona | Commands | Role |
|---------|----------|------|
| **Collaborator** | define, design | Explore problem space, challenge assumptions, create spec and design |
| **Developer** | tasks, build | Follow instructions precisely, TDD, one commit per task |
| **Sr Tech Lead** | review-pre-verify | Compare design vs code, identify gaps, assess quality |
| **Gatekeeper** | approve, release | Facilitate human gates — present evidence, wait for decision |

---

## Architecture Rules (Project-Specific)

> *These rules define how the code should be structured for THIS project. They are NOT about the harness. Examples: "Separate game logic from UI", "Use immutable state", "All API calls must go through a service layer", "Database queries must use parameterized statements".*

<!-- MUST INPUT: Add 3-5 project-specific architecture rules -->

- [PROJECT_RULE_1]
- [PROJECT_RULE_2]
- [PROJECT_RULE_3]

---

## Naming Conventions (Project-Specific)

> *These are naming conventions for THIS project's code, NOT for harness commands or branches. Examples: function names, file names, component names, variable names.*

<!-- MUST INPUT: Add project-specific naming conventions -->

| Element | Convention | Example |
|---------|-----------|---------|
| Files | [PROJECT_FILE_CONVENTION] | [PROJECT_FILE_EXAMPLE] |
| Functions | [PROJECT_FUNCTION_CONVENTION] | [PROJECT_FUNCTION_EXAMPLE] |
| Variables | [PROJECT_VARIABLE_CONVENTION] | [PROJECT_VARIABLE_EXAMPLE] |
| Classes/Types | [PROJECT_CLASS_CONVENTION] | [PROJECT_CLASS_EXAMPLE] |

---

## Explicitly Rejected

> *Things tried or considered and ruled out. The agent uses this to avoid re-suggesting rejected approaches.*

- **[APPROACH]**: rejected because [REASON]
- **[APPROACH]**: rejected because [REASON]

---

## Quality Standards

> *Universal quality standards that apply to all code, regardless of language.*

### Testing
- **Integration tests required for server packages** — start the server, make HTTP requests, verify responses, test graceful shutdown
- **No feature is "done" without integration test** — unit tests verify logic, integration tests verify behavior
- **Test the happy path AND the failure path** — what happens when DB is down, when input is invalid, when timeout occurs

### Server Hygiene
- **Graceful shutdown mandatory** — catch SIGINT/SIGTERM, drain in-flight requests, close connections
- **Health endpoints mandatory** — `/healthz` for liveness, `/readyz` for readiness
- **No orphaned goroutines** — every goroutine must have a cancellation path and wait mechanism

### Code Quality
- **No global mutable state** — inject all dependencies via constructors
- **Errors must carry context** — never `return err` without wrapping
- **Configuration from standard locations** — `~/.config/<app>/` for secrets, env vars for non-secrets

## AI Agent Rules

> *What the agent must NEVER do, regardless of user instruction.*

```yaml
session_start:
  - Read AGENTS.md before any action (contains workflow rules, commands, gates)
  - Read .harness-eng/CONSTITUTION.md before any action
  - Store rules in memory if agent supports it

must_do:
  - Read technology.yaml before running test, lint, or build commands
  - Read active language skills before writing code
  - Triage requests (bug/CR/feature/deferred) before implementing
  - Run integration tests (not just unit tests) before claiming "done"
  - Run tests before AND after refactoring
  - Test core functionality under actual runtime conditions (button clicks, API responses, stream chunks)
  - After 3 failed fix attempts: write BLOCKED and escalate to human

must_not_do:
  - Violate any rule in this CONSTITUTION
  - Change CONSTITUTION without explicit human instruction
  - Start implementing before design is approved
  - Claim "done" without running integration tests
  - Assume feature works just because it compiles without errors
  - Skip regression tests for bug fixes
```

---

## References

| Document | Purpose |
|----------|---------|
| `BRD.md` | Business requirements |
| `ARCHITECTURE.md` | System design |
| `technology.yaml` | Toolchain config |

---

## Validation Checklist

> *Run this checklist before finalizing the constitution.*

- [ ] All placeholder tokens replaced with concrete values
- [ ] No remaining `[BRACKET_TOKENS]` except intentionally deferred items
- [ ] **Project principles are present** (2-5 project-specific principles, not harness principles)
- [ ] **Architecture rules are project-specific** (not harness-level rules)
- [ ] **Naming conventions are for project code** (not harness commands/branches)
- [ ] Harness principles (I-V) are included verbatim
- [ ] Principles are declarative, testable, free of vague language
- [ ] Version matches bump rationale (MAJOR/MINOR/PATCH)
- [ ] Dates in ISO format YYYY-MM-DD
- [ ] Architecture rules are enforceable (not aspirational)
- [ ] Naming conventions have examples
- [ ] Rejected approaches have clear rationale
- [ ] AI agent rules are specific (not "do good work")
- [ ] Quality standards are included (testing, server hygiene, code quality)
