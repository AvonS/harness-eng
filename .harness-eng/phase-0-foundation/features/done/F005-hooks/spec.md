---
name: spec
description: >
  Feature specification for git hooks.
  A pre-commit hook that validates commit messages follow
  the type(ID): description convention and runs basic harness
  checks before allowing commits. Hooks enforce commit quality
  at the client side — before any push or CI.
---

# Feature: Git Hooks

**Feature**: F005 — Git Hooks
**Status**: Complete (reverse-engineered)
**Ref**: PENDING

---

## User Stories

### Story 1 — Commit Message Validation (Priority: P1)

A developer commits code. The pre-commit hook validates the commit message follows the required format: `type(ID): description` where type is one of `fix`, `feat`, `chore`, `docs`, `refactor`, `test`, and ID references a task or issue number.

**Why this priority**: Consistent commits enable automated release notes, changelog generation, and history navigation.

**Independent test**: Attempt a commit with a bad message format — must be rejected with an error explaining the expected format.

**Acceptance Scenarios**:

1. **Given** a commit message `feat(42): add user login`, **When** the pre-commit hook runs, **Then** the commit is allowed.
2. **Given** a commit message `fixed stuff`, **When** the pre-commit hook runs, **Then** the commit is rejected with "Commit message must match format: type(ID): description".
3. **Given** a commit message `FEAT(42): add login` (uppercase type), **When** the pre-commit hook runs, **Then** the commit is rejected with a message about valid types.
4. **Given** a commit message with a valid format but empty description (e.g., `fix(1): `), **When** the pre-commit hook runs, **Then** the commit is rejected.

---

### Story 2 — Pre-Commit Harness Checks (Priority: P2)

Before allowing a commit, the pre-commit hook runs basic harness integrity checks: verifies required files exist, checks for uncommitted template changes, and validates SLICE_LOG format if modified.

**Why this priority**: Catches broken project state before it's committed — cheaper to fix locally than in CI.

**Independent test**: Stage a change that breaks SLICE_LOG format — the commit must be blocked.

**Acceptance Scenarios**:

1. **Given** staged changes to `.harness-eng/SLICE_LOG.md` with malformed entries, **When** the pre-commit hook runs, **Then** it rejects the commit and reports the invalid format.
2. **Given** staged changes that delete a required harness file (e.g., CONSTITUTION.md), **When** the pre-commit hook runs, **Then** it rejects with "Required harness files must not be deleted."
3. **Given** staged changes that pass all checks, **When** the pre-commit hook runs, **Then** it allows the commit to proceed.

---

### Story 3 — Hook Installation (Priority: P2)

A developer runs init or sets up the project. The pre-commit hook must be installed into `.git/hooks/pre-commit` (or symlinked). A setup script handles installation across environments.

**Why this priority**: Hooks don't work if they're not installed. Automatic installation prevents "forgot to install hooks."

**Independent test**: Run the install script and verify `.git/hooks/pre-commit` exists and is executable.

**Acceptance Scenarios**:

1. **Given** a fresh clone of the project with no `.git/hooks/pre-commit`, **When** the init command runs, **Then** it installs the hook from `hooks/pre-commit` into `.git/hooks/pre-commit`.
2. **Given** an existing `.git/hooks/pre-commit` that is out of date, **When** the init command runs with `--force`, **Then** it overwrites the old hook.

---

## Edge Cases

- What if `git` is not installed? Hook can't run — pre-commit is skipped. Not a failure state, but the agent should warn.
- What if the commit is a merge commit (generated message)? The hook should skip validation for merge commits (detect via `MERGE_MSG` or `GIT_REFLOG_ACTION`).
- What if the hook script has a bug that prevents ALL commits? The user can bypass with `git commit --no-verify` — the hook must not modify repo state.

## Functional Requirements

- **FR-001**: The pre-commit hook MUST validate commit message format against the pattern `type(ID): description`.
- **FR-002**: Valid types MUST include: `fix`, `feat`, `chore`, `docs`, `refactor`, `test`, `bugfix`, `cr`.
- **FR-003**: The hook MUST skip validation for merge commits.
- **FR-004**: The hook MUST be installable via init command.
- **FR-005**: The hook MUST NOT modify staged content — it's a read-only validator.

## Success Criteria

| # | Criterion | Measurable? |
|---|-----------|-------------|
| SC-001 | Hook rejects invalid commit message format | ✅ Exit code + error message |
| SC-002 | Hook allows valid commit messages | ✅ Commit succeeds |
| SC-003 | Hook installs via init without manual steps | ✅ `.git/hooks/pre-commit` exists |
| SC-004 | Hook skips merge commits | ✅ Merge commits succeed without validation |

## Key Entities

- **Pre-Commit Hook**: Shell script at `hooks/pre-commit` that runs before each commit.
- **Commit Message Format**: `type(ID): description` — validated by regex.

## Assumptions

- Developers work on macOS/Linux with bash and git.
- The `.git/hooks/` directory is writable.
- The hook is installed via symlink or copy — never edited in place.

## Out of Scope

- Server-side hook enforcement (that's CI/git server policy).
- Multi-hook orchestration (pre-commit is the only hook).
- GUI git clients that bypass hooks.

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
