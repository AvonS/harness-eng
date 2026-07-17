---
name: harness-change
description: Unified change workflow command for bugs and CRs.
persona: Developer
subagent: true
delegation:
  capability: work
  outcome: Resolve bug or CR via classify -> baseline -> delta -> implement -> verify -> archive
  read_paths: [change context, technology.yaml, relevant installed skills]
  write_authority: Task-scoped application files, tests, CHG-NNN.md, and handover.yaml
  return_format: CHG-NNN path, implementation paths, evidence, and verdict
  max_response: 20KB
  context_policy: Pass paths; never inline complete files; history: none
  on_failure: Return ERROR with unresolved blocker

gates:
  - check: spec.md exists (to read workflow level and constraints)
    on_fail: STOP, run /h:define first

actions:
  - classify_change: identify if the change is a bug or CR
  - evaluate_promotion_criteria: promote to full /h:define + /h:design if the change touches a locked stack, public interface, persistent schema, security boundary, or architecture boundary
  - record_baseline: capture baseline revision hash, dirty state, and observed/reproduction behavior
  - read_prior_decisions: read decisions from active spec.md, design.md, and past slices
  - write_change_record: create CHG-NNN.md using templates/feature/change.md carrying forward baseline, delta, decisions, and relevant prior decisions
  - implement_smallest_delta: implement the change using the smallest required code delta
  - run_focused_evidence: verify the change on the affected flow and boundary only
  - regenerate_handover: python3 scripts/harness-status.py --regenerate
  - commit: commit the change record and implementation code
  - route: to /h:verify

must_do:
  - Promote change to full define/design flow if promotion criteria are met
  - Capture dirty worktree state in CHG-NNN baseline section BEFORE making edits
  - Carry forward relevant decisions from prior slices
  - Use the smallest code delta to resolve the bug or CR
  - Run focused evidence on the affected boundary
  - Automatically regenerate handover.yaml

must_not_do:
  - Implement change touching locked stack or schema without promoting to full define/design flow
  - Commit implementation code without passing the focused evidence check
---
<!-- *** Maintained by AvonS/harness-eng, DON'T modify this, will be overwritten during next upgrade *** -->
