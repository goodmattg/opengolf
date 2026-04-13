#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

mkdir -p external models var

if [ ! -d external/sam-3d-body/.git ]; then
  git clone --depth 1 https://github.com/facebookresearch/sam-3d-body external/sam-3d-body
fi

uv sync --python 3.11 --group model-runtime

if [ -n "${OPENCOACH_INSTALL_PIPER:-}" ]; then
  uv sync --python 3.11 --group model-runtime --group tts-runtime
fi

if [ -n "${OPENCOACH_DOWNLOAD_GEMMA:-}" ]; then
  hf download google/gemma-4-E4B-it --local-dir models/gemma-4-E4B-it
fi

if [ -n "${OPENCOACH_DOWNLOAD_SAM3_BODY:-}" ]; then
  hf download facebook/sam-3d-body-dinov3 --local-dir models/sam-3d-body-dinov3
fi
