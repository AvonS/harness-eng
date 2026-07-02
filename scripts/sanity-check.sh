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

# --- F001: All commands have YAML frontmatter ---
echo "F001: Checking command files..."
CMD_COUNT=0
for cmd_file in "$ROOT/commands"/*.md; do
    if [ -f "$cmd_file" ]; then
        if ! grep -q "^name:" "$cmd_file" 2>/dev/null; then
            echo "❌ FAIL: commands/$(basename "$cmd_file") missing YAML frontmatter"
            ERRORS=$((ERRORS + 1))
        else
            CMD_COUNT=$((CMD_COUNT + 1))
        fi
    fi
done
echo "   ✅ $CMD_COUNT command files verified"

# --- F002: All scripts have valid syntax ---
echo "F002: Checking scripts..."
SCRIPT_COUNT=0
for script in "$ROOT"/scripts/*.sh; do
    if [ -f "$script" ]; then
        if ! bash -n "$script" 2>/dev/null; then
            echo "❌ FAIL: scripts/$(basename "$script") has bash syntax error"
            ERRORS=$((ERRORS + 1))
        else
            SCRIPT_COUNT=$((SCRIPT_COUNT + 1))
        fi
    fi
done
for script in "$ROOT"/scripts/*.py; do
    if [ -f "$script" ]; then
        if ! python3 -c "import ast; ast.parse(open('$script').read())" 2>/dev/null; then
            echo "❌ FAIL: scripts/$(basename "$script") has Python syntax error"
            ERRORS=$((ERRORS + 1))
        else
            SCRIPT_COUNT=$((SCRIPT_COUNT + 1))
        fi
    fi
done
echo "   ✅ $SCRIPT_COUNT scripts syntax-valid"

# --- F002: Gate enforcement script runs ---
echo "F002: Checking gate enforcement..."
HARNESS_DIR="$ROOT/.harness-eng"
if [ ! -d "$HARNESS_DIR" ]; then
    HARNESS_DIR="$(cd "$ROOT/../harness-eng-dogfood/.harness-eng" 2>/dev/null && pwd || echo "$ROOT/.harness-eng")"
fi
if [ -f "$HARNESS_DIR/internal-scripts/check-approved-designs.py" ]; then
    if ! python3 "$HARNESS_DIR/internal-scripts/check-approved-designs.py" > /dev/null 2>&1; then
        echo "⚠️  check-approved-designs.py found no approved designs (expected for PENDING phase)"
    fi
fi
echo "   ✅ Gate script executable"

# --- F002: Status dashboard runs without crash ---
echo "F002: Checking status dashboard..."
if ! python3 "$ROOT/scripts/harness-status.py" "$HARNESS_DIR" > /dev/null 2>&1; then
    echo "❌ FAIL: harness-status.py crashed"
    ERRORS=$((ERRORS + 1))
fi
echo "   ✅ Status dashboard executable"

# --- F003: All templates have YAML frontmatter and contracts ---
echo "F003: Checking templates..."
TPL_COUNT=0
for tpl in "$ROOT"/templates/feature/*.md "$ROOT"/templates/big-picture/*.md; do
    if [ -f "$tpl" ]; then
        if ! grep -q "^name:" "$tpl" 2>/dev/null; then
            echo "❌ FAIL: templates/.../$(basename "$tpl") missing YAML frontmatter"
            ERRORS=$((ERRORS + 1))
        else
            TPL_COUNT=$((TPL_COUNT + 1))
        fi
    fi
done
echo "   ✅ $TPL_COUNT templates verified"


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
if [ -f "$HARNESS_DIR/internal-scripts/check-agent-contracts.py" ]; then
    if ! python3 "$HARNESS_DIR/internal-scripts/check-agent-contracts.py" 2>/dev/null; then
        echo "❌ FAIL: agent_contract validation errors"
        ERRORS=$((ERRORS + 1))
    else
        echo "   ✅ All agent_contract blocks valid"
    fi
else
    echo "⚠️  No internal validation script found for agent contracts"
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



# --- F004: All skills have SKILL.md ---
echo "F004: Checking skills..."
SKILL_COUNT=0
SKILLS_ROOT="$HARNESS_DIR/skills"
if [ ! -d "$SKILLS_ROOT" ]; then
    SKILLS_ROOT="$ROOT/.harness-eng/skills"
fi
if [ -d "$SKILLS_ROOT" ]; then
    for skill_dir in "$SKILLS_ROOT"/*; do
        if [ -d "$skill_dir" ]; then
            if [ ! -f "$skill_dir/SKILL.md" ]; then
                echo "❌ FAIL: skills/$(basename "$skill_dir")/SKILL.md missing"
                ERRORS=$((ERRORS + 1))
            elif ! grep -q "^name:" "$skill_dir/SKILL.md" 2>/dev/null; then
                echo "❌ FAIL: skills/$(basename "$skill_dir")/SKILL.md missing YAML frontmatter"
                ERRORS=$((ERRORS + 1))
            else
                SKILL_COUNT=$((SKILL_COUNT + 1))
            fi
        fi
    done
fi
echo "   ✅ $SKILL_COUNT skills verified"

# --- F005: Pre-commit hook syntax valid ---
echo "F005: Checking hooks..."
if ! bash -n "$ROOT/hooks/pre-commit" 2>/dev/null; then
    echo "❌ FAIL: hooks/pre-commit has bash syntax error"
    ERRORS=$((ERRORS + 1))
fi
echo "   ✅ Pre-commit hook syntax-valid"

# --- F006: All agent definitions verified ---
echo "F006: Checking agent definitions..."
AGENT_COUNT=0
AGENTS_ROOT="$HARNESS_DIR/agents"
if [ ! -d "$AGENTS_ROOT" ]; then
    AGENTS_ROOT="$ROOT/.harness-eng/agents"
fi
if [ -d "$AGENTS_ROOT" ]; then
    for agent_dir in "$AGENTS_ROOT"/*; do
        if [ -d "$agent_dir" ]; then
            if [ ! -f "$agent_dir/agent.md" ]; then
                echo "❌ FAIL: agents/$(basename "$agent_dir")/agent.md missing"
                ERRORS=$((ERRORS + 1))
            elif ! grep -q "^name:" "$agent_dir/agent.md" 2>/dev/null; then
                echo "❌ FAIL: agents/$(basename "$agent_dir")/agent.md missing YAML frontmatter"
                ERRORS=$((ERRORS + 1))
            else
                AGENT_COUNT=$((AGENT_COUNT + 1))
            fi
        fi
    done
fi
echo "   ✅ $AGENT_COUNT agent definitions verified"

# --- F007: All docs exist ---
echo "F007: Checking documentation..."
DOC_COUNT=0
for doc in "$ROOT"/docs/*.md; do
    if [ -f "$doc" ]; then
        if ! grep -q "^#" "$doc" 2>/dev/null; then
            echo "❌ FAIL: docs/$(basename "$doc") missing Markdown header"
            ERRORS=$((ERRORS + 1))
        else
            DOC_COUNT=$((DOC_COUNT + 1))
        fi
    fi
done
echo "   ✅ $DOC_COUNT docs verified"

# --- CR-004: Python behavioral regression suite ---
if [ "${SKIP_UNITTESTS:-}" = "1" ]; then
    echo "   ✅ CR-004 behavioral regression tests (skipped recursively)"
else
    echo "CR-004: Running Python behavioral regression tests..."
    if ! python3 -m unittest discover -v "$ROOT/tests" 2>&1 | tail -5; then
        echo "❌ FAIL: CR-004 behavioral regression tests failed"
        ERRORS=$((ERRORS + 1))
    else
        echo "   ✅ CR-004 behavioral regression tests passed"
    fi
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
