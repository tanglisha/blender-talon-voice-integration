#!/bin/bash
# Run integration tests for Talon Blender addon using pytest-blender

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Running Blender addon integration tests with pytest-blender..."
echo ""

# Check if pytest-blender is installed
if ! command -v pytest &> /dev/null; then
    echo "Installing pytest and pytest-blender..."
    pip install pytest pytest-blender
fi

# Run pytest with pytest-blender
# This will automatically run tests inside Blender
cd "$SCRIPT_DIR"
pytest test_addon.py -v

exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo ""
    echo "✓ All tests passed"
else
    echo ""
    echo "✗ Tests failed (exit code: $exit_code)"
fi

exit $exit_code
