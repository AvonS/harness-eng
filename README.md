# harness-eng

**A self-verifying, full-lifecycle software engineering harness for AI coding assistants.**

One repo. Any agent. Any project. From big picture to shipped feature — with human gates, smart templates, and logical phases for large BRDs.

> **Read the full article:** [Harness Engineering in Practice](https://avons.github.io/notes/harness-eng/) — the rationale, design philosophy, worked examples, and limitations.

---

## Quickstart

Open your AI agent in your project directory and paste this:

```
read https://github.com/AvonS/harness-eng/blob/main/commands/init.md and follow the instructions to initialize harness-eng in this folder
```

| Folder state | What the agent does |
|--------------|---------------------|
| **Empty** | Asks questions, builds requirements from conversation |
| **Existing code** | Reverse-engineers BRD, constitution, architecture |
| **PRD + ADR ready** | Derives all documents from existing docs |
| **Has .harness-eng/** | Upgrades tooling, preserves customizations |

---

## Upgrade

```
read https://raw.githubusercontent.com/AvonS/harness-eng/main/commands/upgrade-harness.md
and follow the instructions to upgrade harness-eng in this folder
```

**Important:** The fetched upgrade command may differ from your local version. Always use the FETCHED command's instructions, not your local copy.

**Project-specific files are NEVER overwritten:** CONSTITUTION.md, BRD.md, ARCHITECTURE.md, technology.yaml, sanity-check.sh, SLICE_LOG.md.

### Migration & Recovery
Projects using this harness are tracked under the **`Foundry`** generation identity (stored in `.harness-eng/manifest.json`). When upgrading, a migration engine safely transitions older "legacy" state to the current schema. Backups are automatically created before any writes.
If an upgrade is interrupted, a migration lock protects your state. Run `/h:upgrade-harness` again or use the resume script to safely recover.
---

## The Workflow

The core philosophy of `harness-eng` is the **Autonomous Agent Loop** bounded by strict human gates. The system features a loop *before* design approval and a loop *after* design approval.

```text
{ Pre-Design Loop } → [Human Gate 1] → { Implementation Loop } → [Human Gate 2] → release
```

### 1. Planning & Design (Pre-Design Loop)
Before the first human gate, agents loop to ensure the architecture is sound. If `review-pre-build` detects gaps in the design or spec, it automatically routes back to `define` or `design` for the Analyst to fix them.

| Command | Logical Role | What happens | Gate |
|---------|--------------|-------------|------|
| `/h:init` | Manager | Derive constitution, BRD, architecture | — |
| `/h:define` | Analyst | Create a prioritized feature spec with testable acceptance criteria | — |
| `/h:design` | Analyst | Design architecture, interfaces, file layout | — |
| `/h:review-pre-build` | Sr Architect | Agent validates design against BRD and Constitution before human review | Agent Review 1 |
| `/h:approve` | Gatekeeper | **Human Gate 1:** Review design, approve or request changes | ✅ Human Gate 1 |

Initialization questions collect product context, testing level, and release policy only. They do not authorize implementation; `/h:init` reports the next permitted command and stops.

### 2. The Agent Loop (Autonomous)
Once the design is approved, the agent works through these commands iteratively. If `review-pre-verify` or `verify` catches a bug, the agent automatically loops back to `build` (or `design` for major gaps) to fix it.

| Command | Logical Role | What happens | Gate |
|---------|--------------|-------------|------|
| `/h:tasks` | Developer | Break design into granular tasks with dependencies | — |
| `/h:build` | Developer | Implement against the approved Evidence Contract — one commit per task | — |
| `/h:review-pre-verify`| Sr Tech Lead | Agent reviews code against design to catch gaps | Agent Review 2 |
| `/h:verify` | Gatekeeper | Run tests, check acceptance criteria, write verification.md | — |

### 3. Release
| Command | Logical Role | What happens | Gate |
|---------|--------------|-------------|------|
| `/h:release` | Gatekeeper | **Human Gate 2:** Approve release — PR, merge, update status | ✅ Human Gate 2 |

---

## Bugs and Change Requests

For bugs or CRs, use the shortened workflow:

```
read https://github.com/AvonS/harness-eng/blob/main/commands/bug.md and follow the instructions
```

| Type | Branch | Workflow |
|------|--------|----------|
| **Bug** | `bugfix/BUG-NNN-<slug>` | Skip design; require a regression test when the defect is reproducible through automation |
| **CR** | `cr/CR-NNN-<slug>` | Skip full design, simplified spec + approval |

---

## What Gets Created

```
your-project/
├── AGENTS.md                    ← harness workflow rules
│
└── .harness-eng/
    ├── CONSTITUTION.md          ← principles and rules (never overwritten)
    ├── BRD.md                   ← business requirements (never overwritten)
    ├── ARCHITECTURE.md          ← system design (never overwritten)
    ├── technology.yaml          ← toolchain + tech decisions (never overwritten)
    ├── sanity-check.sh          ← integration tests (project-specific)
    ├── SLICE_LOG.md             ← build narrative
    │
    ├── commands/                ← workflow commands
    ├── scripts/                 ← status, check scripts
    ├── templates/               ← feature templates
    ├── hooks/                   ← pre-commit hook
    ├── skills/                  ← selected project-owned copies from harness-eng-skills
    │
    └── specs/ or phases/        ← feature specs and designs
```

---

## Human Gates

**Gate 1: Design Approval** — Human reviews design before implementation begins.

**Gate 2: Release Approval** — Human approves `Release Ref: APPROVED` in verification.md before creating PR.

Quality comes from:
- **Templates** — constrain LLM output with structure
- **Constitution** — principles the agent must follow
- **Sanity-check** — integration tests that must pass before verification

---

## Commands

Read command files from `.harness-eng/commands/` and follow them.

| Command | What happens |
|---------|-------------|
| `/h:init` | Scan docs, derive constitution/BRD/architecture, generate Phase 0 |
| `/h:define` | Create feature spec from BRD. Large BRDs auto-organize into phases |
| `/h:design` | Design architecture, interfaces, file layout |
| `/h:approve` | **Human gate** — review design, approve or request changes |
| `/h:tasks` | Break design into granular tasks with dependencies |
| `/h:build` | Implement against the approved Evidence Contract — one commit per task |
| `/h:verify` | Run tests, check acceptance criteria, fill verification report |
| `/h:release` | Create PR, merge, archive, update status |
| `/h:upgrade-harness` | Fetch latest instructions from `https://raw.githubusercontent.com/AvonS/harness-eng/main/commands/upgrade-harness.md` |
| `/h:status` | Print project status |
| `/h:health` | Check agent compliance with harness rules |
| `/h:bug` | Process bug fixes with shortened workflow |

---

## Git Branching

```
main                               ← protected
  ├── feature/<FID>-<slug>        ← /h:define
  ├── bugfix/BUG-NNN-<slug>       ← /h:bug (bugs)
  └── cr/CR-NNN-<slug>            ← /h:bug (CRs)
```

Commit convention: `type(ID): description`

---

## Configuration

### technology.yaml

```yaml
project:
  name: "my-project"
stack:
  language: "Go"
  language_rationale: "Performance, deployment model"
  database: "PostgreSQL"
  database_rationale: "ACID transactions"
```

### Secrets

Secrets live in `~/.config/<app>/`, never in the project directory.

---

## Skills

| Skill | Key rules |
|-------|-----------|
| Go | Makefile, go vet, race detection, std-lib-first, graceful shutdown |
| Python | uv, ruff, pytest, std-lib-first, config in ~/.config |
| Node/TS | Strict TypeScript, pnpm, vitest, ESM, Node built-ins |
| SQL | DuckDB dialect, migration testing, idempotent migrations |
| Git | Branch model, commit conventions, pre-commit secret scan |

---

## Status Dashboard

```bash
python scripts/harness-status-server.py [project_dir] [--port PORT]
```

Open http://localhost:8080 — view status, approve designs, auto-refreshes.

---

## Design Philosophy

> *The harness is a protocol, not a plugin.*

Like HTTP works whether you use Chrome or curl — harness-eng works whether you use
Claude, Copilot, or Cursor. It is a **file-based convention**, not a tool dependency.

The workflow is the tool. The folder structure is the state machine.

---

## Why This Exists

The [AI Manifesto](https://krishavanoor.github.io/) names the core problem: *"The greatest risk of AI is not that it will think for us. It is that it will agree with us — and we will not notice."* The harness builds external accountability into every workflow.

---

## Inspired By

- **spec-kit** — Constitution/spec/plan/tasks separation
- **OpenSpec** — Iterative flow, archive pattern
- **modular/skills** — Agent Skills Standard
- **BMAD** — Structured agentic development
- **AI Manifesto** — Six principles for thinking clearly with AI

---

## License

Copyright (c) 2026 [Avon Software Labs](https://avons.github.io).

Licensed under the GNU Affero General Public License v3.0 only (`AGPL-3.0-only`). See [LICENSE](LICENSE).

## Harness Migrations
This version of `harness-eng` uses the `Foundry` lineage.
If you are upgrading from a legacy installation (v1 or unversioned), the `/h:upgrade-harness` command will automatically apply one-time migrations and preserve your state.

### Recovery
In the rare event a migration fails, inspect `.harness-eng/backups/` and `.harness-eng/migrations/reports/` for state details and recovery instructions.
