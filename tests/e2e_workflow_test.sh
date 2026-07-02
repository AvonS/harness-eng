#!/usr/bin/env bash
set -euo pipefail

SCRIPT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TMP_ROOT="$(mktemp -d)"

cleanup() {
    rm -rf "$TMP_ROOT"
}
trap cleanup EXIT

echo "Test 0: Dogfood Script Separation Verification"
for script in check-agent-contracts.py check-approved-designs.py check-approved-designs.sh check-containment.py check-slice-log-entry.py check-slice-log.py; do
    if [ -f "$SCRIPT_ROOT/scripts/$script" ]; then
        echo "FAIL: Dogfood script scripts/$script should not exist in distributed scripts directory"
        exit 1
    fi
done
echo "PASS: Dogfood script separation verified"

create_project() {
    local name="$1"
    local project="$TMP_ROOT/$name"
    mkdir -p "$project/scripts"
    mkdir -p "$project/.harness-eng/phases/phase-e2e/features/active/F999-test"
    cp "$SCRIPT_ROOT/scripts/harness-check.py" "$project/scripts/"
    cp "$SCRIPT_ROOT/scripts/blocked-state.py" "$project/scripts/"
    cp "$SCRIPT_ROOT/scripts/traceability.py" "$project/scripts/"
    cp "$SCRIPT_ROOT/scripts/sensor-runner.py" "$project/scripts/"
    printf 'sensors:\n  - id: unit-tests\n    command: python3 -c '\''print(1)'\''\n    required_before: verify\n    timeout: 5\n    evidence: logs\n  - id: review-check\n    command: python3 -c '\''print(1)'\''\n    required_before: review-pre-verify\n    timeout: 5\n    evidence: logs\n' > "$project/technology.yaml"
    printf '# Spec\n' > "$project/.harness-eng/phases/phase-e2e/features/active/F999-test/spec.md"
    printf '%s\n' "$project"
}

run_check() {
    local project="$1"
    local command="$2"
    (cd "$project" && python3 scripts/harness-check.py "$command")
}

echo "Test 1: Gate 1 (Design Approval)"
project="$(create_project gate-1)"
cat <<'EOF' > "$project/.harness-eng/phases/phase-e2e/features/active/F999-test/design.md"
# Design
**Ref**: PENDING
EOF
if run_check "$project" build >/dev/null 2>&1; then
    echo "FAIL: Allowed build with unapproved design"
    exit 1
fi
cat <<'EOF' > "$project/.harness-eng/phases/phase-e2e/features/active/F999-test/design.md"
# Design
**Ref**: APPROVED
EOF
touch "$project/.harness-eng/phases/phase-e2e/features/active/F999-test/tasks.md"
if ! run_check "$project" build >/dev/null 2>&1; then
    echo "FAIL: Blocked build with approved design"
    exit 1
fi
echo "PASS: Gate 1"

echo "Test 2: Gate 2 (Sr Tech Lead Review)"
project="$(create_project gate-2)"
cat <<'EOF' > "$project/.harness-eng/phases/phase-e2e/features/active/F999-test/design.md"
# Design
**Ref**: APPROVED
EOF
cat <<'EOF' > "$project/.harness-eng/phases/phase-e2e/features/active/F999-test/spec.md"
```yaml
scenario_id: SCN-200
source_requirement: docs/backlog.md#trace
provenance: Confirmed
given: g
when: w
then: t
evidence_strategy: verification.md
```
EOF
printf '%s\n' "- [x] SCN-200 task" > "$project/.harness-eng/phases/phase-e2e/features/active/F999-test/tasks.md"
if run_check "$project" verify >/dev/null 2>&1; then
    echo "FAIL: Allowed verify without review-pre-verify.md"
    exit 1
fi
cat <<'EOF' > "$project/.harness-eng/phases/phase-e2e/features/active/F999-test/review-pre-verify.md"
# Review
**Ref**: APPROVED
SCN-200
EOF
cat <<'EOF' > "$project/.harness-eng/phases/phase-e2e/features/active/F999-test/verification.md"
# Verification
SCN-200
EOF
if ! run_check "$project" verify >/dev/null 2>&1; then
    echo "FAIL: Blocked verify with approved review-pre-verify.md and traceability evidence"
    exit 1
fi
echo "PASS: Gate 2"

echo "Test 3: Gate 3 (Release Approval)"
project="$(create_project gate-3)"
cat <<'EOF' > "$project/.harness-eng/phases/phase-e2e/features/active/F999-test/verification.md"
# Verification
| Acceptance Criteria | Status |
|---------------------|--------|
| Everything works    | PASS |
EOF
if run_check "$project" release >/dev/null 2>&1; then
    echo "FAIL: Allowed release without Release Ref: PENDING"
    exit 1
fi
cat <<'EOF' > "$project/.harness-eng/phases/phase-e2e/features/active/F999-test/verification.md"
# Verification
All passing
**Release Ref: PENDING**
EOF
if ! run_check "$project" release >/dev/null 2>&1; then
    echo "FAIL: Blocked release with Release Ref: PENDING"
    exit 1
fi
echo "PASS: Gate 3"

echo "Test 4: Automatic Blocked Transition"
project="$(create_project blocked)"
printf '%s\n' "- [x] complete" > "$project/.harness-eng/phases/phase-e2e/features/active/F999-test/tasks.md"
for _ in 1 2 3; do
    if run_check "$project" verify >/dev/null 2>&1; then
        echo "FAIL: verify unexpectedly passed during blocked transition setup"
        exit 1
    fi
done
if [ ! -f "$project/.harness-eng/phases/phase-e2e/features/active/F999-test/BLOCKED.md" ]; then
    echo "FAIL: BLOCKED.md not created after three failures"
    exit 1
fi
echo "PASS: Automatic blocked transition"

echo "Test 5: Required Sensor and Traceability Enforcement"
project="$(create_project trace-and-sensor)"
cat <<'EOF' > "$project/.harness-eng/phases/phase-e2e/features/active/F999-test/spec.md"
```yaml
scenario_id: SCN-300
source_requirement: docs/backlog.md#trace
provenance: Confirmed
given: g
when: w
then: t
evidence_strategy: verification.md
```
EOF
cat <<'EOF' > "$project/.harness-eng/phases/phase-e2e/features/active/F999-test/review-pre-verify.md"
# Review
**Ref**: APPROVED
EOF
printf '%s\n' "- [x] unrelated task" > "$project/.harness-eng/phases/phase-e2e/features/active/F999-test/tasks.md"
if run_check "$project" verify >/dev/null 2>&1; then
    echo "FAIL: Allowed verify with missing traceability mapping"
    exit 1
fi
printf "sensors:\n  - id: release-only\n    command: python3 -c 'print(1)'\n    required_before: release\n    timeout: 5\n    evidence: logs\n" > "$project/technology.yaml"
if run_check "$project" verify >/dev/null 2>&1; then
    echo "FAIL: Allowed verify with no configured verify sensors"
    exit 1
fi
echo "PASS: Required sensor and traceability enforcement"

echo "PASS: All E2E integration tests"
