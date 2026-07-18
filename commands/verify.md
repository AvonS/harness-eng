---
name: harness-verify
description: Verify production-ready
persona: Gatekeeper
subagent: true
delegation:
  capability: verify
  outcome: Execute approved evidence and return a reproducible verification verdict
  read_paths: [project.yaml, technology.yaml, active spec.yaml (or spec.md), active design.md, active tasks.md, active review-pre-verify.md]
  write_authority: none
  return_format: Markdown verification report ending with VERDICT PASS or FAIL
  max_response: 20KB
  max_input_tokens: 12000
  max_output_tokens: 4000
  retry_threshold: 3
  context_policy: Pass paths; never inline complete files or raw logs; history: none
  on_failure: Return ERROR with failed command and bounded evidence
  persistence: Manager writes the returned report unchanged to verification.md

gates:
  - check: 'review-pre-verify.md "Ref: APPROVED"' (if workflow_level != S; ABSENT defaults to M/L)
    on_fail: STOP, route to review-pre-verify
  - check: all tasks complete (if workflow_level != S; ABSENT defaults to M/L)
    on_fail: STOP, route to build
  - check: all required evidence passes
    on_fail: STOP, fix evidence failures

actions:
  - check_evidence_reuse: check if config_hash, environment_hash, and revision match the previous verification record; if unchanged, reuse recorded evidence and skip re-running tests
  - read_deferred_ledger: if deferred.md exists in active feature, read it for reporting
  - run_evidence_contract_checks: (for S: run only happy-path or cheapest deterministic inspection; no unit-test quota)
  - run_existing_regression_suite: (run once, only when level/risk requires it for S)
  - run_required_sensors from technology.yaml
  - if evidence_fails: STOP, fix evidence failures
  - check_readme_updated (if user-facing changes)
  - check_release_notes_updated
  - report_deferred_items: include a "Deferred Items" section in the verification output listing open items with IDs and destinations
  - write_verification (Release Ref: PENDING)
  - commit_verification
  - regenerate_handover: python3 scripts/harness-status.py --regenerate
  - route: to /h:release (human gate)

must_do:
  - Reuse recorded evidence when config_hash, environment_hash, and revision are unchanged
  - All required evidence must pass
  - Existing regression suite must not regress
  - README updated if user-facing changes
  - RELEASE-NOTES.md updated
  - Include Release Ref: PENDING
  - Report deferred items separately from required evidence

must_not_do:
  - Skip required evidence
  - Write verification if tests fail
  - Skip documentation checks
  - Block verification for unresolved deferred items unless promoted to blocker
---
<!-- *** Maintained by AvonS/harness-eng, DON'T modify this, will be overwritten during next upgrade *** -->
