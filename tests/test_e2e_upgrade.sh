#!/usr/bin/env bash
set -e
echo "Running E2E upgrade workflow..."

TEST_DIR=$(mktemp -d)
echo "Setting up in $TEST_DIR"
cd "$TEST_DIR"

# 1. Setup a legacy environment
mkdir -p .harness-eng/commands
mkdir -p migrations
cp -r "$OLDPWD/migrations/"* migrations/
echo "Legacy state" > .harness-eng/legacy_file.txt

# 2. Run version check
python3 "$OLDPWD/scripts/version-check.py" . .harness-eng || true

# 3. Plan migration
python3 "$OLDPWD/scripts/migrate-harness.py" plan --target staged --harness-dir .harness-eng

# 4. Apply migration
python3 "$OLDPWD/scripts/migrate-harness.py" apply --target staged --harness-dir .harness-eng

# 5. Assert manifest exists
if [ ! -f .harness-eng/manifest.json ]; then
    echo "FAILED: manifest.json not created"
    exit 1
fi

if ! grep -q "Foundry" .harness-eng/manifest.json; then
    echo "FAILED: manifest.json does not contain Foundry lineage"
    exit 1
fi

echo "E2E upgrade simulation pass."
rm -rf "$TEST_DIR"
