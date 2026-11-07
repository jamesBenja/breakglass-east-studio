# Breakglass East — Ways Mills Studio Conversion

Professional design-development project for converting the actual agricultural building at Ways Mills, Québec into a world-class production and recording facility.

## Status

- **Source archive:** collected in owner's Google Drive / local reference folder, not automatically public.
- **v0.6 3D viewer, layouts and renderings:** **REJECTED**. Do not reuse their geometry or equipment placement.
- **Current assignment:** reconstruct existing control room and camera-match it to actual photographs before proposing any studio fit-out.
- **v0.1 existing-conditions control room (Claude, draft for review):** solver-based 3-photo camera match, Blender model, plan and sections. See [docs/STRATEGY_AND_ASSESSMENT.md](docs/STRATEGY_AND_ASSESSMENT.md), [evidence/GEOMETRY_LEDGER.md](evidence/GEOMETRY_LEDGER.md), [model/README.md](model/README.md). Gate 1 **not yet passed**.
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
