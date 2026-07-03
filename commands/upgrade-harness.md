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
    on_fail: STOP, commit or stash changes before upgrading

actions:
  - run_version_check: python3 .harness-eng/scripts/version-check.py . .harness-eng
  - bootstrap_migration_engine: If .harness-eng/scripts/migrate-harness.py or .harness-eng/migrations/catalog.json are missing, download them from the canonical repository before planning migration.
  - plan_migration: python3 .harness-eng/scripts/migrate-harness.py plan --target staged
  - apply_pre_migration: python3 .harness-eng/scripts/migrate-harness.py apply --target staged
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
    - all active/done phases
  - initialize_design_registry_if_missing: create an empty .harness-eng/design-registry.yaml for project-specific additions if it doesn't exist
  - validate_migration: python3 .harness-eng/scripts/migrate-harness.py status
  - finalize_migration: update manifest target release
  - fetch_skill_source: update https://github.com/AvonS/harness-eng-skills.git in the user cache
  - use_skill_selector: install selected upstream skills while preserving project-modified copies
  - append_slice_log: record the upgrade and the new version in .harness-eng/SLICE_LOG.md
  - report: list of updated files
  - commit: "chore: upgrade harness-eng to latest"
  - run_health_check: run /h:health to verify the project is healthy post-upgrade

must_do:
  - Execute the fetched canonical upgrade contract instead of the installed local copy
  - Fetch exactly the specified folders from canonical source
  - Run migration engine before replacing files
  - Always preserve project customizations and state
  - Create design-registry.yaml only when the project file is missing
  - Exclude sanity-check.sh from script updates
  - Report changes clearly
  - Record the harness-eng-skills source revision and installed skill digests

must_not_do:
  - Continue from an installed local upgrade command after fetching its replacement
  - Overwrite an existing project design-registry.yaml
  - Overwrite project-level files (BRD, CONSTITUTION, SLICE_LOG)
  - Upgrade with uncommitted changes
---
<!-- *** Maintained by AvonS/harness-eng, DON'T modify this, will be overwritten during next upgrade *** -->
