---
name: harness-verify
description: Verify production-ready
persona: Gatekeeper

gates:
  - check: 'review-pre-verify.md "Ref: APPROVED"'
    on_fail: STOP, route to review-pre-verify
  - check: all tasks complete
    on_fail: STOP, route to build
  - check: all tests pass
    on_fail: STOP, fix failing tests

actions:
  - run_all_tests (unit + integration)
  - if tests_fail: STOP, fix tests
  - check_readme_updated (if user-facing changes)
  - check_release_notes_updated
  - write_verification (Release Ref: PENDING)
  - commit_verification
  - route: to /h:release (human gate)

must_do:
  - All tests must pass
  - README updated if user-facing changes
  - RELEASE-NOTES.md updated
  - Include Release Ref: PENDING

must_not_do:
  - Skip test run
  - Write verification if tests fail
  - Skip documentation checks
---
