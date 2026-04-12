# OpenCoach Docs

## Status

OpenCoach is currently in bootstrap and planning mode.

As of April 12, 2026, this repo has been partially reset away from an older Tauri/Vite app. The deleted frontend files in the worktree should stay deleted. V0 should proceed as a Python-only application.

## Product Summary

OpenCoach v0 is a single-screen Python app for one operator-visible workflow:

1. Configure one `V4L2` camera stream.
2. Start the stream.
3. Show the live camera feed.
4. Continuously describe, out loud, what the camera sees about the golfer.

The camera is aimed at a golfer standing on a hitting mat. The app is a live demo, not a training platform, analytics suite, or multi-user product.

## V0 Contract

V0 succeeds only if it runs end to end with real local models:

- `RF-DETR` running locally.
- `SAM 3D Body` fully supported and runnable locally.
- `Gemma 4` fully supported and runnable locally.
- Local text-to-speech output so the system can speak commentary aloud.

The app should stay narrow:

- one camera
- one screen
- one live preview
- one commentary pipeline
- no cloud inference
- no mobile app
- no multi-camera orchestration

## Recommended Technical Direction

- Runtime: Python `3.11`
- Package/tooling: `uv`, `ruff`, `pytest`
- Web app: `FastAPI` + `Jinja2`
- Schemas and config models: `pydantic`
- Camera backend: `cv2.VideoCapture(..., cv2.CAP_V4L2)` with a small adapter layer
- Preview transport: MJPEG stream served by FastAPI
- Inference orchestration: background workers with bounded queues and explicit cadences
- Reasoning: `Gemma 4` multimodal prompt using the current frame plus structured signals from detection / pose
- Speech: local TTS adapter with subprocess playback through `ffplay` or `aplay`

We should not add any Node, Tauri, Electron, or frontend build tooling back into this repo.

All structured schemas in OpenCoach should use `pydantic`. That includes request models, response models, app settings, camera config, runtime status, scene snapshots, model outputs, and TTS payloads.

## Machine Readiness Snapshot

These facts were verified on April 12, 2026:

- `uv 0.9.10` is installed.
- `ruff 0.15.2` is installed.
- Python `3.11` is available through `uv`.
- The machine has an `NVIDIA RTX PRO 6000 Blackwell` with about `96 GB` VRAM.
- `ffmpeg`, `ffplay`, `aplay`, `hf`, `cmake`, `ninja`, `gcc`, and `nvcc` are present.

Current blockers:

- No `/dev/video*` device is present right now, so real camera validation is blocked.
- `v4l2-ctl` is not installed, so camera capability inspection is blocked until `v4l-utils` is installed.
- Hugging Face CLI is authenticated, but `SAM 3D Body` checkpoint access is still gated. A dry run against `facebook/sam-3d-body-dinov3` returned `Access denied. This repository requires approval.` on April 12, 2026.
- `Gemma 4` access is available. Dry runs against `google/gemma-4-E4B-it` and `google/gemma-4-26B-A4B-it` succeeded on April 12, 2026.

## Core V0 Design Choices

- Treat the hitting mat as an operator-configured region of interest in v0. Do not depend on a generic detector to find it.
- Use `RF-DETR` to establish golfer visibility and a stable person crop.
- Use `SAM 3D Body` on sampled frames, not every frame, because it is a single-image human mesh model and will be the slowest part of the stack.
- Use `Gemma 4` to verbalize a grounded scene summary, not to invent scene state from raw pixels alone.
- Add a short cooldown and dedupe layer before speech so the app does not chatter constantly.

## Docs Map

- [OpenCoach V0 Execution Plan](/home/matt/Documents/dev/0golf/docs/tasks/opencoach-v0-execution-plan-2026-04-12.md)

## Immediate Next Work

1. Bootstrap the Python project at repo root with `uv`, `ruff`, and Python `3.11`.
2. Install `v4l-utils` and reconnect or expose a real `V4L2` camera.
3. Request and confirm access to the `SAM 3D Body` Hugging Face checkpoints.
4. Implement the camera session, preview endpoint, and one-page UI.
5. Add real model adapters and end-to-end speech output.
