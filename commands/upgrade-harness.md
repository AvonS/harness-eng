---
name: harness-upgrade
description: Upgrade harness to latest version

persona: Manager
subagent: false
reason: Bootstrap operation
canonical_url: https://raw.githubusercontent.com/AvonS/harness-eng/main/commands/upgrade-harness.md
execution_source: fetched_canonical_required

gates:
  - check: current upgrade contract was fetched from canonical_url for this invocation
    on_fail: STOP, fetch canonical_url and restart using the fetched contract
  - check: .harness-eng/ exists
    on_fail: STOP, run /h:init
  - check: git status is clean
    on_fail: STOP, record the dirty worktree and ask the user to commit or explicitly direct a separate continuation plan

actions:
  - run_version_check: python3 .harness-eng/scripts/version-check.py . .harness-eng
  - inspect_existing_project:
    - read current harness version and manifest, if present
    - inspect .harness-eng/CONSTITUTION.md, BRD.md, ARCHITECTURE.md, PHASES.md, active and archived slices/specs/changes
    - inspect current workflow commands and existing project customizations
    - record branch, revision, dirty state, active slice, and authorized paths
    - identify legacy layout and migration requirements
  - recommend_workflow_level:
    - classify the existing project as S, M, or L using uncertainty, security/data risk, integrations, reversibility, operational impact, duration, and collaboration size
    - show the recommendation and concrete rationale to the user
    - identify whether the recommendation applies to future slices only or may apply to the active slice
  - await_explicit_migration_consent:
    - STOP after presenting the recommendation
    - do not write workflow_level, replace project files, or apply migrations before explicit user approval
    - if rejected, record "migration recommended, not approved" in the authoritative SLICE_LOG.md and leave lifecycle behavior unchanged
  - record_migration_consent:
    - write .harness-eng/migration/workflow-level-YYYYMMDD.yaml only after approval
    - include from_version, to_version, previous_workflow, recommended_level, approved_level, approval, rationale, applies_to, and notes
    - use a disambiguating suffix if today's migration artifact already exists
  - bootstrap_migration_engine:
    - fetch the current migrate-harness.py, migration catalog, and referenced migration modules
    - inspect the migration plan before applying it
  - plan_migration:
    - calculate ordered migrations from the detected current version/layout to the target version
    - report files to create, update, preserve, or archive
    - STOP if the plan would overwrite project-owned state or an unknown dirty path
  - apply_pre_migration:
    - run migration: python3 .harness-eng/scripts/migrate-harness.py apply
    - preserve active in-flight slices on their existing workflow unless the user separately approved mid-slice migration
    - apply the approved workflow level to future slices and changes
  - fetch_and_replace_from_canonical:
    - commands/ -> .harness-eng/commands/
    - agents/ -> .harness-eng/agents/
    - scripts/ -> .harness-eng/scripts/ (EXCLUDE: sanity-check.sh)
    - migrations/ -> .harness-eng/migrations/
    - templates/ -> .harness-eng/templates/
    - AGENTS.md -> ./AGENTS.md
    - VERSION -> .harness-eng/VERSION
  - preserve_project_state:
    - .harness-eng/CONSTITUTION.md
    - .harness-eng/BRD.md
    - .harness-eng/ARCHITECTURE.md
    - .harness-eng/SLICE_LOG.md
    - .harness-eng/design-registry.yaml
    - .harness-eng/scripts/sanity-check.sh
    - all active/archive phases and active/done bug or CR specs
  - initialize_design_registry_if_missing: create an empty .harness-eng/design-registry.yaml for project-specific additions if it doesn't exist
  - validate_migration: python3 .harness-eng/scripts/migrate-harness.py status
  - validate_preservation:
    - confirm constitution, BRD, architecture, slice log, project registry, active/archive slices, changes, and user-modified skills remain intact
    - confirm the migration artifact records the approved scope
    - confirm current active work retains its prior workflow unless mid-slice migration was separately approved
  - generate_handover: regenerate .harness-eng/handover.yaml from authoritative project artifacts
  - finalize_migration: update manifest target release
  - fetch_skill_source: update https://github.com/AvonS/harness-eng-skills.git in the user cache
  - use_skill_selector: install selected upstream skills while preserving project-modified copies
  - append_slice_log: record the upgrade and the new version in .harness-eng/SLICE_LOG.md
  - report: list of updated files
  - commit: "chore: upgrade harness-eng to latest"

must_do:
  - Execute the fetched canonical upgrade contract instead of the installed local copy
  - Inspect and report the existing project before recommending migration
  - Present the S/M/L recommendation and rationale before requesting consent
  - Fetch exactly the specified folders from canonical source only after the migration decision is recorded
  - Run migration engine before replacing files
  - Always preserve project customizations and state
  - Create design-registry.yaml only when the project file is missing
  - Exclude sanity-check.sh from script updates
  - Report changes clearly
  - Record the harness-eng-skills source revision and installed skill digests
  - Require explicit user approval before writing workflow level or applying a migration
  - Record rejected migration without changing lifecycle behavior
  - Keep in-flight slices on their previous workflow by default
  - Verify the migration plan and preservation results before finalizing the upgrade

must_not_do:
  - Continue from an installed local upgrade command after fetching its replacement
  - Overwrite an existing project design-registry.yaml
  - Overwrite project-level files (BRD, CONSTITUTION, SLICE_LOG)
  - Upgrade with uncommitted changes
  - Silently assign an S/M/L workflow level
  - Write migration consent or approval on behalf of the user
  - Apply a workflow change to an active slice without separate explicit approval
---
<!-- *** Maintained by AvonS/harness-eng, DON'T modify this, will be overwritten during next upgrade *** -->
