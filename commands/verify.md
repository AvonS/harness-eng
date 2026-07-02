---
name: harness-verify
description: Verify production-ready
persona: Gatekeeper

gates:
  - check: 'review-pre-verify.md "Ref: APPROVED"'
    on_fail: STOP, route to review-pre-verify
  - check: all tasks complete
    on_fail: STOP, route to build
  - check: all required evidence passes
    on_fail: STOP, fix evidence failures

actions:
  - run_evidence_contract_checks
  - run_existing_regression_suite
  - run_required_sensors from technology.yaml
  - if evidence_fails: STOP, fix evidence failures
  - check_readme_updated (if user-facing changes)
  - check_release_notes_updated
  - write_verification (Release Ref: PENDING)
  - commit_verification
  - route: to /h:release (human gate)

must_do:
  - All required evidence must pass
  - Existing regression suite must not regress
  - README updated if user-facing changes
  - RELEASE-NOTES.md updated
  - Include Release Ref: PENDING

must_not_do:
  - Skip required evidence
  - Write verification if tests fail
  - Skip documentation checks
---
<!-- *** Maintained by AvonS/harness-eng, DON'T modify this, will be overwritten during next upgrade *** -->
