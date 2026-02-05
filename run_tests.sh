#!/bin/bash
# Run integration tests for Talon Blender addon

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEST_SCRIPT="$SCRIPT_DIR/test_addon.py"

echo "Running Blender addon integration tests..."
echo "Test script: $TEST_SCRIPT"
echo ""

# Run Blender in background mode with the test script
blender --background --python "$TEST_SCRIPT" 2>&1 | grep -E '(===|✓|✗|PASS|FAIL|TEST SUMMARY|Passed:|All tests|failed)'

# Capture the exit code
exit_code=${PIPESTATUS[0]}

if [ $exit_code -eq 0 ]; then
    echo ""
    echo "✓ Tests passed"
else
    echo ""
    echo "✗ Tests failed (exit code: $exit_code)"
fi

exit $exit_code
