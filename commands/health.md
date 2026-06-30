---
name: harness-health
description: Check agent compliance

persona: Sr Tech Lead
subagent: true
reason: Needs fresh perspective

prerequisites:
  - check: .harness-eng/ exists
    on_fail: STOP, run /h:init

actions:
  - verify: constitution read before actions
  - verify: design approved before build
  - verify: SLICE_LOG updated on commits
  - verify: tests before implementation
  - verify: correct branch for work
  - verify: tasks followed in order
  - verify: commit message convention
  - report: violations found
  - if violations: STOP, explain corrective action

must_do:
  - Check all 7 compliance rules
  - Report violations clearly
  - Suggest corrective actions

must_not_do:
  - Skip any rule check
  - Soft-pedal violations
---
<!-- *** Maintained by AvonS/harness-eng, DON'T modify this, will be overwritten during next upgrade *** -->

