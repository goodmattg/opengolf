# 4D Volumetric Video Research Report

Date: 2026-04-04  
Research question: what are the current best technical options for producing a high-quality 4D volumetric video from input video of a single human subject, with the specific target of a golfer swinging a club and a user later being able to pan and zoom around the motion over time?

This is an expanded second-pass report. Compared with the first pass, this version broadens the scope across:

- older but still relevant human performance capture and neural rendering papers
- sparse-view and dense multi-view human-specific Gaussian methods
- monocular avatar methods with stronger priors
- relightable human capture and physically based avatar work
- human-object interaction methods
- blur-aware and event-guided methods
- volumetric video systems, compression, delivery, and long-video representations
- surveys, benchmarks, datasets, and toolkits

## Deliverables In This Folder

- Consolidated source inventory: [source_manifest_all.csv](./source_manifest_all.csv)
- Round-one inventory: [source_manifest.csv](./source_manifest.csv)
- Round-two inventory: [source_manifest_round2.csv](./source_manifest_round2.csv)
- Consolidated asset map: [asset_index_all.csv](./asset_index_all.csv)
- Downloaded PDFs: [papers/](./papers/)
- Saved project/article pages: [pages/](./pages/)

Current corpus size:

- 98 evaluated sources
- 96 local PDFs
- 98 local page/article copies

Two items in the corpus are page-only because I did not find an openly downloadable PDF during this pass:

- CloCap-GS
- Live4D

## Executive Summary

After a substantially broader pass, the main conclusion is unchanged but better supported:

1. If quality is the priority, calibrated multi-view human capture is still the best path.
2. Sparse calibrated multi-view is currently the best practical compromise.
3. Human-specific Gaussian or hybrid mesh-plus-Gaussian pipelines are the most promising class for this use case.
4. Monocular methods are improving quickly, but they are still materially riskier for a golf swing than sparse multi-view.
5. The golf club is not a detail. It is one of the hardest parts of the problem and should be treated explicitly.
6. Motion blur is not a nuisance variable for golf. It is one of the core constraints.
7. The strongest “current capabilities” picture is not captured by generic dynamic-scene 4DGS papers alone. The best human results come from systems that mix:
   - body priors
   - canonicalization
   - explicit meshes or UV parameterization
   - Gaussian appearance models
   - learned deformation
   - sometimes relighting and inverse-rendering machinery

If I had to choose one concrete technical direction today for a premium golf-swing artifact, it would be:

- sparse synchronized multi-view RGB capture
- short exposure and aggressive blur control at capture time
- a human-specific sparse-view Gaussian or hybrid mesh-plus-Gaussian method as the reconstruction core
- an explicit club/object branch
- optional relightable components only if lighting control or downstream editing matters

## Strongest Updated Takeaways

### 1. Dense Multi-View Still Sets The Quality Ceiling

The expanded pass strengthened this conclusion. The older NeRF-era quality leaders and the newer GS-era human systems line up on the same point: when you give the system dense synchronized views of a single performer, quality goes up sharply and uncertainty goes down.

Most relevant papers in this bucket:

- HumanRF
- HiFi4G
- DualGS
- RePerformer
- EVA
- UMA
- MeshAvatar
- Deep Relightable Textures
- The Relightables

What this means for golf:

- If you want the cleanest orbiting views during and after the swing, this regime is still the safest.
- This is also the regime where zooming in on cloth folds, hands, and body posture is most likely to remain convincing.

### 2. Sparse Multi-View Has Matured Into The Best Practical Option

The second pass turned up many more papers that support sparse-view capture than the first pass alone suggested. This family is now deep enough that it is not just one or two standout papers.

Most relevant sparse-view and generalizable human papers:

- Holoported Characters
- MetaCap
- DUT
- RoGSplat
- GIGA
- GPS-Gaussian
- GPS-Gaussian+
- Generalizable Human Gaussians for Sparse View Synthesis
- GBC-Splat
- CloCap-GS
- Relightable and Animatable Neural Avatar from Sparse-View Video
- Relightable Holoported Characters
- Diffuman4D

This family now covers multiple sub-approaches:

- optimized subject-specific sparse-view capture
- generalizable sparse-view human rendering
- clothed-human digitalization
- relightable sparse-view avatars
- diffusion-assisted sparse-view 4D consistency

What this means for golf:

- If you can place 4 to 12 synchronized cameras around the player and calibrate them well, the literature now strongly favors that path over monocular capture.
- This is the best balance between achievable artifact quality and feasible engineering effort.

### 3. Monocular Human Avatars Are Better Than Before, But Still Not The Quality Winner

The second pass expanded the monocular family considerably. It now includes not only the earlier HumanNeRF / MonoHuman / HUGS line, but also a richer set of 2024-2026 methods:

- High-Fidelity Human Avatars from a Single RGB Camera
- HiFECap
- GaussianBody
- GauHuman
- GaussianAvatar
- GoMAvatar
- HUGS
- RMAvatar
- Vid2Avatar-Pro
- WonderHuman
- Deblur-Avatar
- JOintGS
- AHOY
- Parametric Gaussian Human Model
- Large-scale Codec Avatars

What changed versus the earlier literature:

- stronger priors
- better generalization
- better handling of unseen regions
- more use of large-scale pretraining
- better photorealistic detail in some cases

What did not change enough:

- backside ambiguity
- self-occlusion
- thin-object capture
- fast motion blur
- confidence under arbitrary orbiting viewpoints

The benchmark paper Monocular Dynamic Gaussian Splatting is Fast and Brittle but Smooth Motion Helps remains an important sanity check. It is the right reminder that many monocular dynamic GS claims are still brittle on real, messy footage.

What this means for golf:

- Monocular can produce an impressive avatar.
- Monocular is still the wrong default choice if the requirement is the best possible golf-swing artifact.

### 4. Human-Object Interaction Papers Matter More Than They First Appear

The first pass already highlighted GASPACHO. The second pass reinforced that conclusion with:

- HOSNeRF
- HOGS
- Physics-aware Human-Object Rendering from Sparse Views via 3D Gaussian Splatting

This matters because golf is not a pure human-only problem. The club creates exactly the kinds of failures that human-only papers often hide:

- very thin geometry
- high angular velocity
- motion blur
- frequent occlusion by torso, hands, and legs
- rigid object semantics with tight human contact constraints

Inference from the combined corpus:

- treating the club as background is a mistake
- treating the club as just another body part is also a mistake
- the club should be modeled explicitly, ideally as its own object branch or with human-object contact constraints

### 5. Relighting And Physically Based Human Rendering Are More Relevant Than They Seem

At first glance, relightable humans may look orthogonal to a golf-swing viewer. After the broader pass, I think they matter for two reasons:

1. They often imply a stronger decomposition of geometry, material, and illumination.
2. They give a useful signal about which pipelines are trying to preserve physically meaningful appearance, not only photometric fit.

Relevant papers:

- Deep Relightable Textures
- The Relightables
- Relighting4D
- RANA
- Relightable and Animatable Neural Avatars from Videos
- Relightable and Animatable Neural Avatar from Sparse-View Video
- SGIA
- Interactive RAGA
- RnD-Avatar
- Relightable Holoported Characters
- HumanOLAT dataset
- SceneShine

Why this matters for golf:

- clothing sheen, shadows, and skin reflectance all become noticeable when the user pans and zooms aggressively
- outdoor or mixed lighting capture can otherwise cause unstable appearance over time
- if the eventual product wants scene insertion, compositing, or relighting, these papers become even more relevant

### 6. Blur And Fast Motion Are Core Constraints, Not Edge Cases

The broader pass strengthened the blur story. The most relevant methods now include:

- Deblur-Avatar
- BARD-GS
- Event-guided 3D Gaussian Splatting for Dynamic Human and Scene Reconstruction
- SceneShine

The literature supports a simple engineering conclusion:

- solve blur first in capture if you can
- only then ask reconstruction to solve what remains

For a golf swing, I infer the following from the combined evidence:

- use global shutter if possible
- use short exposure
- use enough light to support that exposure
- do not assume a standard handheld monocular video is a good input
- consider event cameras or hybrid event/RGB sensing if high-speed motion becomes a hard blocker

### 7. Explicit Mesh And Hybrid Avatar Methods Are Still Important

The expanded pass surfaced several methods that are not “pure Gaussian everything” and are still highly relevant:

- High-Fidelity Human Avatars from a Single RGB Camera
- MeshAvatar
- HR Human
- ExAvatar
- HAHA
- GoMAvatar

The pattern here is important:

- Gaussian splats are often used for appearance
- meshes remain useful for topology, control, rigging, deformation, and graphics compatibility

For golf, this is attractive because:

- the human body has known structure
- downstream animation and analysis may benefit from explicit surfaces
- object attachment and editing are easier when the human representation is not purely amorphous

### 8. The Latest Frontier Papers Improve Priors, Not Physics

The newest papers in the expanded pass include:

- Parametric Gaussian Human Model
- Large-scale Codec Avatars
- JOintGS
- AHOY
- Diffuman4D
- UMA
- SceneShine

These papers are important because they push:

- better priors
- larger-scale pretraining
- better generalization
- better sparse-input robustness
- better detail in expressive regions

But the frontier still does not remove the core golf constraints:

- club handling
- blur
- exact fast-motion geometry
- robust backside recovery from poor viewpoints

In other words:

- the latest papers reduce uncertainty
- they do not eliminate the hard physics of the capture problem

## Best Families For The Golf-Swing Use Case

### Best overall quality family

Dense or high-quality sparse multi-view human capture with subject-specific optimization.

Papers to study first:

- HumanRF
- HiFi4G
- UMA
- EVA
- RePerformer
- DualGS
- Holoported Characters
- DUT

### Best practical family

Sparse calibrated multi-view human-specific Gaussian or hybrid mesh-plus-Gaussian methods.

Papers to study first:

- DUT
- Holoported Characters
- MetaCap
- RoGSplat
- GIGA
- GPS-Gaussian+
- Generalizable Human Gaussians
- GBC-Splat
- Relightable Holoported Characters

### Best monocular fallback family

Monocular human avatars with strong priors or relightable/dynamic augmentation.

Papers to study first:

- Vid2Avatar-Pro
- RMAvatar
- WonderHuman
- Deblur-Avatar
- RnD-Avatar
- Relightable and Animatable Neural Avatars from Videos
- Parametric Gaussian Human Model
- JOintGS
- AHOY
- Large-scale Codec Avatars

### Best family for explicit club handling

Human-object interaction and physics-aware rendering.

Papers to study first:

- GASPACHO
- HOSNeRF
- HOGS

### Best family for relightable or editable premium output

- Deep Relightable Textures
- The Relightables
- Relighting4D
- RANA
- SGIA
- Interactive RAGA
- HumanOLAT
- SceneShine

### Best family for delivery after reconstruction

- DualGS
- V^3
- QUEEN
- Play4D
- LongVolCap
- Live4D
- LiveVV
- MetaStream
- FVV Live

## Updated Practical Recommendation

### If quality matters most

Use multi-view.

More specifically:

- 6 to 12 synchronized calibrated RGB cameras at minimum
- more if budget and space allow
- high resolution
- high frame rate if possible
- short exposure
- explicit club visibility in at least some views throughout the swing

### Reconstruction stack I would prioritize first

1. Sparse-view human capture core:
   - DUT
   - Holoported Characters
   - RoGSplat
   - GBC-Splat
   - GIGA

2. Add explicit human-object modeling:
   - GASPACHO or HOGS-style object branch

3. If lighting quality matters:
   - borrow relighting ideas from SGIA, RnD-Avatar, Relightable Holoported Characters, or SceneShine

4. If long playback or deployment matters:
   - compress/package with DualGS, V^3, QUEEN, Play4D, or LongVolCap-style methods

### Capture recommendations inferred from the literature

These are engineering recommendations inferred from the research corpus, not direct claims from any single paper:

- use global shutter or the best possible rolling-shutter conditions
- target roughly 1/1000 to 1/2000 second exposure if lighting allows
- do not rely on automatic exposure for the swing
- strongly prefer controlled background and stable lighting
- include camera viewpoints that keep the club separated from the torso in at least some frames
- collect a calibration sequence and a neutral-pose sequence
- if possible, capture a slower warm-up sequence in addition to full-speed swings to improve coverage and surface detail

## What I Would Actually Prototype

### Prototype A: sparse multi-view, quality-first

- Capture a synchronized sparse rig around the golfer.
- Start with DUT or Holoported Characters as the main reference.
- Add an explicit club branch inspired by GASPACHO or HOGS.
- Evaluate artifact quality under orbiting playback and close zoom.

This is my top recommendation.

### Prototype B: dense multi-view benchmark

- If a larger rig is available, benchmark against HumanRF, HiFi4G, UMA, EVA, and RePerformer-style quality.
- Use this as the quality ceiling reference against which the sparse setup is judged.

### Prototype C: monocular fallback

- If multi-view is impossible, use Vid2Avatar-Pro, RnD-Avatar, WonderHuman, Deblur-Avatar, and PGHM as the initial stack.
- Expect failure modes around backside views, club recovery, and blur.

## Highest-Signal Papers To Read First

If the goal is to narrow quickly to the most relevant papers, I would read these first:

### Directly relevant to the likely production path

- HumanRF
- HiFi4G
- Holoported Characters
- DUT
- MetaCap
- RoGSplat
- GIGA
- GBC-Splat
- GASPACHO
- HOGS
- Deblur-Avatar
- Relightable Holoported Characters
- UMA

### Critical monocular fallback papers

- Vid2Avatar-Pro
- RMAvatar
- WonderHuman
- RnD-Avatar
- PGHM
- JOintGS
- AHOY
- Large-scale Codec Avatars

### Important system and deployment references

- DualGS
- V^3
- QUEEN
- Play4D
- LongVolCap
- Live4D
- LiveVV
- MetaStream

## Open Problems That Still Matter For Golf

Even after the broader pass, these remain the main unsolved or weakly solved issues:

1. Thin fast objects like golf clubs.
2. Severe motion blur during the downswing and follow-through.
3. High-fidelity recovery of unseen views from monocular input.
4. Stable rendering of hands and club contact under close zoom.
5. Outdoor relighting and scene integration if lighting changes during capture.
6. A clean balance between explicit controllability and fully photorealistic rendering.

## Final Conclusion

The expanded literature search makes the recommendation more confident, not less:

- Do not default to monocular if the target is a premium golf-swing volumetric artifact.
- Use sparse or dense calibrated multi-view capture.
- Use a human-specific Gaussian or hybrid mesh-plus-Gaussian method.
- Model the club explicitly.
- Treat blur control as a capture requirement, not an afterthought.

The broadest reading of current capabilities is that the field is now strong enough to make a convincing free-view golf-swing artifact, but only if the input regime is aligned with the physics of the problem. The main technical gap is no longer “can dynamic human novel-view synthesis work at all?” The main gap is “can it still look excellent under sparse views, fast motion, a thin club, and close-up inspection?” Multi-view human-specific pipelines are currently the most credible answer.

## Inventory Notes

Use [source_manifest_all.csv](./source_manifest_all.csv) as the authoritative inventory. It includes:

- foundational pre-GS human capture papers
- 2024-2026 human Gaussian avatar papers
- relightable human papers
- human-object interaction papers
- blur and event papers
- delivery and streaming systems
- surveys, datasets, and toolkits

The consolidated asset table is [asset_index_all.csv](./asset_index_all.csv).
