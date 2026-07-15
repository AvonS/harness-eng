---
name: harness-health
description: Check agent compliance

persona: Sr Tech Lead
subagent: true
reason: Needs fresh perspective
delegation:
  capability: review
  outcome: Return a lifecycle-aware compliance report
  read_paths: [AGENTS.md, CONSTITUTION.md, technology.yaml, active artifacts, SLICE_LOG.md]
  write_authority: none
  return_format: Report classifying each rule PASS, FAIL, PENDING, or N/A
  max_response: 20KB
  context_policy: Pass paths; never inline complete files or raw logs
  on_failure: Return ERROR with unavailable evidence

prerequisites:
  - check: .harness-eng/ exists
    on_fail: STOP, run /h:init

actions:
  - derive_lifecycle_state: inspect filesystem artifacts and gate markers before evaluating compliance
  - verify: constitution read before actions
  - verify: design approved before build
  - verify: SLICE_LOG updated on commits
  - verify: tests before implementation
  - verify: correct branch for work
  - verify: tasks followed in order
  - verify: commit message convention
  - verify: deferred ledger schema compliance (valid destinations, valid statuses, no orphaned items)
  - classify_each_check: [PASS: required now and satisfied, FAIL: required now and unsatisfied, PENDING: expected next, N/A: not required in current state]
  - report: lifecycle-aware findings
  - if violations: STOP, explain corrective action

must_do:
  - Check all 7 compliance rules
  - Evaluate each rule only when applicable to the derived lifecycle state
  - Report future-stage artifacts as PENDING or N/A
  - Report violations clearly
  - Suggest corrective actions
  - Verify deferred ledger schema compliance when deferred.md exists

must_not_do:
  - Skip any rule check
  - Soft-pedal violations
  - Report a future-stage artifact as a violation
---
<!-- *** Maintained by AvonS/harness-eng, DON'T modify this, will be overwritten during next upgrade *** -->
