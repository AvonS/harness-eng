---
name: harness-triage
description: Triage incoming requests (bug, CR, feature)

persona: Analyst
subagent: false
reason: Routing decision

gates:
  - check: .harness-eng/ exists
    on_fail: STOP, run /h:init

actions:
  - analyze: user request
  - classify_request_type: critical_bug, wip_phase_cr, or non_critical_or_feature
  - if critical_bug:
    - route to /h:bug
  - if wip_phase_cr:
    - classify_change: material (behavior, interface, schema, security, scope, evidence contract) or editorial (wording, comments, documentation sync, test-expectation alignment)
    - if material:
      - update active phase spec.md with the CR
      - instruct user to run /h:design to incorporate CR into architecture
    - if editorial:
      - append finding to active feature's deferred.md with destination=next-cr or backlog
      - inform user the approval-preserving editorial amendment is recorded in the deferred ledger, no design cycle required
  - if non_critical_or_feature:
    - append to .harness-eng/docs/backlog.md
    - inform user it has been deferred

must_do:
  - Classify before routing
  - Explain classification reasoning
  - Classify incoming changes as material or editorial before routing
  - Route editorial amendments to the deferred.md ledger, not the full design cycle

must_not_do:
  - Skip classification
  - Route without explaining why
  - Route editorial amendments through the full design cycle
---
<!-- *** Maintained by AvonS/harness-eng, DON'T modify this, will be overwritten during next upgrade *** -->

