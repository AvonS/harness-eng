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
    - write_test (must fail)
    - implement (must pass test)
    - commit
  - after_all_tasks:
    - run_all_tests
    - if tests_fail: STOP, fix tests
    - if tests_pass: route to /h:review-pre-verify

must_do:
  - Write test first (TDD)
  - Test must fail before implementation
  - Test must pass after implementation
  - Commit after each task

must_not_do:
  - Implement without test
  - Skip failing test
  - Commit without passing test
---
