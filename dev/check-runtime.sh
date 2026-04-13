#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

uv run ruff format --check src tests
uv run ruff check src tests
uv run pytest

if [ -n "${OPENCOACH_SMOKE_IMAGE:-}" ]; then
  uv run python -m opencoach smoke-rfdetr --image "$OPENCOACH_SMOKE_IMAGE"
fi
