---
name: harness-build
description: Implement features using the approved evidence contract
persona: Developer
subagent: true
delegation:
  capability: work
  outcome: Implement only the approved incomplete tasks and their evidence
  read_paths: [technology.yaml, active spec.md, active design.md, active tasks.md, relevant installed skills]
  write_authority: Task-scoped application files, tests, tasks.md, and SLICE_LOG.md
  return_format: Bounded summary of tasks, changed paths, checks, commits, and blockers
  max_response: 20KB
  context_policy: Pass paths and concise retry state; never inline complete files or raw logs
  on_failure: Return ERROR with blocker and partial task state

gates:
  - check: 'design.md "Ref: APPROVED"'
    on_fail: STOP, route to design
  - check: tasks.md exists
    on_fail: STOP, route to tasks
  - check: no BLOCKED.md in active features
    on_fail: STOP, route to blocked-state recovery

preflight:
  - read_design (architecture, interfaces)
  - read_tasks (what to build)
  - read_review_pre_verify (to fix code defects if returning from failure)
  - read_deferred_ledger (if deferred.md exists in active feature)

actions:
  - for_each_task:
    - execute_ponytail_decision_ladder: evaluate before adding any dependencies or abstractions
    - produce_required_evidence: follow the approved evidence contract
    - use_tdd_for_executable_logic: confirm failure before implementation when a meaningful executable test exists
    - commit
  - resolve_deferred_items: iterate current-build deferred items, resolve each or reroute with explicit destination update to pre-verify or next-cr
  - update_ledger_status: mark resolved items with resolution evidence in deferred.md
  - after_all_tasks:
    - run_required_evidence
    - run_existing_regression_suite
    - if evidence_fails: STOP, fix evidence failures
    - if evidence_passes: route to /h:review-pre-verify

must_do:
  - Strictly follow the Ponytail YAGNI framework when writing code
  - Use the cheapest deterministic evidence that proves the task
  - Use regression-first testing for bug fixes
  - Use TDD for executable logic
  - Record why a required evidence item is not applicable
  - Commit after each task
  - Resolve or explicitly reroute assigned current-build deferred items
  - Update ledger status with resolution evidence

must_not_do:
  - Implement executable logic without its required evidence
  - Add test categories excluded by the approved evidence contract without a discovered design gap
  - Commit without passing required evidence
  - Silently drop deferred items
---
<!-- *** Maintained by AvonS/harness-eng, DON'T modify this, will be overwritten during next upgrade *** -->
