---
name: harness-init
description: >
  Initialize harness in project. Detect scenario, derive docs, create scaffold.

persona: Manager
subagent: false
reason: Bootstrap operation

gates:
  - check: "! .harness-eng/ exists"
    on_fail: STOP, .harness-eng already exists. Use /h:upgrade-harness instead.

actions:
  - scan: project for existing docs (README, PRD, ADR, code)
  - classify_scenario: [A: greenfield, B: brownfield, C: documented]
  - create: .harness-eng/ directory structure
  - if_brownfield: convert existing agents.md or rules to .harness-eng/CONSTITUTION.md
  - fetch_and_replace_from_canonical:
    - commands/ -> .harness-eng/commands/
    - agents/ -> .harness-eng/agents/
    - scripts/ -> .harness-eng/scripts/
    - skills/ -> .harness-eng/skills/
    - templates/ -> .harness-eng/templates/
    - AGENTS.md -> ./AGENTS.md
  - derive_constitution: from project analysis + user input (if not converted)
  - derive_brd: from PRD/docs/conversation
  - derive_architecture: from code structure/docs/conversation
  - derive_technology: from detected stack
  - present: all docs to human for review
  - wait: human approval
  - commit: initial harness setup

must_do:
  - Get human approval on all docs
  - Copy engine folders exactly as specified
  - Preserve any existing agent rules in CONSTITUTION.md
  - Explain what was derived and why

must_not_do:
  - Skip human review
  - Guess without asking
  - Overwrite existing files without asking
---
