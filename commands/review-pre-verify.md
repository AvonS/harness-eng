---
name: harness-review-pre-verify
description: Fresh-eyes review in isolated subagent context
persona: Sr Tech Lead
subagent: true
reason: Fresh-eyes review, completely isolated from the build process

gates:
  - check: 'design.md "Ref: APPROVED"'
    on_fail: STOP, route to design
  - check: spec.md exists
    on_fail: STOP, route to define (or /h:bug)
  - check: all tasks complete
    on_fail: STOP, route to build

actions:
  - read_changed_files_and_relevant_dependencies
  - read_design (architecture, interfaces)
  - read_spec (requirements, acceptance criteria)
  - run_required_sensors from technology.yaml
  - check_evidence_contract_compliance
  - check_design_implementation_gaps
  - check_spec_requirement_gaps
  - check_required_evidence_coverage
  - check_code_quality (patterns, conventions, errors)
  - write_review_report: verdict, critical_gaps, high_gaps, medium_gaps, low_gaps
  - if verdict == PASS:
    - set_ref: APPROVED
    - route: to /h:verify
  - if verdict == CONDITIONAL:
    - set_ref: APPROVED (with gap list)
    - route: to /h:verify
  - if verdict == FAIL:
    - set_ref: PENDING
    - STOP, route to build

must_do:
  - Audit code for Ponytail YAGNI compliance (flag unnecessary third-party dependencies or excessive abstractions)
  - Read every changed file and each dependency needed to judge the change
  - Verify sanity-check.sh covers changes required by the evidence contract
  - Verify sanity-check.sh has regression tests for bug fixes
  - Compare against design and spec
  - Identify gaps (not suggestions)
  - Be strict (production-ready bar)
  - Classify each missing item as defect, design_gap, or improvement
  - Block defects and design gaps
  - Record improvements as non-blocking backlog items

must_not_do:
  - Assume build agent did things correctly
  - Skip relevant changed files or dependencies
  - Skip sanity check completeness check
  - Give PASS if sanity check incomplete
  - Give PASS if gaps exist
  - Add a new test category merely because it is possible
  - Expand the approved evidence contract unless security exposure, changed scope, or a false design assumption is demonstrated
---
<!-- *** Maintained by AvonS/harness-eng, DON'T modify this, will be overwritten during next upgrade *** -->
