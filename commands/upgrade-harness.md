---
name: harness-upgrade
description: Upgrade harness to latest version

persona: Manager
subagent: false
reason: Bootstrap operation

gates:
  - check: .harness-eng/ exists
    on_fail: STOP, run /h:init
  - check: current version < latest version
    on_fail: report "already up to date"

actions:
  - fetch: latest commands from harness repo
  - fetch: latest scripts from harness repo (EXCLUDING sanity-check.sh)
  - fetch: latest templates from harness repo
  - compare: local vs remote for each file
  - preserve: project-specific files (constitution, BRD, architecture, sanity-check.sh)
  - update: harness files only
  - report: what changed
  - commit: upgrade changes

must_do:
  - Fetch from canonical source
  - Preserve project customizations
  - Exclude sanity-check.sh from updates (it is a project-specific file)
  - Report changes clearly

must_not_do:
  - Overwrite project-level files (e.g., sanity-check.sh)
  - Skip comparison
  - Upgrade without reporting
---
