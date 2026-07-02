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
  - read_all_code_files (no skipping)
  - read_design (architecture, interfaces)
  - read_spec (requirements, acceptance criteria)
  - run_required_sensors from technology.yaml
  - check_sanity_check_completeness: new_features_have_tests, bug_fixes_have_regression_tests, all_phases_covered
  - check_design_implementation_gaps
  - check_spec_requirement_gaps
  - check_test_coverage (do tests cover all requirements?)
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
  - Read ALL code files
  - Verify sanity-check.sh covers new features
  - Verify sanity-check.sh has regression tests for bug fixes
  - Compare against design and spec
  - Identify gaps (not suggestions)
  - Be strict (production-ready bar)

must_not_do:
  - Assume build agent did things correctly
  - Skip files
  - Skip sanity check completeness check
  - Give PASS if sanity check incomplete
  - Give PASS if gaps exist
---
<!-- *** Maintained by AvonS/harness-eng, DON'T modify this, will be overwritten during next upgrade *** -->
