---
name: harness-status
description: Display current project state

persona: Manager
subagent: false
reason: Read-only operation

gates:
  - check: .harness-eng/ exists
    on_fail: STOP, run /h:init

actions:
  - read: version.txt
  - read: .harness-eng/PHASES.md
  - read: .harness-eng/SLICE_LOG.md
  - scan: specs/active/*
  - scan: deferred.md in active features
  - display_formatted_status_report: version, phases progress, active specs, deferred item counts, recent commits

must_do:
  - Show complete state snapshot
  - Include last 3 SLICE_LOG entries

must_not_do:
  - Modify anything
---
<!-- *** Maintained by AvonS/harness-eng, DON'T modify this, will be overwritten during next upgrade *** -->

