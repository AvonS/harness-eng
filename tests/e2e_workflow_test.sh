#!/usr/bin/env bash
# e2e_workflow_test.sh - Integration test for harness gates
set -euo pipefail

echo "Setting up E2E tests..."
mv .harness-eng/phase-0-foundation/features/active .harness-eng/phase-0-foundation/features/active_bak 2>/dev/null || true
rm -rf .harness-eng/phase-e2e-test
mkdir -p .harness-eng/phase-e2e-test/features/active/F999-test
touch .harness-eng/phase-e2e-test/features/active/F999-test/spec.md

echo "Test 1: Gate 1 (Design Approval)"
cat << 'EOF' > .harness-eng/phase-e2e-test/features/active/F999-test/design.md
# Design
**Ref**: PENDING
EOF
if python3 scripts/harness-check.py build 2>/dev/null; then
    echo "❌ FAIL: Allowed build with unapproved design"
    exit 1
fi
cat << 'EOF' > .harness-eng/phase-e2e-test/features/active/F999-test/design.md
# Design
**Ref**: APPROVED
EOF
touch .harness-eng/phase-e2e-test/features/active/F999-test/tasks.md
if ! python3 scripts/harness-check.py build >/dev/null; then
    echo "❌ FAIL: Blocked build with approved design"
    exit 1
fi
echo "✅ Gate 1 Passed"

echo "Test 2: Gate 2 (Sr Tech Lead Review)"
if python3 scripts/harness-check.py verify 2>/dev/null; then
    echo "❌ FAIL: Allowed verify without review-pre-verify.md"
    exit 1
fi
cat << 'EOF' > .harness-eng/phase-e2e-test/features/active/F999-test/review-pre-verify.md
# Review
**Ref**: APPROVED
EOF
if ! python3 scripts/harness-check.py verify >/dev/null; then
    echo "❌ FAIL: Blocked verify with approved review-pre-verify.md"
    exit 1
fi
echo "✅ Gate 2 Passed"

echo "Test 3: Gate 3 (Release Approval)"
cat << 'EOF' > .harness-eng/phase-e2e-test/features/active/F999-test/verification.md
# Verification
| Acceptance Criteria | Status |
|---------------------|--------|
| Everything works    | ✅ PASS |
EOF
if python3 scripts/harness-check.py release 2>/dev/null; then
    echo "❌ FAIL: Allowed release without Release Ref: PENDING"
    exit 1
fi
cat << 'EOF' > .harness-eng/phase-e2e-test/features/active/F999-test/verification.md
# Verification
All passing
**Release Ref: PENDING**
EOF
if ! python3 scripts/harness-check.py release >/dev/null; then
    echo "❌ FAIL: Blocked release with Release Ref: PENDING"
    exit 1
fi
echo "✅ Gate 3 Passed"

rm -rf .harness-eng/phase-e2e-test
mv .harness-eng/phase-0-foundation/features/active_bak .harness-eng/phase-0-foundation/features/active 2>/dev/null || true
echo "✅ All E2E Integration Tests Passed!"
