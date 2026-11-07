# Geometry ledger: control room existing conditions **v0.2**

**v0.2 basis:** the **native iPhone-LiDAR mesh** (Polycam, captured 2022-10-24, exported by the owner 2026-11-07; 40,920 vertices, 31.1 × 14.0 × 6.2 m overall), **fused** with the three photo camera matches.

| File | Contents |
|---|---|
| `model/scan_control_room_measurements.json` | numbers read directly from the scan |
| `model/solve_result.json` | fused scan + photo solve |
| `model/solve_result_photo_only.json` | v0.1 photo-only solve, kept for comparison |
| `model/solve_result_scan_fixed.json` | cameras solved against the scan geometry frozen |

- **Frame:** `docs/COORDINATE_SYSTEM.md`. Units: metres.
- **σ:** 1-sigma from the least-squares solve; it does not include LiDAR systematic error (phone LiDAR: typically ±1–2 % over room scale, a few cm locally).
- **The mesh itself stays private** (`inputs/originals/scan/`, gitignored). Only derived numbers are committed.

## What the native scan changed

| Item | v0.1 (photos + screenshot labels) | **v0.2 (scan + photos)** | Why it changed |
|---|---|---|---|
| Width, wall to wall | 10.34 ± 0.19 | **11.25** | The 10.51 / 10.38 screenshot labels did **not** span wall to wall (visible on the overhead screenshot), and v0.1 used them as its scale. Cross-check: live-room width measured in the same mesh is 11.9 m vs its label 11.81 m, so the mesh scale is sound. |
| Depth | 8.10 ± 0.19 | **8.20** | The scan confirms the photo solve; the 7.86 label was short. |
| Flat ceiling | 4.01 ± 0.09 | **4.11 ± 0.03** | Scan 4.105, fused 4.113, photos agree. |
| Section symmetry | assumed symmetric | **asymmetric** | Discrepancy X1 from v0.1 is resolved (below). |

## Control-room values (v0.2, fused)

| Element | Value | σ | Class | Notes |
|---|---|---|---|---|
| Width W (wall to wall) | **11.25** | 0.03 | SCAN-MEASURED | side walls fit to 2.6 / 4.7 cm scatter |
| Depth D (gable to partition) | **8.20** | 0.03 | SCAN-MEASURED | |
| Flat central ceiling | **4.11** | 0.03 | SCAN-MEASURED + photos | scan 4.105; screenshot label 4.07 |
| Flat ceiling width | 3.54 | 0.06 | PHOTO-SOLVED (scan prior 3.30) | the decimated mesh rounds the edges; the photos see the beam lines |
| **Flat ceiling / building axis** | **X = 5.88** | 0.07 | SCAN + PHOTO | room mid-width is 5.62 → the axis is offset **+0.26 m** toward the long-window wall |
| Left low zone: depth / height | 2.58 / 2.25 | 0.08 / 0.03 | SCAN + PHOTO | |
| Right low zone: depth / height | 2.00 / 2.30 | 0.07 / 0.06 | SCAN + PHOTO | **0.58 m shallower than the left** |
| Beam underside (post tops), L / R | 2.08 / 2.10 | 0.04 | PHOTO-SOLVED (scan prior) | |
| Slope foot, L / R | 2.45 / 2.45 | 0.06 | PHOTO-SOLVED (scan prior) | slopes ≈ 45° |
| Posts (one per side): Y from gable | 4.24 / 4.30 | 0.06 | PHOTO-SOLVED | too thin to resolve in the decimated mesh; ≈ mid-depth |
| Exterior entry door (gable) | X 5.45–6.32, head 2.01 | 0.08 / 0.05 | PHOTO-SOLVED | centre **5.88** = building axis |
| Gable clerestory | X 5.58–6.15, Z 2.83–3.95 | 0.08 | PHOTO-SOLVED | centre **5.86** = building axis |
| Partition doorway | X 5.31–6.43, head 2.05 | 0.08 / 0.05 | PHOTO-SOLVED | centre **5.87** = building axis |
| Gable interior door | X 8.07–9.08, head 2.08 | 0.11 / 0.06 | PHOTO-SOLVED | leads to ? (UNKNOWN) |
| Long window, X=W wall | Y 4.45–6.48+, sill 1.15, head 1.86 | 0.05–0.08 | PHOTO-SOLVED (partial) | scan shows a deep reveal (~0.7 m) at about this height; full length still to read from the mesh |
| Floor level | control-room floor is **0.35 m above the live-room slab** | 0.02 | SCAN-MEASURED | |
| Roof structure / void above ceiling | — | — | **UNKNOWN** | the scan did not see above the finished ceiling |

### Interpretation (for design review, not a decision)
The doors, the clerestory and the ceiling share one axis at X ≈ 5.88. The side walls are **not** symmetric about it: the left wall is 5.88 m from the axis and the right wall 5.36 m. The left side may carry an added lining or a different wall build-up; this is an UNKNOWN to check in the field.

For monitoring, a listening axis on the building axis keeps the ceiling, front wall and doors symmetric but leaves the side walls 0.52 m asymmetric. That is a manageable acoustic condition (side-wall treatment can equalise it), but it has to be designed for, not ignored.

## Camera matches (fused model)

| Photo | Points | RMS px | Status |
|---|---|---|---|
| CR1 Control Room 1 | 24 | 6.0 | ✅ |
| CR2 Control Room 2 | 15 | 8.4 | ✅ (repeatability vs CR1) |
| CR3 Control Room 3 | 22 | 6.3 | ✅ |
| WV Window view | 6 | — | ❌ unsolved (zero redundancy) |

Overall fused RMS is **6.8 px**, against 6.3 px for the unconstrained photo-only fit. The scan geometry therefore explains the photographs about as well as free parameters do: an independent agreement between two capture methods.

Freezing the geometry to my first hand-read scan breakpoints (`scan_fixed`) gives 11.8 px. That is why the breakpoints carry 0.10 m priors rather than being fixed.

## Discrepancy register

| ID | Status | Note |
|---|---|---|
| X1 Right-beam residual (v0.1) | **Explained**: real asymmetry (scan) | |
| X2 Post residuals in CR3 (12–17 px) | Open | possible residual ultrawide distortion at the frame edge; tape-measure post positions |
| X3 D vs 7.86 label | **Explained**: the label was short; scan 8.19 | |
| X4 Void above ceiling | Open | not in the scan; hatch inspection needed |
| X5 WV unsolved | Open | low priority now that the scan exists |
| X6 Whole-scan bend | Open | control-room walls run 2.7° off the scan's whole-building average axis: either real skew or phone-LiDAR drift over 31 m. **Each room is aligned to its own walls**; do not chain rooms through the global frame without a check tape (outside length of the building). |
| X7 Screenshot labels | **Closed** | the labels are user-picked points, not wall-to-wall dimensions; superseded by direct mesh measurement |
