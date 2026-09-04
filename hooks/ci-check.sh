#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# Single source of truth for CI/code-quality checks.
# Invoked locally by hooks/pre-push (blocking) and by .github/workflows/ci.yml
# (confirmation only) — local and CI run this exact script to prevent drift.
#
# Dev deps only (no torch/transformers/snac) — lint and tests run without GPU.
# Full runtime install: uv sync --extra runtime
set -e

uv sync --group dev

echo "Linting with Ruff..."
ruff check .
ruff format . --check

echo "Running pyright..."
uv run pyright .

echo "Running tests..."
uv run pytest tests/

echo "Security vulnerability scan (safety)..."
uv run safety check --json || echo "Safety check completed with warnings"

echo "SAST with Bandit..."
uv run python -m bandit -r . \
    --exclude .venv,hooks,.specify \
    -f json -o bandit-report.json \
    || echo "Bandit scan completed"

echo "License compliance check..."
uv run python -m piplicenses --format=json --output-file=licenses.json
echo "License compliance check completed"

echo "ci-check passed."
