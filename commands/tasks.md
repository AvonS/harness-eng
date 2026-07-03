---
name: harness-tasks
description: Developer persona - break design into granular tasks

persona: Developer
subagent: true
delegation:
  capability: work
  outcome: Create dependency-ordered tasks for the approved design
  read_paths: [CONSTITUTION.md, active spec.md, active design.md, relevant installed skills]
  write_authority: Active feature tasks.md only
  return_format: Path, task count, dependencies, evidence, and blockers
  max_response: 20KB
  context_policy: Pass paths; never inline complete files
  on_failure: Return ERROR with missing prerequisite

gates:
  - check: design.md exists
    on_fail: STOP, route to design
  - check: 'design.md "Ref: APPROVED"'
    on_fail: STOP, route to approve
  - check: spec.md exists
    on_fail: STOP, route to define (or /h:bug)

preflight:
  - read_spec (requirements, acceptance criteria)
  - read_design (architecture, interfaces, file layout)
  - read_constitution (conventions, rules)
  - read_review_pre_verify (to add tasks for gaps if returning from failure)

actions:
  - for_each_user_story:
    - identify_what_needs_to_change
    - list_files_to_create_or_modify
    - estimate_complexity
  - order_tasks_by_dependency
  - ensure_test_first_order
  - write_tasks (tasks.md)
  - set_ref: PENDING
  - route: to /h:build

outputs:
  - tasks.md with Ref: PENDING

must_do:
  - One commit per task
  - Test before implementation
  - Include verification steps

must_not_do:
  - Skip dependencies
  - Bundle multiple changes in one task
---
<!-- *** Maintained by AvonS/harness-eng, DON'T modify this, will be overwritten during next upgrade *** -->

