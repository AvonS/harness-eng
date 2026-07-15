---
name: harness-release
description: >
  Release approved work using the project constitution release policy.

persona: Gatekeeper
subagent: false
reason: Human gate operation

gates:
  - check: verification.md exists
    on_fail: STOP, run /h:verify
  - check: "verification.md contains 'Release Ref: PENDING'"
    on_fail: STOP, verification not approved
  - check: "on feature branch (unless strategy is direct)"
    on_fail: STOP, switch to feature branch
  - check: "on target branch (if strategy is direct)"
    on_fail: STOP, switch to target branch
  - check: constitution contains a valid release_policy strategy
    on_fail: STOP, ask human to choose local_merge, pull_request, or direct

actions:
  - read_deferred_ledger: if deferred.md exists in active feature, read it for disclosure
  - block_on_promoted_blockers: if any deferred item has status=promoted-to-blocker, STOP and route to the earliest affected command
  - read_release_policy: strategy, target_branch, require_human_approval, push_branch, push_tag
  - disclose_deferred_items: present open deferred items to human before the approval gate with IDs and destinations
  - wait_for_explicit_human_gate_2_approval
  - if strategy == local_merge:
    - checkout_target_branch
    - merge_feature_branch
    - push_target_branch_if_enabled
  - if strategy == pull_request:
    - create_verified_pull_request
    - output_pull_request_url
    - wait_for_human_merge
    - synchronize_target_branch
  - if strategy == direct:
    - push_target_branch_if_enabled
  - archive_deferred_ledger: move deferred.md with the feature archive (specs/done/ or phases/archive/)
  - if phase_release: move .harness-eng/phases/active/<phase> → .harness-eng/phases/archive/<phase>
  - if bug_or_cr_release: move .harness-eng/specs/active/<item> → .harness-eng/specs/done/<item>
  - run: python3 scripts/harness-status.py
  - update: VERSION according to phase, change, or bug version policy
  - create_release_tag
  - push_release_tag_if_enabled
  - delete_feature_branch_after_merge
  - update: .harness-eng/SLICE_LOG.md (add release entry)

must_do:
  - Read release_policy from the project constitution
  - Require explicit human approval before either merge strategy
  - Push the target branch when push_branch is true
  - Push the release tag when push_tag is true
  - Verify the published target branch and tag match the local release
  - Archive spec to done/
  - Archive deferred.md with the feature
  - Disclose unresolved deferred items before human gate
  - Update SLICE_LOG.md

must_not_do:
  - Assume pull_request when the project selects local_merge or direct
  - Merge or publish without human approval
  - Skip archiving
  - Forget version bump
  - Skip SLICE_LOG update
  - Block release for unresolved deferred items unless promoted to blocker
---
<!-- *** Maintained by AvonS/harness-eng, DON'T modify this, will be overwritten during next upgrade *** -->
