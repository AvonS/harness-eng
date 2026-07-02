---
name: migrate-harness
description: Run the migration engine to update project state to a new release
agent_contract:
  prerequisites:
    - id: PRE-001
      action: "Check .harness-eng/manifest.json and .harness-eng/migrations/"
      on_failure: "FAIL: Migration structures missing"
  actions:
    - id: ACT-001
      action: "Run python3 scripts/migrate-harness.py plan"
    - id: ACT-002
      action: "Run python3 scripts/migrate-harness.py apply"
  outputs:
    - id: OUT-001
      path: ".harness-eng/migrations/applied.jsonl"
---
# /h:migrate-harness
Execute the file-based migration engine.
