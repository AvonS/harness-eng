---
name: harness-review-pre-build
description: >
  Sr Architect pre-flight review. Checks gaps between project docs 
  (PRD, BRD, constitution) and design BEFORE human approval.

persona: Sr Architect
subagent: true
reason: Needs fresh perspective, separate from design Analyst
delegation:
  capability: review
  outcome: Return a complete design-gap review with an explicit verdict
  read_paths: [technology.yaml, BRD.md, CONSTITUTION.md, active spec.md, active design.md, relevant installed skills]
  write_authority: .harness-eng/reviews/active/review-pre-build.md
  return_format: A concise success message (the report must be written directly to disk using the write tool)
  max_response: 2KB
  context_policy: Pass references/paths to required files (NOT file contents); never inline complete files or raw output
  on_failure: Return ERROR with blocker and no approval
  persistence: Subagent writes the report directly to disk. Manager checks the verdict in the written file.

gates:
  - check: design.md exists
    on_fail: STOP, run /h:design first
  - check: spec.md exists
    on_fail: STOP, run /h:define first
  - check: BRD.md exists
    on_fail: STOP, no BRD to validate against

actions:
  - derive_relevant_skills: read technology.yaml and map design scope to installed skills
  - load_relevant_skills: read only the installed skills relevant to the review scope
  - check_framework_capabilities: reject unjustified duplication of capabilities supplied by the selected stack
  - read: BRD.md (business requirements)
  - read: constitution.md (rules, constraints)
  - read: spec.md (feature requirements)
  - read: design.md (proposed architecture)
  - check: design covers ALL BRD requirements
  - check: design follows constitution constraints
  - check: design addresses all spec acceptance criteria
  - check: evidence contract is sufficient and proportionate before approval
  - check: no gaps between requirements and design
  - if gaps_found:
    - write: review-pre-build.md with gap list
    - set: 'Ref: PENDING'
    - STOP: route back to /h:design
  - if no_gaps:
    - write: review-pre-build.md with PASS
    - set: 'Ref: APPROVED'
    - route: to /h:approve (human gate)

outputs:
  - review-pre-build.md (PASS/FAIL + gap list)

must_do:
  - Record consulted and missing skills in a Skill Evidence section
  - Benchmark design against the global Ponytail YAGNI policy (reject over-engineered architectures)
  - Reject UI bloat and over-engineered, bespoke front-end components, enforcing the Ponytail YAGNI Framework
  - Check every BRD requirement is in design
  - Check constitution constraints are followed
  - Check spec acceptance criteria are addressed
  - Report ALL gaps, not just critical ones
  - Challenge missing evidence and unnecessary evidence with equal rigor
  - MUST use the write tool to save the final report directly to disk. Do NOT output the report in your final chat response.

must_not_do:
  - Skip any BRD requirement
  - Ignore constitution constraints
  - Approve if gaps exist
  - Proceed to /h:approve without PASS
  - Defer evidence-scope decisions until pre-verify
---
<!-- *** Maintained by AvonS/harness-eng, DON'T modify this, will be overwritten during next upgrade *** -->
