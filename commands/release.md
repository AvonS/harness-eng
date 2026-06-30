---
name: harness-release
description: >
  Release approved feature. Create PR, wait for merge, archive, tag.

persona: Gatekeeper
subagent: false
reason: Human gate operation

gates:
  - check: verification.md exists
    on_fail: STOP, run /h:verify
  - check: "verification.md contains 'Release Ref: PENDING'"
    on_fail: STOP, verification not approved
  - check: on feature branch (not main)
    on_fail: STOP, switch to feature branch

actions:
  - run_gh_pr_create: 'base=main, title="feat: <feature> [VERIFIED]", labels="verified"'
  - output: PR URL
  - wait: human merges PR
  - run: git checkout main && git pull
  - run: git branch -d <feature-branch>
  - run: git push origin --delete <feature-branch>
  - move: .harness-eng/specs/active/<feature> → .harness-eng/specs/done/
  - run: python3 scripts/harness-status.py
  - update: version.txt (bump patch)
  - run: git tag v<version>
  - run: git push origin v<version>
  - update: .harness-eng/SLICE_LOG.md (add release entry)

must_do:
  - PR includes [VERIFIED] label
  - Wait for human merge (never self-merge)
  - Archive spec to done/
  - Tag with version
  - Update SLICE_LOG.md

must_not_do:
  - Merge PR without human approval
  - Skip archiving
  - Forget version bump
  - Skip SLICE_LOG update
---
<!-- *** Maintained by AvonS/harness-eng, DON'T modify this, will be overwritten during next upgrade *** -->

