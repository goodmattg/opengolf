# Golf Volumetric Demo Execution Plan

Date: 2026-04-04  
Role: TPM plan for two staff software engineers  
Target platform: Ubuntu 24.04 host, Python 3.13 host runtime, single NVIDIA RTX PRO 6000 GPU  
Demo objective: produce a reviewable free-viewpoint volumetric golf-swing artifact from synchronized multi-view RGB video, with scripted end-to-end execution and final MP4 review outputs for the TPM.

## Decision Summary

The primary demo stack is:

1. Multi-view capture only. Monocular is explicitly out of scope for the passing demo.
2. Foreground-only 4K4D training on top of EasyVolcap as the reconstruction engine.
3. Python 3.13 host orchestrator plus a pinned GPU worker container for the research stack.
4. Static-background controlled capture so masks are reliable and the project avoids an unnecessary full-scene background branch.
5. TPM review via rendered MP4 outputs, not an interactive viewer.

This is the best balance of:

- quality
- public code availability
- public smoke-test assets
- documented custom-data training path
- acceptable operational risk

## Why This Stack And Not The Alternatives

### Selected Primary Stack

`4K4D` is the only candidate from the current high-quality research set that simultaneously gives us:

- official public code
- official public pretrained rendering assets
- official public minimal datasets for smoke testing
- an explicit custom multi-view training path in the README
- a human-focused, high-quality subject-specific pipeline

`EasyVolcap` is the framework `4K4D` is built on and is therefore part of the primary stack rather than an optional dependency.

### Explicitly Not Chosen As The Primary Demo Path

`HumanRF` is not acceptable for the critical path because its quick-start dataset access requires an ActorsHQ access YAML requested from the dataset owners. That violates the "no inaccessible weights/data on the critical path" rule.

`RoGSplat` is not acceptable for the critical path because the public repo is training-oriented, depends on RenderPeople plus preprocessed SMPL data, and does not provide a clean one-command custom-data inference/demo path with public checkpoints.

`Diffuman4D` is promising and worth benchmarking, but not acceptable as the primary shipping demo because its README states the intended 4DGS reconstruction path is not fully open-sourced yet and its custom preprocessing path adds a separate Sapiens dependency chain. It is a useful research benchmark lane, not the delivery lane.

`4D-Humans`, `HMR2`, and similar monocular/body-prior pipelines are not acceptable for the critical path because the strongest variants still rely on gated SMPL-family assets or materially underperform sparse multi-view on unseen views and thin fast objects like the golf club.

## Non-Negotiable Demo Scope

The passing demo is not "general 4D human capture."

The passing demo is:

- one golfer
- one swing clip
- controlled environment
- synchronized multi-view RGB
- foreground-only reconstruction
- high-quality rendered orbit and zoom review videos

Anything outside that scope is a stretch goal.

## Passing Criteria

The demo passes only if all of the following are true.

### Functional Gates

1. A clean Ubuntu 24.04 machine with Python 3.13 can run the host bootstrap entrypoint without manual file edits.
2. The public smoke test completes end to end and writes reviewable MP4s to `artifacts/smoke_test/`.
3. The custom golf run completes end to end from input manifest to review artifacts with a single top-level command.
4. The final script exits `0` and writes a manifest JSON that lists every produced artifact.
5. The TPM can open the final MP4s directly from the artifact directory without launching a notebook or GUI tool.

### Artifact Gates

The golf demo must write all of the following:

- `artifacts/<session>/review/01_input_multiview_grid.mp4`
- `artifacts/<session>/review/02_heldout_reprojection.mp4`
- `artifacts/<session>/review/03_novel_view_orbit.mp4`
- `artifacts/<session>/review/04_novel_view_zoom.mp4`
- `artifacts/<session>/review/05_side_by_side.mp4`
- `artifacts/<session>/metrics/calibration_report.json`
- `artifacts/<session>/metrics/mask_report.json`
- `artifacts/<session>/metrics/training_report.json`
- `artifacts/<session>/manifest.json`

### Automated Quality Gates

1. Calibration median reprojection error must be `<= 0.5 px`.
2. Calibration p95 reprojection error must be `<= 1.0 px`.
3. Static-frame installation smoke training must hit `>= 24 dB` PSNR within the first `200` iterations, matching the 4K4D README sanity check.
4. The render validation script must confirm:
   - no black frames
   - no NaN frames
   - no missing output sequence directories
   - output frame count matches requested frame window
5. The mask QA script must report no full-frame subject dropouts.

### Manual TPM Review Gates

The TPM signs off only if all items below are true when watching `05_side_by_side.mp4` and the two novel-view renders:

1. The golfer remains spatially stable through backswing, downswing, impact, and follow-through.
2. The club remains visible and materially coherent through the swing; brief local artifacts are acceptable, disappearance is not.
3. The novel-view camera motion is smooth and does not expose catastrophic topology collapse.
4. Zoomed views preserve body posture and hand-club relationship well enough to inspect the swing.
5. The result is clearly better than a flat 2D crop-and-zoom video.

## Hard Constraint On Input Modality

The shipping demo accepts only synchronized multi-view RGB as the primary path.

Monocular input is explicitly rejected for the passing demo because it does not meet the quality bar for:

- aggressive pan/zoom
- fast golf-club motion
- unseen views around the body
- robust temporal stability

## Recommended Capture Specification

The engineers should enforce this capture protocol instead of trying to make weak footage work.

### Cameras

- Minimum: 8 synchronized RGB cameras
- Preferred: 10 to 12 synchronized RGB cameras
- Resolution: `1920x1080` minimum
- Frame rate: `120 fps` minimum, `180-240 fps` preferred
- Exposure: target `1/2000 s` or faster, faster if lighting permits
- Lens layout: approximately 180 to 240 degrees around the golfer, with at least 2 elevated views

### Environment

- Static matte background
- High, even lighting
- No moving background objects
- No reflective clutter
- Fixed cameras on rigid mounts
- Capture volume marked on floor

### Golf-Club-Specific Rules

- Use a club with high visual contrast relative to background
- Prefer matte shaft tape or visible markers on the shaft and head
- Ensure at least 4 cameras see the club clearly at impact
- Reject any capture day where impact frames exhibit strong club blur in more than half the cameras

### Additional Required Captures

- Empty-background plate for every camera
- ChArUco calibration board capture for every camera rig configuration
- A short T-pose or A-pose warm-up clip for QA and bounding-box sanity checks

## Input Contract

The top-level custom run consumes a session manifest. Precomputed calibration is the recommended input mode.

### Required Inputs

- synchronized per-camera subject videos
- synchronized per-camera empty-background videos or stills
- precomputed `intri.yml` and `extri.yml`, or calibration image/video set
- frame window to reconstruct

### Session Manifest

```yaml
session_id: golfer_demo_001
frame_window:
  start: 0
  stop: 119
  step: 1
capture_fps: 180
mode: precomputed_calibration
calibration:
  intri: inputs/calibration/golf_rig/intri.yml
  extri: inputs/calibration/golf_rig/extri.yml
background:
  cam00: inputs/golf/golfer_demo_001/background/cam00.mp4
  cam01: inputs/golf/golfer_demo_001/background/cam01.mp4
  cam02: inputs/golf/golfer_demo_001/background/cam02.mp4
  cam03: inputs/golf/golfer_demo_001/background/cam03.mp4
  cam04: inputs/golf/golfer_demo_001/background/cam04.mp4
  cam05: inputs/golf/golfer_demo_001/background/cam05.mp4
  cam06: inputs/golf/golfer_demo_001/background/cam06.mp4
  cam07: inputs/golf/golfer_demo_001/background/cam07.mp4
videos:
  cam00: inputs/golf/golfer_demo_001/videos/cam00.mp4
  cam01: inputs/golf/golfer_demo_001/videos/cam01.mp4
  cam02: inputs/golf/golfer_demo_001/videos/cam02.mp4
  cam03: inputs/golf/golfer_demo_001/videos/cam03.mp4
  cam04: inputs/golf/golfer_demo_001/videos/cam04.mp4
  cam05: inputs/golf/golfer_demo_001/videos/cam05.mp4
  cam06: inputs/golf/golfer_demo_001/videos/cam06.mp4
  cam07: inputs/golf/golfer_demo_001/videos/cam07.mp4
render:
  output_fps: 30
  orbit_views: 180
  zoom_views: 120
  resolution: 1920x1080
```

### Optional Alternate Calibration Mode

If precomputed calibration is unavailable, the manifest may instead point to:

- ChArUco board specification
- calibration videos or still-image directories per camera

That mode is supported by the plan, but it is not the preferred operating mode.

## Runtime Architecture

### Host Runtime

The host runtime is Python 3.13. It owns:

- CLI orchestration
- input validation
- downloads
- dataset packaging
- QA reports
- artifact collation
- container invocation

### GPU Worker Runtime

The GPU worker is a Docker image with a pinned Python 3.10 environment. This is intentional.

Reason:

- `4K4D` and `EasyVolcap` specify `python>=3.9` and depend on `PyTorch3D`, `tiny-cuda-nn`, and `Open3D`
- the official `PyTorch3D` installation guide explicitly lists support through PyTorch `2.4.1`
- the research stack uses custom CUDA extensions and is not credible as a native Python 3.13 install target today

Therefore the delivery requirement is satisfied by:

- Python 3.13 on the host
- deterministic containerized research runtime under the hood

This is the only serious way to make the demo reproducible.

## Primary Method Configuration

The custom golf demo uses the `foreground-only` training path from the 4K4D README, not the more complicated background-plus-foreground joint path.

Reason:

- the target is a single subject
- we control the background
- quality matters more than scene completeness
- fewer moving parts means lower delivery risk

The worker pipeline will:

1. prepare `images/`, `masks/`, `intri.yml`, `extri.yml`
2. extract visual hulls
3. generate a tight object bounds config
4. run static first-frame training as a fast failure gate
5. run full foreground training
6. render held-out and novel-view videos
7. package MP4 review outputs

## Repository Blueprint

The engineers should implement the following repo structure.

```text
demo/
  volumetric/
    README.md
    pyproject.toml
    src/volcap_demo/
      cli.py
      config.py
      bootstrap.py
      downloads.py
      ingest.py
      calibration.py
      masks.py
      dataset_packager.py
      config_templates.py
      worker.py
      render_review.py
      qa.py
      artifact_manifest.py
docker/
  4k4d-worker.Dockerfile
  worker_entrypoint.sh
scripts/
  volcap/
    bootstrap_ubuntu24.sh
    build_worker_image.sh
    smoke_test.sh
    run_golf_demo.sh
    run_worker.sh
configs/
  volcap/
    templates/
      dataset_base.yaml.j2
      dataset_obj.yaml.j2
      exp_4k4d_fg.yaml.j2
      exp_4k4d_fg_static.yaml.j2
inputs/
  calibration/
  golf/
artifacts/
vendor/
third_party/
```

## Script Contract

There must be exactly three top-level entrypoints that the TPM can rely on.

### 1. Host Bootstrap

```bash
./scripts/volcap/bootstrap_ubuntu24.sh
```

Responsibilities:

- validate Ubuntu 24.04
- validate Python 3.13
- install host packages
- install Docker if missing
- install NVIDIA Container Toolkit if missing
- create `.venv-volcap-host`
- install the host Python package
- clone pinned third-party repos
- build the GPU worker image

### 2. Public Smoke Test

```bash
./scripts/volcap/smoke_test.sh
```

Responsibilities:

- download official 4K4D pretrained models
- download official 4K4D minimal datasets
- unpack the minimal dataset
- run 4K4D extraction scripts
- render a dynamic novel-view orbit using official configs
- encode review MP4s
- write artifacts under `artifacts/smoke_test/`

### 3. Custom Golf End-To-End Run

```bash
./scripts/volcap/run_golf_demo.sh inputs/golf/golfer_demo_001/session.yaml
```

Responsibilities:

- validate manifest
- extract frames from all cameras
- calibrate or load calibration
- generate masks
- package the custom dataset in 4K4D/EasyVolcap format
- generate configs
- run visual hull extraction
- run static first-frame smoke train
- run full foreground training
- render held-out view QA
- render orbit and zoom MP4s
- collate outputs into `artifacts/<session>/`

## Exact External Commands The Worker Will Use

### Smoke Test Commands

The smoke test worker implementation should use the official 4K4D commands below.

```bash
python scripts/realtime4dv/extract_images.py --data_root data/renbody/0013_01
python scripts/realtime4dv/extract_masks.py --data_root data/renbody/0013_01
evc-test -c configs/projects/realtime4dv/rendering/4k4d_0013_01.yaml,configs/specs/video.yaml,configs/specs/eval.yaml,configs/specs/spiral.yaml,configs/specs/ibr.yaml
```

The orchestration layer must then locate the rendered frames and encode:

- orbit MP4
- input-view QA MP4
- side-by-side MP4

### Custom Dataset Preparation Commands

The worker implementation should generate a dataset of the form:

```text
data/golf/<session>/
  intri.yml
  extri.yml
  images/
    00/000000.jpg
    00/000001.jpg
    ...
  masks/
    00/000000.png
    00/000001.png
    ...
```

### Custom 4K4D Initialization Commands

```bash
evc-test -c configs/base.yaml,configs/models/r4dv.yaml,configs/datasets/golf/<session>.yaml,configs/specs/optimized.yaml,configs/specs/vhulls.yaml
evc-test -c configs/base.yaml,configs/models/r4dv.yaml,configs/datasets/golf/<session>.yaml,configs/specs/optimized.yaml,configs/specs/surfs.yaml
```

The host-side parser must read the aggregated bounds from the initialization logs and write the generated `*_obj.yaml` dataset config automatically.

### Static First-Frame Training Gate

```bash
evc-train -c configs/exps/4k4d/4k4d_<session>_r4.yaml,configs/specs/static.yaml,configs/specs/tiny.yaml exp_name=4k4d_<session>_r4_static
```

This is a required stop/go gate. If PSNR does not cross the threshold, the pipeline must stop and mark the run as failed.

### Full Foreground Training

```bash
evc-train -c configs/exps/4k4d/4k4d_<session>_r4.yaml
```

### Final Review Rendering

Held-out evaluation:

```bash
evc-test -c configs/exps/4k4d/4k4d_<session>_r4.yaml,configs/specs/eval.yaml
```

Novel-view orbit:

```bash
evc-test -c configs/exps/4k4d/4k4d_<session>_r4.yaml,configs/specs/spiral.yaml,configs/specs/ibr.yaml
```

Novel-view zoom:

The host package must generate a camera-path config for a forward zoom and then invoke:

```bash
evc-test -c configs/exps/4k4d/4k4d_<session>_r4.yaml,configs/volcap/generated/<session>_zoom.yaml,configs/specs/ibr.yaml
```

## Masking Strategy

The masking strategy must be ordered and deterministic.

### Primary Path

Classical background subtraction with background plates plus morphological cleanup.

Why:

- zero model downloads
- deterministic
- best match for a controlled capture stage

### Fallback 1

BackgroundMattingV2 with official PyTorch weights and a background reference image.

Preferred fallback weight:

- `pytorch_resnet50.pth`

### Fallback 2

RobustVideoMatting with official PyTorch weights.

Preferred fallback weight:

- `rvm_resnet50.pth`

### Fallback 3

SAM 2.1 large for manual rescue on a small failed frame range.

Preferred checkpoint:

- `sam2.1_hiera_large.pt`

SAM2 is not the default because interactive prompting is the opposite of a clean unattended path. It is only a rescue tool.

## Bootstrap Details

### Host System Packages

The bootstrap script should install at least:

- `git`
- `curl`
- `wget`
- `ffmpeg`
- `build-essential`
- `cmake`
- `pkg-config`
- `jq`
- `unzip`
- `libgl1`
- `libegl1`
- `libglib2.0-0`
- `libsm6`
- `libxext6`
- `libxrender1`

### Host Python 3.13 Package Set

The host Python package should include at least:

- `typer`
- `pydantic`
- `pyyaml`
- `jinja2`
- `rich`
- `numpy`
- `pandas`
- `opencv-python-headless`
- `ffmpeg-python`
- `gdown`
- `huggingface_hub`

### Worker Base Image

Use:

- `nvidia/cuda:12.4.1-cudnn-devel-ubuntu22.04`

Reason:

- CUDA toolchain available for custom extension builds
- stable match for a PyTorch 2.4.x era stack
- avoids pretending the research stack is natively ready for Ubuntu 24 + Python 3.13

### Worker Python Environment

Use a micromamba or conda environment named `fourd` with:

- `python=3.10`
- `pytorch=2.4.1`
- `torchvision`
- `torchaudio`
- `pytorch-cuda=12.1`

Then install:

- core EasyVolcap / 4K4D Python requirements
- `open3d`
- `iopath`
- `git+https://github.com/facebookresearch/pytorch3d.git@stable`
- `git+https://github.com/NVlabs/tiny-cuda-nn/#subdirectory=bindings/torch`

Do not make `detectron2`, `diff-point-rasterization`, or other optional EasyVolcap development dependencies part of the critical path.

### GPU Architecture Detection

The worker build scripts must detect the GPU compute capability and export:

- `TCNN_CUDA_ARCHITECTURES`
- `TORCH_CUDA_ARCH_LIST`

Do not hardcode an Ada-only architecture value.

## Third-Party Repos And Pins

Mandatory pins are listed in `external_dependency_manifest.csv` in the same folder as this plan.

The critical mandatory repos are:

- `zju3dv/4K4D` at `712eccb0e0eeef744c19eb221cfb424a2915b474`
- `zju3dv/EasyVolcap` at `4cb3c000a31b8764834c79792b355f110d947e75`
- `facebookresearch/pytorch3d` at `b6a77ad7aaf41ed90fca80ce6a2bac3c462a7881`
- `NVlabs/tiny-cuda-nn` at `6ee3546bda615f51abe684ce9edefeb414689135`

Optional mask fallbacks are also pinned in the manifest.

## Engineer Ownership

### Engineer A: Platform, Inputs, QA, Review Artifacts

Owned files and surfaces:

- `demo/volumetric/src/volcap_demo/bootstrap.py`
- `demo/volumetric/src/volcap_demo/cli.py`
- `demo/volumetric/src/volcap_demo/downloads.py`
- `demo/volumetric/src/volcap_demo/ingest.py`
- `demo/volumetric/src/volcap_demo/calibration.py`
- `demo/volumetric/src/volcap_demo/masks.py`
- `demo/volumetric/src/volcap_demo/qa.py`
- `demo/volumetric/src/volcap_demo/render_review.py`
- `demo/volumetric/src/volcap_demo/artifact_manifest.py`
- `scripts/volcap/bootstrap_ubuntu24.sh`
- `scripts/volcap/smoke_test.sh`

Deliverables:

- host bootstrap
- public asset downloader
- frame extraction
- calibration loader and optional ChArUco calibration
- mask generation with fallback chain
- QA JSON reports
- MP4 packaging
- artifact manifest

### Engineer B: Worker Runtime, 4K4D Integration, Training And Rendering

Owned files and surfaces:

- `docker/4k4d-worker.Dockerfile`
- `docker/worker_entrypoint.sh`
- `demo/volumetric/src/volcap_demo/dataset_packager.py`
- `demo/volumetric/src/volcap_demo/config_templates.py`
- `demo/volumetric/src/volcap_demo/worker.py`
- `scripts/volcap/build_worker_image.sh`
- `scripts/volcap/run_worker.sh`
- `scripts/volcap/run_golf_demo.sh`
- `configs/volcap/templates/*`

Deliverables:

- pinned worker container
- 4K4D/EasyVolcap installation
- dataset packager to EasyVolcap layout
- auto-generated configs
- log parsing for bounds and PSNR gates
- training invocation
- held-out and novel-view renders

## Delivery Milestones

### Milestone 0: Stack Lock

Duration: 0.5 day

Done when:

- all repo pins are checked in
- worker image design is approved
- smoke-test asset URLs are verified

### Milestone 1: Bootstrap And Smoke Test

Duration: 1.5 days

Done when:

- bootstrap works on a clean Ubuntu 24 host
- smoke test downloads official assets
- smoke test writes review MP4s

### Milestone 2: Custom Input Pipeline

Duration: 2 days

Done when:

- a session manifest validates
- videos become per-camera frame directories
- calibration loads or calibrates
- masks are generated and QA-reported
- EasyVolcap dataset folder is produced

### Milestone 3: Static Gate And Full Training

Duration: 2 to 3 days

Done when:

- static first-frame training passes the PSNR gate
- full foreground training completes on a trimmed swing window

### Milestone 4: Final Render And TPM Review Package

Duration: 1 day

Done when:

- held-out QA render exists
- orbit render exists
- zoom render exists
- side-by-side review exists
- manifest exists

## Runtime Expectations

These are planning estimates, not guarantees.

- host bootstrap: `1-2 hours`
- smoke-test asset download and render: `0.5-2 hours`
- custom preprocessing: `1-3 hours`
- static first-frame gate: `5-20 minutes`
- full foreground training on a `90-120` frame swing clip: `12-24 hours`
- review rendering and MP4 packaging: `1-3 hours`

The full-training estimate is an inference from the 4K4D README statement that full training can take a day or two, adjusted down because this demo uses a short foreground-only clip instead of a larger full-scene sequence.

## Risks And Required Mitigations

### Risk 1: Motion Blur On The Club

Mitigation:

- high frame rate
- fast shutter
- bright lighting
- club contrast enhancement
- reject bad footage before training

### Risk 2: Calibration Drift

Mitigation:

- fixed camera rig
- ChArUco capture before session
- automated reprojection QA
- hard stop if reprojection thresholds fail

### Risk 3: Mask Failure On Thin Club Geometry

Mitigation:

- controlled background
- background plates
- BackgroundMattingV2 fallback
- SAM2 manual rescue on short spans only

### Risk 4: Worker Build Instability

Mitigation:

- containerize
- pin repos
- avoid optional dependencies on the critical path
- verify smoke test before any custom capture work

### Risk 5: Training Completes But Output Is Visually Weak

Mitigation:

- do not train on full long session first
- trim to a single swing
- enforce static first-frame gate
- render held-out views before final novel-view packaging

## Research Benchmark Lane

After the primary path passes, Engineer B may run one benchmark lane:

- `Diffuman4D` on the same sparse-view session, if time remains

This is explicitly non-blocking and non-critical because:

- it adds an additional preprocessing stack
- it depends on Sapiens for custom keypoints
- its README does not present a complete open final 4DGS reconstruction path

The purpose is comparison, not delivery.

## Definition Of Done

The work is done when a TPM can clone the repo on an Ubuntu 24 box with Python 3.13, run:

```bash
./scripts/volcap/bootstrap_ubuntu24.sh
./scripts/volcap/smoke_test.sh
./scripts/volcap/run_golf_demo.sh inputs/golf/golfer_demo_001/session.yaml
```

and then review the final MP4s in `artifacts/golfer_demo_001/review/` without opening a notebook, editing config files by hand, or chasing missing model weights.
