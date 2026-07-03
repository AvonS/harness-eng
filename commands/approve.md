---
name: harness-approve
description: Human gate for design approval
persona: Gatekeeper
subagent: false

gates:
  - check: 'IF NOT bug/cr THEN review-pre-build.md "Ref: APPROVED"'
    on_fail: STOP, route to /h:review-pre-build (Agent Gate 1 must pass first)
  - check: design.md exists
    on_fail: STOP, route to design
  - check: 'design.md "Ref: PENDING"'
    on_fail: STOP, Design already approved or rejected

actions:
  - present_design_to_human
  - wait_for_human_response
  - if approved:
    - set_ref: 'APPROVED (in design.md)'
    - prompt_testing_level: ask user to confirm or select the feature's Testing Level (S/M/L) and update design.md header
    - route: to /h:tasks
  - if changes_requested:
    - set_ref: 'REJECTED (in design.md)'
    - route_to_design

must_do:
  - Present full design document
  - Wait for explicit human approval
  - Confirm or select Testing Level (S/M/L) and update design.md header upon approval
  - Update Ref marker in design.md

must_not_do:
  - Approve without human confirmation
  - Proceed without Ref: APPROVED
---
<!-- *** Maintained by AvonS/harness-eng, DON'T modify this, will be overwritten during next upgrade *** -->
