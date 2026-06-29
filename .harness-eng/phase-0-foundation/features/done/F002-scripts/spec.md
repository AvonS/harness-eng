---
name: spec
description: >
  Feature specification for enforcement scripts.
  Scripts act as gatekeepers — they grep for cross-document reference markers,
  validate version consistency, check gate status, and produce status dashboards.
  Commands call these scripts in pre-flight blocks; if a script exits non-zero,
  the command stops.
---

# Feature: Enforcement Scripts

**Feature**: F002 — Enforcement Scripts
**Status**: Complete (reverse-engineered)
**Ref**: PENDING

---

## User Stories

### Story 1 — Gate Enforcement (Priority: P1)

An agent runs a command that requires an approved design. Before executing, the agent must verify that all design files have **Ref**: APPROVED. If any design is not approved, the command must block.

**Why this priority**: Without gate enforcement, agents can skip approval gates and produce unverified code.

**Independent test**: Call `check-approved-designs.sh` against a directory with mixed APPROVED/PENDING designs — must exit non-zero.

**Acceptance Scenarios**:

1. **Given** a design file with **Ref**: PENDING, **When** `check-approved-designs.sh` runs, **Then** it exits non-zero and lists the unapproved file.
2. **Given** all design files with **Ref**: APPROVED, **When** `check-approved-designs.sh` runs, **Then** it exits zero and prints "All designs approved."
3. **Given** no design directory exists, **When** `check-approved-designs.sh` runs, **Then** it exits zero (no designs = nothing to enforce).

---

### Story 2 — Status Dashboard (Priority: P1)

A developer wants a quick overview of project health without manually inspecting files. A status script scans the project structure and reports which files exist, which phases are defined, and any broken references.

**Why this priority**: Quick status is the most frequent developer interaction.

**Independent test**: Run `harness-status.py` in a harness project — must produce a structured report.

**Acceptance Scenarios**:

1. **Given** a complete harness project, **When** `harness-status.py` runs, **Then** it prints a table of all expected files with existence/validity status.
2. **Given** a harness with a missing CONSTITUTION.md, **When** `harness-status.py` runs, **Then** it includes a warning about the missing file.
3. **Given** an HTTP server request to `harness-status-server.py`, **When** the agent visits the server URL, **Then** it renders a visual dashboard in the browser.

---

### Story 3 — Version Check (Priority: P1)

The agent must check whether the local harness version is up to date. If an upgrade is available, the agent informs the developer.

**Why this priority**: Outdated harness versions may have missing commands or outdated instruction sets.

**Independent test**: Run `version-check.py` against a known version — must detect outdated vs current status.

**Acceptance Scenarios**:

1. **Given** the local `.harness-eng/VERSION` is older than the latest GitHub release tag, **When** `version-check.py` runs, **Then** it prints "Upgrade available: X.Y.Z → A.B.C".
2. **Given** the local version matches the latest GitHub release, **When** `version-check.py` runs, **Then** it prints "Version X.Y.Z is current."

---

### Story 4 — Sanity Checks (Priority: P1)

The agent must verify basic project structure health before running workflow commands. A sanity check script inspects required files, directories, and constraints.

**Why this priority**: Prevents the agent from working in a broken or incomplete project setup.

**Independent test**: Run `harness-check.sh` in a valid project — exits zero; run in an incomplete project — exits non-zero with specific errors.

**Acceptance Scenarios**:

1. **Given** a valid harness project, **When** `harness-check.py` runs, **Then** it exits zero.
2. **Given** a project missing the `.harness-eng/VERSION` file, **When** `harness-check.py` runs, **Then** it exits non-zero with "Missing: .harness-eng/VERSION".
3. **Given** a project with a bad symlink, **When** `harness-check.py` runs, **Then** it reports the broken symlink.

---

### Story 5 — Slice Log Validation (Priority: P2)

The agent must ensure the SLICE_LOG.md follows the required format before appending a new entry. Individual entry validation is also needed for review.

**Why this priority**: Consistent narrative format supports resumption between sessions.

**Independent test**: Run `check-slice-log.sh` against a valid and an invalid SLICE_LOG.

**Acceptance Scenarios**:

1. **Given** a SLICE_LOG.md with entries in `<date> | <type> | <message>` format, **When** `check-slice-log.sh` runs, **Then** it exits zero.
2. **Given** a SLICE_LOG.md with a malformed entry (missing `|` delimiter), **When** `check-slice-log.sh` runs, **Then** it exits non-zero and reports the bad line.
3. **Given** a single entry string, **When** `check-slice-log-entry.sh` runs, **Then** it validates the entry format.

---

### Story 6 — Release Notes Generation (Priority: P2)

The agent must generate release notes from git history when preparing a release.

**Why this priority**: Manual release notes are error-prone and inconsistent.

**Independent test**: Run `generate-release-notes.sh` in a repo with commits — must produce a Markdown changelog.

**Acceptance Scenarios**:

1. **Given** a git repository with commits in `type(ID): description` format, **When** `generate-release-notes.sh` runs, **Then** it produces a Markdown changelog grouped by type.
2. **Given** a repository with no commits since the last tag, **When** `generate-release-notes.sh` runs, **Then** it prints "No changes since [TAG]."

---

### Story 7 — Release Logging (Priority: P2)

The agent must record a release event after a successful release, creating a timestamped record of version, date, and notes.

**Why this priority**: Release history is needed for audit and rollback decisions.

**Independent test**: Run `log-release.sh` with a version argument — must create a release record file.

**Acceptance Scenarios**:

1. **Given** a release version "1.2.3", **When** `log-release.sh 1.2.3` runs, **Then** it creates or appends a record to the releases file with version, date, and summary.

---

## Edge Cases

- What happens when the GitHub API is unreachable during version check? Script must handle network errors gracefully and print a timeout warning.
- What happens when a script is called from the wrong working directory? Scripts must use relative or resolved paths.
- How does the status server handle concurrent requests? Single-threaded blocking — designed for one user.
- What if multiple designs exist with mixed approval status? Script reports ALL unapproved designs, not just the first.

## Functional Requirements

- **FR-001**: Gate scripts MUST exit non-zero when conditions are not met, and zero when satisfied.
- **FR-002**: Status scripts MUST produce deterministic output — same input always yields same output.
- **FR-003**: Version check MUST compare local VERSION against the latest GitHub release tag.
- **FR-004**: Pre-flight scripts MUST NOT modify any project files (read-only enforcement).
- **FR-005**: All scripts MUST accept the project root path as the first argument.
- **FR-006**: Scripts MUST print actionable error messages (not just "FAIL").

## Success Criteria

| # | Criterion | Measurable? |
|---|-----------|-------------|
| SC-001 | Gate script exits non-zero for unapproved designs | ✅ Script exit code |
| SC-002 | Status dashboard renders complete project map | ✅ Visual inspection |
| SC-003 | Version check detects outdated harness | ✅ Exit code + message |
| SC-004 | Sanity check detects missing required files | ✅ Exit code + specific error |
| SC-005 | All scripts accept root path argument | ✅ grep for `$1` or argument parsing |

## Key Entities

- **Gate Script**: A script that enforces a workflow condition by checking file state. Exits non-zero on violation.
- **Status Script**: A script that aggregates project state and produces a human-readable report.
- **Validation Script**: A script that checks format or structure compliance of a specific file type.
- **Release Script**: A script that records or generates release artifacts.

## Assumptions

- Scripts are always called by a command's pre-flight block — never run independently by users.
- The project root is always passed as the first argument.
- Scripts run on macOS/Linux with bash and Python 3 available.

## Out of Scope

- GUI-based status dashboards (the HTTP server provides minimal HTML — not a full web app).
- CI/CD pipeline integration (scripts are local-agent-only).
- Windows compatibility.

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
