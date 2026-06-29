---
name: design
description: >
  Technical architecture design for per-language skill files.
  7 skill directories, each with a SKILL.md that defines test
  framework, formatting, library choices, error handling, and
  conventions for a single language. Skills are read by the
  agent during design and review phases — they are the "style
  guide" section of the harness contract.
---

# Design: Language Skills

**Branch**: `main`
**Date**: 2026-06-22
**Spec**: `phases/phase-0-foundation/features/active/F004-skills/spec.md`
**Ref**: APPROVED
**Approved by**: PENDING
**Approved date**: PENDING

**Input**: Feature specification for language skills

---

## Summary

7 skill directories at `skills/<lang>/SKILL.md` that encode per-language code conventions. Each skill covers: test framework, formatting rules, approved libraries, error handling patterns, and project-specific conventions. Design and review commands reference skill files — agent must read the relevant skill before writing code in that language. Skills are the "lint rules" of the harness contract.

---

## Technical Context

**Language/Version**: Markdown (SKILL.md files)

**Primary Dependencies**: None (skills are read-only references)

**Storage**: File-based at `skills/<lang>/SKILL.md`

**Testing**: Manual — review compares code output against skill rules

**Target Platform**: Any AI agent that reads markdown

**Performance Goals**: N/A

---

## Constitution Check

| Rule | Status | Notes |
|------|--------|-------|
| I. TDD Mandatory | ✅ PASS | Skills inform test framework choice — don't replace TDD |
| II. Std Lib First | ✅ PASS | Skills document which std libraries to prefer |
| III. Verify Before Assuming | ✅ PASS | Agent reads skill before writing code — verify before act |
| IV. Files Are Instructions | ✅ PASS | SKILL.md IS the instruction for how to write that language |
| V. Human in Control | ✅ PASS | Skills document human decisions about conventions |

---

## Architecture

### Component Map

```
┌──────────────────────────────────────────────────────────────────────┐
│                          SKILLS LAYER (skills/)                       │
│                                                                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│  │   go/    │  │ python/  │  │  node/   │  │   sql/   │           │
│  │ SKILL.md │  │ SKILL.md │  │ SKILL.md │  │ SKILL.md │           │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘           │
│                                                                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                          │
│  │  git/    │  │datastar/ │  │  oat/    │                          │
│  │ SKILL.md │  │ SKILL.md │  │ SKILL.md │                          │
│  └──────────┘  └──────────┘  └──────────┘                          │
└──────────────────────────────────────────────────────────────────────┘
          │ read by                       │ referenced in
          ▼                               ▼
┌──────────────────┐          ┌─────────────────────────┐
│  DESIGN PHASE     │          │  REVIEW PHASE            │
│                   │          │                          │
│  Agent reads      │          │  Reviewer compares       │
│  skill to know:   │          │  code against skill:     │
│  • test framework │          │  • test framework match? │
│  • formatting     │          │  • formatting matches?   │
│  • lib choices    │          │  • lib choices match?    │
│  • error handling │          │  • error handling match? │
│  • conventions    │          │  • conventions match?    │
└──────────────────┘          └──────────────────────────┘
          │                                │
          ▼                                ▼
┌──────────────────────────────────────────────────────────────────────┐
│                     CODE PRODUCTION                                  │
│                                                                      │
│  Agent writes code following skill conventions.                      │
│  If a language has no skill — agent must use default conventions.    │
│  If a language has a skill — agent MUST follow it.                   │
└──────────────────────────────────────────────────────────────────────┘
```

| Component | Responsibility | Depends On |
|-----------|---------------|------------|
| SKILL.md | Define all conventions for one language | Agent compliance |
| design.md (feature) | Reference relevant skills in Technical Context | skills/<lang>/ |
| review-pre-verify | Check code against skill conventions | skills/<lang>/ + implementation |
| pre-commit hook | Validate git conventions (from git skill) | skills/git/SKILL.md |

### Data Flow

```
Design Flow:
  1. Agent identifies languages needed for feature
  2. Agent reads skills/<lang>/SKILL.md for each language
  3. Agent writes design.md with Technical Context citing skills
  4. Agent writes code following skill conventions

Review Flow:
  1. Reviewer opens skill/<lang>/SKILL.md
  2. Reviewer compares each code file against skill rules
  3. Reviewer marks PASS (all match) or FAIL (violation found)
  4. Violations are documented in review output

Skill File Structure:
  # <Language> Conventions
  ## Test Framework
  - <framework> (e.g., "testing" for Go, "pytest" for Python)
  - <test file naming> (e.g., "*_test.go", "test_*.py")

  ## Formatting
  - <tool> (e.g., "gofmt", "black")
  - <rules> (e.g., "tabs, no trailing whitespace")

  ## Libraries
  - <approved> / <avoid>
  - <preferred package> for <use case>

  ## Error Handling
  - <pattern> (e.g., "return error, never panic")

  ## Conventions
  - <project-specific rules>
```

### Interfaces

```markdown
# Skill YAML frontmatter (optional, for machine parsing)
---
language: <name>
version: <preferred version>
test_framework: <name>
formatter: <name>
---

# Skill sections (all skills follow this structure):
## Test Framework
## Formatting
## Libraries
## Error Handling
## Conventions
```

```bash
# Discovery — agent lists available skills:
ls skills/*/SKILL.md
# → skills/go/SKILL.md  skills/python/SKILL.md  ...

# Read — agent reads relevant skill:
cat skills/go/SKILL.md
```

---

## File Layout

**New Files:** None — all 7 skill directories already exist.

**Modified Files:** None — skills are stable.

---

## Research

| Decision | Rationale | Alternatives Rejected |
|----------|-----------|----------------------|
| One SKILL.md per language directory | Clear mapping — language name IS the directory name | Single file with all languages (messy, hard to update per language) |
| Required sections (Test Framework, Formatting, etc.) | Guarantees minimum completeness — agent knows what to expect | Free-form (inconsistent across skills, agent can't compare) |
| Skills read by agent, not enforced by script | Language analysis is subjective — agent judgment needed | Automated linting (limited to formatting only, can't check patterns) |

---

## Complexity Tracking

N/A — No constitutional violations.

---

## Design Confidence

| Claim | Confidence | Source |
|-------|-----------|--------|
| All 7 skill directories exist | VERIFIED | `ls skills/` |
| Each has SKILL.md | VERIFIED | `ls skills/*/SKILL.md` |
| Each SKILL.md has Test Framework section | VERIFIED | grep for "Test Framework" in each |
| Each SKILL.md has Formatting section | VERIFIED | grep for "Formatting" in each |
| Each SKILL.md has Libraries section | VERIFIED | grep for "Libraries" in each |

---

## Self-Challenge

**What is the strongest reason this design might be wrong?**
Skills are human-readable markdown with no machine-enforceable rules. The agent "following" the skill is an instruction-level promise, not a technical guarantee. Nothing compels the agent to read the skill before writing code.

**What assumption am I making that I haven't stated?**
That the agent will proactively read skill files during design and review. In practice, the agent may skip this unless the command file explicitly instructs it.

**What would need to be true for this to fail?**
If a skill's conventions conflict with the agent's training data defaults (e.g., agent prefers pytest but skill says unittest), the agent may inadvertently follow its training instead of the skill.

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
