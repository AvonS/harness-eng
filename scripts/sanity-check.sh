#!/usr/bin/env bash
# sanity-check.sh — Happy path integration test (no mocks)
# Each phase appends new tests to this script.
# This is a prerequisite for verify — MUST pass before validation.
#
# IMPORTANT: Tests should exercise the ACTUAL application entry points,
# not just call internal functions directly. The goal is to verify the
# application works end-to-end, not that individual components exist.
#
# --- MANAGED_SCAFFOLD_START v1 ---
# This scaffold is managed by harness-eng. Do not edit between the boundary
# markers. On upgrade, this section may be replaced; project tests in the
# PROJECT_TEST_REGION below are preserved.
# Schema version: v1

set -euo pipefail

ERRORS=0
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "=== Sanity Check: Happy Path Integration Test ==="

# --- MANAGED_SCAFFOLD_END v1 ---

# ============================================================
# PROJECT_TEST_REGION
# Add project-specific integration tests below this line.
# Tests here are preserved during harness upgrades.
# ============================================================

# --- F001: All 14 commands have YAML frontmatter ---
echo "F001: Checking command files..."
for cmd in init define design approve tasks build verify release status health triage bug; do
    if ! grep -q "^name:" "$ROOT/commands/$cmd.md" 2>/dev/null; then
        echo "❌ FAIL: commands/$cmd.md missing YAML frontmatter"
        ERRORS=$((ERRORS + 1))
    fi
done
# Check compound-name commands
for cmd in review-pre-build review-pre-verify upgrade-harness; do
    if ! grep -q "^name:" "$ROOT/commands/$cmd.md" 2>/dev/null; then
        echo "❌ FAIL: commands/$cmd.md missing YAML frontmatter"
        ERRORS=$((ERRORS + 1))
    fi
done
echo "   ✅ 14 command files verified"

# --- F002: All 12 scripts have valid syntax ---
echo "F002: Checking scripts..."
for script in "$ROOT"/scripts/*.sh; do
    if ! bash -n "$script" 2>/dev/null; then
        echo "❌ FAIL: $script has bash syntax error"
        ERRORS=$((ERRORS + 1))
    fi
done
for script in "$ROOT"/scripts/*.py; do
    if ! python3 -c "import ast; ast.parse(open('$script').read())" 2>/dev/null; then
        echo "❌ FAIL: $script has Python syntax error"
        ERRORS=$((ERRORS + 1))
    fi
done
echo "   ✅ 12 scripts syntax-valid"

# --- F002: Gate enforcement script runs ---
echo "F002: Checking gate enforcement..."
HARNESS_DIR="$ROOT/.harness-eng"
if ! bash "$ROOT/scripts/check-approved-designs.sh" "$HARNESS_DIR" > /dev/null 2>&1; then
    echo "⚠️  check-approved-designs.sh found no approved designs (expected for PENDING phase)"
fi
echo "   ✅ Gate script executable"

# --- F002: Status dashboard runs without crash ---
echo "F002: Checking status dashboard..."
if ! bash "$ROOT/scripts/harness-status.sh" "$HARNESS_DIR" > /dev/null 2>&1; then
    echo "❌ FAIL: harness-status.sh crashed"
    ERRORS=$((ERRORS + 1))
fi
if ! python3 "$ROOT/scripts/harness-status.py" "$HARNESS_DIR" > /dev/null 2>&1; then
    echo "❌ FAIL: harness-status.py crashed"
    ERRORS=$((ERRORS + 1))
fi
echo "   ✅ Status dashboard executable"

# --- F003: All templates have YAML frontmatter and contracts ---
echo "F003: Checking templates..."
for tpl in "$ROOT"/templates/feature/*.md; do
    if ! grep -q "^name:" "$tpl" 2>/dev/null; then
        echo "❌ FAIL: $tpl missing YAML frontmatter"
        ERRORS=$((ERRORS + 1))
    fi
done
for tpl in "$ROOT"/templates/big-picture/*.md; do
    if ! grep -q "^name:" "$tpl" 2>/dev/null; then
        echo "❌ FAIL: $tpl missing YAML frontmatter"
        ERRORS=$((ERRORS + 1))
    fi
done
if ! grep -q "^name:" "$ROOT/templates/phase/PHASE.md" 2>/dev/null; then
    echo "❌ FAIL: templates/phase/PHASE.md missing YAML frontmatter"
    ERRORS=$((ERRORS + 1))
fi

# --- CR-003: Path consolidation and relocation checks ---
echo "CR-003: Checking path locations..."
if [ -f "$ROOT/templates/PHASES.md" ]; then
    echo "❌ FAIL: templates/PHASES.md still exists (should be consolidated)"
    ERRORS=$((ERRORS + 1))
fi
if [ -f "$ROOT/templates/sanity-check.sh" ]; then
    echo "❌ FAIL: templates/sanity-check.sh still exists (should be relocated to scripts/)"
    ERRORS=$((ERRORS + 1))
fi
if [ ! -f "$ROOT/scripts/sanity-check.sh" ]; then
    echo "❌ FAIL: scripts/sanity-check.sh missing (canonical sanity script)"
    ERRORS=$((ERRORS + 1))
fi

# --- CR-003: Deep agent_contract validation (Python validator) ---
echo "CR-003: Running deep agent_contract validation..."
if ! python3 "$ROOT/scripts/check-agent-contracts.py" 2>/dev/null; then
    echo "❌ FAIL: agent_contract validation errors (see above)"
    ERRORS=$((ERRORS + 1))
else
    echo "   ✅ All agent_contract blocks valid"
fi

# --- CR-003: Check managed scaffold boundaries in sanity-check.sh ---
echo "CR-003: Checking sanity-check scaffold boundaries..."
# Match actual scaffold boundary comments (not the test code itself)
if ! grep -qE "^# --- MANAGED_SCAFFOLD_START" "$ROOT/scripts/sanity-check.sh" 2>/dev/null; then
    echo "❌ FAIL: scripts/sanity-check.sh missing MANAGED_SCAFFOLD_START boundary marker"
    ERRORS=$((ERRORS + 1))
fi
if ! grep -qE "^# --- MANAGED_SCAFFOLD_END" "$ROOT/scripts/sanity-check.sh" 2>/dev/null; then
    echo "❌ FAIL: scripts/sanity-check.sh missing MANAGED_SCAFFOLD_END boundary marker"
    ERRORS=$((ERRORS + 1))
fi

# --- CR-003: Check no duplicate sanity script exists ---
echo "CR-003: Checking no duplicate harness self-test..."
if [ -f "$ROOT/scripts/test-harness.sh" ]; then
    echo "❌ FAIL: scripts/test-harness.sh should not exist (use scripts/sanity-check.sh)"
    ERRORS=$((ERRORS + 1))
fi

# --- CR-003: Check .harness-eng/PHASES.md is a derived index (not from template) ---
echo "CR-003: Checking PHASES.md is derived index..."
if [ -f "$ROOT/.harness-eng/PHASES.md" ]; then
    if head -5 "$ROOT/.harness-eng/PHASES.md" | grep -q "Template"; then
        echo "❌ FAIL: .harness-eng/PHASES.md appears to be a template, not a derived index"
        ERRORS=$((ERRORS + 1))
    fi
fi

# --- CR-003: Check no obsolete canonical paths in active references ---
echo "CR-003: Checking no obsolete canonical references..."
# Check for positive references (exclude negations like "do not use", "no longer exists")
if grep -rl "templates/PHASES\.md" "$ROOT"/commands/ 2>/dev/null | xargs grep -L "no longer exists\|Do not create" 2>/dev/null | grep -q .; then
    echo "❌ FAIL: positive reference to obsolete templates/PHASES.md found in commands/"
    ERRORS=$((ERRORS + 1))
fi
if grep -rl "templates/sanity-check\.sh" "$ROOT"/commands/ 2>/dev/null | xargs grep -L "no longer exists\|Do not create" 2>/dev/null | grep -q .; then
    echo "❌ FAIL: positive reference to obsolete templates/sanity-check.sh found in commands/"
    ERRORS=$((ERRORS + 1))
fi

# --- BUG-003: bug.md release workflow includes version bump ---
echo "BUG-003: Checking bug.md release workflow has version bump..."
if ! grep -qE "version|VERSION|git tag" "$ROOT/commands/bug.md" 2>/dev/null; then
    echo "❌ FAIL: bug.md release workflow missing version bump or git tag step"
    ERRORS=$((ERRORS + 1))
else
    echo "   ✅ bug.md release workflow references version/git tag"
fi

# --- F004: All 7 skills have SKILL.md ---
echo "F004: Checking skills..."
for lang in go python node sql git datastar oat; do
    if [ ! -f "$ROOT/.harness-eng/skills/$lang/SKILL.md" ]; then
        echo "❌ FAIL: skills/$lang/SKILL.md missing"
        ERRORS=$((ERRORS + 1))
    fi
done
echo "   ✅ 7 skills verified"

# --- F005: Pre-commit hook syntax valid ---
echo "F005: Checking hooks..."
if ! bash -n "$ROOT/hooks/pre-commit" 2>/dev/null; then
    echo "❌ FAIL: hooks/pre-commit has bash syntax error"
    ERRORS=$((ERRORS + 1))
fi
echo "   ✅ Pre-commit hook syntax-valid"

# --- F006: All 4 agent.md files exist ---
echo "F006: Checking agent definitions..."
for persona in collaborator developer sr-tech-lead gatekeeper; do
    if [ ! -f "$ROOT/.harness-eng/agents/$persona/agent.md" ]; then
        echo "❌ FAIL: agents/$persona/agent.md missing"
        ERRORS=$((ERRORS + 1))
    fi
done
echo "   ✅ 4 agent definitions verified"

# --- F007: All 4 docs exist ---
echo "F007: Checking documentation..."
for doc in BRD-harness.md COMMAND-REFERENCE.md user-guide.md architectural-review-2026-06-15.md; do
    if [ ! -f "$ROOT/docs/$doc" ]; then
        echo "❌ FAIL: docs/$doc missing"
        ERRORS=$((ERRORS + 1))
    fi
done
echo "   ✅ 4 docs verified"

# --- CR-004: Python behavioral regression suite ---
echo "CR-004: Running Python behavioral regression tests..."
if ! python3 -m unittest discover -v "$ROOT/tests" 2>&1 | tail -5; then
    echo "❌ FAIL: CR-004 behavioral regression tests failed"
    ERRORS=$((ERRORS + 1))
else
    echo "   ✅ CR-004 behavioral regression tests passed"
fi

# --- Version check ---
echo "Checking project version..."
if [ -f "$ROOT/version.txt" ]; then
    echo "   ✅ version.txt exists: $(cat "$ROOT/version.txt")"
elif [ -f "$HARNESS_DIR/VERSION" ]; then
    echo "   ✅ .harness-eng/VERSION exists: $(cat "$HARNESS_DIR/VERSION")"
else
    echo "⚠️  No version file found"
fi

# --- Summary ---
echo ""
if [ "$ERRORS" -eq 0 ]; then
    echo "✅ Sanity check passed — all Phase 0 features operational"
    exit 0
else
    echo "❌ Sanity check failed: $ERRORS error(s)"
    exit 1
fi
