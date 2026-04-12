# OpenCoach V0 Execution Plan

## Goal

Ship a Python-only demo that connects to a real `V4L2` camera, shows a live preview, and speaks short live descriptions of what it sees about a golfer on a hitting mat.

This plan is deliberately optimized for execution, not elegance. V0 should prove the end-to-end path with real local models and real local audio.

## Scope

In scope:

- Python-only repo and runtime
- one camera
- one screen
- one live preview
- one live commentary pipeline
- real local `RF-DETR`
- real local `SAM 3D Body`
- real local `Gemma 4`
- real local audio playback

Out of scope for v0:

- cloud inference
- accounts, auth, persistence, or analytics
- mobile clients
- multi-camera support
- shot history
- coaching scores or training plans
- polished golf biomechanics
- accurate club or ball tracking

## Current State

Repo facts:

- The repo is mostly empty apart from research and notebook material.
- The old Tauri/Vite app appears intentionally deleted in the worktree.
- There is no root Python project yet.

Machine facts verified on April 12, 2026:

- `uv` and `ruff` are installed.
- Python `3.11` is available via `uv` and should be the project baseline.
- GPU capacity is not the problem on this machine.
- No `/dev/video*` camera device is currently visible.
- `v4l2-ctl` is not installed.
- Hugging Face auth is configured.
- `Gemma 4` download access is available.
- `SAM 3D Body` download access is not yet approved.

## Decision Log

### 1. Use Python 3.11

`SAM 3D Body` publishes Python `3.11` setup guidance. `RF-DETR` supports Python `>=3.10`, and `Gemma 4` is fine in modern `transformers`.

Do not copy `vigil-annotate`'s Python `3.13` target into OpenCoach. That would make the hardest dependency, `SAM 3D Body`, worse for no upside.

### 2. Use a server-rendered web app

Build the app as `FastAPI + Jinja2` with one page and minimal browser JavaScript.

Reasons:

- It keeps the repo Python-only.
- It matches the simplicity of v0.
- It avoids reintroducing Node or frontend build tooling.
- It is close enough to the proven Vigil control-plane style to reuse habits without inheriting extra complexity.

### 3. Use Pydantic for all schemas

Add `pydantic` as a required dependency and use it for every structured schema in the repo.

That includes:

- app settings
- camera configuration
- camera status payloads
- model runtime configuration
- model output payloads
- scene snapshots
- commentary requests and responses
- TTS job payloads
- internal state exchanged across module boundaries

Do not mix `dataclass` schema types with `pydantic` schema types for the same boundary. V0 is small enough that one schema system is the right call.

### 4. Separate “seeing” from “talking”

The live commentary stack should be:

1. camera frame
2. `RF-DETR` visibility / crop / segmentation
3. `SAM 3D Body` pose and mesh inference on sampled frames
4. scene summarizer that produces structured state
5. `Gemma 4` to phrase the state naturally
6. local TTS playback

Do not prompt `Gemma 4` directly on arbitrary raw frames and hope it behaves. That is the easy way to ship hallucinations.

## Recommended Repository Shape

```text
docs/
  README.md
  tasks/
src/
  opencoach/
    __init__.py
    app.py
    settings.py
    logging_config.py
    schemas/
      camera.py
      commentary.py
      models.py
      runtime.py
      scene.py
      tts.py
    web/
      routes.py
      templates/
      static/
    camera/
      models.py
      session.py
      v4l2.py
      preview.py
    pipelines/
      orchestrator.py
      snapshot.py
      commentary.py
      state_machine.py
    models/
      base.py
      rfdetr.py
      sam3_body.py
      gemma4.py
    tts/
      base.py
      player.py
      piper.py
dev/
  bootstrap-python.sh
  bootstrap-models.sh
  check-runtime.sh
tests/
  test_settings.py
  test_commentary.py
  test_state_machine.py
  test_prompt_builder.py
```

## Phase Plan

### Phase 0: Bootstrap the Repo

Deliverables:

- copy in `AGENTS.md`
- add `docs/README.md`
- add root `pyproject.toml`
- add root `.python-version` set to `3.11`
- add `src/opencoach/` package
- add `tests/`

Python config should be copied from the Vigil style, then simplified:

- keep `setuptools`
- keep `uv`
- keep `ruff`
- keep `pytest`
- do not add monorepo-specific settings
- do not copy `Python 3.13`

Recommended dependency baseline:

- `fastapi`
- `uvicorn[standard]`
- `jinja2`
- `python-multipart`
- `click`
- `pydantic>=2`
- `pydantic-settings`
- `structlog`
- `numpy`
- `opencv-python`
- `pillow`
- `pyyaml`

Recommended dev dependencies:

- `pytest`
- `ruff`
- `httpx`

Model dependencies should be kept explicit and pinned, but the `SAM 3D Body` stack should be bootstrapped with a dedicated script because it depends on:

- `detectron2` from a pinned Git revision
- optional `sam3`
- gated checkpoint downloads

Schema rules for Phase 0:

- every schema in `src/opencoach/schemas/` should inherit from `pydantic.BaseModel`
- runtime configuration should use `pydantic-settings`
- request and response payloads should never be raw dicts outside narrow adapter glue
- if a value crosses a module boundary in structured form, it should usually be a `pydantic` model

### Phase 1: Prove Camera Bring-Up

Deliverables:

- one config form with:
  - device path
  - width
  - height
  - fps
  - pixel format
  - model selection
  - checkpoint paths
  - commentary enable toggle
- connect / disconnect controls
- live preview in the same page
- status strip with current camera state and error text

Implementation notes:

- use `cv2.VideoCapture(device_path, cv2.CAP_V4L2)`
- set width, height, fps, and fourcc before starting capture
- maintain a dedicated capture thread
- publish the latest frame into a bounded latest-frame buffer
- expose preview as MJPEG over HTTP so the browser can render it with a plain `<img>`
- represent camera config, live status, and preview state with `pydantic` models

Verification:

- real camera opens
- preview stays live for at least 10 minutes
- disconnect and reconnect work
- invalid config surfaces a clear operator error

### Phase 2: Add Model Runtime Adapters

#### RF-DETR

Plan:

- use the open-source `rfdetr` package directly
- start with `RFDETRSegSmall` or `RFDETRSegMedium`
- run inference on downscaled frames at a fixed cadence, not every preview frame
- use person segmentation or person detection as the stable golfer anchor

V0 expectation:

- reliable golfer visibility detection
- stable crop for downstream models
- optional segmentation mask overlay for debugging
- outputs wrapped in `pydantic` models rather than loose dictionaries

#### SAM 3D Body

Plan:

- support both `facebook/sam-3d-body-vith` and `facebook/sam-3d-body-dinov3`
- default to `vith` first because it is lighter than the `dinov3` release
- clone and pin the upstream repo under `external/` or install from a pinned commit in bootstrap
- build `detectron2` exactly as required by upstream
- load checkpoints from a configured local model directory

Important constraint:

`SAM 3D Body` is a single-image full-body mesh model, not a live video tracker. We should run it on sampled frames when the golfer is confidently visible and smooth the outputs across time ourselves.

V0 use of its output:

- body visibility confirmation
- coarse pose stability
- rough torso tilt / stance orientation
- change-of-state cues for setup, movement, and finish
- normalized into `pydantic` scene and pose schemas before downstream prompting

Do not promise precise biomechanics in v0.

#### Gemma 4

Plan:

- support `google/gemma-4-E4B-it` and `google/gemma-4-26B-A4B-it`
- default to `E4B` for interactive latency
- keep `26B-A4B` selectable in config because this machine has enough VRAM
- use `AutoProcessor` and `AutoModelForMultimodalLM`

Prompt contract:

- input image: current frame or golfer crop
- input structured text:
  - golfer visible / not visible
  - inside mat ROI / outside mat ROI
  - coarse body state
  - pose-derived notes
  - last spoken phrase
- output: one short grounded sentence, or `silent`

Represent both the prompt input bundle and the generated commentary payload as `pydantic` models.

### Phase 3: Build the Live Commentary Pipeline

Use a small stateful orchestrator:

- camera thread writes latest frame
- inference scheduler samples the latest frame on cadence
- `RF-DETR` runs first
- `SAM 3D Body` runs only when golfer confidence is high enough
- summarizer produces a `SceneSnapshot`
- `Gemma 4` turns the snapshot into short natural language
- speech layer dedupes and speaks

Every handoff between these stages should use `pydantic` schemas, not ad hoc dictionaries.

Recommended cadences:

- preview: camera native fps
- `RF-DETR`: 3 to 5 Hz
- `SAM 3D Body`: 1 to 2 Hz
- `Gemma 4`: every 2 to 4 seconds, or immediately on state change

Speech rules:

- suppress repeats of the same idea
- impose a cooldown between utterances
- allow an interrupt only for high-salience state changes

Initial state machine:

- no golfer visible
- golfer visible but off mat
- golfer on mat and static
- golfer setting up
- golfer moving through swing
- golfer in follow-through

This gives us stable, grounded commentary even before we have refined golf-specific logic.

### Phase 4: Verification With Real Models

This phase is mandatory. V0 is not done until all of these pass on the real machine.

#### Runtime Smoke Checks

- `RF-DETR` loads local weights and produces a person detection on a real golf frame
- `SAM 3D Body` loads a real checkpoint and returns a mesh / pose output on a real golf frame
- `Gemma 4` loads locally and returns grounded text for an image prompt
- TTS generates audible speech through the machine speakers

#### Integrated Checks

- preview remains live while model workers run
- commentary still works after reconnecting the camera
- commentary continues for at least a 5-minute session without queue growth or worker death
- GPU memory stays bounded and recoverable across restarts

#### Human Acceptance Check

Run one full demo with:

- a real golfer
- a real hitting mat
- a real connected camera
- audio heard from the machine

Success condition:

The operator can start the camera, see the live view, hear grounded short descriptions, and recover from a disconnect without restarting the whole app.

## Test Plan

Write focused tests for the parts that matter:

- config parsing
- schema validation and serialization
- prompt building
- commentary dedupe / cooldown
- state machine transitions
- snapshot serialization
- camera session behavior with a fake frame source

Do not waste time snapshot-testing HTML in v0.

For model tests:

- add explicit smoke commands instead of pretending unit tests can cover heavy model runtime
- keep them in `dev/check-runtime.sh`

## Blocking Risks

### 1. No camera device is visible

This blocks true end-to-end validation today.

Action:

- reconnect the camera
- confirm `/dev/video*`
- install `v4l-utils`
- record the exact supported formats with `v4l2-ctl --list-formats-ext`

### 2. SAM 3D Body access is still gated

This blocks the hardest model requirement today.

Action:

- request approval on the Hugging Face repos
- verify `hf download facebook/sam-3d-body-vith model.ckpt --dry-run`

### 3. Detectron2 build friction

This is the highest-probability dependency failure.

Action:

- isolate it in a bootstrap script
- pin the exact repo revision
- keep a machine-check script that validates importability before app bring-up

### 4. TTS backend choice is still open

We need a concrete local backend, but it should stay behind an adapter.

Recommendation:

- start with a local subprocess-based backend that writes WAV and plays it with `ffplay`
- keep the adapter boundary so we can swap voices or engines without disturbing the rest of the app

## Immediate Sequence

1. Bootstrap Python project files.
2. Install `v4l-utils` and reconnect a real camera.
3. Confirm `SAM 3D Body` access.
4. Build the single-page camera preview app.
5. Add `RF-DETR` adapter and verify golfer detection.
6. Add `SAM 3D Body` adapter and verify pose output.
7. Add `Gemma 4` adapter and grounded prompt path.
8. Add TTS and speech cooldown logic.
9. Run the live end-to-end demo on a real golfer.

## External References

- `SAM 3D Body` repo: https://github.com/facebookresearch/sam-3d-body
- `SAM 3D Body` install guide: https://github.com/facebookresearch/sam-3d-body/blob/main/INSTALL.md
- `RF-DETR` repo: https://github.com/roboflow/rf-detr
- `Gemma 4 E4B` model card: https://huggingface.co/google/gemma-4-E4B
