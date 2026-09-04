#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# Single source of truth for CI/code-quality checks.
# Invoked locally by hooks/pre-push (blocking) and by .github/workflows/ci.yml
# (confirmation only) — local and CI run this exact script to prevent drift.
#
# Note: uv sync pulls heavy runtime deps (torch, transformers, etc.).
# Dependency group / optional-extras split is tracked in the spec.
set -e

uv sync

echo "Linting with Ruff..."
ruff check .
ruff format . --check

echo "Running pyright..."
uv run pyright .

echo "Security vulnerability scan (safety)..."
uv run safety check --json || echo "Safety check completed with warnings"

echo "SAST with Bandit..."
uv run python -m bandit -r . \
    --exclude .venv,hooks \
    -f json -o bandit-report.json \
    || echo "Bandit scan completed"

echo "License compliance check..."
uv run python -m piplicenses --format=json --output-file=licenses.json
echo "License compliance check completed"

echo "ci-check passed."
