# Golf Volumetric Demo Execution Plan - Vid2Avatar-Pro Monocular Path

Date: 2026-04-08  
Role: TPM plan for two staff software engineers  
Target platform: Ubuntu 24.04 host, `uv`-managed execution, single NVIDIA GPU with `>= 48 GB` VRAM  
Demo objective: produce a reviewable free-viewpoint golf-swing artifact from a single monocular swing video using a Vid2Avatar-Pro-style personalization pipeline, with one top-level `uv` command, deterministic artifact packaging, and aggressively strict pass/fail gates.

## Decision Summary

The primary demo stack is:

1. Static monocular RGB capture only for the passing path.
2. Vid2Avatar-Pro personalization only:
   - frozen universal prior model
   - frozen canonical texture inpainting model
   - no universal prior pretraining on the critical path
3. AIOS-style SMPL-X initialization, Sapiens 2D keypoints, and SAM-HQ masks for preprocessing, matching the supplemental method description.
4. `uv` is the only execution entrypoint for bootstrap, smoke test, and custom run orchestration.
5. TPM review is based on packaged MP4s and machine-readable QA reports, not notebooks or ad hoc scripts.

This is the best balance of:

- fidelity to the Vid2Avatar-Pro method
- monocular-first execution
- realistic engineering scope
- strict automation and QA

## Why This Stack And Not The Alternatives

### Selected Primary Stack

The plan is based on the Vid2Avatar-Pro project page and supplemental:

- monocular in-the-wild personalization from a pre-trained universal prior model
- preprocessing using off-the-shelf human pose/shape estimation, Sapiens keypoints, and SAM-HQ masks
- canonical template reconstruction and texture unwrapping
- diffusion-based canonical texture inpainting
- short personalization fine-tune on a frozen prior

The supplemental is explicit about the intended split:

- universal prior training is large-scale offline research training
- personalization is the runtime path for a new monocular identity

That split is the only credible way to build a demo on one machine.

### Explicitly Not Chosen For The Passing Path

Training the Vid2Avatar-Pro universal prior from scratch is explicitly out of scope.

Reason:

- the supplemental states universal prior training uses `64` NVIDIA A100 GPUs for about `5` days
- that is not a demo path
- that is not a script-development path
- that is not credible on the available execution footprint

Moving-camera monocular capture is also out of scope for the passing path.

Reason:

- the paper shows it can work on some moving-camera iPhone captures
- the demo development problem is stricter than the paper result
- static-camera capture is the only serious way to make preprocessing, pose refinement, and artifact QA deterministic enough for a passing script contract

Unrestricted 360-degree orbiting is out of scope for pass.

Reason:

- monocular input does not support that quality bar reliably for a golf swing
- the plan must target a limited, believable orbit envelope around the source view

## Non-Negotiable Demo Scope

The passing demo is not "general monocular avatar creation."

The passing demo is:

- one golfer
- one trimmed swing clip
- one static monocular RGB video
- one frozen Vid2Avatar-Pro prior checkpoint pack
- one frozen inpainting checkpoint
- automated preprocessing, personalization, rendering, and review packaging
- limited-angle novel-view orbit and zoom

Anything outside that scope is a stretch goal.

## Hard External Preconditions

The passing path requires all items below before any script work can be called complete.

### Required Model Assets

- universal prior model checkpoint pack
- canonical texture inpainting checkpoint
- SMPL-X model assets
- AIOS checkpoint
- Sapiens checkpoint
- SAM-HQ checkpoint

### Required Asset Policy

All model assets must be:

- present locally before the demo run
- declared in the session manifest
- hash-verified before stage execution
- immutable during a run

If any required asset is missing or hash-mismatched, the top-level script must fail before frame extraction.

### Critical Reality Check

As of 2026-04-08, the Vid2Avatar-Pro project page exposes:

- paper
- supplemental PDF
- video
- public comparison outputs

It does not expose an official public Vid2Avatar-Pro code release or public pre-trained UPM checkpoint on the project page itself.

Therefore the passing plan assumes a supplied internal or otherwise authorized frozen checkpoint pack. If that pack does not exist, the plan is blocked at Milestone 0.

## Passing Criteria

The demo passes only if all of the following are true.

### Functional Gates

1. A clean Ubuntu 24.04 machine can install `uv`, run `uv sync --frozen`, and execute the bootstrap command without manual file edits.
2. A single top-level `uv run` smoke test completes end to end and writes review artifacts to `artifacts/smoke_test_v2ap/`.
3. A single top-level `uv run` custom golf command completes end to end from session manifest to final review artifacts.
4. Every stage writes a machine-readable JSON report and a plain-text log.
5. The final command exits `0` only if all required QA gates pass.
6. Any missing model asset, failed subprocess, NaN loss, missing frame, or threshold breach must terminate the run with a non-zero exit code.
7. Resume from the last completed stage must work without re-running successful earlier stages.
8. No stage may silently skip work or silently fall back to a different algorithm.

### Artifact Gates

The golf demo must write all of the following:

- `artifacts/<session>/review/01_input_clip.mp4`
- `artifacts/<session>/review/02_mask_overlay.mp4`
- `artifacts/<session>/review/03_pose_overlay.mp4`
- `artifacts/<session>/review/04_canonical_template_turntable.mp4`
- `artifacts/<session>/review/05_heldout_source_reconstruction.mp4`
- `artifacts/<session>/review/06_novel_view_orbit.mp4`
- `artifacts/<session>/review/07_novel_view_zoom.mp4`
- `artifacts/<session>/review/08_side_by_side.mp4`
- `artifacts/<session>/debug/canonical_texture_before_inpaint.png`
- `artifacts/<session>/debug/canonical_texture_after_inpaint.png`
- `artifacts/<session>/debug/canonical_mask.png`
- `artifacts/<session>/metrics/environment_report.json`
- `artifacts/<session>/metrics/ingest_report.json`
- `artifacts/<session>/metrics/pose_report.json`
- `artifacts/<session>/metrics/mask_report.json`
- `artifacts/<session>/metrics/template_report.json`
- `artifacts/<session>/metrics/training_report.json`
- `artifacts/<session>/metrics/render_report.json`
- `artifacts/<session>/manifest.json`

### Script-Development Gates

These are strict and non-negotiable.

1. The passing command must be exactly one top-level `uv run` invocation plus a manifest path.
2. No environment activation commands may be required from the TPM.
3. No config file edits may be required after clone.
4. No notebook may be required for inspection or post-processing.
5. No manually typed ffmpeg command may be required.
6. All subprocess command lines used by the orchestrator must be captured in `manifest.json`.
7. All external assets must be listed with source URL, local path, and SHA256 in `manifest.json`.
8. All produced files must be listed with SHA256 in `manifest.json`.
9. The run must be restart-safe:
   - rerunning the same command after success must not corrupt previous artifacts
   - rerunning after failure must resume from the last valid checkpoint unless `--force` is set
10. The CLI must have a `--dry-run` mode that validates everything except the GPU-heavy stages.

### Automated Quality Gates

The passing demo must satisfy all metrics below.

#### Input and Capture Gates

1. Source video resolution must be `>= 1920x1080`.
2. Source frame rate must be `>= 60 fps`.
3. The input swing window must be between `90` and `240` frames inclusive.
4. Static-camera verification must pass:
   - estimated background homography translation p95 `<= 2.0 px`
   - estimated scale drift p95 `<= 0.5%`
5. The ingest validator must reject clips with severe dropped-frame cadence irregularities.

#### Pose Refinement Gates

1. AIOS initialization must produce valid SMPL-X estimates for `>= 98%` of frames.
2. The offline refinement stage must reduce mean 2D reprojection error by at least `25%` relative to initialization.
3. Final mean 2D reprojection error must be `<= 7 px`.
4. Final p95 2D reprojection error must be `<= 15 px`.
5. No more than `2` consecutive frames may fall back to interpolated pose parameters.

#### Mask Gates

1. SAM-HQ mask generation must produce a non-empty subject mask on `>= 99%` of frames.
2. All high-confidence 2D keypoints must lie inside the subject mask on `>= 99%` of frames.
3. No full-frame subject dropout is allowed.
4. The club may be imperfect, but the mask QA must show that the hand-club region remains non-empty through the impact window.

#### Canonical Template Gates

1. Canonical template extraction must complete with finite geometry bounds and finite vertex attributes.
2. The canonical texture unwrap must produce a valid canonical mask.
3. Pre-inpainting visible canonical texture coverage inside the canonical mask must be `>= 30%`.
4. Post-inpainting valid pixel coverage inside the canonical mask must be `100%`.

#### Personalization Training Gates

1. The fine-tune stage must complete the configured `2000` iterations unless an explicit `--max-iters` override is set in the manifest.
2. No NaN or Inf losses are allowed.
3. Total loss at the end of fine-tuning must be at least `20%` lower than at iteration `0`.
4. A checkpoint must be written at least every `250` iterations.
5. Held-out source-view foreground reconstruction on withheld frames must satisfy:
   - PSNR `>= 24.0 dB`
   - SSIM `>= 0.95`
6. The training report must include:
   - wall-clock time
   - VRAM peak
   - final iteration
   - initial and final loss
   - held-out metrics

#### Render Validation Gates

1. All required frame sequences must exist and be contiguous.
2. No black frames are allowed.
3. No NaN frames are allowed.
4. Output resolution must be `>= 960x540`.
5. Orbit range must stay inside the configured monocular-safe envelope:
   - yaw sweep `<= 100 degrees`
   - pitch offset `<= 15 degrees`
6. The side-by-side review video must have matching frame counts across all panes.

### Manual TPM Review Gates

The TPM signs off only if all items below are true when watching the final review MP4s.

1. The golfer remains spatially stable through address, backswing, downswing, impact, and follow-through.
2. The club remains attached to the hands in the source view and near-source novel views through the impact window.
3. The limited novel-view orbit looks materially 3D and not like a simple 2D warp.
4. Close zoom preserves posture, shoulder turn, and hand-club relationship well enough to inspect the swing.
5. The result is clearly better than a flat crop-and-zoom of the original video.
6. Brief local club artifacts are acceptable; disappearance of the club for more than `3` consecutive frames is not.

## Hard Constraint On Model Scope

The shipping demo accepts only the Vid2Avatar-Pro personalization path as the primary model path.

That means:

- frozen UPM
- frozen inpainting model
- monocular personalization
- no UPM pretraining

If the team cannot supply frozen UPM and inpainting checkpoints, the passing demo is blocked and must not be represented as "ready except for polish."

## Recommended Capture Specification

The engineers should enforce this capture protocol instead of trying to make weak footage work.

### Camera

- Single RGB camera only for pass
- Static tripod or rigid mount only
- `1920x1080` minimum
- `60 fps` minimum
- `120 fps` preferred
- target shutter `1/1000 s` or faster if lighting permits
- locked exposure, white balance, and focus

### Viewpoint

- preferred: down-the-line or slight 3/4 view
- allowed: face-on if the club remains visible at impact
- disallowed for pass: handheld orbiting camera

### Environment

- static background
- even lighting
- no reflective clutter behind the golfer
- no large moving background objects
- full golfer visible for the entire swing window

### Golf-Club-Specific Rules

- use a club with strong contrast against the background
- prefer matte tape or visible shaft markers if allowed
- reject clips where impact frames are heavily blurred across the entire club-hand region

## Input Contract

The top-level custom run consumes a session manifest.

### Required Inputs

- one monocular RGB video clip
- one frame window to reconstruct
- all required model assets with hashes
- optional trim metadata for the swing window

### Session Manifest

```yaml
session_id: golfer_demo_001
video: inputs/golf/golfer_demo_001/source.mp4
frame_window:
  start: 0
  stop: 149
  step: 1
capture:
  fps_min_expected: 60
  static_camera_required: true
  source_view: down_the_line
  resolution_expected: 1920x1080
model_assets:
  upm_checkpoint: models/v2ap/upm_frozen.ckpt
  upm_sha256: "<sha256>"
  inpaint_checkpoint: models/v2ap/inpaint_frozen.ckpt
  inpaint_sha256: "<sha256>"
  smplx_root: models/smplx
  aios_checkpoint: models/aios/model.pt
  sapiens_checkpoint: models/sapiens/model.pt
  sam_hq_checkpoint: models/sam_hq/model.pt
preprocess:
  keypoint_detector: sapiens
  segmenter: sam_hq
  body_init: aios
  holdout_ratio: 0.2
train:
  finetune_iters: 2000
  batch_size: 1
render:
  output_fps: 30
  resolution: 960x540
  orbit_yaw_degrees: 90
  orbit_pitch_degrees: 10
  orbit_frames: 180
  zoom_frames: 120
qa:
  reprojection_mean_px_max: 7.0
  reprojection_p95_px_max: 15.0
  heldout_psnr_min: 24.0
  heldout_ssim_min: 0.95
```

## Runtime Architecture

### Execution Model

Everything is executed through `uv`.

The top-level commands are:

```bash
uv sync --frozen --extra v2ap
uv run --frozen python -m golf_v2ap.bootstrap --check
uv run --frozen python -m golf_v2ap.cli smoke inputs/smoke/v2ap_smoke.yaml
uv run --frozen python -m golf_v2ap.cli demo inputs/golf/golfer_demo_001/session.yaml
```

### Python Runtime

Use one pinned `uv` environment with:

- `python==3.10.*`
- pinned `torch` stack compatible with the chosen CUDA runtime
- pinned preprocessing and rendering dependencies

Do not pretend this stack is ready for Python `3.13`.

### Host Responsibilities

- CLI orchestration
- manifest validation
- model asset validation
- frame extraction
- pose/mask/template stage launching
- QA report generation
- review packaging
- final artifact manifest generation

## Primary Method Configuration

The worker pipeline must implement these stages in order.

1. Input validation and frame extraction
2. AIOS-based initial SMPL-X estimation
3. Sapiens 2D keypoint estimation
4. Offline refinement of pose, shape, and camera parameters by 2D keypoint reprojection loss
5. SAM-HQ foreground mask extraction using keypoint prompts
6. Canonical template reconstruction and canonical texture unwrapping
7. Diffusion-based canonical texture inpainting
8. Identity normalization to match the frozen prior input contract
9. Frozen-UPM personalization for `2000` iterations
10. Held-out source-view rendering
11. Limited novel-view orbit rendering
12. Zoom render and side-by-side packaging

No additional research branch may be on the critical path.

## Repository Blueprint

The implementation should live in a dedicated package surface such as:

```text
demo/vid2avatar_pro/
  pyproject.toml
  uv.lock
  src/golf_v2ap/
    bootstrap.py
    cli.py
    manifests.py
    assets.py
    ingest.py
    pose_init.py
    pose_refine.py
    masks.py
    canonical_template.py
    inpaint.py
    finetune.py
    render.py
    qa.py
    artifact_manifest.py
  scripts/
    bootstrap_ubuntu24.sh
```

## Script Contract

### 1. Bootstrap

The bootstrap command must:

- verify `uv`
- verify NVIDIA driver visibility
- install the pinned Python version through `uv`
- `uv sync --frozen`
- verify ffmpeg
- verify all required system binaries

### 2. Smoke Test

The smoke test must:

- validate the asset pack
- run a trimmed fixture session
- exercise every stage at least once
- write the full review package

If the smoke test uses lighter data or shorter iteration counts, that must be explicit in the smoke manifest and not hardcoded.

### 3. Custom Golf End-To-End Run

The custom command must:

- accept only a manifest path
- create a unique artifact directory
- validate inputs and asset hashes first
- run all stages in order
- stop on the first hard failure
- write final review artifacts and reports

## Delivery Milestones

### Milestone 0: Asset Lock

Duration: `0.5 day`

Done when:

- all required checkpoint files exist
- all hashes are recorded
- the team explicitly rejects UPM pretraining as critical path work

### Milestone 1: Bootstrap And Smoke

Duration: `1.5 days`

Done when:

- `uv sync --frozen` works on a clean Ubuntu 24.04 host
- bootstrap validates the GPU and assets
- smoke test runs end to end and writes all required artifacts

### Milestone 2: Preprocessing Pipeline

Duration: `2 days`

Done when:

- AIOS init, Sapiens, refinement, and SAM-HQ all run from one manifest
- pose and mask QA reports satisfy the thresholds on the smoke fixture

### Milestone 3: Canonical Template And Personalization

Duration: `2 days`

Done when:

- canonical template and inpainting artifacts are written
- the `2000`-iteration personalization run completes
- held-out metrics pass

### Milestone 4: Final Review Package

Duration: `1 day`

Done when:

- orbit, zoom, and side-by-side MP4s are present
- all JSON reports exist
- `manifest.json` includes every dependency and output hash

## Runtime Expectations

These are planning estimates, not guarantees.

- bootstrap and environment sync: `30-90 minutes`
- monocular preprocessing: `4-8 hours`
- personalization fine-tune: `10-45 minutes` depending on GPU class
- final rendering and packaging: `30-120 minutes`

The preprocessing estimate is grounded by the supplemental statement that in-the-wild preprocessing takes about `6` hours. The fine-tuning estimate is grounded by the supplemental statement that personalization takes about `10` minutes on `1` A100 GPU.

## Execution Risks And Required Mitigations

### Risk 1: No Official Public Vid2Avatar-Pro Checkpoints

Mitigation:

- treat checkpoint availability as Milestone 0
- fail fast if asset pack is missing
- do not allow the team to substitute "we will train the prior later"

## Definition Of Done

The work is done when a TPM can clone the repo on Ubuntu 24.04, run:

```bash
uv sync --frozen --extra v2ap
uv run --frozen python -m golf_v2ap.bootstrap --check
uv run --frozen python -m golf_v2ap.cli smoke inputs/smoke/v2ap_smoke.yaml
uv run --frozen python -m golf_v2ap.cli demo inputs/golf/golfer_demo_001/session.yaml
```

and then review the final MP4s in `artifacts/golfer_demo_001/review/` without:

- activating a virtualenv manually
- editing config files by hand
- opening a notebook
- hunting for missing weights
- rerunning failed stages manually

## Source Basis

- Vid2Avatar-Pro project page: <https://moygcc.github.io/vid2avatar-pro/>
- Vid2Avatar-Pro supplemental PDF: <https://moygcc.github.io/vid2avatar-pro/static/CVPR2025_Vid2Avatar_Pro_supp.pdf>
- Public Vid2Avatar repository, used only as a public implementation reference for monocular custom-video preprocessing structure: <https://github.com/MoyGcc/vid2avatar>
