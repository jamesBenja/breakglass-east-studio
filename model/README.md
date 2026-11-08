# Existing-conditions model — how to reproduce

```bash
pip install bpy==5.2.3 numpy scipy pillow
```

```bash
python3 -I model/scan_analysis.py
```

```bash
python3 -I model/scan_measure_control_room.py
```

```bash
python3 model/camera_solve.py
```

```bash
python3 model/build_existing_shell.py
```

```bash
python3 model/make_drawings.py
```

```bash
python3 model/make_comparisons.py
```

```bash
python3 model/monitoring_geometry.py
```

```bash
BG_RENDER=1 python3 model/build_studio.py
```

```bash
python3 model/make_proposed_plans.py
```

| Script | Input | Output |
|---|---|---|
| `scan_analysis.py` | private native mesh `inputs/originals/scan/polycam_2022-10-24.glb` | `scan_frame.json` (axis transform) |
| `scan_measure_control_room.py` | private surface samples of the mesh | `scan_control_room_measurements.json` (numbers only) |
| `camera_solve.py` | `annotations/*.json` + scan priors | `solve_result.json` (fused, default), `solve_result_scan_fixed.json`, `solve_result_photo_only.json` (`BG_SOLVE_MODE=`) |
| `section.py` | solve + scan | the one asymmetric section used by every script below |
| `scan_openings.py` | private mesh samples | `scan_openings_control_room.json` (window reveals) |
| `scan_measure_building.py` | private mesh samples | `scan_building_measurements.json` (live room, middle zone, loft) |
| `independence_report.py` | solve modes | `independence_report.json` (scale-free photo-vs-scan check + held-out test; review G1-02) |
| `monitoring_geometry.py` | shell + owner tape measurements | `monitoring_geometry.json` (LP, RL 901K, console, 7.1.4, modes, SBIR) |
| `build_studio.py` | all of the above | `breakglass_east_v03.blend` (existing + actual equipment + proposed); `BG_RENDER=1` → `renders/design/*.png` |
| `make_proposed_plans.py` | all of the above | `drawings/PR-101`, `PR-102` |
| `build_existing_shell.py` | `solve_result.json` | `existing_control_room_v02.blend`, `renders/qa/clay_*.png` |
| `make_drawings.py` | `solve_result.json` | `drawings/EX-101/201/202*.svg` |
| `make_comparisons.py` | `solve_result.json` + private photo previews | `renders/qa/edges_*.png` (public); `inputs/private/comparisons/match_*.jpg` (private) |

- **Software verified:** Python 3.13, Blender 5.2.3 (`bpy`), Cycles CPU (48 samples, denoised; set `BG_SAMPLES` to change), scipy 1.x.
- **Render settings:** QA clay at 800×600, AgX view transform, 4 point lights at 1.7 m plus a dim grey world. Workbench/Eevee are unavailable in GPU-less containers.

## Method
`camera_solve.py` minimises the reprojection error of the annotated points over:
- the parametric, **asymmetric** tray-ceiling section `W, D, dsL, dsR, hloR, hbbL, hbbR, hbL, hbR, hc, wc, xf` and the post positions (`hloL` comes straight from the scan);
- one pinhole camera per photo (position, yaw/pitch/roll);
- one focal length per physical lens, with an EXIF 35 mm-equivalent prior of ±6 %;
- nuisance unknowns for opening positions.

**v0.2 (default `fused`)**: every section parameter carries a prior from the native LiDAR mesh (σ 0.03 m for directly measured walls and planes, 0.10 m for breakpoints read off the smoothed mesh profile), and the photos refine it. Two comparison modes are kept: `photo_only` (v0.1 behaviour: all heights free, scale from W/D) and `scan_fixed` (geometry frozen to scan, cameras only). A robust (soft-L1) loss is used. Annotations record the photo title, viewing note and per-point σ (pixels). Excluded views and points stay in the files with their reasons.

## Private inputs
Photos are read from `inputs/private/preview/<title>.jpg` (1600 px previews decoded from the Drive originals). `inputs/` is gitignored. Annotation pixel coordinates refer to these previews.

## Changing the model
The native mesh needs splitting to pass through the Drive connector (max ~6 MB per file). It is reassembled byte-exact (size + glTF header check) into gitignored `inputs/originals/scan/`.

Never hand-edit the `.blend` geometry. Change the annotations or the parameter definitions, re-solve and rebuild. The `.blend` is a build product kept for convenience (and review in the Blender GUI).
