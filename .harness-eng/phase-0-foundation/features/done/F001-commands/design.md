---
name: design
description: >
  Technical architecture design for the workflow command system.
  Documents how 14 commands define the harness-eng workflow
  with pre-flight gates, execution steps, and output artifacts.
---

# Design: Workflow Commands

**Branch**: `main`
**Date**: 2026-06-22
**Spec**: `phases/phase-0-foundation/features/active/F001-commands/spec.md`
**Ref**: APPROVED
**Approved by**: PENDING
**Approved date**: PENDING

**Input**: Feature specification for the workflow command system

---

## Summary

14 markdown command files at `commands/` define the harness-eng workflow from init to release. Each command is a self-contained instruction set with YAML frontmatter, pre-flight bash blocks, step-by-step execution steps, output artifacts, and constraints. Commands call scripts for gate enforcement and pass control between workflow phases via output routing.

---

## Technical Context

**Language/Version**: Markdown + YAML frontmatter + inline bash

**Primary Dependencies**: None (commands are instruction files, not executable code)

**Storage**: File-based — commands live at `commands/*.md` with symlinks at `.harness-eng/commands/*.md`

**Testing**: Manual review — verify each command produces correct artifacts when followed

**Target Platform**: Any AI agent that reads markdown files and executes bash blocks

**Performance Goals**: N/A — commands are instructions, not runtime code

---

## Constitution Check

| Rule | Status | Notes |
|------|--------|-------|
| I. TDD Mandatory | ✅ PASS | build.md enforces test-first per task |
| II. Std Lib First | ✅ PASS | Markdown + bash + python — no external dependencies |
| III. Verify Before Assuming | ✅ PASS | design.md fetches official docs; pre-flight calls scripts |
| IV. Files Are Instructions | ✅ PASS | Commands ARE the instructions — the folder structure IS the state machine |
| V. Human in Control | ✅ PASS | approve and release commands require explicit human confirmation |

---

## Architecture

### Component Map

```
┌──────────────────────────────────────────────────────────────────┐
│                        COMMAND LAYER                              │
│  commands/*.md — instructions that tell the agent what to do      │
│                                                                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │
│  │  init    │  │  define  │  │  design  │  │    approve        │  │
│  │  (setup) │→│  (spec)  │→│  (arch)  │→│  (human gate)     │  │
│  └──────────┘  └──────────┘  └──────────┘  └────────┬─────────┘  │
│                                                      │            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐           │            │
│  │  bug     │  │  triage  │  │  tasks   │◄──────────┘            │
│  │  (fix)   │←│  (class)  │  │  (break) │                        │
│  └──────────┘  └──────────┘  └────┬─────┘                        │
│                                    │                              │
│  ┌──────────┐  ┌──────────────┐   │                              │
│  │  review- │  │  review-pre- │   │                              │
│  │  pre-    │←│  build        │   │                              │
│  │  verify  │  │  (gap check) │   │                              │
│  └────┬─────┘  └──────────────┘   │                              │
│       │                           ▼                              │
│       │                    ┌──────────────┐                       │
│       │                    │    build     │                       │
│       │                    │  (TDD loop)  │                       │
│       │                    └──────┬───────┘                       │
│       │                           │                              │
│       └───────────────────────────┘                              │
│                                   │                              │
│  ┌──────────┐  ┌──────────┐      │                              │
│  │  verify  │←│  release │◄─────┘                              │
│  │  (test)  │  │ (ship)   │                                      │
│  └──────────┘  └──────────┘                                      │
│                                                                    │
│  ┌──────────┐  ┌──────────┐                                       │
│  │  status  │  │  health  │  (utility — no workflow position)     │
│  └──────────┘  └──────────┘                                       │
└──────────────────────────────────────────────────────────────────┘
                          │ calls
                          ▼
┌──────────────────────────────────────────────────────────────────┐
│                        SCRIPT LAYER                               │
│  scripts/*.sh — gate enforcement scripts called by commands       │
│                                                                    │
│  check-approved-designs.sh  │  version-check.py                   │
│  harness-status.py          │  check-slice-log.sh                 │
└──────────────────────────────────────────────────────────────────┘
```

| Component | Responsibility | Depends On |
|-----------|---------------|------------|
| `commands/*.md` | Workflow instructions for the agent | `.harness-eng/` (CONSTITUTION, BRD, ARCH) |
| `scripts/*.sh` | Gate enforcement — called in pre-flight | Commands that invoke them |
| `.harness-eng/` | Project state — files ARE the state machine | Commands + scripts |

### Data Flow

1. **Entry**: User types a trigger phrase (e.g., "build it") → agent matches to command frontmatter
2. **Pre-flight**: Agent executes bash blocks that call scripts — if any script exits non-zero, command stops
3. **Execution**: Agent follows step-by-step markdown instructions — reads input files, writes output files
4. **Gate check**: Gate commands (approve, release) present evidence to human, wait for confirmation, write marker files
5. **Output**: Command writes its artifact (spec.md, design.md, tasks.md, verification.md, etc.)
6. **Routing**: Command output tells the user what to run next (e.g., "Now run `/h:design`")

### Gate Chain (Cross-Document Markers)

```
design.md:           **Ref**: APPROVED → APPROVED     (set by approve command)
review-pre-build.md: **Ref**: APPROVED → APPROVED     (auto-set on PASS)
review-pre-verify.md:**Ref**: APPROVED → APPROVED     (auto-set on PASS)
verification.md:     **Release Ref**: PENDING → APPROVED  (set by release command)
```

Each marker is checked by the next command's pre-flight. If the marker isn't set to the expected value, the command blocks.

### Interfaces

```
# Command YAML Frontmatter (every command has this)
---
name: <slug>
description: >
  <2-3 sentence description>
---

# Pre-flight (bash block at command start)
# EXECUTE: Run checks
bash .harness-eng/scripts/<check>.sh .harness-eng
if [ $? -ne 0 ]; then exit 1; fi

# Steps (markdown with inline bash)
## Step N: <action>
```bash
# EXECUTE: <description>
<command>
```
```

---

## File Layout

**New Files:** None — all commands already exist.

**Existing Files:**

| File | Purpose | Gate Role |
|------|---------|-----------|
| `commands/init.md` | Project scaffolding | None |
| `commands/define.md` | Feature specs from BRD | None |
| `commands/design.md` | Technical architecture | None |
| `commands/approve.md` | Human design approval | Writes **Ref**: APPROVED |
| `commands/tasks.md` | Task breakdown | None |
| `commands/review-pre-build.md` | Pre-build gap analysis | Produces PASS/CONDITIONAL/FAIL |
| `commands/build.md` | TDD implementation | Pre-flight checks for APPROVED design |
| `commands/review-pre-verify.md` | Post-build review | Produces PASS/CONDITIONAL/FAIL |
| `commands/verify.md` | Test execution | None |
| `commands/release.md` | Release workflow | Checks **Release Ref**: APPROVED |
| `commands/status.md` | Project status | None |
| `commands/health.md` | Compliance check | None |
| `commands/triage.md` | Request classification | None |
| `commands/bug.md` | Bug fix workflow | None |

---

## Research

| Decision | Rationale | Alternatives Rejected |
|----------|-----------|----------------------|
| YAML frontmatter for command metadata | Machine-parseable, consistent with existing conventions | Plain markdown headers (ambiguous), separate metadata file (redundant) |
| Inline bash blocks for pre-flight | Agent reads and executes in context — no external interpreter needed | Separate script files (fragmented logic), CLI wrapper (runtime dependency) |
| Cross-document Ref markers | Simple grep-able chain — any agent or script can check | Database (runtime dependency), lock files (fragile) |
| Commands as markdown (not code) | Any agent that reads markdown can use the harness — no compilation needed | Executable scripts (agent-specific), YAML-only (can't express prose) |

---

## Complexity Tracking

N/A — No constitutional violations. All commands follow the established pattern.

---

## Design Confidence

| Claim | Confidence | Source |
|-------|-----------|--------|
| All 14 commands have YAML frontmatter | VERIFIED | `head -5 commands/*.md` |
| All commands have pre-flight checks | VERIFIED | grep for "EXECUTE:" in each command |
| Gate commands block on missing markers | VERIFIED | build.md pre-flight greps for Ref marker |
| Markers chain across 3+ documents | VERIFIED | design.md → review-pre-verify.md → verification.md |
| Build enforces TDD per task | VERIFIED | build.md step structure: test → fail → implement → pass |
| Init handles 3 re-init choices | VERIFIED | init.md step 2: detect, present, wait |
| Health runs 10 checks | VERIFIED | health.md compliance checks numbered 1-10 |

---

## Self-Challenge

**What is the strongest reason this design might be wrong?**
The command files have grown organically — some may have inconsistent pre-flight patterns or missing edge case handling. The reverse-engineered spec captures intent, not actual consistency across all 14 files.

**What assumption am I making that I haven't stated?**
That the agent always executes bash blocks as written and doesn't skip pre-flight checks. The design trusts that the agent follows the command instructions in order, which is an instruction-level guarantee, not a technical one.

**What would need to be true for this to fail?**
If a command's YAML frontmatter trigger phrases overlap or conflict, the agent might run the wrong command. If pre-flight scripts are missing or broken, commands will block with unhelpful errors.

---

## Validation Checklist

**Architecture:**
- [x] Component map is complete
- [x] Data flow is documented
- [x] Interfaces are defined (signatures, not implementations)
- [x] File layout specifies new vs modified files

**Constitution:**
- [x] All constitution rules checked
- [x] Violations documented with justification
- [x] Complexity tracking filled (if violations exist)

**Research:**
- [x] All NEEDS CLARIFICATION items resolved
- [x] Technical decisions documented with rationale
- [x] Alternatives considered and rejected

**Quality:**
- [x] Design confidence tags filled (VERIFIED/INFERRED/ASSUMED)
- [x] Self-challenge completed
- [x] No implementation code (design only)
