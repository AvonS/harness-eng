---
name: harness-review-pre-verify
description: Template for Sr Tech Lead review
agent_contract:
  prerequisites:
    - id: PRE-001
      action: "Confirm build is complete and all tasks marked done."
      on_failure: "STOP: Cannot review without completed build."
  actions:
    - id: ACT-001
      action: "Fill coverage matrix, code quality assessment, process compliance, and verdict."
  must_do:
    - id: MUST-001
      action: "Include coverage matrix showing every story status."
  must_not_do:
    - id: NEVER-001
      action: "Do not finalize without verdict and coverage matrix."
  outputs:
    - id: OUT-001
      path: "review-pre-verify.md with verdict"
---

# Sr Tech Lead Review: <feature>

**Date**: <date>
**Feature**: <feature name>
**Reviewer**: Automated (Sr Tech Lead prompt)
**Ref**: PENDING
**Status**: PASS / FAIL / CONDITIONAL

## Story Coverage

| Story | Implemented | Tests | Design Match | Quality | Status |
|-------|-------------|-------|--------------|---------|--------|
| US1 | ✅/❌ | ✅/❌ | ✅/❌ | ✅/❌ | PASS/FAIL |
| US2 | ✅/❌ | ✅/❌ | ✅/❌ | ✅/❌ | PASS/FAIL |

## Gap Analysis

| # | Story | Gap | Category | Severity | Fix |
|---|-------|-----|----------|----------|-----|
| 1 | <story> | <description> | Feature/Test/Code | CRITICAL/HIGH/MEDIUM | <fix> |

## Quality Findings

| # | File | Issue | Severity | Fix |
|---|------|-------|----------|-----|
| 1 | <file:line> | <description> | HIGH/MEDIUM/LOW | <fix> |

## Constitution Violations

| # | Rule | Violation | Justified? | Fix |
|---|------|-----------|------------|-----|
| 1 | <rule> | <description> | Yes/No | <fix> |

## Summary

- CRITICAL gaps: N
- HIGH gaps: N
- MEDIUM gaps: N
- Stories passing: N/M
- Test coverage: N%

## Verdict

- **PASS**: All stories implemented, tested, and quality acceptable → proceed to verify
- **CONDITIONAL**: High gaps found → back to build for fixes
- **FAIL**: Critical gaps found → back to build for fixes

## Handover (if FAIL or CONDITIONAL)

<list of specific CRs/bugs to create>

### CR/BUG-001: <title>
- Type: CR / Bug
- Story: US<N>
- Gap: <description>
- Files: <file paths>
- Fix: <what needs to change>
- Priority: P1/P2/P3
