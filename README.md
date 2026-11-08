# Breakglass East — Ways Mills Studio Conversion

Professional design-development project for converting the actual agricultural building at Ways Mills, Québec into a world-class production and recording facility.

## Status

- **Source archive:** collected in owner's Google Drive / local reference folder, not automatically public.
- **v0.6 3D viewer, layouts and renderings:** **REJECTED**. Do not reuse their geometry or equipment placement.
- **Current assignment:** reconstruct existing control room and camera-match it to actual photographs before proposing any studio fit-out.
- **v0.3 (Claude, draft for review, PR #1):** whole building from the native LiDAR scan; the actual Spectra Sonics console and both Geithain RL 901K modelled from owner tape measurements; proposed control room (stereo + 7.1.4 + screening), live room, support rooms, loft position; renders, plans and a build plan. Start here:
  - [docs/BUILD_PLAN.md](docs/BUILD_PLAN.md): phases, budget, decisions, next steps
  - [docs/CONTROL_ROOM_DESIGN.md](docs/CONTROL_ROOM_DESIGN.md)
  - [docs/LIVE_ROOM_LOFT_SUPPORT.md](docs/LIVE_ROOM_LOFT_SUPPORT.md)
  - [evidence/GEOMETRY_LEDGER.md](evidence/GEOMETRY_LEDGER.md)
  - `drawings/PR-101`, `drawings/PR-102`
  - `renders/design/`

  Owner review copies in Google Drive: folder "Breakglass East — Review Package (Claude, current: v0.4)" (Design & Build Plan Doc + Budget/Decisions/Next steps/Tape check Sheet, both v0.4 fireside + cinema).

  The existing shell is still under Gate 1 revision; the design was produced on owner instruction and is labelled PROPOSED throughout.
- **Agent coordination:** Claude Code implements on branches and creates PRs; ChatGPT independently reviews source fidelity and documentation via GitHub.

The project is intentionally **public**, and that is fine. Publish code, general specifications, review summaries and owner-approved images openly. Avoid exposing the private source photos / scans or confidential property details without owner approval.

## Starting Claude Code (already installed)

Clone this repository locally, then open it:

```sh
git clone https://github.com/jamesBenja/breakglass-east-studio.git
cd breakglass-east-studio
claude
```

Claude reads [CLAUDE.md](CLAUDE.md), then completes [Assignment 01](docs/FIRST_ASSIGNMENT.md) using [quality gates](docs/ACCEPTANCE_GATES.md).

## Original source evidence

The owner holds the complete Ways Mills source archive: exterior and interior photographs, labelled 3D-scan stills, scan-orbit video, loft/garage photographs, exact existing Sunny Suite Spectra Sonics and paired Geithain photographs, and Clark acoustic treatment salvage images. Claude is already connected to the owner's Google Drive ecosystem and must use that source access first, verify the exact source files, and maintain a structured evidence manifest. Stage only the files requiring local rendering into `inputs/originals/` (gitignored), if necessary; do not treat manual downloads as a required owner setup step. An orbit video alone is **not** a certified point cloud.

## Hard design decisions and dimensions

- No extra dividing walls; preserve continuous original roof geometry, post placement, openings, loft and garage access.
- Farm equipment remains in live room; grand piano, chamber recording and mobile acoustics must work around it.
- Control room contains the **actual Spectra Sonics console and BOTH actual Geithain mains**, once gear models and listening orientation have been independently verified.
- Calm minimal control room lighting / detailing; industrial agricultural live room; reuse Clark acoustic panels and wood where it performs.
- Indicative **scan-labelled** floor rectangles: control room approximately 10.51 × 7.86 m; live room approximately 11.81 × 12.88 m. These are not a complete as-built survey and do not locate windows/posts/loft elevations.

## Deliverable gate

Before a polished rendering, submit: sources-to-geometry ledger; annotated as-is plans/sections; three original-photo camera matches; valid editable Blender file; exact list of inferred measurements. Stop for design review if those cannot be demonstrated.

## Collaboration

See [GitHub process](docs/GITHUB_COLLABORATION.md). All commits and PRs remain reviewable by both connected assistants.
