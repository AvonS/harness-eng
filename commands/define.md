---
name: harness-define
description: Analyst persona - create feature spec from BRD

persona: Analyst
subagent: true
delegation:
  capability: work
  outcome: Create spec.md in the active phase feature folder
  read_paths: [BRD.md, CONSTITUTION.md, PHASES.md, relevant installed skills]
  write_authority: Active feature spec.md only
  return_format: Path, coverage, assumptions, and blockers
  max_response: 20KB
  context_policy: Pass paths; never inline complete files; history: none
  on_failure: Return ERROR with unresolved requirement
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
  - resolve_active_phase: use .harness-eng/phases/active/<phase-id>
  - create_feature_folder: use <active-phase>/features/<feature-id>/
  - identify_feature_from_brd
  - classify_change: documentation, configuration, executable_logic, workflow, bug_fix, business_behavior, ui_behavior, security_boundary, migration, or prototype
  - perform_adaptive_behavior_discovery: use examples only when behavior, state transitions, or user outcomes require clarification
  - propose_behavior_model: identify actors, goals, initial conditions, event flow, state transitions, and invariants
  - identify_primary_functional_flow: name the primary happy-path functional flow or justify inspection as stronger and cheaper
  - propose_testing_level: select S/M/L from change classification, risk, and boundary depth
  - propose_workflow_level: select S/M/L from risk, size, reversibility, and stack familiarity
  - propose_locked_constraints: identify user-specified technology constraints
  - propose_state_classification: classify persisted state by authority (model, operational, curated, external authoritative)
  - present_behavior_playback_to_human: ask bounded, contextual questions about load-bearing uncertainties
  - for_each_requirement:
    - create_testable_acceptance_examples: use Given/When/Then only for material behavior
    - identify_acceptance_criteria
  - write_spec: write spec.md including workflow_level, constraints.locked, state_classification, and technical decisions using templates/feature/spec.md
  - set_ref: PENDING
  - regenerate_handover: python3 scripts/harness-status.py --regenerate
  - route: to /h:design if workflow_level != S, else to /h:build

outputs:
  - spec.md with Ref: PENDING (including workflow_level, testing level, constraints, state classification, and decisions)

must_do:
  - Classify the change before selecting evidence
  - Perform behavior discovery when behavior is material or uncertain
  - Mark statements as confirmed, observed, inferred, or assumed
  - Present a concise behavior playback to the human before writing spec
  - Make acceptance criteria testable without forcing one notation
  - Cover all acceptance criteria
  - Define one primary happy-path functional flow or justify inspection as stronger and cheaper
  - Propose S/M/L workflow level and testing level from risk and boundary depth
  - Get human review of spec
  - Write locked technology constraints and state classification to spec.md
  - Regenerate derived handover.yaml after spec is written

must_not_do:
  - Skip requirements
  - Assume implementation details
  - Proceed without human approval
---
<!-- *** Maintained by AvonS/harness-eng, DON'T modify this, will be overwritten during next upgrade *** -->
