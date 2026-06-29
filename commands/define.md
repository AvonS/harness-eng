---
name: harness-define
description: Collaborator persona - create feature spec from BRD

persona: Collaborator
subagent: true

gates:
  - check: BRD.md exists
    on_fail: STOP, run /h:init
  - check: CONSTITUTION.md exists
    on_fail: STOP, run /h:init

preflight:
  - read_brd (requirements, goals, constraints)
  - read_constitution (rules, conventions)
  - read_previous_feedback (to act on gap list or rejection notes if returning from failure)

actions:
  - identify_feature_from_brd
  - for_each_requirement:
    - create_given_when_then_stories
    - identify_acceptance_criteria
  - write_spec (spec.md)
  - set_ref: PENDING
  - route: to /h:design

outputs:
  - spec.md with Ref: PENDING

must_do:
  - Include Given/When/Then stories
  - Cover all acceptance criteria
  - Get human review of spec

must_not_do:
  - Skip requirements
  - Assume implementation details
  - Proceed without human approval
---
