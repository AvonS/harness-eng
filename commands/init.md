---
name: harness-init
description: >
  Initialize harness in project. Detect scenario, derive docs, create scaffold.

persona: Manager
subagent: false
reason: Bootstrap operation
goal: Produce rich, expressive, and highly readable foundational documents (BRD, Architecture) using the provided templates in .harness-eng/templates/.

gates:
  - check: "! .harness-eng/ exists"
    on_fail: STOP, .harness-eng already exists. Use /h:upgrade-harness instead.

actions:
  - scan: project for existing docs (README, PRD, ADR, code)
  - classify_scenario: [A: greenfield, B: brownfield, C: documented]
  - create: .harness-eng/ directory structure
  - stamp_manifest: write .harness-eng/manifest.json with product harness-eng, lineage Foundry, schema 2, release 0.2.0
  - if_brownfield: convert existing agents.md, claude.md, .cursorrules, or other agent files to .harness-eng/CONSTITUTION.md
  - fetch_and_replace_from_canonical:
    - commands/ -> .harness-eng/commands/
    - agents/ -> .harness-eng/agents/
    - scripts/ -> .harness-eng/scripts/
    - templates/ -> .harness-eng/templates/
    - AGENTS.md -> ./AGENTS.md
  - symlink_agent_configs: symlink claude.md, .cursorrules, .clinerules to ./AGENTS.md
  - derive_constitution: from project analysis + user input (default release_policy.strategy to local_merge, but allow user to opt into pull_request or direct)
  - derive_brd: from PRD/docs/conversation (Use templates/big-picture/BRD.md to ensure rich markdown structure)
  - derive_architecture: from code structure/docs/conversation (Use templates/big-picture/ARCHITECTURE.md and include mermaid diagrams)
  - derive_design_registry: copy templates/big-picture/design-registry.yaml to .harness-eng/design-registry.yaml
  - derive_technology: from detected stack
  - fetch_skill_source: clone or update https://github.com/AvonS/harness-eng-skills.git in the user cache
  - preview_skills: run scripts/skill-selection.py with the cached repository skills path
  - install_selected_skills: copy only skills required by the derived technology stack
  - present: all docs to human for review
  - wait: human approval
  - commit: initial harness setup

must_do:
  - Get human approval on all docs
  - Copy engine folders exactly as specified
  - Preserve all existing agent rules (claude.md, .cursorrules, etc.) into CONSTITUTION.md
  - Symlink all alternative agent config files to AGENTS.md
  - Explain what was derived and why
  - Record the harness-eng-skills source revision and installed skill digests

must_not_do:
  - Skip human review
  - Guess without asking
  - Overwrite existing files without asking
---
<!-- *** Maintained by AvonS/harness-eng, DON'T modify this, will be overwritten during next upgrade *** -->
