---
name: harness-build
description: Implement features using TDD
persona: Jr Programmer

gates:
  - check: 'design.md "Ref: APPROVED"'
    on_fail: STOP, route to design
  - check: tasks.md exists
    on_fail: STOP, route to tasks

preflight:
  - read_design (architecture, interfaces)
  - read_tasks (what to build)
  - read_review_pre_verify (to fix code defects if returning from failure)

actions:
  - for_each_task:
    - execute_ponytail_decision_ladder: evaluate before adding any dependencies or abstractions
    - write_test (must fail)
    - implement (must pass test)
    - commit
  - after_all_tasks:
    - run_all_tests
    - if tests_fail: STOP, fix tests
    - if tests_pass: route to /h:review-pre-verify

must_do:
  - Strictly follow the Ponytail YAGNI framework when writing code
  - Write test first (TDD)
  - Test must fail before implementation
  - Test must pass after implementation
  - Commit after each task

must_not_do:
  - Implement without test
  - Skip failing test
  - Commit without passing test
---
<!-- *** Maintained by AvonS/harness-eng, DON'T modify this, will be overwritten during next upgrade *** -->

