---
name: harness-upgrade
description: Upgrade harness to latest version

persona: Manager
subagent: false
reason: Bootstrap operation

gates:
  - check: .harness-eng/ exists
    on_fail: STOP, run /h:init
  - check: git status is clean
    on_fail: STOP, commit or stash changes before upgrading

actions:
  - fetch_and_replace_from_canonical:
    - commands/ -> .harness-eng/commands/
    - agents/ -> .harness-eng/agents/
    - scripts/ -> .harness-eng/scripts/ (EXCLUDE: sanity-check.sh)
    - templates/ -> .harness-eng/templates/
    - AGENTS.md -> ./AGENTS.md
  - preserve_project_state:
    - .harness-eng/CONSTITUTION.md
    - .harness-eng/BRD.md
    - .harness-eng/ARCHITECTURE.md
    - .harness-eng/SLICE_LOG.md
    - .harness-eng/scripts/sanity-check.sh
    - all active/done phases
  - fetch_skill_source: update https://github.com/AvonS/harness-eng-skills.git in the user cache
  - use_skill_selector: install selected upstream skills while preserving project-modified copies
  - report: list of updated files
  - commit: "chore: upgrade harness-eng to latest"

must_do:
  - Fetch exactly the specified folders from canonical source
  - Always preserve project customizations and state
  - Exclude sanity-check.sh from script updates
  - Report changes clearly
  - Record the harness-eng-skills source revision and installed skill digests

must_not_do:
  - Overwrite project-level files (BRD, CONSTITUTION, SLICE_LOG)
  - Upgrade with uncommitted changes
---
<!-- *** Maintained by AvonS/harness-eng, DON'T modify this, will be overwritten during next upgrade *** -->
