---
name: spec
description: >
  Feature specification for document templates.
  Templates are skeletons for every agent-generated document —
  specs, designs, tasks, BRDs, CONSTITUTION, ARCHITECTURE, phases,
  status dashboards, SLICE_LOG, and sanity-check scripts.
  Every agent-produced document fills from a template.
---

# Feature: Document Templates

**Feature**: F003 — Document Templates
**Status**: Complete (reverse-engineered)
**Ref**: PENDING

---

## User Stories

### Story 1 — Feature Spec Template (Priority: P1)

An agent needs to create a feature specification. The spec template provides the structure with Given/When/Then stories, edge cases, functional requirements, and success criteria. The agent fills each section — never invents the structure.

**Why this priority**: Specs are the first document after feature definition. Every other document depends on spec clarity.

**Independent test**: Open `templates/feature/spec.md` and verify all template sections are present: User Stories, Acceptance Scenarios, Edge Cases, FRs, Success Criteria, Key Entities, Assumptions, Out of Scope.

**Acceptance Scenarios**:

1. **Given** a new feature is being specified, **When** the agent copies `templates/feature/spec.md`, **Then** the resulting document contains all template sections in the correct order.
2. **Given** a spec template, **When** the agent fills in stories, **Then** every story has at least one Given/When/Then acceptance scenario.

---

### Story 2 — Feature Design Template (Priority: P1)

An agent needs to create a technical architecture design. The design template provides component maps, data flow, interfaces, file layout, constitution check, and design confidence tracking.

**Why this priority**: Designs are reviewed and approved by humans. Consistent format is essential for gate tracking.

**Independent test**: Open `templates/feature/design.md` and verify all sections: Summary, Technical Context, Constitution Check, Architecture, File Layout, Research, Complexity Tracking, Design Confidence, Self-Challenge, Validation Checklist.

**Acceptance Scenarios**:

1. **Given** an approved spec, **When** the agent creates a design from the template, **Then** the design includes a **Ref**: PENDING marker at the top.
2. **Given** a design template, **When** the agent fills in the Constitution Check table, **Then** every constitutional rule is checked (not skipped).

---

### Story 3 — Feature Tasks Template (Priority: P1)

An agent needs to break a design into implementation tasks. The tasks template provides dependency tracking, status, and file references.

**Why this priority**: Tasks are the atomic execution unit. Consistent format ensures clean progress tracking.

**Independent test**: Open `templates/feature/tasks.md` and verify task structure with dependencies and status.

**Acceptance Scenarios**:

1. **Given** an approved design, **When** the agent creates tasks from the template, **Then** each task has a unique ID, file path, and status marker.
2. **Given** a task with dependencies, **When** the dependencies are incomplete, **Then** the dependent task shows "BLOCKED" status.

---

### Story 4 — Big-Picture Templates (Priority: P1)

The agent needs to create or update three high-level project documents: CONSTITUTION (rules), BRD (business requirements), and ARCHITECTURE (system design). Templates ensure these documents follow harness structure.

**Why this priority**: These documents define the project contract. Incomplete structure leads to agent confusion.

**Independent test**: Open each big-picture template and confirm it matches the expected sections.

**Acceptance Scenarios**:

1. **Given** the CONSTITUTION template, **When** the agent fills it, **Then** it includes Rules, Gates, Commands, and Dogfood sections.
2. **Given** the BRD template, **When** the agent fills it, **Then** it includes Problem Statement, Users, Features, Workflow sections.
3. **Given** the ARCHITECTURE template, **When** the agent fills it, **Then** it includes Contract Architecture, Templates, Gates, Personas, Flow Diagrams sections.

---

### Story 5 — Phase Template (Priority: P2)

The agent needs to define a project phase containing multiple features. The phase template provides exit criteria, feature list, and status tracking.

**Why this priority**: Phases organize features into releasable milestones. Without the template, phases are unstructured.

**Independent test**: Open `templates/phase/PHASE.md` and verify phase structure with exit criteria.

**Acceptance Scenarios**:

1. **Given** a phase with 3 features, **When** the agent creates PHASE.md from template, **Then** each feature has a status (Pending/Active/Done) and exit criteria section.

---

### Story 6 — SLICE_LOG Template (Priority: P2)

The agent logs build sessions to SLICE_LOG.md. The template defines the date|type|message format for machine-parseable resume context.

**Why this priority**: SLICE_LOG is the primary session-resumption mechanism. Consistent format is essential.

**Independent test**: Open `templates/SLICE_LOG.md` and verify the header format and sample entry.

**Acceptance Scenarios**:

1. **Given** an agent completes a build step, **When** it appends to SLICE_LOG.md following the template format, **Then** the entry is parseable by `check-slice-log-entry.sh`.
2. **Given** the template is followed exactly, **When** the agent resumes a session, **Then** it can recover the last 3 entries for context.

---

### Story 7 — Sanity Check Script Template (Priority: P2)

The agent needs to deploy a sanity-check script to the project root. The template provides a working skeleton that verifies the harness project is correctly set up.

**Why this priority**: Sanity checks are the first line of defense against broken project state.

**Independent test**: Run the generated `scripts/sanity-check.sh` — must exit zero for a valid project and non-zero with specific errors for broken state.

**Acceptance Scenarios**:

1. **Given** the sanity-check template, **When** the agent deploys it to the project root, **Then** it checks for `.harness-eng/`, `AGENTS.md`, `commands/`, and `CONSTITUTION.md`.

---

## Edge Cases

- What happens when a template is used for a feature that doesn't fit the template structure? The agent must adapt within the template — never remove sections, use "N/A" for irrelevant parts.
- How do we handle template version drift when harness is upgraded? Templates are the canonical source — init and upgrade must overwrite them.
- What if a user modifies the template? On upgrade, templates are overwritten. User modifications must be in CONSTITUTION.md.

## Functional Requirements

- **FR-001**: Every template MUST include YAML frontmatter with `name` and `description`.
- **FR-002**: Feature templates MUST include **Ref**: marker for gate tracking.
- **FR-003**: Templates MUST NOT contain implementation-specific content — only structure.
- **FR-004**: The sanity-check script template MUST produce a valid executable when deployed.

## Success Criteria

| # | Criterion | Measurable? |
|---|-----------|-------------|
| SC-001 | All 11 template files exist under `templates/` | ✅ File existence |
| SC-002 | Each template has YAML frontmatter | ✅ grep for `---` |
| SC-003 | Feature templates include **Ref**: marker | ✅ grep for `Ref:` |
| SC-004 | Sanity-check template is valid bash | ✅ `bash -n` passes |
| SC-005 | SLICE_LOG template format matches validation script | ✅ check-slice-log-entry.sh passes |

## Key Entities

- **Feature Template**: Template for a single-feature document (spec, design, tasks).
- **Big-Picture Template**: Template for project-wide document (CONSTITUTION, BRD, ARCHITECTURE).
- **Phase Template**: Template for organizing multiple features into a milestone.
- **Status Template**: Template for quick status dashboard.
- **Log Template**: Template for build narrative log.

## Assumptions

- Templates are read-only source files never modified by agents during production use.
- The agent copies a template to the target location before filling it.
- Template files are versioned alongside project source.

## Out of Scope

- Dynamic template generation (templates are static markdown files).
- Template validation beyond structure (content validation is done by scripts).

## Validation Checklist

**Content Quality:**
- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [ ] Written for non-technical stakeholders
- [x] All mandatory sections completed

**Requirement Completeness:**
- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] Success criteria are technology-agnostic
- [x] All acceptance scenarios use Given/When/Then
- [x] Edge cases identified
- [x] Scope clearly bounded

**Feature Readiness:**
- [x] All stories have acceptance criteria
- [x] Stories cover primary user flows
- [x] Feature meets measurable success criteria
- [x] No implementation details in spec
