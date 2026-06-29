---
name: design
description: >
  Technical architecture design for git hooks.
  A single pre-commit hook that validates commit message format
  and runs basic harness integrity checks. Hooks are the "last
  chance" gate before bad code enters the repository.
---

# Design: Git Hooks

**Branch**: `main`
**Date**: 2026-06-22
**Spec**: `phases/phase-0-foundation/features/active/F005-hooks/spec.md`
**Ref**: APPROVED
**Approved by**: PENDING
**Approved date**: PENDING

**Input**: Feature specification for git hooks

---

## Summary

A single `hooks/pre-commit` script that runs before every `git commit`. It validates the commit message against `type(ID): description` format using regex matching, then runs harness sanity checks on staged files. On failure, it prints an error message and exits non-zero — blocking the commit. Installed by the init command via copy or symlink into `.git/hooks/pre-commit`.

---

## Technical Context

**Language/Version**: bash 3.2+ (macOS default)

**Primary Dependencies**: `git` (all operations use git plumbing commands)

**Storage**: `hooks/pre-commit` (source), `.git/hooks/pre-commit` (installed copy)

**Testing**: Manual — run `git commit` with valid/invalid messages and observe behavior

**Target Platform**: macOS/Linux with bash and git

**Performance Goals**: Hook must complete in < 500ms (it runs on every commit)

---

## Constitution Check

| Rule | Status | Notes |
|------|--------|-------|
| I. TDD Mandatory | ✅ PASS | Hook validates TDD-required commit format |
| II. Std Lib First | ✅ PASS | bash + git plumbing — no dependencies |
| III. Verify Before Assuming | ✅ PASS | Hook verifies message format and file state before allowing commit |
| IV. Files Are Instructions | ✅ PASS | Hook script IS the instruction for commit validation |
| V. Human in Control | ✅ PASS | `git commit --no-verify` provides human override |

---

## Architecture

### Component Map

```
┌──────────────────────────────────────────────────────────────────────┐
│                       GIT COMMIT LIFECYCLE                            │
│                                                                      │
│  User runs: git commit -m "feat(42): add login"                      │
│       │                                                               │
│       ▼                                                               │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │                    PRE-COMMIT HOOK                               │ │
│  │                                                                  │ │
│  │  1. Read commit message from .git/COMMIT_EDITMSG                 │ │
│  │                                                                  │ │
│  │  2. Is this a merge commit?                                      │ │
│  │     ├── YES → Skip validation, exit 0                            │ │
│  │     └── NO  → Continue                                           │ │
│  │                                                                  │ │
│  │  3. Validate message format:                                     │ │
│  │     ^(fix|feat|chore|docs|refactor|test|bugfix|cr)              │ │
│  │      \(\d+\): .+$                                                │ │
│  │     ├── MATCH → Continue                                         │ │
│  │     └── NO MATCH → Print error, exit 1                           │ │
│  │                                                                  │ │
│  │  4. Run harness checks on staged files:                          │ │
│  │     ├── SLICE_LOG.md modified → validate format                  │ │
│  │     ├── Required file deleted → warn                             │ │
│  │     └── All good → Continue                                      │ │
│  │                                                                  │ │
│  │  5. Exit 0 → Allow commit to proceed                             │ │
│  └─────────────────────────────────────────────────────────────────┘ │
│       │                                                               │
│       ▼                                                               │
│  Commit proceeds → new commit object in git history                   │
└──────────────────────────────────────────────────────────────────────┘

               ┌───────────────────────────────┐
               │    HOOK INSTALLATION            │
               │                                 │
               │  hooks/pre-commit (source)       │
               │       │                          │
               │       │ (copy/symlink)           │
               │       ▼                          │
               │  .git/hooks/pre-commit           │
               │  (must be executable)            │
               └────────────────────────────────┘
```

| Component | Responsibility | Depends On |
|-----------|---------------|------------|
| `hooks/pre-commit` | Source hook script | bash, git |
| `.git/hooks/pre-commit` | Installed hook (runs on commit) | `hooks/pre-commit` source |
| init command | Installs hook during project setup | `hooks/pre-commit` |

### Data Flow

```
Commit Message Validation Flow:

  1. git reads commit message from .git/COMMIT_EDITMSG
  2. Hook runs before git creates the commit object
  3. Hook reads COMMIT_EDITMSG directly
  4. Hook applies regex: ^(fix|feat|chore|docs|refactor|test|bugfix|cr)\(\d+\): .+$
  5. Hook captures:
     - type group (fix, feat, etc.)
     - ID group (numeric task/issue ref)
     - description group (free text)
  6. If match → exit 0; if no match → print error, exit 1
  7. After format check, run harness integrity check on staged files
  8. If all checks pass → exit 0; commit proceeds
```

### Interfaces

```bash
#!/bin/bash
# hooks/pre-commit — runs inside .git/hooks/
# No arguments — reads from environment and COMMIT_EDITMSG

# Commit message format regex:
#   ^(fix|feat|chore|docs|refactor|test|bugfix|cr)\(\d+\): .+$

# Merge commit detection:
#   [[ "$GIT_REFLOG_ACTION" == "merge" ]] && exit 0

# Harness check (optional):
#   Staged files — via `git diff --cached --name-only`
#   SLICE_LOG format — via scripts/check-slice-log.sh
```

---

## File Layout

**New Files:** None — `hooks/pre-commit` already exists.

**Modified Files:** None — hook is stable.

---

## Research

| Decision | Rationale | Alternatives Rejected |
|----------|-----------|----------------------|
| Hook as standalone bash script | No dependencies — works on any system with git | Python (needs interpreter), JavaScript (needs Node) |
| Copy vs symlink for installation | Copy is safer — survives `.git/` deletion/recreation | Symlink (breaks on `.git` reinit) |
| Skip merge commits | Merge commit messages are auto-generated — can't follow format | Validate merges (impossible — format is not developer-controlled) |
| `grep -Eq` for validation | Fast, portable, no external dependencies | Python regex (slow on hook startup), sed/awk (fragile) |

---

## Complexity Tracking

N/A — No constitutional violations.

---

## Design Confidence

| Claim | Confidence | Source |
|-------|-----------|--------|
| Hook file exists | VERIFIED | `ls hooks/pre-commit` |
| Hook is executable | VERIFIED | `ls -l hooks/pre-commit` |
| Hook uses regex for format validation | VERIFIED | Source inspection |
| Hook skips merge commits | VERIFIED | Source inspection for MERGE_MSG check |
| Hook can be bypassed with --no-verify | VERIFIED | Standard git behavior |

---

## Self-Challenge

**What is the strongest reason this design might be wrong?**
The regex is rigid — it requires exactly `type(ID): description` with numeric ID. Non-numeric IDs (e.g., `feat(auth):`) are rejected. This may be too strict for some workflows.

**What assumption am I making that I haven't stated?**
That the developer uses the command line for commits. GUI tools (GitHub Desktop, VS Code) may not run hooks the same way, and some bypass the pre-commit hook entirely.

**What would need to be true for this to fail?**
If `git commit -m` is used with a one-line message that passes the regex but has a meaningless description (e.g., `fix(1): x`), the hook passes. Content quality of the description is not validated.

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
