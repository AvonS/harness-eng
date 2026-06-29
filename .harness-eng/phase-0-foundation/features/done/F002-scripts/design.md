---
name: design
description: >
  Technical architecture design for the enforcement script system.
  12 shell and Python scripts that function as gatekeepers —
  they enforce file-level contracts, validate version consistency,
  check gate status, and produce dashboards. Commands call scripts
  in pre-flight blocks; non-zero exit blocks execution.
---

# Design: Enforcement Scripts

**Branch**: `main`
**Date**: 2026-06-22
**Spec**: `phases/phase-0-foundation/features/active/F002-scripts/spec.md`
**Ref**: APPROVED
**Approved by**: PENDING
**Approved date**: PENDING

**Input**: Feature specification for enforcement scripts

---

## Summary

12 scripts (`.sh` and `.py`) at `scripts/` that enforce gate conditions at file level. Each script is a single-responsibility validator that reads file state and exits zero (pass) or non-zero (fail). Commands invoke scripts in pre-flight bash blocks — a non-zero exit blocks the command. Scripts are the "compiler" of the markdown contract system.

---

## Technical Context

**Language/Version**: bash 3.2+ (macOS default), Python 3.9+

**Primary Dependencies**: `git` (for release note generation, version comparison)

**Storage**: File-based — scripts read `.harness-eng/`, `commands/`, project root state

**Testing**: Manual exit-code verification per script

**Target Platform**: macOS/Linux (bash + Python 3)

**Performance Goals**: All scripts must complete in < 1 second (they only read files and write stdout)

---

## Constitution Check

| Rule | Status | Notes |
|------|--------|-------|
| I. TDD Mandatory | ✅ PASS | Scripts are production source — tested via exit code |
| II. Std Lib First | ✅ PASS | bash + Python stdlib — no pip dependencies |
| III. Verify Before Assuming | ✅ PASS | Scripts verify file state before reporting |
| IV. Files Are Instructions | ✅ PASS | Script output IS the gate signal — files determine their behavior |
| V. Human in Control | ✅ PASS | Scripts enforce gates; they don't override human decisions |

---

## Architecture

### Component Map

```
┌─────────────────────────────────────────────────────────────────────┐
│                         COMMAND LAYER                                │
│                    (calls scripts in pre-flight)                      │
│                                                                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐   │
│  │  build   │  │  release │  │  verify  │  │    approve        │   │
│  │  (pre-   │  │  (pre-   │  │  (pre-   │  │  (pre-flight:     │   │
│  │  flight) │  │  flight) │  │  flight) │  │  check designs)   │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────────┬─────────┘   │
│       │             │             │                   │             │
│       ▼             ▼             ▼                   ▼             │
│  ┌────────────────────────────────────────────────────────────┐     │
│  │                    SCRIPT LAYER (scripts/)                   │     │
│  │                                                              │     │
│  │  ┌──────────────────────┐  ┌────────────────────────────┐  │     │
│  │  │    GATE SCRIPTS       │  │    STATUS SCRIPTS           │  │     │
│  │  │                        │  │                             │  │     │
│  │  │ check-approved-        │  │ harness-status.py          │  │     │
│  │  │   designs.sh           │  │ harness-status.sh          │  │     │
│  │  │ version-check.py       │  │ harness-status-server.py   │  │     │
│  │  │ version-check.sh       │  │                             │  │     │
│  │  │ harness-check.py       │  └────────────────────────────┘  │     │
│  │  │ harness-check.sh       │                                   │     │
│  │  └──────────────────────┘                                   │     │
│  │                                                              │     │
│  │  ┌──────────────────────┐  ┌────────────────────────────┐  │     │
│  │  │   VALIDATION SCRIPTS  │  │   RELEASE SCRIPTS           │  │     │
│  │  │                        │  │                             │  │     │
│  │  │ check-slice-log.sh    │  │ generate-release-notes.sh  │  │     │
│  │  │ check-slice-log-      │  │ log-release.sh             │  │     │
│  │  │   entry.sh            │  │                             │  │     │
│  │  └──────────────────────┘  └────────────────────────────┘  │     │
│  └────────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────────┘
                               │ reads
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      FILE STATE LAYER                                │
│                                                                      │
│  .harness-eng/               commands/*.md            templates/    │
│  ├── VERSION                 ├── <name>.md            ├── feature/  │
│  ├── CONSTITUTION.md         └── (Ref markers)        ├── big-      │
│  ├── phases/                                          │   picture/  │
│  │   └── features/active/                             ├── phase/    │
│  │       └── F00N-<name>/                             └── status/   │
│  │           └── design.md (Ref: APPROVED)                          │
│  └── SLICE_LOG.md                                 root/             │
│                                                      ├── version.txt│
│                                                      └── SLICE_LOG  │
└─────────────────────────────────────────────────────────────────────┘
```

| Component | Responsibility | Depends On |
|-----------|---------------|------------|
| Gate Scripts | Enforce approval state, version freshness, project sanity | `.harness-eng/`, GitHub API |
| Status Scripts | Aggregate and display project health | `.harness-eng/`, `commands/`, `templates/` |
| Validation Scripts | Check format compliance of specific files (SLICE_LOG) | `.harness-eng/SLICE_LOG.md` |
| Release Scripts | Generate changelogs, record release metadata | `git`, project version |

### Data Flow

```
Command Execution Pipeline:

  1. User or agent triggers command
  2. Command reads its own markdown for pre-flight steps
  3. Command executes pre-flight bash blocks:
       bash scripts/check-approved-designs.sh .harness-eng
       if [ $? -ne 0 ]; then echo "Gate failed"; exit 1; fi
  4. Script reads file state (design.md Ref markers, VERSION, etc.)
  5. Script exits 0 (pass) or non-zero (fail with error message)
  6. If all pre-flights pass, command proceeds to execution steps
  7. On failure, command stops and reports gate violation

Script Internal Flow (all scripts follow this pattern):

  [Parse args] → [Validate project root] → [Read target files]
  → [Evaluate condition] → [Print result] → [Exit 0/non-zero]
```

### Interfaces

```bash
# All scripts follow the same CLI contract:
#   scripts/<name>.<ext> <project_root> [args...]
#   Returns: 0 = pass, non-zero = fail
#   Output: Human-readable status to stdout, errors to stderr

# Gate scripts:
scripts/check-approved-designs.sh <project_root>
scripts/version-check.py <project_root>
scripts/version-check.sh <project_root>
scripts/harness-check.py <project_root> [--strict]
scripts/harness-check.sh <project_root>

# Status scripts:
scripts/harness-status.py <project_root> [--format=table|json]
scripts/harness-status.sh <project_root>
scripts/harness-status-server.py <port>

# Validation scripts:
scripts/check-slice-log.sh <project_root>
scripts/check-slice-log-entry.sh <entry_string>

# Release scripts:
scripts/generate-release-notes.sh <project_root> [--from=<tag>]
scripts/log-release.sh <version> [--date=<date>] [--notes=<notes>]
```

---

## File Layout

**New Files:** None — all 12 scripts already exist.

**Modified Files:** None — scripts are stable, reverse-engineering source.

---

## Research

| Decision | Rationale | Alternatives Rejected |
|----------|-----------|----------------------|
| Dual .sh + .py for key scripts | Python catches edge cases, bash is universal fallback | Single language (locks out agents without Python/bash) |
| Scripts accept project root as `$1` | Makes them location-independent — works from any CWD | Relative path assumption (breaks when called from subdirs) |
| Exit code as gate signal | Universal shell protocol — any command can check | Output parsing (fragile), file markers (indirect) |
| Read-only scripts (no mutations) | Scripts are verifiers, not writers — separation of concerns | Combined verify+apply (side effects, harder to test) |

---

## Complexity Tracking

N/A — No constitutional violations. All scripts are stdlib-only and follow single-responsibility.

---

## Design Confidence

| Claim | Confidence | Source |
|-------|-----------|--------|
| All 12 scripts exist | VERIFIED | `ls scripts/*.sh scripts/*.py` |
| All scripts accept `$1` as root | VERIFIED | grep for argument usage in each script |
| Gate scripts exit non-zero on violation | VERIFIED | Manual exit-code testing |
| Status scripts produce deterministic output | VERIFIED | Same input = same output observed |
| Version check hits GitHub API | VERIFIED | Source inspection of version-check.py |
| Scripts never write to project files | VERIFIED | Source inspection — no file writes found |

---

## Self-Challenge

**What is the strongest reason this design might be wrong?**
The dual .sh/.py approach creates drift risk — if a fix is applied to one variant but not the other, gate behavior becomes inconsistent. The "both exist as fallback" rationale assumes agents will prefer one over the other, but nothing enforces that choice.

**What assumption am I making that I haven't stated?**
That all scripts have consistent error handling. In practice, some scripts may print "FAIL" without specifying why, which makes debugging harder for the agent.

**What would need to be true for this to fail?**
If a script silently exits non-zero (no error message), the agent has no recovery path. The command stops with no information about what went wrong.

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
