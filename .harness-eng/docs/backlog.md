# Product Backlog

## End-to-End (E2E) Integration Testing for Workflow Gates
Currently, `sanity-check.sh` only tests if files exist, and Python tests isolate function behavior, meaning the actual blocking capability of workflow gates isn't fully validated. 

We need to build an E2E Integration Test Script (e.g., `tests/e2e_workflow_test.sh`) to simulate moving through the lifecycle, intentionally trying to bypass gates to prove they block execution correctly.

### Testing Strategy

#### 1. Test Gate 1: Design Approval (Human Gate)
* **The Setup:** Scaffold a fake `.harness-eng/specs/active/F001/` folder with a `spec.md` and an unapproved `design.md` (`**Ref**: PENDING`).
* **The Test:** Try to execute the `build` prerequisite check (`scripts/harness-check.sh build`).
* **The Assertion:** The script must exit with a non-zero status, proving that an agent *cannot* start building an unapproved design.
* **The Passage:** Modify the file to `**Ref**: APPROVED`, re-run the check, and assert it exits `0`.

#### 2. Test Gate 2: Sr Tech Lead Review (Agent Gate)
* **The Setup:** Create a `tasks.md` with all boxes checked `[x]` (simulating a finished build). Do *not* create a `review-pre-verify.md` file.
* **The Test:** Try to execute the `verify` prerequisite check (`scripts/harness-check.sh verify`).
* **The Assertion:** The script must fail, proving the agent cannot verify code before the Sr Tech Lead persona has reviewed it.
* **The Passage:** Scaffold a passing `review-pre-verify.md` and assert the check now passes.

#### 3. Test Gate 3: Release Approval (Human Gate)
* **The Setup:** Create a `verification.md` file that has all passing tests, but the release marker is `**Release Ref**: PENDING`.
* **The Test:** Execute the `release` check.
* **The Assertion:** It must fail, proving the agent cannot merge or tag the release without human sign-off.

---

## Split up `upgrade-harness.md`
At 931 lines, `upgrade-harness.md` is a massive "token budget bomb" that will cause LLM context windows to struggle. It tries to fetch files, migrate templates, manage backups, and deploy hooks all in one file.
* **The Fix:** We will split it into three smaller files: `upgrade-fetch.md`, `upgrade-migrate.md`, and `upgrade-deploy.md`, which are orchestrated by a much smaller coordinator file.

---

## Fix General Documentation Drift
There are several places where the documentation has drifted from reality.
* **The Fixes:** Correcting the `technology.yaml` example in the README, updating the `ARCHITECTURE.md` status from "Draft" to "Complete", fixing duplicate step numbers in the command reference, and formally documenting how `RELEASE.md` works.

---

## Remove Duplicate Shell Scripts (Keep Only Python)
Currently, several scripts exist in both Bash and Python (`version-check`, `harness-check`, `harness-status`), doubling the maintenance burden. The shell scripts also suffer from cross-platform portability issues (macOS vs. Linux command differences).
* **The Fix:** Delete the `.sh` duplicates and standardize entirely on the `.py` equivalents. This instantly solves the maintenance duplication and entirely drops the need to rewrite shell scripts for portability.

---

## Enforce Persona Ownership in Command Validation
While commands are being updated to include `agent: <persona>` in their YAML frontmatter, there is currently no programmatic enforcement to prevent regressions. If a developer or agent creates a new command and forgets to assign an owner, it will silently lack guardrails.
* **The Fix:** Update `scripts/check-agent-contracts.py` to parse the YAML frontmatter of every command file, asserting that the `agent:` key exists and that its value exactly matches one of the four valid persona directories (`collaborator`, `developer`, `gatekeeper`, or `sr-tech-lead`).
