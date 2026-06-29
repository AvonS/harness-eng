---
name: design
description: >
  Technical architecture design for the document template system.
  11 template files at templates/ serve as skeletons for every
  agent-generated document. Templates are the "schema" of the
  harness — they define the structure that every spec, design,
  task list, and project document must follow.
---

# Design: Document Templates

**Branch**: `main`
**Date**: 2026-06-22
**Spec**: `phases/phase-0-foundation/features/active/F003-templates/spec.md`
**Ref**: APPROVED
**Approved by**: PENDING
**Approved date**: PENDING

**Input**: Feature specification for document templates

---

## Summary

11 markdown and shell template files organized in 4 groups: feature-level templates (spec, design, tasks), big-picture templates (CONSTITUTION, BRD, ARCHITECTURE), phase/status templates, and a sanity-check script skeleton. Every agent-produced document is a copy of a template with sections filled in. Templates are the "type system" of the harness — they guarantee structural consistency across LLM sessions.

---

## Technical Context

**Language/Version**: Markdown + YAML frontmatter + bash (sanity-check template)

**Primary Dependencies**: None (templates are static files)

**Storage**: File-based at `templates/` — organized by group in subdirectories

**Testing**: Manual inspection — verify each template produces valid documents when filled

**Target Platform**: Any AI agent that reads markdown

**Performance Goals**: N/A (templates are static — no runtime)

---

## Constitution Check

| Rule | Status | Notes |
|------|--------|-------|
| I. TDD Mandatory | ✅ PASS | Templates are structure, not implementation |
| II. Std Lib First | ✅ PASS | Markdown + bash — zero dependencies |
| III. Verify Before Assuming | ✅ PASS | Templates are stable source — agent copies, never edits |
| IV. Files Are Instructions | ✅ PASS | Templates ARE the instructions for document structure |
| V. Human in Control | ✅ PASS | Templates provide structure; humans fill content |

---

## Architecture

### Component Map

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          TEMPLATES LAYER (templates/)                        │
│                                                                              │
│  ┌──────────────────────┐    ┌──────────────────────────┐                   │
│  │   FEATURE TEMPLATES   │    │   BIG-PICTURE TEMPLATES   │                   │
│  │   (per-feature docs)  │    │   (project-wide docs)     │                   │
│  │                       │    │                           │                   │
│  │  feature/spec.md      │    │  big-picture/CONSTITUTION │                   │
│  │  feature/design.md    │    │  big-picture/BRD.md       │                   │
│  │  feature/tasks.md     │    │  big-picture/ARCHITECTURE │                   │
│  └───────────────────────┘    └───────────────────────────┘                   │
│                                                                              │
│  ┌──────────────────────┐    ┌──────────────────────────┐                   │
│  │   PHASE/STATUS        │    │   ROOT TEMPLATES         │                   │
│  │                       │    │                           │                   │
│  │  phase/PHASE.md       │    │  SLICE_LOG.md            │                   │
│  │  status/STATUS.md     │    │  sanity-check.sh         │                   │
│  │  PHASES.md            │    │                           │                   │
│  └───────────────────────┘    └───────────────────────────┘                   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │ copied & filled by agent
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        GENERATED DOCUMENTS LAYER                             │
│                                                                              │
│  .harness-eng/                         commands/                            │
│  ├── CONSTITUTION.md  ← big-picture/   ├── init.md                          │
│  ├── BRD.md           ← big-picture/   ├── define.md                        │
│  ├── ARCHITECTURE.md  ← big-picture/   └── ...                              │
│  ├── SLICE_LOG.md     ← template/                                          │
│  └── phases/                           root/                                │
│      └── <phase>/features/active/      ├── scripts/sanity-check.sh ← tpl   │
│          └── F00N-<name>/              └── PHASES.md ← templates/PHASES.md │
│              ├── spec.md    ← feature/                                      │
│              ├── design.md  ← feature/                                      │
│              └── tasks.md   ← feature/                                      │
└─────────────────────────────────────────────────────────────────────────────┘

Template → Document mapping:

  templates/feature/spec.md       → .harness-eng/phases/*/F00N-*/spec.md
  templates/feature/design.md     → .harness-eng/phases/*/F00N-*/design.md
  templates/feature/tasks.md      → .harness-eng/phases/*/F00N-*/tasks.md
  templates/big-picture/CONSTITUTION.md → .harness-eng/CONSTITUTION.md
  templates/big-picture/BRD.md          → .harness-eng/BRD.md
  templates/big-picture/ARCHITECTURE.md → .harness-eng/ARCHITECTURE.md
  templates/phase/PHASE.md        → .harness-eng/phases/<phase>/PHASE.md
  templates/status/STATUS.md      → .harness-eng/STATUS.md
  templates/SLICE_LOG.md          → .harness-eng/SLICE_LOG.md
  templates/sanity-check.sh       → scripts/sanity-check.sh
  templates/PHASES.md             → .harness-eng/PHASES.md
```

| Component | Responsibility | Depends On |
|-----------|---------------|------------|
| Feature templates | Define structure for per-feature documents (spec/design/tasks) | Workflow commands that create them |
| Big-picture templates | Define structure for project-wide documents | Init command |
| Phase/status templates | Define structure for milestones and reports | Phase create + status commands |
| Root templates | Define SLICE_LOG format and sanity-check script | Agent adherence |

### Data Flow

```
Document Creation Pipeline:

  1. Agent reads template from templates/<group>/<name>.md
  2. Agent copies template to target location
  3. Agent fills each section (YAML frontmatter, stories, sections)
  4. Agent preserves template structure — never removes sections
  5. Validation script verifies document against template (optional)
  6. Gate script checks **Ref**: markers for approval flow

Template Design Pattern (each template):

  ┌─ YAML frontmatter (name, description)
  ├─ Title + metadata (Feature/Design/Tasks refs)
  ├─ Section 1 (e.g., User Stories in spec)
  ├─ Section 2 (e.g., Architecture in design)
  ├─ ...
  └─ Validation checklist (pre-completion gate)
```

### Interfaces

```yaml
# Template YAML frontmatter (all templates)
---
name: <template_name>
description: >
  <template purpose and use instructions>
---

# Template files follow markdown with:
# - Placeholder text in [BRACKETS] for agent to fill
# - "N/A" allowed for irrelevant sections — never remove them
# - Lists and tables with headers preserved from template
```

---

## File Layout

**New Files:** None — all 11 templates already exist.

**Modified Files:** None — templates are stable.

---

## Research

| Decision | Rationale | Alternatives Rejected |
|----------|-----------|----------------------|
| YAML frontmatter in every template | Machine-parseable metadata — can be grepped by scripts | Prose-only (no metadata extraction possible) |
| Placeholder text in [BRACKETS] | Visually distinct — agent can't miss what needs filling | {{mustache}} (needs template engine), comments (not rendered) |
| Feature/design/tasks as separate files | One concept per file — clear separation of concerns | Single spec document (too long, mixed concerns) |
| Templates organized in groups | Feature-level vs big-picture vs root — different use patterns | Flat directory (harder to find relevant template) |

---

## Complexity Tracking

N/A — No constitutional violations.

---

## Design Confidence

| Claim | Confidence | Source |
|-------|-----------|--------|
| All 11 templates exist | VERIFIED | `ls -R templates/` |
| Each template has YAML frontmatter | VERIFIED | `head -5` on each template |
| Feature templates include **Ref**: marker | VERIFIED | grep for "Ref:" in feature templates |
| Sanity-check template is valid bash | VERIFIED | `bash -n templates/sanity-check.sh` |
| SLICE_LOG template has date|type|message format | VERIFIED | Direct inspection |

---

## Self-Challenge

**What is the strongest reason this design might be wrong?**
Templates are copied, not inherited. If a template is updated after documents were generated, old documents don't benefit from the new structure. There's no re-generation mechanism for existing documents.

**What assumption am I making that I haven't stated?**
That the agent will faithfully copy the template structure without skipping sections. Nothing enforces this at runtime — it's an agent-instruction-level guarantee.

**What would need to be true for this to fail?**
If a template has ambiguous section headers, different agents may interpret them differently, producing inconsistent documents despite using the same template.

---

## Validation Checklist

**Architecture:**
- [x] Component map is complete
- [x] Data flow is documented
- [x] Interfaces are defined
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
