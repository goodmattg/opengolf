# OpenCoach Overview

## Status

OpenCoach is in active v0 implementation. The app is Python-only and the older Tauri/Vite frontend remains intentionally removed.

## Product Summary

OpenCoach v0 is a single-screen Python app for one operator-visible workflow:

1. Configure one `V4L2` camera stream.
2. Start the stream.
3. Show the live camera feed.
4. Use local `RF-DETR` to early-exit until a golfer is visible.
5. Use live pose cues to arm when the golfer is at address.
6. Record the swing clip.
7. Asynchronously run `SAM 3D Body DinoV3` on the recorded swing and write an overlay video artifact.
8. Speak a short local TTS phrase after the swing finishes.

The camera is aimed at a golfer standing on a hitting mat. The app is a live demo, not a training platform, analytics suite, or multi-user product.

## V0 Contract

V0 succeeds only if it runs end to end with real local models:

- `RF-DETR` running locally.
- `SAM 3D Body` fully supported and runnable locally.
- Local text-to-speech output so the system can speak commentary aloud.

`Gemma 4` remains supported in the repo, but it is not part of the live swing-capture path for v0.

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
- Live gating: `RF-DETR` + pose heuristics for golfer visibility, address, swing start, and finish
- Post-process: async `SAM 3D Body` mesh rendering onto saved swing clips
- Speech: local TTS adapter with subprocess playback through `ffplay` or `aplay`

We should not add any Node, Tauri, Electron, or frontend build tooling back into this repo.

All structured schemas in OpenCoach should use `pydantic`. That includes request models, response models, app settings, camera config, runtime status, scene snapshots, model outputs, and TTS payloads.

All model artifacts should be stored under the repo-root `models/` directory. That includes `RF-DETR` weights, `SAM 3D Body` checkpoints and assets, `Gemma 4` snapshots, and local voice models for TTS.

For this repo, the default `SAM 3D Body` target is `facebook/sam-3d-body-dinov3`, stored at `models/sam-3d-body-dinov3/`.

## Machine Readiness Snapshot

These facts were verified on April 12, 2026:

- `uv 0.9.10` is installed.
- `ruff 0.15.2` is installed.
- Python `3.11` is available through `uv`.
- The machine has an `NVIDIA RTX PRO 6000 Blackwell` with about `96 GB` VRAM.
- `ffmpeg`, `ffplay`, `aplay`, `hf`, `cmake`, `ninja`, `gcc`, and `nvcc` are present.
- A `STEREOLABS ZED-M` camera is available and readable through `/dev/video0`.

Current blockers:

- `v4l2-ctl` is not installed, so camera capability inspection is blocked until `v4l-utils` is installed.
- Hugging Face CLI is authenticated, `facebook/sam-3d-body-dinov3` access is approved, and the checkpoint artifacts are downloaded under `models/sam-3d-body-dinov3/`.
- `Gemma 4` access is available. Dry runs against `google/gemma-4-E4B-it` and `google/gemma-4-26B-A4B-it` succeeded on April 12, 2026.

## Core V0 Design Choices

- Treat the hitting mat as an operator-configured region of interest in v0. Do not depend on a generic detector to find it.
- Use `RF-DETR` to establish golfer visibility and a stable person crop.
- Use `SAM 3D Body` asynchronously on recorded swing clips so the live camera loop stays responsive.
- Use simple, inspectable address and finish heuristics in v0 rather than pretending we have a full biomechanics model.
- Keep speech fixed and short after each completed swing.

## Docs Map

- [OpenCoach V0 Execution Plan](/home/matt/Documents/dev/0golf/docs/tasks/opencoach-v0-execution-plan-2026-04-12.md)

## Immediate Next Work

1. Tighten the live address / swing-finish heuristics against real golf footage.
2. Keep verifying the ZED-M capture path under the web runtime, not only isolated scripts.
3. Add focused regression tests for swing artifact queueing and overlay generation.
