# OpenCoach Agent Guide

`AGENTS.md` is the agent-facing operating summary for this repository. Use it as the short version of the project contract while the fuller implementation context is built out under `docs/`.

## Platform Summary

- OpenCoach is a Python-only application.
- OpenCoach v0 is a single-screen demo app.
- The application configures one `V4L2` camera stream, shows the live feed, and speaks short descriptions of what it sees about a golfer.
- The camera is aimed at a golfer standing on a hitting mat.

## Core Capabilities

- Enumerate or accept a configured `V4L2` camera device path.
- Open the camera with explicit width, height, fps, and pixel format settings.
- Render a live preview in the app.
- Run local `RF-DETR` inference on live frames.
- Detect address, swing start, and swing finish with simple local heuristics.
- Record swing clips once address is armed.
- Run local `SAM 3D Body` processing asynchronously on recorded swing clips.
- Produce local spoken TTS phrases after completed swings.
- Keep local `Gemma 4` support available, but outside the live v0 swing path.

## Architecture Guardrails

- The app must remain Python-only for v0.
- Use `uv` for dependency management.
- Use `ruff` for formatting and linting.
- Use `pytest` for tests.
- Use Python `3.11` as the project baseline.
- Use `pydantic` for all schemas and `pydantic-settings` for application configuration.
- Do not reintroduce Node, Tauri, Electron, or any frontend build pipeline.
- Keep the UI server-rendered and simple.
- Prefer `V4L2` integration through OpenCV or another vendor-agnostic Linux path.
- Hosted inference is forbidden for the core demo path. `RF-DETR`, `SAM 3D Body`, and `Gemma 4` must run locally.
- All model artifacts must live under the repo-root `models/` directory.
- The default `SAM 3D Body` model target is `facebook/sam-3d-body-dinov3` under `models/sam-3d-body-dinov3/`.
- Treat the hitting mat as configured operator context in v0 unless a later step proves automatic detection is reliable enough.
- The live v0 path is `camera -> RF-DETR -> address gate -> clip recording -> async SAM 3D Body overlay -> local TTS phrase`.
- Keep model integrations behind small adapter boundaries so checkpoints and runtimes can change without rewriting the app.

## Frontend Constraints

- The UI is one screen.
- The screen should contain camera configuration, model/runtime status, and the live preview.
- Once configured, the operator should stay on the same page while the preview and commentary run.
- Favor plain HTML, Jinja2 templates, and minimal browser JavaScript.
- The app should prioritize clarity and operability over styling.

## Repository Structure

- `docs/` contains project planning and implementation notes.
- `docs/tasks/` contains execution artifacts and phased plans.
- `src/opencoach/` should contain the application package.
- `src/opencoach/camera/` should own camera session and preview logic.
- `src/opencoach/models/` should own model adapters.
- `src/opencoach/pipelines/` should own orchestration, state, and commentary logic.
- `src/opencoach/tts/` should own speech generation and playback adapters.
- `src/opencoach/web/` should own routes, templates, and static assets.
- `dev/` should contain bootstrap and machine-check scripts.
- `models/` should contain all downloaded or user-provided model artifacts, including RF-DETR weights, SAM 3D Body checkpoints, Gemma snapshots, and Piper voice models.
- `tests/` should contain the Python test suite.

## Development Standards

- Work incrementally and keep the app runnable as the feature set grows.
- Prove the real runtime path early; do not hide behind mocks for the main requirements.
- Write focused tests for config parsing, state transitions, prompt building, queueing, and other logic-heavy code.
- Do not spend time snapshot-testing simple HTML for v0.
- Keep imports at module top unless there is a real lazy-load reason.
- Avoid broad exceptions in production code.
- Use explicit, inspectable config objects for camera and model runtime settings.
- All structured request, response, config, and internal boundary payloads should be `pydantic` models.
- Keep concurrency simple: bounded queues, latest-frame buffers, and clearly owned worker threads.

## Boundaries

- Ask first before adding heavy new dependencies that are not required for the camera or model runtime.
- Ask first before introducing cloud services or external hosted APIs.
- Ask first before changing the app from a one-screen design.
- Never commit model weights, tokens, or secrets.
- Never use destructive git operations unless explicitly requested.

## Immediate Priorities

- Bootstrap the root Python project with `uv`, `ruff`, and Python `3.11`.
- Confirm local access to `RF-DETR`, `SAM 3D Body DinoV3`, and `Gemma 4`.
- Bring up a real `V4L2` camera preview.
- Wire the live swing-capture pipeline end to end with local speech output and SAM overlay artifacts.
