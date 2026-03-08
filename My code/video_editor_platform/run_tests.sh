#!/bin/bash
# Regression Test Runner for GenAI Video Editor

set +e  # Don't exit on error, we want to see all results

echo "=========================================="
echo "GenAI Video Editor - Regression Test Suite"
echo "=========================================="
echo ""
echo "Start Time: $(date)"
echo ""

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo "⚠️  pytest not found. Installing..."
    pip install pytest pytest-asyncio pytest-cov pytest-mock
fi

# Change to project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo "Project Directory: $PROJECT_DIR"
echo "Python Version: $(python --version)"
echo "pytest Version: $(pytest --version)"
echo ""

# Run different test suites
echo "=========================================="
echo "1. Unit Tests"
echo "=========================================="
pytest tests/unit/ -v --tb=short 2>&1 | head -100

echo ""
echo "=========================================="
echo "2. Integration Tests"
echo "=========================================="
pytest tests/integration/ -v --tb=short 2>&1 | head -100

echo ""
echo "=========================================="
echo "3. All Tests with Coverage"
echo "=========================================="
pytest tests/ -v --cov=src --cov-report=term-missing --tb=short 2>&1 | head -150

echo ""
echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo "✅ Regression tests completed!"
echo "End Time: $(date)"
echo "=========================================="
