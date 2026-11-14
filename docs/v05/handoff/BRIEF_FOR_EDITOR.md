# v0.5 presentation hand-off brief for a second editor (e.g. ChatGPT)

This brief is for anyone producing the **client-facing v0.5 presentation**. Claude produces the model, the analysis and every image. The editor's job is layout, editing and the final document. The editor must not change the design, any number or any image.

## Who does what
| Task | Owner |
|---|---|
| Geometry, acoustics, costs, drawings, all renders (interior and exterior) | Claude, in this repo (`model/`, `acoustics/`, `renders/`, `drawings/`) |
| Narrative, layout, typography, captions (shortened only), one native Google Doc + PDF | Editor |
| Fact-check of the editor's draft against this brief and the manifest; reply on the PR | Claude |
| Design decisions | Owner only |

## Inputs (read from GitHub, no downloads needed)
1. `docs/v05/handoff/IMAGE_MANIFEST.md` / `.json`: every image, with a raw URL pinned to a commit, a caption, the image kind and its provenance. ★ marks hero images.
2. `docs/v05/V05_ACOUSTIC_INTEGRATION.md`: design rationale, analysis, commissioning plan, owner decisions.
3. `docs/v05/CHANGELOG_v04_to_v05.md` and `docs/v05/UNRESOLVED.md`.
4. `acoustics/out/costs_v05.csv` and `acoustics/out/deployment_matrix.md`.
5. `docs/v05/presentation_v05.html`: Claude's reference layout. Content source, not a style to copy.

## Imagery rules (non-negotiable)
1. **Use the manifest images as they are.** You may crop them for layout as long as no labelled element is lost. Do not regenerate, repaint, upscale with generative fill, relight, colour-grade, add people or props, or "enhance" them.
2. **The realistic views are the `render-photo` images.** They come from the real model, so they are both realistic and true to the design. Use them instead of AI-generated imagery.
3. **No generated building imagery anywhere.** That covers exteriors, interiors, axonometrics and site views. The exterior renders show the real barn shape. Do not substitute an invented one.
4. **Optional mood images (only if you want them).** They go in one fenced appendix titled "Atmosphere studies — not design". Each one must sit next to the manifest render it was derived from, with the differences listed. Never use one on the cover or in a design section.
5. **Keep provenance on the page.** Every image keeps a short source line, e.g. "Model render, photo look (materials/lighting only)". Context such as lawn, trees and sky is labelled indicative.
6. **Drawings must stay legible.** Use full width with one drawing per page, or link the full-resolution PNG.

## Facts that must not change (quote exactly)
**Design state**
- v0.5 is PROPOSED. It evolves the approved v0.4 "fireside + cinema" design.
- Nothing is for construction. Acoustic figures are screening ranges, not predictions.

**Unchanged from v0.4**
- Envelope, roof, posts, openings, room divisions.
- The Spectra Sonics console and both Geithain RL 901Ks: listening geometry ±30°, 2.70 m from the baffle to the front wall.

**Room acoustics**
- Control room: 289 m³. EBU Tech 3276 target decay T_m = 0.36 s. Schroeder frequency ≈ 64 Hz.
- First reflections: 11 of 16 paths meet treatment. Of the other 5:
  - 2 are console-shadowed;
  - 1 is rear cardioid radiation at the front wall;
  - 3 are late (≥ 19.9 ms) and ≤ −10.7 dB, landing on glass.
- Decay-time ranges at 500 Hz in the control room: bare 1.00–2.34 s → Clark panels only 0.58–1.12 s → recommended v0.5 0.39–0.68 s.

**Salvage**
- Clark inventory: 74 counted units in 41 families.
- 71 allocated, 3 reserve/held, 0 over-allocated.
- ABS-014 is held as a possible duplicate of ABS-010.

**Lounge**
- Every lounge seat faces the stove glass.
- Stove clearance ≥ 0.92 m; 0.90 m is a placeholder pending the WETT/label value.
- 5–6 seats in cinema mode.
- A third fireside seat does not fit.

**Phasing and cost**
- Phase 1 is Geithain stereo only (owner decision, 14 Nov).
- Essential build: $37.3k–$112.5k ($41.0k–$129.4k with contingency).
- Later phase: $15.5k–$82k.
- Change from v0.4: +$2.0k / +$3.0k.

**Errata**
- The v0.4 overhead speakers were mis-aimed. v0.5 aims all four exactly at the listening position.
- The entry gable has **one** door. The white rectangle beside it is an interior electrical cabinet (owner, 14 Nov). Never show or describe a second front door. v0.4 images still show it, so don't use v0.4 exterior or rear views as current.

## Suggested structure (12 sections)
1. **Cover:** ★ `ext_entry_v05_photo` or `cr_front_v05_photo`. No generated image.
2. **The barn today and what stays:** the exterior set and the axonometric.
3. **What v0.5 changes:** the changelog table and matched v0.4/v0.5 pairs.
4. **Control room:** the photo views, then the phase 1 views.
5. **Acoustic concept:** ceiling halo, front wall, rear wall, LF traps (PR-501, 502, 505, ceiling render).
6. **Fireside lounge, corrected:** PR-506, fireside and fire-seat renders.
7. **Live room and farm mode:** piano, drums, farm, loft; PR-511.
8. **Salvage deployment:** the allocation table (summarised) and the link to the full matrix.
9. **Analysis and uncertainty:** the table from §3 of the rationale document, with confidence notes.
10. **Phasing and cost:** phase 1 vs the later phase.
11. **Commissioning C0–C6 and open items:** UNRESOLVED U1–U17, summarised.
12. **Appendix:** drawings at full size, the image manifest, and (optionally) fenced atmosphere studies.

## Deliverables and QA
**Deliverables**
- One native Google Doc with real headings, tables and inline images (not page screenshots), plus a PDF export of it.
- One QA ledger listing, for each image: manifest path, page, crop yes/no, and caption changed yes/no.

**Finishing up**
- Mark older editions SUPERSEDED rather than leaving duplicates.
- Post one comment on the v0.5 PR listing what was produced and any fact you could not reconcile. Don't silently "fix" it.
