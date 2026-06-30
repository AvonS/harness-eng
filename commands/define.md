---
name: harness-define
description: Collaborator persona - create feature spec from BRD

persona: Collaborator
subagent: true
goal: Produce a rich, expressive, and human-readable spec.md document that explicitly follows templates/feature/spec.md.

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
  - perform_adaptive_behavior_discovery: choose Example Mapping, Journey Mapping, or Event Storming based on complexity
  - propose_behavior_model: identify actors, goals, initial conditions, event flow, state transitions, and invariants
  - present_behavior_playback_to_human: ask bounded, contextual questions about load-bearing uncertainties
  - for_each_requirement:
    - create_given_when_then_stories
    - identify_acceptance_criteria
  - write_spec: use templates/feature/spec.md to produce a detailed, well-formatted markdown document
  - set_ref: PENDING
  - route: to /h:design

outputs:
  - spec.md with Ref: PENDING

must_do:
  - Perform behavior discovery before generating acceptance scenarios
  - Mark statements as confirmed, observed, inferred, or assumed
  - Present a concise behavior playback to the human before writing spec
  - Include Given/When/Then stories
  - Cover all acceptance criteria
  - Get human review of spec

must_not_do:
  - Skip requirements
  - Assume implementation details
  - Proceed without human approval
---
<!-- *** Maintained by AvonS/harness-eng, DON'T modify this, will be overwritten during next upgrade *** -->

