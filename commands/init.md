---
name: harness-init
description: >
  Initialize harness in project. Detect scenario, derive docs, create scaffold.

persona: Manager
subagent: false
reason: Bootstrap operation
goal: Produce rich, expressive, and highly readable foundational documents (BRD, Architecture) using the provided templates in .harness-eng/templates/.

preflight:
  - read_canonical_agents: Read canonical source AGENTS.md before scanning, clarifying, creating files, or running commands
  - capture_init_baseline: Run scripts/init-boundary.py snapshot --output .harness-eng-init-baseline.json

gates:
  - check: "! .harness-eng/ exists"
    on_fail: STOP, .harness-eng already exists. Use /h:upgrade-harness instead.

actions:
  - scan: project for existing docs (README, PRD, ADR, code)
  - classify_scenario: [A: greenfield, B: brownfield, C: documented]
  - bind_clarification_context: Treat every requested user answer as initialization input until this command stops
  - create_from_manifest: create every directory declared in templates/init-layout.json
  - stamp_manifest: write .harness-eng/manifest.json with product harness-eng, lineage Foundry, schema 3, current release
  - if_brownfield: convert existing agents.md, claude.md, .cursorrules, or other agent files to .harness-eng/CONSTITUTION.md
  - fetch_and_replace_from_canonical:
    - commands/ -> .harness-eng/commands/
    - agents/ -> .harness-eng/agents/
    - scripts/ -> .harness-eng/scripts/
    - templates/ -> .harness-eng/templates/
    - hooks/ -> .harness-eng/hooks/
    - VERSION -> .harness-eng/VERSION
    - AGENTS.md -> ./AGENTS.md
  - symlink_agent_configs: symlink claude.md, .cursorrules, .clinerules to ./AGENTS.md
  - derive_constitution: from project analysis + user input (default release_policy.strategy to local_merge, but allow user to opt into pull_request or direct)
  - prompt_testing_level: ask user for project-wide testing level (S, M, or L, default S) and persist in CONSTITUTION.md
  - derive_brd: from PRD/docs/conversation (Use templates/big-picture/BRD.md to ensure rich markdown structure)
  - derive_architecture: from code structure/docs/conversation (Use templates/big-picture/ARCHITECTURE.md and include mermaid diagrams)
  - derive_design_registry: create an empty .harness-eng/design-registry.yaml for project-specific additions
  - derive_technology: from detected stack
  - fetch_skill_source: clone or update https://github.com/AvonS/harness-eng-skills.git in the user cache
  - preview_skills: run scripts/skill-selection.py with the cached repository skills path
  - install_selected_skills: copy only skills required by the derived technology stack
  - initialize_phase_index: create derived .harness-eng/PHASES.md
  - initialize_slice_log: create .harness-eng/SLICE_LOG.md
  - initialize_skill_log: create .harness-eng/skill-install.json
  - derive_runtime_smoke: add the cheapest real-entry-point smoke check to the sanity project region for executable applications
  - validate_layout: run scripts/validate-layout.py against templates/init-layout.json
  - present: all docs to human for review
  - wait: human approval
  - validate_init_boundary: Run scripts/init-boundary.py check --baseline .harness-eng-init-baseline.json
  - commit: initial harness setup
  - remove_init_baseline: Delete .harness-eng-init-baseline.json
  - report_next_command: Derive the earliest permitted command from harness filesystem state
  - stop_after_init: Return control to the user without invoking another workflow command

must_do:
  - Get human approval on all docs
  - Copy engine folders exactly as specified
  - Preserve all existing agent rules (claude.md, .cursorrules, etc.) into CONSTITUTION.md
  - Symlink all alternative agent config files to AGENTS.md
  - Explain what was derived and why
  - Record the harness-eng-skills source revision and installed skill digests
  - Use clarification answers only for bootstrap artifacts and configuration
  - Stop after reporting the next permitted command

must_not_do:
  - Skip human review
  - Guess without asking
  - Overwrite existing files without asking
  - Create application implementation files
  - Interpret a requested clarification answer as authorization for another command
  - Invoke define, design, tasks, build, verify, or release automatically
---
<!-- *** Maintained by AvonS/harness-eng, DON'T modify this, will be overwritten during next upgrade *** -->
