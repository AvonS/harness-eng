---
name: harness-init
description: >
  Initialize harness in project. Detect scenario, derive docs, create scaffold.

persona: Manager
subagent: false
reason: Bootstrap operation

gates:
  - check: "! .harness-eng/ exists"
    on_fail: STOP, run /h:upgrade-harness

actions:
  - scan: project for existing docs (README, PRD, ADR, code)
  - classify_scenario: [A: greenfield, B: brownfield, C: documented]
  - derive_constitution: from project analysis + user input
  - derive_brd: from PRD/docs/conversation
  - derive_architecture: from code structure/docs/conversation
  - derive_technology: from detected stack
  - fetch: AGENTS.md from harness repo
  - create: .harness-eng/ symlink structure
  - present: all docs to human for review
  - wait: human approval
  - commit: initial harness setup

must_do:
  - Get human approval on all docs
  - Fetch AGENTS.md from canonical source
  - Create complete symlink structure
  - Explain what was derived and why

must_not_do:
  - Skip human review
  - Guess without asking
  - Leave docs unapproved
---
