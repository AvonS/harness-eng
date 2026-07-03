---
name: harness-bug
description: Process bug/CR with simplified workflow
persona: Analyst
subagent: true
delegation:
  capability: work
  outcome: Create one simplified bug or CR item under specs/active
  read_paths: [BRD.md, CONSTITUTION.md, technology.yaml, triage result, relevant installed skills]
  write_authority: One specs/active item folder only
  return_format: Paths, classification, scope, evidence, and blockers
  max_response: 20KB
  context_policy: Pass paths; never inline complete files
  on_failure: Return ERROR with unresolved classification

gates:
  - check: triage_classified (critical bug)
    on_fail: STOP, route to triage
  - check: branch_created (bugfix/BUG-NNN)
    on_fail: STOP, create branch

actions:
  - create_branch (bugfix/BUG-NNN)
  - write_simplified_spec (spec.md with bug description and acceptance criteria)
  - write_design (design.md with impact analysis, technical design, and ui_brief if applicable)
  - set_ref: 'PENDING (in design.md)'
  - STOP: instruct user to run /h:approve <bug-id>

must_do:
  - Ensure spec includes clear reproduction steps
  - Ensure design includes impact analysis
  - Stop and wait for human approval via /h:approve

must_not_do:
  - Fix the bug directly
  - Skip human approval
---
<!-- *** Maintained by AvonS/harness-eng, DON'T modify this, will be overwritten during next upgrade *** -->

