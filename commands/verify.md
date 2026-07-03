---
name: harness-verify
description: Verify production-ready
persona: Gatekeeper
subagent: true
delegation:
  capability: verify
  outcome: Execute approved evidence and return a reproducible verification verdict
  read_paths: [technology.yaml, active spec.md, active design.md, active tasks.md, active review-pre-verify.md]
  write_authority: none
  return_format: Markdown verification report ending with VERDICT PASS or FAIL
  max_response: 20KB
  context_policy: Pass paths; never inline complete files or raw logs
  on_failure: Return ERROR with failed command and bounded evidence
  persistence: Manager writes the returned report unchanged to verification.md

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
