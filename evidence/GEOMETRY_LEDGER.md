# Geometry ledger — control room existing conditions v0.1

Single source of truth: `model/solve_result.json` (regenerate with `python3 model/camera_solve.py`).
Frame: see `docs/COORDINATE_SYSTEM.md`. Units: metres. σ = 1-sigma from the least-squares covariance, scaled by the residual. Treat σ as a **relative** indicator; it does not include model-form error such as the symmetry assumption.

## Solved / labelled values

| Element | Value | σ | Class | Evidence | Independent cross-check |
|---|---|---|---|---|---|
| Room width W (X) | 10.34 | 0.19 | SCAN-LABELLED → solved | scan labels 10.51 (overhead), 10.38 (front view), used as prior 10.51 ± 0.15 | labels disagree by 0.13 among themselves |
| Room depth D (Y) | 8.10 | 0.19 | SCAN-LABELLED → solved | scan label 7.86 used as prior ± 0.15 | +0.24 vs label (1.2σ). Watch item |
| Low side ceiling at wall `hlo` | 2.23 | 0.09 | PHOTO-SOLVED | CR1 k2; beam geometry | scan label 2.12 m (vertical, location ambiguous) is within ~1σ |
| Beam underside / post top `hbb` | 2.02 | 0.05 | PHOTO-SOLVED | posts CR1/2/3 | — |
| Foot of sloped ceiling `hb` | 2.36 | 0.07 | PHOTO-SOLVED | far and gable walls | — |
| Flat central ceiling `hc` | **4.01** | 0.09 | PHOTO-SOLVED | beams, end walls CR1/2/3 | **scan label 4.07 m, NOT used in the solve** |
| Flat ceiling width `wc` | 3.49 | 0.09 | PHOTO-SOLVED | end-wall trapezoids | top/bottom width ratio 0.55 identical at both ends → vertical end walls, not a hip |
| Beam/post line inset `ds` | 1.94 | 0.07 | PHOTO-SOLVED | both sides, **symmetry assumed** | systematic residual on X=W side → possible asymmetry |
| Post Y (X=ds line) | 4.20 | 0.12 | PHOTO-SOLVED | CR1/2/3 | ≈ mid-depth |
| Post Y (X=W−ds line) | 4.23 | 0.12 | PHOTO-SOLVED | CR1/2/3 | ≈ mid-depth |
| Post / beam section | 0.14 / 0.19 | — | PHOTO-INFERRED | visual estimate | needs tape |
| Exterior entry door (gable) | X 4.72–5.58, head 1.96 | 0.10 / 0.07 | PHOTO-SOLVED | CR3 | 0.86 m wide = standard door ✔ |
| Gable clerestory | X 4.86–5.41, Z 2.76–3.85 | ~0.10 | PHOTO-SOLVED | CR3 | centred on gable as seen outside ✔ |
| Gable interior door | X 7.28–8.26, head 2.02 | 0.15 / 0.07 | PHOTO-SOLVED | CR3 | 0.98 m wide (wide for a passage door): check |
| Partition doorway (to intermediate zone) | X 4.57–5.66, head 1.92–1.99 | 0.10 | PHOTO-SOLVED | CR1, CR2 | centred on room ✔ |
| Long window, X=W wall (far end) | Y ≤ 6.39, sill 1.11, head 1.78 | 0.06–0.16 | PHOTO-SOLVED (partial) | CR1 | full length UNKNOWN |
| Gable side windows (2) | — | — | UNKNOWN (seen) | CR3, exterior | not yet solved |
| X=0 wall windows | — | — | UNKNOWN (seen) | CR1, CR3 | not yet solved |
| Wood stove + flue | — | — | UNKNOWN (seen) | CR1, CR2 | existing appliance; clearances matter |
| Wall/roof thickness, roof pitch, void above ceiling | — | — | **UNKNOWN** | — | interior slope ≈47° vs low exterior pitch → void likely |
| Floor construction / level | — | — | UNKNOWN | — | hallway tile at a different finish (CR3) |

## Camera solutions (photo matches)

| Photo | Points | RMS px | Max px | Camera (X, Y, Z) | Status |
|---|---|---|---|---|---|
| CR1 Control Room 1 | 24 | 5.9 | 14.9 | 5.25, 0.40, 1.52 | ✅ match |
| CR2 Control Room 2 | 15 | 7.8 | 19.3 | 5.21, 0.42, 1.55 | ✅ match (repeatability vs CR1) |
| CR3 Control Room 3 | 22 | 6.4 | 15.6 | 5.08, 7.95, 1.26 | ✅ match (camera at partition threshold) |
| WV Window view | 6 | — | — | — | ❌ **UNSOLVED**: zero redundancy after removing an ambiguous point |

Shared ultrawide focal length: 590 ± 16 px (EXIF predicts 601 px).

## Discrepancy register (open)

| ID | Observation | Likely cause | Resolution path |
|---|---|---|---|
| X1 | Right beam underside at far wall: +15/+19 px in CR1 and CR2 (same sign) | Room or low zones not symmetric; or beam depth differs from far fascia | Free `ds` per side once a third side view exists; native scan |
| X2 | Posts in CR3: 12–15 px | Residual ultrawide distortion near frame edge, or posts not exactly on beam line | Native scan; tape offsets |
| X3 | D solves 0.24 m longer than the 7.86 label | Label endpoints not on wall faces; or annotation bias | Native scan |
| X4 | Interior ceiling slope ≈47° vs shallow exterior roof | Void above ceiling (hypothesis) | Hatch inspection / scan |
| X5 | WV unsolved | Ambiguous identity of vertical element seen through glass | More control points or native scan |
