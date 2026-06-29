---
name: harness-tasks
description: Developer persona - break design into granular tasks

persona: Developer
subagent: true

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
