---
name: design
description: >
  Technical architecture design for user-facing documentation.
  4 documents at docs/ that explain the harness-eng system
  at different levels: BRD (business), command reference
  (quick lookup), user guide (tutorial), and architecture
  review (design rationale). Human-oriented, not agent-oriented.
---

# Design: User-Facing Documentation

**Branch**: `main`
**Date**: 2026-06-22
**Spec**: `phases/phase-0-foundation/features/active/F007-docs/spec.md`
**Ref**: APPROVED
**Approved by**: PENDING
**Approved date**: PENDING

**Input**: Feature specification for user-facing documentation

---

## Summary

4 markdown documents at `docs/` that serve the human audience (not the agent). Each document targets a different reader and purpose: the BRD explains "why the harness exists" to stakeholders; the command reference is a quick lookup for developers mid-session; the user guide is a step-by-step tutorial for new team members; the architecture review captures design rationale for future maintainers. Together they form the complete documentation surface for the harness.

---

## Technical Context

**Language/Version**: Markdown

**Primary Dependencies**: None (documents are standalone)

**Storage**: File-based at `docs/`

**Testing**: Manual — human review for accuracy, completeness, clarity

**Target Platform**: Human readers (developers, architects, stakeholders)

**Performance Goals**: N/A

---

## Constitution Check

| Rule | Status | Notes |
|------|--------|-------|
| I. TDD Mandatory | ✅ PASS | Documentation — not production code |
| II. Std Lib First | ✅ PASS | Markdown — no dependencies |
| III. Verify Before Assuming | ✅ PASS | Documents describe actual system — must be verified against reality |
| IV. Files Are Instructions | ✅ PASS | Documents are instructions for humans, not agents |
| V. Human in Control | ✅ PASS | Documents support human decision-making |

---

## Architecture

### Component Map

```
┌─────────────────────────────────────────────────────────────────────┐
│                     DOCUMENT LAYER (docs/)                            │
│                                                                      │
│  ┌─────────────────────────┐                                        │
│  │    BRD-harness.md        │  ← Business stakeholders               │
│  │                         │     "Why do we need this harness?"      │
│  │  • Problem statement    │     "What problem does it solve?"       │
│  │  • Solution overview    │     "How does the workflow work?"       │
│  │  • 11-step workflow     │                                        │
│  │  • 3 gates              │                                        │
│  └─────────────────────────┘                                        │
│                                                                      │
│  ┌─────────────────────────┐                                        │
│  │  COMMAND-REFERENCE.md   │  ← Developers mid-session               │
│  │                         │     "What command do I run next?"       │
│  │  • 14 commands listed   │     "Does this one need human gate?"    │
│  │  • Trigger phrase       │                                        │
│  │  • Purpose              │                                        │
│  │  • Gate type (human/auto)│                                       │
│  │  • Persona              │                                        │
│  │  • Output artifact      │                                        │
│  └─────────────────────────┘                                        │
│                                                                      │
│  ┌─────────────────────────┐                                        │
│  │   user-guide.md         │  ← New team members                     │
│  │                         │     "How do I use this thing?"          │
│  │  • Step-by-step walk-   │     "Walk me through my first task"     │
│  │    through              │                                        │
│  │  • Troubleshooting      │                                        │
│  │  • Glossary             │                                        │
│  └─────────────────────────┘                                        │
│                                                                      │
│  ┌─────────────────────────┐                                        │
│  │ architectural-review-   │  ← Architects / future maintainers      │
│  │  2026-06-15.md          │     "Why was it designed this way?"     │
│  │                         │     "What alternatives were rejected?"  │
│  │  • Design decisions     │                                        │
│  │  • Trade-offs           │                                        │
│  │  • Rationale            │                                        │
│  └─────────────────────────┘                                        │
└─────────────────────────────────────────────────────────────────────┘
```

| Document | Audience | Purpose | Content |
|----------|----------|---------|---------|
| BRD-harness.md | Stakeholders, new devs | Explain "why" | Problem, solution, workflow, gates |
| COMMAND-REFERENCE.md | Developers mid-session | Quick lookup | Tables: trigger, purpose, gate, persona, output |
| user-guide.md | New team members | Tutorial | Step-by-step walkthrough, troubleshooting |
| architectural-review-*.md | Architects, maintainers | Decision record | Rationale, trade-offs, alternatives |

### Document Relationship

```
                    ┌──────────────────┐
                    │      BRD         │  ← START HERE for "why"
                    │  (high-level)    │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │   User Guide     │  ← THEN for "how"
                    │  (step-by-step)  │
                    └────────┬─────────┘
                             │
               ┌─────────────┴─────────────┐
               ▼                            ▼
      ┌──────────────────┐       ┌──────────────────────┐
      │ Command Reference│       │ Architecture Review   │
      │ (quick lookup)   │       │ (deep rationale)      │
      └──────────────────┘       └──────────────────────┘
```

### Interfaces

```markdown
# All documents follow standard markdown with:
# - H1 title matching filename purpose
# - H2 sections for major topics
# - Tables for structured data (command reference)
# - Code blocks for examples
# - Lists for step-by-step instructions

# BRD structure:
## Problem Statement
## Solution Overview
## Users
## Workflow (11 steps + 3 gates)

# Command Reference structure:
## All Commands Table
| Command | Trigger | Purpose | Gate | Persona | Output |

# User Guide structure:
## Prerequisites
## Step 1: Init
## Step N: Release
## Troubleshooting
## Glossary
```

---

## File Layout

**New Files:** None — all 4 documents exist.

**Modified Files:** None — documents are stable.

---

## Research

| Decision | Rationale | Alternatives Rejected |
|----------|-----------|----------------------|
| 4 documents, 4 audiences | Each audience gets the right level of detail without noise | Single document (too long, mixed audiences), wiki (not versioned with code) |
| Architecture review has dated filename | Versioning — reader knows which review they're looking at | Generic name (no version signal, can't tell if outdated) |
| Documents at docs/ | Separate from templates/ (agent files), commands/, and .harness-eng/ (project state) | In .harness-eng/ (confuses project state with documentation), in root (clutter) |

---

## Complexity Tracking

N/A — No constitutional violations.

---

## Design Confidence

| Claim | Confidence | Source |
|-------|-----------|--------|
| All 4 documents exist | VERIFIED | `ls docs/` |
| BRD covers problem + solution + workflow + gates | VERIFIED | Section inspection |
| Command reference covers all 14 commands | VERIFIED | grep for command names in file |
| User guide walks from init to release | VERIFIED | Section order inspection |
| Architecture review has dated filename | VERIFIED | Filename includes 2026-06-15 |

---

## Self-Challenge

**What is the strongest reason this design might be wrong?**
Documentation drifts from reality as the harness evolves. The BRD describes the ideal workflow, but commands may have been modified or extended — the BRD may describe a workflow that no longer matches the command files.

**What assumption am I making that I haven't stated?**
That documents are read by humans in the order: BRD → User Guide → Command Reference → Architecture Review. In practice, users jump between documents as needed — the hierarchy may not match actual reading patterns.

**What would need to be true for this to fail?**
If the BRD and commands disagree about the workflow, the developer gets conflicting information. The BRD says "11-step workflow with 3 gates" but new commands may have been added, or gates changed — the BRD must be updated in lockstep.

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
