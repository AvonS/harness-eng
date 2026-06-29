---
name: spec
description: >
  Feature specification for language skills.
  7 per-language skill directories that tell the agent how to
  write code in each language for this project — test framework,
  formatting, library choices, conventions. Skills are referenced
  by commands/design.md and commands/review-pre-build.md for
  compliance checking during design and review.
---

# Feature: Language Skills

**Feature**: F004 — Language Skills
**Status**: Complete (reverse-engineered)
**Ref**: PENDING

---

## User Stories

### Story 1 — Language Convention Reference (Priority: P1)

An agent is asked to write Go code. Before writing, the agent reads `skills/go/SKILL.md` to learn the project's Go conventions: which test framework to use, how to format code, how to handle errors, which libraries are approved.

**Why this priority**: Without skill files, the agent invents conventions that may not match the project's established patterns.

**Independent test**: Create a feature that requires Go code, then check the review step references skills/go/SKILL.md — the produced code must follow the skill's conventions.

**Acceptance Scenarios**:

1. **Given** a Go feature requiring implementation, **When** the agent reads `skills/go/SKILL.md`, **Then** the produced code follows the skill's test framework, error handling, and formatting rules.
2. **Given** a Python feature, **When** the agent reads `skills/python/SKILL.md`, **Then** the produced code follows the skill's type hint, import style, and test conventions.

---

### Story 2 — Design Compliance Check (Priority: P1)

During design creation, the agent references skill files to ensure the proposed file layout and technology choices match project conventions. The design document must list which skills were consulted.

**Why this priority**: Designs that ignore project conventions waste implementation effort.

**Independent test**: Review a design.md that references skill files — the implementation section must cite skills used.

**Acceptance Scenarios**:

1. **Given** a design.md for a feature, **When** the agent consults relevant skills (e.g., skills/go/ for a Go feature), **Then** the design's Technical Context section includes the language version, test framework, and dependencies from the skill.
2. **Given** a design that does NOT reference any skill, **When** review-pre-build.sh runs, **Then** it flags the missing skill references.

---

### Story 3 — Review Compliance (Priority: P2)

The pre-verify review compares implemented code against the skill conventions. If the code violates skill rules (wrong test framework, wrong formatting), the review marks it as non-compliant.

**Why this priority**: Skills are the standard — reviews must enforce them.

**Independent test**: Write code that intentionally violates a skill convention and run review — must be flagged.

**Acceptance Scenarios**:

1. **Given** implementation code that uses `fmt.Sprintf("...%v", x)` instead of the skill's preferred error wrapping style, **When** review-pre-verify runs, **Then** it flags the violation.
2. **Given** implementation code that exactly matches skill conventions, **When** review-pre-verify runs, **Then** it passes with "code follows skill conventions."

---

### Story 4 — Git Convention Enforcement (Priority: P2)

The agent follows `skills/git/SKILL.md` for commit message format, branch naming, and PR conventions. The pre-commit hook validates commit messages against this skill.

**Why this priority**: Consistent git history supports automation (release notes, changelog generation).

**Independent test**: Make a commit with a non-conforming message — the pre-commit hook must reject it.

**Acceptance Scenarios**:

1. **Given** a commit message that follows `type(ID): description` format, **When** the pre-commit hook validates it, **Then** the commit is allowed.
2. **Given** a commit message without an ID (e.g., `fix: stuff`), **When** the pre-commit hook validates it, **Then** the commit is rejected.

---

### Story 5 — New Language Onboarding (Priority: P2)

A developer adds a new language to the project. They create a new skill directory with a SKILL.md covering test framework, formatting, library choices, and conventions.

**Why this priority**: The skill system must be extensible — new languages are added, not hardcoded.

**Independent test**: Create a new `skills/rust/SKILL.md` — the status dashboard must detect it as a known skill.

**Acceptance Scenarios**:

1. **Given** a new language is introduced to the project, **When** the developer creates `skills/<lang>/SKILL.md`, **Then** the agent discovers it during design and review phases without any configuration change.
2. **Given** a new skill file with incorrect format (missing required sections), **When** the agent attempts to read it, **Then** it reports "INCOMPLETE SKILL: <missing sections>."

---

## Edge Cases

- What if a feature uses multiple languages (Go backend + JS frontend)? The agent must read ALL relevant skills and follow each.
- What if a skill references a framework version that's not installed? The agent should note the discrepancy but still follow the conventions.
- What if two skills conflict (e.g., SQL naming convention differs between teams)? The project must resolve this — skills are single-source-of-truth per language.

## Functional Requirements

- **FR-001**: Each skill MUST contain a SKILL.md with sections: Test Framework, Formatting, Libraries, Error Handling, Conventions.
- **FR-002**: Skills MUST be referenced in the design's Technical Context section.
- **FR-003**: Review MUST check code against skill conventions and flag violations.
- **FR-004**: Git skill MUST define commit message format, branch naming, and PR conventions.
- **FR-005**: New skills MUST be discoverable by directory listing — no registration step.

## Success Criteria

| # | Criterion | Measurable? |
|---|-----------|-------------|
| SC-001 | All 7 skill directories exist with SKILL.md | ✅ File existence |
| SC-002 | Each SKILL.md has Test Framework, Formatting, Libraries sections | ✅ grep for headers |
| SC-003 | Designs reference relevant skills | ✅ grep for "skills/" in design.md |
| SC-004 | Review flags skill violations | ✅ Review output |

## Key Entities

- **Skill File (SKILL.md)**: Per-language convention reference. Single source of truth for how to write that language in this project.
- **Skill Directory**: Language-named directory under `skills/` containing SKILL.md.

## Assumptions

- The agent reads skills before writing code in a given language.
- Skills are stable — updated via PR, not ad-hoc by the agent.
- One skill per language — no "alternate" skills for the same language.

## Out of Scope

- Automated skill enforcement in CI (enforcement is agent-side during review).
- Skill conflict resolution between languages (different languages have different skills).
- Runtime/compilation of skill rules (skills are human-readable markdown).

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
