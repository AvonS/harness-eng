---
name: business-requirements-document
description: Big-picture template for the business requirements document.

gates:
  - check: project goals, stakeholders, and problem statement gathered
    on_fail: STOP, Cannot write BRD without project understanding

actions:
  - Fill all sections (problem, stakeholders, user journey, gates, success criteria)

outputs:
  - .harness-eng/BRD.md

must_do:
  - Every requirement must map to a measurable success criterion

must_not_do:
  - Finalize with unanswered stakeholder questions
---

# Business Requirements Document
# Project: <project-name>
# Date: <YYYY-MM-DD>
# Status: Draft | Approved

---

## Executive Summary
<2-3 sentences: what, for whom, why now>

---

## Stakeholders

| Role | Name/Team | Interest |
|------|-----------|---------|
| Product Owner | <name> | <what they care about> |
| End User | <persona> | <pain point solved> |
| Developer | <name/team> | <technical needs> |

---

## Problems Being Solved

1. <problem with today's situation>
2. <problem>
3. <problem>

---

## Success Metrics

| Metric | Current | Target | Measurement |
|--------|---------|--------|-------------|
| <metric> | <now> | <goal> | <how measured> |

---

## Constraints

- Timeline: <deadline or phases>
- Budget: <if relevant>
- Regulatory: <compliance requirements>
- Technical: <existing systems, dependencies>

---

## Out of Scope

- <what this project explicitly does NOT solve>
- <deferred capability — may become a future epic>

---

## References

| Document | What it provides |
|----------|-----------------|
| `CONSTITUTION.md` | Principles and rules that govern this project |
| `ARCHITECTURE.md` | System design and component boundaries |
| `domain-ctx.txt` | Domain vocabulary and business events |
| `technology.yaml` | Toolchain and build configuration |

---

## Validation Checklist

> *Run this checklist before finalizing the BRD.*

**Completeness:**
- [ ] Executive summary is 2-3 sentences (not a paragraph)
- [ ] All stakeholders identified with clear interests
- [ ] Problems are specific (not vague like "improve efficiency")
- [ ] Success metrics are measurable (numbers, not adjectives)
- [ ] Constraints are explicit (timeline, budget, regulatory)
- [ ] Out of scope is listed (prevents scope creep)

**Quality:**
- [ ] No implementation details (languages, frameworks, tools)
- [ ] Written for business stakeholders, not developers
- [ ] Every problem maps to at least one success metric
- [ ] Every constraint has a clear implication

**Traceability:**
- [ ] Problems trace to stakeholder needs
- [ ] Success metrics trace to problems
- [ ] Constraints trace to business reality
