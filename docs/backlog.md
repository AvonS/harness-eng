# Harness-Eng Gap-Closure Handover

**Document type:** Agent handover and backlog authority
**Target:** File-based `harness-eng`
**Target phase:** Phase 1
**Target release:** `0.1.0` after the phase release gate
**Prepared:** 2026-07-02
**Status:** Implemented as a Phase 1 release candidate; awaiting `/h:release`

---

## 1. Mission

Close the gaps between the current file-based harness, its completed Phase 0 record, and the capabilities presented as available in `harness-eng-deck.html`.

The result must remain a portable, file-based protocol. Do not introduce a resident service, database-backed workflow state, agent runtime, scheduler, or multi-user layer.

This handover is input to the normal harness lifecycle. It does not authorize direct edits outside that lifecycle.

```yaml
handover:
  next_command: "/h:release"
  implementation_authorized: true
  required_human_gates:
    - "/h:approve"
    - "/h:release"
  required_independent_reviews:
    - "/h:review-pre-build"
    - "/h:review-pre-verify"
```

---

## 2. Why This Work Exists

The core file workflow is operational, but its records and presentation have drifted:

1. Phase 0 describes an older repository inventory and persona model.
2. Progressive skill fetching is declared by `/h:init` but lacks a deterministic mechanism and tests.
3. Retry and escalation behavior is stated in the constitution but is not consistently implemented by command contracts.
4. BDD discovery produces scenarios, but scenario-to-test-to-verification traceability is not enforced.
5. Existing scripts validate harness structure and workflow prerequisites, but no canonical contract exists for invoking project-defined deterministic quality checks.
6. Some future runtime ideas were mixed into the file-harness backlog and deck.
7. The dogfood sanity check still references old canonical paths for checks intentionally moved to `.harness-eng/internal-scripts/`.

The deck has been corrected to identify CodeGraph, Context Hub, mutation testing, and `SOUL.md` as optional `pi-harness` capabilities. This backlog must preserve that boundary.

---

## 3. Current-State Reconciliation

The first Phase 1 feature must establish an accurate baseline before adding capability.

### Observed repository state

| Area | Phase 0 record | Current repository | Required action |
|---|---:|---:|---|
| Commands | 14 | 15 | Derive inventory mechanically and update phase evidence |
| Canonical product scripts | 12 combined/historical | 7 | Record the smaller distributable surface accurately |
| Dogfood internal scripts | Not distinguished | 5 | Keep under `.harness-eng/internal-scripts/`; exclude from product distribution |
| Skills | 7 | 8 | Include Ponytail or classify it separately from language skills |
| Agent directories | 4 | 5 | Reconcile with the logical Manager and Analyst roles |
| Phase directories | 1 | 1 | Add Phase 1 only through the phase workflow |

Counts above are observations from 2026-07-02. Do not turn them into new hard-coded assertions where discovery is possible.

The current `.harness-eng` path is the dogfood project state. Its `internal-scripts/` directory contains project-specific conformance checks. These scripts are not missing canonical product files and must not be moved back into `scripts/` merely to satisfy historical assertions.

### Required canonical terminology

Define one authoritative role model and use it consistently across `AGENTS.md`, the constitution, commands, agent definitions, templates, tests, phase records, and user documentation.

```yaml
logical_roles:
  - Manager
  - Analyst
  - Sr Architect
  - Developer
  - Sr Tech Lead
  - Gatekeeper

authority_classes:
  - orchestration
  - discovery_and_design
  - independent_pre_build_review
  - implementation
  - independent_pre_verify_review
  - human_decision_carrier
```

The implementation may map more than one logical role to a shared file-based agent definition, but that mapping must be explicit. Do not use `Collaborator`, `Analyst`, and `Manager` interchangeably without defining the relationship.

### Required gate terminology

Use these terms consistently:

- **Human Gate 1:** Design approval through `/h:approve`.
- **Agent Review 1:** Sr Architect pre-build review.
- **Agent Review 2:** Sr Tech Lead pre-verify review.
- **Human Gate 2:** Release approval through `/h:release`.

Do not describe all reviews as human gates. Do not reduce independent reviews to ordinary workflow steps.

---

## 4. Phase 1 Scope

Phase 1 should contain the following five features. `/h:define` may adjust identifiers, but it must preserve the boundaries and acceptance intent.

### F101 — Canonical Inventory and Role Reconciliation

**Outcome:** Project records describe the repository that actually exists.

```yaml
must_do:
  - Reconcile Phase 0 feature evidence with the current repository.
  - Define the mapping between logical roles and agent definition files.
  - Normalize human-gate and independent-review terminology.
  - Replace obsolete fixed-count tests with discovered inventory where practical.
  - Make dogfood checks call `.harness-eng/internal-scripts/` explicitly.
  - Keep canonical product scripts separate from dogfood-only conformance scripts.
  - Update README, command reference, architecture, phase index, and release notes.

must_not_do:
  - Rewrite historical evidence without recording the correction.
  - Copy dogfood-only internal scripts into the distributed canonical script set.
  - Claim runtime persona isolation in the file edition.
  - Add new personas for methods such as BDD, TDD, accessibility, or design research.
```

**Acceptance evidence:**

- One canonical role table is referenced by all public documentation.
- No conflicting `4-persona`, `5-agent`, or `6-role` claim remains unexplained.
- Repository inventory tests pass without obsolete file references.
- Phase 0 remains historically identifiable; corrections are recorded rather than silently erased.

### F102 — Deterministic Progressive Skill Selection

**Outcome:** `/h:init` installs only skills required by the derived technology stack using a reproducible, reviewable process.

```yaml
must_do:
  - Define the canonical skill source and source revision.
  - Resolve technology identifiers to skill directories deterministically.
  - Preview selected skills before installation.
  - Preserve project-owned skill modifications during upgrade.
  - Record installed skill name, source, revision, and installation time.
  - Support an explicit offline failure with actionable recovery instructions.
  - Add an idempotent test using a local fixture source.

must_not_do:
  - Require Context Hub.
  - Fetch arbitrary URLs selected by an LLM.
  - Silently replace project-modified skills.
  - Copy all skills when the stack is known.
  - Make network access mandatory for harness operation.
```

**Build-time behavior:**

If `/h:build` identifies a missing convention, it must stop and report the missing skill or knowledge requirement. It must not autonomously download content during implementation. Skill installation remains an explicit, reviewable operation.

**Review behavior:**

`/h:review-pre-build` and `/h:review-pre-verify` must report whether a finding may result from a missing, incompatible, or stale project skill. The reviewer recommends an action; it does not modify skills.

### F103 — Bounded Failure and `BLOCKED.md` Contract

**Outcome:** Repeated failure produces one durable, actionable escalation artifact instead of an ambiguous loop.

```yaml
attempt_policy:
  maximum_fix_attempts: 3
  counter_scope: "work item plus failing check"
  reset_condition: "the failing check passes or a human authorizes a revised approach"
  terminal_action: "write BLOCKED.md and stop"

must_record:
  - work item identifier
  - failing command or check
  - first observed failure
  - attempts and material changes made
  - latest evidence
  - likely ownership of the gap
  - bounded question or decision required from the human
  - safe resume command
```

`BLOCKED.md` is a file-based escalation record, not an asynchronous process. No background worker or chat loop is required.

**Acceptance evidence:**

- First and second failures permit a bounded corrective attempt.
- Third failure creates or updates exactly one scoped `BLOCKED.md` and stops.
- Re-running without human resolution does not create an infinite loop or duplicate escalation files.
- Successful recovery closes or archives the blocked state with provenance.

### F104 — BDD Scenario Traceability

**Outcome:** Behavior discovered during `/h:define` remains traceable through implementation and verification.

```yaml
scenario_contract:
  required_fields:
    - scenario_id
    - source_requirement
    - provenance
    - given
    - when
    - then
    - evidence_strategy
  provenance_values:
    - Confirmed
    - Observed
    - Inferred
    - Assumed
```

```yaml
must_do:
  - Assign stable IDs to material acceptance scenarios.
  - Trace each required scenario to a test or approved non-test evidence strategy.
  - Make tasks identify the scenarios they implement.
  - Make pre-verify review detect missing scenario evidence.
  - Make verification report scenario status and evidence location.
  - Escalate only load-bearing behavioral uncertainty to the human.

must_not_do:
  - Create a QA persona.
  - Require Event Storming for every feature.
  - Treat a plausible Given/When/Then statement as confirmed behavior.
  - Require human approval for routine behavior grounded in existing evidence.
```

### F105 — Project Sensor Contract

**Outcome:** The file harness can execute project-selected deterministic checks without bundling every quality tool.

The file edition should define a small sensor contract in `technology.yaml` or another approved canonical project file.

```yaml
sensors:
  - id: unit-tests
    command: "project-defined command"
    required_before: [review-pre-verify, verify]
    timeout: "project-defined"
    evidence: "exit status plus captured summary"
```

```yaml
must_do:
  - Use project-owned commands rather than hard-coded ecosystem tools.
  - Run required sensors at declared lifecycle points.
  - Record command, result, timestamp, and evidence location.
  - Fail closed when a required sensor cannot run.
  - Preserve the Ponytail rule by adding no dependency merely to satisfy the harness.

must_not_do:
  - Implement a scheduler or resident sensor service.
  - Bundle CodeGraph, mutation testing, SAST, or dependency-cruiser.
  - Assume every project uses Node, Python, Go, or a specific test framework.
  - Allow an LLM to reinterpret a failing required sensor as passing.
```

---

## 5. Already Implemented — Reconcile, Do Not Rebuild

### Behavior discovery foundation

`commands/define.md` already requires adaptive behavior discovery, behavior playback, provenance labels, and Given/When/Then scenarios. F104 extends traceability; it must not replace the working discovery contract.

### Design registry foundation

The canonical design registry already includes Oat, shadcn, Radix Themes, Carbon, and Fluent. `commands/design.md` already requires:

- starting from the existing application design system;
- using the registry before broad web search;
- climbing the Ponytail dependency ladder;
- extracting decisions rather than code or pixels;
- adapting references to current project constraints;
- recording adopted patterns and source URLs.

Treat this capability as implemented. Add tests or documentation corrections only when evidence shows a gap.

The earlier Obsidian, Notion, Basecamp, Fizzy, Dark Factory, and Augmented Coding references are Hasp/product-design research inputs. They are not replacements for the file harness's canonical implementation-oriented design registry.

### Human authority

The two human gates remain unchanged. Phase 1 must not introduce a new routine human gate.

---

## 6. Transferred to Optional Pi-Harness Scope

The following capabilities are explicitly outside the file-based Phase 1 scope:

| Capability | Destination | Reason |
|---|---|---|
| Local CodeGraph | Optional `pi-harness` | Runtime context service and indexed source navigation |
| Context Hub | Optional `pi-harness` | Networked current-document retrieval with provenance and policy |
| Mutation testing orchestration | Optional `pi-harness` sensor | Potentially expensive runtime scheduling and feedback loop |
| `SOUL.md` communication profiles | Optional `pi-harness` presentation layer | Runtime/user-specific response adaptation |

Additional transferred capabilities:

- SQLite workflow state;
- resident services;
- background schedules;
- automatic subagent retry workers;
- runtime tool denial and persona isolation;
- multi-user presentation and synchronization.

The file harness may define compatible artifact or sensor contracts. It must not implement these runtime services.

---

## 7. Explicitly Deferred or Rejected

### Git-hook lifecycle enforcement

Do not add a generic pre-commit rule that blocks every commit when design is unapproved. Specifications, designs, reviews, and corrective evidence also require commits before approval.

Retain Git hooks for repository invariants that can be evaluated without inferring human intent. Runtime-aware transition enforcement belongs to `pi-harness`.

### External database state

Do not add SQLite or another database as workflow truth for the file edition. Files and Git remain the state and audit mechanism.

### Natural-language proof systems

Do not attempt to prove semantic correctness with a heuristic English parser. Deterministic validation covers declared structural rules; independent review covers semantic equivalence.

---

## 8. Required Delivery Sequence

The implementing agent must follow the dogfood process.

```yaml
delivery_sequence:
  - step: "Create Phase 1 contract"
    command: "/h:define Phase 1 gap closure"
    output: "phase feature specifications with acceptance scenarios"

  - step: "Design the changes"
    command: "/h:design"
    output: "impact analysis, interfaces, file changes, migration behavior"

  - step: "Run independent architecture review"
    command: "/h:review-pre-build"
    output: "review-pre-build.md"

  - step: "Obtain Human Gate 1"
    command: "/h:approve"
    output: "approved design reference"

  - step: "Create executable tasks"
    command: "/h:tasks"
    output: "ordered tasks with scenario traceability"

  - step: "Implement through TDD"
    command: "/h:build"
    output: "one task-scoped commit per task"

  - step: "Run independent technical review"
    command: "/h:review-pre-verify"
    output: "review-pre-verify.md"

  - step: "Verify behavior and documentation"
    command: "/h:verify"
    output: "verification evidence and pending release reference"

  - step: "Obtain Human Gate 2"
    command: "/h:release"
    output: "0.1.0 release"
```

Do not combine all five features into one implementation task. Preserve feature-level evidence and permit independent rollback.

---

## 9. Verification Requirements

Before requesting release approval, reproduce and record:

```bash
bash scripts/sanity-check.sh
python3 .harness-eng/internal-scripts/check-agent-contracts.py
bash tests/e2e_workflow_test.sh
```

The internal validator command is dogfood evidence, not a command distributed to initialized user projects. If a command is not supported by the current project, correct the verification contract during design rather than silently skipping it.

The verification report must also demonstrate:

- A fresh greenfield fixture can initialize with only selected skills.
- An offline skill-selection failure is explicit and recoverable.
- A project-modified skill is not silently overwritten.
- Three repeated failures produce one valid `BLOCKED.md`.
- A scenario missing evidence blocks pre-verify review or verification.
- Project-defined sensors execute without ecosystem assumptions.
- Existing bug and CR workflows remain operational.
- Both human gates remain the only human gates.
- README, command reference, architecture, phase records, deck claims, and release notes agree.

---

## 10. Stop Conditions

Stop and request human input when:

- Phase 1 requires a third human gate.
- Progressive skill installation requires arbitrary network execution.
- Existing project-owned skills cannot be preserved safely.
- The role reconciliation would remove an independent review authority.
- A proposed sensor requires adding a project dependency solely for harness compliance.
- The implementation begins to reproduce optional `pi-harness` runtime behavior.
- Historical Phase 0 evidence cannot be corrected without losing provenance.

---

## 11. Completion Definition

This backlog is complete when:

1. F101–F105 are released through the dogfood workflow.
2. Phase and repository inventories agree.
3. Deck present-tense claims match demonstrated file-edition behavior.
4. Optional Pi capabilities remain explicitly outside the file edition.
5. A newly initialized project can follow the lifecycle without undocumented agent interpretation at the identified gaps.

Until then, this document remains the authoritative handover for file-harness gap closure.
