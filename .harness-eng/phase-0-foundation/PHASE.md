# Phase 0: Foundation — Workflow Definition

**Status:** Completed
**Started:** 2026-06-22
**Goal:** Define and codify the 4-persona workflow as the canonical process

## Features

| Feature | Status | Description |
|---------|--------|-------------|
| F001: Workflow Commands | ✅ Built | 14 command files (init, define, design, build, verify, release, etc.) |
| F002: Enforcement Scripts | ✅ Built | 12 shell/Python scripts for gate enforcement, status, version checks |
| F003: Document Templates | ✅ Built | Feature templates (spec, design, tasks) + big-picture templates |
| F004: Language Skills | ✅ Built | 7 per-language skill conventions (Go, Python, Node, SQL, etc.) |
| F005: Git Hooks | ✅ Built | Pre-commit hook for commit message validation |
| F006: Agent Definitions | ✅ Built | 4 persona-specific agent instructions |
| F007: User-Facing Docs | ✅ Built | User guide, BRD, command reference, architectural review |

## Exit Criteria

### Feature Coverage
- [x] All 7 product source directories reverse-engineered into features (F001–F007)
- [x] Each feature has a spec.md describing purpose and file inventory
- [x] Each feature has a tasks.md listing every file as a completed task
- [x] spec.md uses Given/When/Then format for user stories

### Architecture
- [x] ARCHITECTURE.md documents contract architecture, templates, gates, personas, workflow loop, symlink design, dogfood version tracking, and change impact analysis
- [x] High-level flow diagram shows 4-stage pipeline with 3 gates
- [x] Detailed workflow loop shows 12-step lifecycle with all routing paths
- [x] Symlink architecture documented (product source symlinks vs project copies)

### Constitution
- [x] CONSTITUTION.md has SST Golden Rules, Core Principles, Mandatory Gates, 4-Persona Workflow, Architecture Rules, Naming Conventions, AI Agent Rules
- [x] Dogfood Rules section for template sync workflow
- [x] All 3 gates documented (design approval, sr tech lead review, release approval)

### Commands (F001)
- [x] All 14 command files exist under commands/
- [x] Every command has YAML frontmatter (name, description, trigger)
- [x] Every command has pre-flight checks, execution steps, output artifacts, constraints
- [x] Cross-command workflow is consistent: init → define → design → approve → tasks → review-pre-build → build → review-pre-verify → verify → release
- [x] Gate commands (approve, release) handle marker writing (Ref: APPROVED)
- [x] Bug/CR triage and shortened workflow exists

### Scripts (F002)
- [x] All 12 script files exist under scripts/
- [x] Gate enforcement scripts grep for cross-document markers
- [x] Version check compares local vs remote
- [x] Status scripts produce readable dashboard output
- [x] SLICE_LOG scripts validate narrative format

### Templates (F003)
- [x] Feature templates (spec, design, tasks) exist with placeholder tokens
- [x] Big-picture templates (CONSTITUTION, BRD, ARCHITECTURE) exist with fill instructions
- [x] Phase template and PHASES.md template exist
- [x] sanity-check.sh template exists for integration testing
- [x] SLICE_LOG template exists

### Skills (F004)
- [x] 7 skill directories exist (go, python, node, sql, git, datastar, oat)
- [x] Each skill has SKILL.md with language-specific conventions
- [x] Skills are referenced by design and review-pre-build commands

### Hooks (F005)
- [x] Pre-commit hook exists enforcing commit message format
- [x] Hook runs basic harness checks before allowing commits

### Agent Definitions (F006)
- [x] 4 personas defined: Collaborator, Developer, Sr Tech Lead, Gatekeeper
- [x] Each persona has agent.md with commands, mode, gate responsibilities
- [x] Persona switching documented in CONSTITUTION.md and ARCHITECTURE.md

### Documentation (F007)
- [x] BRD-harness.md documents full 11-step workflow vision
- [x] Command reference exists
- [x] User guide exists
- [x] Architectural review notes exist

### Dogfood & Versioning
- [x] .harness-eng/VERSION is symlinked to version.txt when root version.txt exists
- [x] upgrade-harness skips VERSION write when it's a symlink
- [x] Dogfood Rules in CONSTITUTION.md define template sync workflow
- [x] "sync dog food" trigger phrase maps to template sync steps
