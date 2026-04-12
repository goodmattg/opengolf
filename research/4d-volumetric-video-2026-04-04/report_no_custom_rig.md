# 4D Volumetric Video Research Report - No-Custom-Rig Constraint

Date: 2026-04-08  
Research question: given that data acquisition does not allow a custom capture rig, and the golf swing input will come from either a single monocular camera or multiple sensors from the same platform (for example an iPhone camera stack), what are the best current technical options for producing a convincing free-view golf-swing artifact, with the ranking biased toward both artifact quality and the ability to stand up a demo immediately?

This is a constrained follow-on report to `report.md`. It reuses the same 2026-04-04 literature corpus, but changes the recommendation logic in three important ways:

- custom multi-view rigs are out of scope for the primary recommendation
- sparse-view and dense multi-view papers are filtered out unless they are still useful as priors or negative controls
- implementation readiness now matters almost as much as paper quality

I also did a fresh source check on the most relevant public project pages and repositories on 2026-04-08 to verify which methods are actually usable now versus which are still mainly paper-level references.

## Constraint Reset

The original report was right on the science and wrong for this operational constraint.

Dense or sparse calibrated multi-view still sets the quality ceiling. That has not changed. What changed is that the ceiling is no longer actionable. If the input is limited to:

- one monocular camera, or
- multiple sensors from the same device platform

then the primary comparison class is no longer:

- HumanRF
- HiFi4G
- DUT
- Holoported Characters
- RoGSplat
- GIGA
- GPS-Gaussian+
- Diffuman4D
- 4K4D

Those methods remain quality references, but they are no longer the decision set.

The decision set is now:

- monocular human avatar methods with strong priors
- monocular mesh-plus-Gaussian methods
- monocular human-object methods
- same-platform sensor fusion methods that do not assume a custom external rig
- blur-aware monocular methods

## Executive Summary

1. Once custom rigs are removed, monocular human avatar methods become the primary family, not the fallback family.
2. Same-platform multi-sensor capture should be treated as an augmented monocular problem, not as a substitute for true sparse multi-view geometry.
3. The best immediate custom-video starting point is still the older `Vid2Avatar` codebase, because it explicitly ships a custom monocular video preprocessing path and demo assets, even though its visual ceiling is below the newest 2025-2026 Gaussian avatar papers.
4. The best quality-oriented upgrade path within the constraint is a monocular mesh-plus-Gaussian stack such as `RMAvatar` or `GoMAvatar`, with `JOintGS` as the strongest robustness-oriented research lane.
5. `Vid2Avatar-Pro`, `WonderHuman`, `AHOY`, and `PGHM` are high-upside papers, but they are not the safest day-zero delivery path as of 2026-04-08.
6. `4DGT` is the cleanest public same-device reference I found, but it is built around Project Aria style data and is not a drop-in iPhone golf solution.
7. Golf-club visibility and motion blur remain the dominant failure modes. No monocular paper actually removes those constraints.

If I had to choose one concrete direction today under this constraint, it would be:

- day-zero baseline on a locked-off monocular clip using `Vid2Avatar`
- quality upgrade on the same cleaned footage using `RMAvatar` or `GoMAvatar`
- explicit club masking or object branch inspired by `HOSNeRF`
- same-device depth or secondary sensors used only as auxiliary priors, not as the main geometry backbone

## Strongest Updated Takeaways

### 1. Multi-view Is Filtered Out, Not Refuted

The original report recommended sparse or dense calibrated multi-view because that is still the best way to get a premium orbitable artifact. That conclusion remains technically correct.

But it is not useful if capture is constrained to:

- a single phone camera
- a single phone plus same-device auxiliary sensors
- no external synchronized ring or arc of cameras

So the new report does not try to rescue multi-view recommendations. It removes them from the main ranking.

### 2. Same-Platform Sensor Arrays Are Not Equivalent To Sparse Multi-View

This is an engineering inference, not a direct quote from any one paper:

- an iPhone camera array has a tiny baseline compared with a room-scale sparse-view rig
- the lenses have different intrinsics and fields of view
- the capture APIs and timing guarantees are not the same as a calibrated synchronized external rig
- full-body golf-swing geometry, especially the club, is still underconstrained from such a small baseline

So same-device sensors should be treated as:

- depth priors
- segmentation priors
- photometric priors
- relighting or scene-composition aids

They should not be treated as a drop-in replacement for 4 to 12 surrounding cameras.

### 3. Day-Zero Practicality Re-Ranks The Monocular Field

The literature ranking and the delivery ranking are now different.

As of 2026-04-08, the public-code situation looks like this:

- `Vid2Avatar` has a public repo, demo assets, and an explicit custom monocular video preprocessing path.
- `GauHuman` has public code and very fast training claims, but the repo is still benchmark-dataset oriented.
- `RMAvatar` has public code, but the README is centered on `PeopleSnapshot`.
- `GoMAvatar` has public code and pretrained checkpoints, but again the setup is benchmark-oriented rather than custom-video oriented.
- `JOintGS` has public code, pretrained checkpoints, and strong robustness ideas, but the released instructions are centered on `NeuMan` and `EMDB`.
- `WonderHuman` has an official repo, but the README still lists major TODOs for preprocessing, rendering, and data release.
- `4DGT` has a polished repo, pretrained model download, and inference instructions, but those are built around Project Aria style `.vrs` data and Aria datasets.
- `PGHM` has a project page with a code button, but the linked GitHub repo was not reachable on 2026-04-08.
- `SceneShine` has a public GitHub repo, but as of 2026-04-08 it appears to be a one-commit placeholder with only a minimal README.
- `AHOY` has a project page but I did not find a public code link on the official page.

That moves some older methods up the delivery ranking and pushes some newer, stronger papers down.

### 4. Monocular Quality Is Now Good Enough For A Credible Demo

This is the main good news in the constrained setting.

Compared with the original report, the monocular family is now strong enough that a convincing demo is realistic if expectations are scoped properly:

- modest orbit range is more realistic than full unrestricted 360 inspection
- the frontal and 3/4 views will be materially stronger than the true backside
- body shape and clothing can look convincing
- the club remains the weak link unless modeled explicitly

In other words:

- a demo is viable
- a premium artifact is still hard
- the gap between those two outcomes is mostly about club handling, blur, and backside ambiguity

### 5. Mesh-Plus-Gaussian Methods Are The Best Fit Under This Constraint

The most promising constrained family is not generic dynamic scene 4DGS. It is monocular human reconstruction with explicit human structure:

- `RMAvatar`
- `GoMAvatar`
- `JOintGS`
- `Vid2Avatar-Pro`
- `WonderHuman`

Why this family fits golf better than generic dynamic monocular GS:

- the human body still benefits from an explicit surface or body prior
- deformation is easier to control
- novel-view consistency is better than purely amorphous dynamic splat fields
- there is a cleaner place to attach club-specific logic later

### 6. Same-Device Papers Matter, But Mostly As Specialized Side Lanes

The two most relevant same-device or mobile-adjacent references are:

- `4DGT`
- `SceneShine`

They matter because they prove that high-value reconstruction can be built around sensor data from one platform rather than from a custom room rig.

But they are still not the best direct delivery stack for an iPhone golf swing:

- `4DGT` is strongest when the data already looks like Project Aria processing output
- `SceneShine` is more about illumination-aware human-scene composition from mobile capture than about immediate golf-avatar delivery

I would keep both in the research lane, not the primary demo lane.

### 7. Blur And Club Handling Remain The Two Real Problems

The no-custom-rig constraint makes the original warning even more important:

- the golf club is too thin and too fast to trust to a generic human-only pipeline
- phone capture blur is now even more dangerous because we cannot lean on surrounding cameras to recover missing geometry

The most relevant filtered literature under this constraint is:

- `HOSNeRF` for single-video human-object-scene reasoning
- `Deblur-Avatar` for blur-aware monocular reconstruction
- `MoDGS` for casual monocular capture with depth priors

The practical inference is simple:

- solve blur at capture time first
- isolate the club in preprocessing if possible
- assume a pure human-only avatar method will underperform exactly at impact

## Filtered-Out Families

The following families were important in the original report but are intentionally de-prioritized here because they depend on multi-view geometry from multiple viewpoints around the subject:

- dense multi-view human capture
- sparse-view calibrated human capture
- sparse-view human-scene Gaussian methods
- diffusion-assisted sparse-view 4D human synthesis

Examples intentionally filtered out from the primary ranking:

- `HumanRF`
- `HiFi4G`
- `EVA`
- `UMA`
- `RePerformer`
- `DualGS`
- `DUT`
- `Holoported Characters`
- `MetaCap`
- `RoGSplat`
- `GIGA`
- `GPS-Gaussian+`
- `GBC-Splat`
- `Diffuman4D`
- `4K4D`

## Ranked Shortlist Under The New Constraint

### Best day-zero baseline on your own monocular golf clip

`Vid2Avatar` (legacy 2023 codebase, not the newer Pro paper)

Why it ranks first for immediate delivery:

- public repo
- explicit custom-video preprocessing path
- downloadable demo sequence and checkpoint
- built for monocular in-the-wild footage

Why it does not rank first on quality:

- older NeRF-based stack
- training is slow
- the visual ceiling is below the best newer Gaussian avatar methods

This is the safest "get a real custom clip through a published pipeline" choice.

### Best quality-first upgrade path within the constraint

`RMAvatar` and `GoMAvatar`

Why this pair is strongest:

- both are monocular
- both use explicit mesh structure plus Gaussian appearance
- both are better aligned with high-quality human rendering than generic casual-scene methods

Why they are not the day-zero winner:

- public docs are still benchmark-centric
- neither repo provides the same level of explicit custom monocular video onboarding that `Vid2Avatar` does

If the team can absorb some pipeline adaptation work, this is the best practical quality lane.

### Best robustness-first research lane

`JOintGS`

Why it matters:

- joint optimization of cameras, body, and Gaussians is exactly the kind of machinery that helps when monocular initialization is bad
- that is valuable for phone capture, imperfect framing, and in-the-wild footage

Why it is not the first delivery stack:

- released setup is centered on `NeuMan` and `EMDB`
- custom own-video path is not yet documented as cleanly as the paper title suggests

### Best fast-training baseline if we can adapt preprocessing

`GauHuman`

Why it matters:

- public code
- 1 to 2 minute training claim
- real-time rendering emphasis

Why it is not the default recommendation:

- dataset setup is centered on `ZJU-MoCap` and `MonoCap`
- there is no equally explicit custom-video path in the public instructions

This is the best "quick monocular Gaussian baseline" if we are willing to do some data engineering.

### Best same-device research lane

`4DGT`

Why it matters:

- public repo
- pretrained model on Hugging Face
- documented inference path
- closest match to a same-platform sensor philosophy

Why it is still not the primary recommendation:

- the released path is tied to Project Aria and Aria Digital Twin style data
- that is not the same as a standard iPhone golf clip

If the capture platform evolves toward a richer same-device sensor stack, this becomes more important.

### Best high-upside frontier papers that are not immediate delivery choices

- `Vid2Avatar-Pro`
- `WonderHuman`
- `AHOY`
- `PGHM`

These papers are highly relevant for future quality, especially unseen regions and robustness to poor viewpoints, but they are not yet the cleanest demo path:

- `Vid2Avatar-Pro` points to a public repo, but the linked code path appears to still be the older `Vid2Avatar` repository rather than a clearly separated Pro release
- `WonderHuman` still has major TODOs in the public repo
- `AHOY` has a project page but no public code link on the official site
- `PGHM` had a project-page code link, but the linked repository was not reachable on 2026-04-08

### Best club-specific reference inside the filtered set

`HOSNeRF`

Why it survives the filter:

- single-video setting
- explicit human-object-scene formulation

Why it is not the production backbone:

- three-stage training
- multi-GPU training examples
- older NeRF stack

It is most useful as a design reference for explicit club handling, not as the primary delivery engine.

## Practical Ranking Table

| Stack | Artifact quality upside | Day-zero demo fit | Own golf video readiness | Recommendation |
| --- | --- | --- | --- | --- |
| `Vid2Avatar` | Medium | High | High | Primary baseline |
| `RMAvatar` | High | Medium-Low | Medium-Low | Quality upgrade |
| `GoMAvatar` | High | Medium-Low | Medium-Low | Quality upgrade |
| `JOintGS` | High | Medium-Low | Low-Medium | Robustness research lane |
| `GauHuman` | Medium | Medium | Low-Medium | Fast baseline if we adapt preprocessing |
| `4DGT` | Medium-High | Medium | Low for iPhone capture | Same-device research lane |
| `WonderHuman` | High | Low | Low | Future-quality lane |
| `Vid2Avatar-Pro` | Very High | Low | Low | Future-quality lane |
| `HOSNeRF` | Medium | Low | Low | Club/object reference only |
| `SceneShine` | Medium | Very Low | Very Low | Mobile-specific concept only |

## Updated Practical Recommendation

### If we need a reviewable demo as soon as possible

Use a monocular pipeline first, not a same-device multi-sensor experiment.

More specifically:

1. Capture a clean tripod-mounted phone video with locked exposure and focus.
2. Run `Vid2Avatar` as the first end-to-end custom clip baseline.
3. Use the output to validate:
   - mask quality
   - body prior stability
   - orbit range that still looks believable
   - failure modes around the club
4. Only then upgrade to `RMAvatar` or `GoMAvatar`.

### If artifact quality matters more than fastest integration

Use:

- `RMAvatar` or `GoMAvatar` as the reconstruction core
- `JOintGS` as the fallback if camera and body initialization are unstable
- `HOSNeRF` ideas for explicit club handling

This is the strongest constrained path that still has public code behind it.

### If we must use multiple sensors from one device

Treat that setup as an auxiliary-prior problem:

- use one lens as the main image stream
- use any available depth or segmentation as additional supervision
- do not architect the pipeline around sparse-view triangulation assumptions

The literature analogs here are:

- `4DGT`
- `SceneShine`
- `MoDGS`

But I would not make them the first milestone unless the device stack already exports data in a clean, synchronized, developer-friendly format.

## Capture Recommendations Inferred From The Literature

These are engineering recommendations inferred from the literature and the verified repo states, not direct claims from any single paper:

- use a locked-off phone on a tripod or rigid mount
- prefer side or slight 3/4 view over head-on framing
- use 120 fps minimum if the phone supports it cleanly
- use the shortest exposure the lighting allows
- lock exposure, focus, and white balance
- use a clean background and bright light
- add high-contrast tape or markers to the club if permitted
- capture a short neutral-pose or slow-turn clip before or after the swing if possible
- if the app can export depth, masks, or lens metadata, keep them
- do not expect an unrestricted 360 orbit to hold up on a single-swing monocular clip

## What I Would Actually Prototype

### Prototype A: day-zero custom-video baseline

- input: one locked-off monocular iPhone swing clip
- stack: `Vid2Avatar`
- goal: get a real custom clip through a published pipeline with minimal research surgery

This is my top recommendation for immediate momentum.

### Prototype B: quality upgrade on the same footage

- input: the same cleaned clip and masks
- stack: `RMAvatar` first, `GoMAvatar` second
- goal: improve human detail, stability, and orbit quality without changing acquisition

### Prototype C: robustness lane

- input: the same clip
- stack: `JOintGS`
- goal: test whether joint camera/body optimization helps with monocular instability and in-the-wild framing errors

### Prototype D: explicit club experiment

- input: the same clip plus manual or semi-automatic club masks
- stack: monocular human backbone plus `HOSNeRF`-style human-object decomposition
- goal: reduce club disappearance and hand-club collapse near impact

### Prototype E: same-device sensor experiment

- input: phone RGB plus any exported depth or auxiliary sensor stream
- stack: `4DGT` or `SceneShine` style ideas
- goal: determine whether auxiliary same-device sensing is worth the engineering cost

This is not a first milestone. It is a side lane.

## Highest-Signal Papers And Repositories To Read First

### For immediate delivery

- `Vid2Avatar` repo and custom-video preprocessing path
- `RMAvatar` repo
- `GoMAvatar` repo
- `GauHuman` repo

### For robustness and future quality

- `JOintGS`
- `Vid2Avatar-Pro`
- `WonderHuman`
- `AHOY`

### For same-device or mobile-adjacent thinking

- `4DGT`
- `SceneShine`
- `MoDGS`

### For club-aware design

- `HOSNeRF`

## Open Problems That Still Matter For Golf

1. Thin fast objects like golf clubs under monocular capture.
2. Motion blur during downswing and impact.
3. Backside and unseen-surface recovery from a single short clip.
4. Stable hand-club contact under aggressive zoom.
5. Clean use of same-device auxiliary sensors without pretending they are a sparse-view rig.
6. The gap between a credible front/3-4-view demo and a truly premium unrestricted orbitable artifact.

## Final Conclusion

Under the no-custom-rig constraint, the recommendation changes materially:

- do not spend time optimizing a sparse-view external-rig plan
- treat the problem as monocular or augmented-monocular from the start
- use `Vid2Avatar` first if the goal is an immediate custom-video demo
- move to `RMAvatar` or `GoMAvatar` for better artifact quality on the same footage
- keep `JOintGS` as the best robustness-oriented research lane
- treat `4DGT` and `SceneShine` as same-device research references, not the default delivery path
- model the golf club explicitly if the artifact needs to survive inspection near impact

The constrained reading of the current field is that a convincing golf-swing free-view demo is realistic now from monocular capture, but only if we optimize for the real bottlenecks:

- preprocessing and masks
- locked capture and blur control
- explicit human priors
- explicit club handling
- realistic expectations on orbit range

The main question is no longer "can a monocular avatar demo work at all?" The main question is "which monocular path gives us a real custom-video demo fastest without painting us into a quality dead end?" Today, the answer is:

- `Vid2Avatar` for immediate delivery
- `RMAvatar` or `GoMAvatar` for the first quality upgrade
- `JOintGS` as the best next research bet when robustness becomes the blocker

## Verified Public Implementation Notes

Source checks below were performed on 2026-04-08.

- `Vid2Avatar` repo README includes demo data, checkpoints, and a `Play on custom video` section: <https://github.com/MoyGcc/vid2avatar>
- `Vid2Avatar-Pro` project page links the public code button to the same `Vid2Avatar` repo: <https://moygcc.github.io/vid2avatar-pro/>
- `RMAvatar` public repo: <https://github.com/RMAvatar/RMAvatar>
- `GoMAvatar` public repo: <https://github.com/wenj/GoMAvatar>
- `GauHuman` public repo: <https://github.com/skhu101/GauHuman>
- `JOintGS` public repo and checkpoints page: <https://github.com/MiliLab/JOintGS>
- `WonderHuman` public repo, but README still lists TODOs for preprocessing and rendering: <https://github.com/wyiguanw/WonderHuman>
- `4DGT` public repo with install script, pretrained models, and Aria inference path: <https://github.com/facebookresearch/4dgt>
- `HOSNeRF` public repo: <https://github.com/TencentARC/HOSNeRF>
- `SceneShine` public repo exists, but the repo appears minimal as of this date: <https://github.com/XuqianRen/SceneShine>
- `AHOY` official project page: <https://miraymen.github.io/ahoy/>
- `PGHM` official project page: <https://pengc02.github.io/pghm/>
- `MoDGS` public repo, but README still lists missing training and self-data instructions: <https://github.com/MobiusLqm/MoDGS>
