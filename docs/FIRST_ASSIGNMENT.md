# Assignment 01 — Reconstruct existing Ways Mills control room (no interior design yet)

## Scope
Produce an evidence-grounded existing-conditions model of the control room, linked to the overall existing roof/adjacent areas where genuinely supported. Do not copy any rejected v0.6 mesh. Do not put studio equipment in the first accepted geometry render.

## Inputs
Primary source: original photographs; dimensional scan screenshots/labels; scan orbit video; exterior photos, and legacy control-room equipment references. Access them FIRST using Claude's already-connected Google Drive ecosystem. Project index: https://docs.google.com/document/d/1RTL9yHimtZGz-gsyDRrONvW7okwdXZftuZAngoMyyLE/edit. Original archive: https://drive.google.com/drive/folders/1NfCB7MELSA7hZDa1-T1MAhVO0-TxBaR2. Actual Spectra Sonics/Geithain photos: https://drive.google.com/drive/folders/1cgxLtisp46ZwTy_axg0njd5UEju_JAzZ. If local bytes are technically necessary for Blender, stage them privately after reading Drive; do not assume that the owner needs to copy files manually. Previous v0.6 is **audit-only, invalid design base**.

## First actions
- Verify all available source originals and create asset manifest with filename, category, date if known, resolution and source ID.
- Determine whether actual mesh/point-cloud export exists; an orbit video is not equivalent to a measured 3D mesh.
- Analyze geometry, post locations, windows, doorway, roof slope/height, floor surface, material boundaries. Record known vs unknown dimensions.
- Establish a model coordinate system, datum, units (meters), controlled field/survey variables.
- Construct shell/columns/openings in Blender, with unknown coordinates parameterized and annotated.
- Set THREE camera poses to reproduce three ORIGINAL PHOTOS. Compare edge geometry and perspectives directly.
- Submit contact-sheet comparisons, existing plans/sections, .blend and code/script, and discrepancy table as PR.
- STOP at review gate. Do not start aspirational interior renderings.

## Reject automatically if
- Unexplained window/post/roof discrepancies in the camera matches.
- Fabricated dimensions are labelled measured.
- New walls/roof added, or loft/garage relationship contradicted.
- Missing evidence mapping, editable source, or comparison images.
- QA screenshots only show a generic room instead of the existing one.

## Review deliverable
One PR: `claude/01-existing-conditions`, descriptive before/after source comparison and list of unresolved dimensions requiring field measurement.

## Subsequent gate (not part of this first PR)
Model the actual legacy Spectra Sonics and both actual Geithains as independently verified equipment assets. No fabricated monitor geometry, missing speaker or reversed console.
