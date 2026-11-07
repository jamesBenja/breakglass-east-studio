# PROJECT LAUNCH — Breakglass East | Existing-conditions reconstruction and acoustic-led architecture

## Mission
Act as an integrated architecture, architectural-visualization, acoustics, and technical-studio design team. This is **design development for a real Ways Mills agricultural building**, not a generic recording-studio visualization. Owner expects best-in-class visual clarity, geometric honesty, studio workflow, and professional technical discipline. The output must permit expert review and future contractor coordination; no AI model is a licensed architect or acoustician or replaces field survey.

Read this with `CLAUDE.md`, `docs/FIRST_ASSIGNMENT.md`, `docs/ACCEPTANCE_GATES.md`, and the Drive project index. Earlier v0.6 geometry/overlay/renders were rejected. Do not patch them.

## Independent challenge and revised strategy — MANDATORY at project kickoff
Before committing to the prescribed phase sequence, critically evaluate the *project plan itself*, the source evidence, the modelling/rendering toolchain, the handoff arrangement, and the intended deliverables. Treat previous assistant plans as hypotheses, not instructions to obey unquestioningly.

Recommend the best professional approach even if it differs substantially from this document. Explicitly consider whether a single integrated site survey/model, photogrammetry/LiDAR export, camera calibration, measured console and speaker geometry, or a professional acoustician-led monitoring layout should precede the currently proposed control-room-only model.

Your initial report must contain: (1) weaknesses in the proposed plan; (2) a recommended revised workflow with milestones, prioritized technical risks, and quality gates; (3) viable alternatives with tradeoffs in speed, accuracy, cost and final visual quality; (4) a list of work that should be stopped, deferred or reassigned to a qualified architect/acoustician; and (5) a preferred approach with a reasoned justification.

**Authority:** You are free to reorder tasks, replace modelling/rendering methods, and challenge assumed room orientations. You do not need to preserve the current workflow for the sake of agreement. Flag any fundamental change to project goals, building constraints, cost or ownership decisions for owner review. Continue with evidence collection and safe reversible work while reviewing strategy; do not build an elaborate model on a questionable base.

## Source-first working contract
1. Discover and test the connected Google Drive tools in this **Code session**. Use the complete Ways Mills original photographs, 3D scan screenshots, scan orbit video, existing roof/exterior shots, loft/garage views, Clark salvage, and the **actual Sunny Suite Spectra Sonics console and BOTH Geithains**. Create an asset index and grouped contact sheets. Do not claim file access until concrete files are retrieved. If a connector is unavailable in this session, record exact connector/tool and minimally scoped remedy.
2. Inspect actual data format. Survey/scan-labelled floor rectangle `control approximately 10.51 × 7.86 m` and `live approximately 11.81 × 12.88 m` are approximate anchors, not a complete survey. A scan orbit video is not a real point cloud. Seek original CAD/3D export if available, but do not fabricate it.
3. Evidence register: each modeled element must have source filename/view, numeric evidence where available, coordinate axis, confidence `measured/scan-labelled/photo-inferred/proposed/unknown`, and uncertainty. Do not invent walls, ceiling volumes, post locations, windows, garage geometry or loft extent.

## Design mandate — retain throughout, but do not jump ahead of shell validation
- Preserve **the actual continuous roof, same roof height across the building**, existing walls, openings, posts, existing loft, agricultural equipment/garage route; **no new partitions**.
- Quiet Light control room, highly restrained Turrell/minimal and aspirational Miraval-level architectural detailing, reusing Clark wood/panels after acoustic suitability checks.
- Centre the **actual Spectra Sonics console** and **both actual Geithain speakers** on a credible stereo listening axis; fully symmetric monitoring geometry, verified facing/orientation and realistic equipment proportions; account for patch, outboard, racks, hybrid analog/digital workflow, screen/viewing position, future immersive/cinema system.
- Farm Industrial live room accommodates machinery in realistic storage/operating clearance when studio unoccupied, plus concert grand, strings/chamber ensembles, flexible recording gobos and the existing loft; ensure noise/fumes/safety separation.
- Planning must include acoustics/isolation, reflection control and LF strategy, quiet HVAC, structural/loading, power/audio/data and acoustician/architect/MEP review gates. Do not invent NRC/STC/RT figures as measured performance.

## First deliverable: substantive visual reconstruction, not just a plan to plan
Produce a `claude/01-existing-conditions` pull request containing:
A. A concise 1–2 page independent audit: failures in v0.6, source coverage, design constraints, three most material uncertainties, reconstruction method, real execution limits and whether Blender is usable in this cloud environment.
B. A source contact sheet with actual control, live, roof, loft/exterior and gear photos. Keep non-public image bytes in Drive/private workspace rather than committing them to a public repo without owner consent. Provide safe evidence index in repo.
C. A Blender-based (or equivalent editable professional 3D) existing-conditions model for the actual CONTROL ROOM with floor, walls, ceiling shape, documented posts, openings and windows. Represent uncertain features as labelled provisional geometry, never false measured facts. Coherent units, origin, naming/collections, parametric script.
D. **At least THREE matched camera comparisons**: original room photo beside render/wireframe from corresponding camera. Assess differences in posts, roof, openings and perspective. Acceptable for the first milestone to show unsolved discrepancies clearly; NOT acceptable to conceal or relabel them.
E. A dimensioned schematic plan and two corresponding sections (measured vs inferred legend, clear disclaimers) generated consistently from the model.
F. A geometry acceptance table and measured-items request prioritised by impact. Include the equipment reference inventory and initial geometric requirements for the later actual console plus two Geithains. Do not insert any fake gear into existing-conditions room model.
G. Reproducible scripts/project, renders, and a minimal README: software versions, commands to regenerate, changed paths and tests performed. Commit on feature branch and open one PR.

## Acceptance and stop rules
- Never reuse rejected v0.6 meshes as foundation.
- Avoid displacing source inspection with generic text, concept boards, fake renders or generic library equipment.
- Do not mark a model 'accurate as-built' until independently surveyed; use 'photo/scan-constrained reconstruction' where appropriate.
- If **source access** or **Blender execution** is genuinely blocked, still commit the audited evidence/source ledger, reproducible draft model or scripts and honest blocker, with a short path to resolution.
- Stop after the evidence-backed existing-shell PR for owner/independent review. Do NOT spend resources on photorealistic aspirational interiors before shell quality gate passes.
- Don't change Drive originals or push private source files into public GitHub.
