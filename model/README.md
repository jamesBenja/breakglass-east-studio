# Existing-conditions model — how to reproduce

```bash
pip install bpy==5.2.3 numpy scipy pillow
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

| Script | Input | Output |
|---|---|---|
| `camera_solve.py` | `annotations/*.json` (hand-picked control points) | `solve_result.json` |
| `build_existing_shell.py` | `solve_result.json` | `existing_control_room_v01.blend`, `renders/qa/clay_*.png` |
| `make_drawings.py` | `solve_result.json` | `drawings/EX-101/201/202*.svg` |
| `make_comparisons.py` | `solve_result.json` + private photo previews | `renders/qa/edges_*.png` (public); `inputs/private/comparisons/match_*.jpg` (private) |

- **Software verified:** Python 3.13, Blender 5.2.3 (`bpy`), Cycles CPU (48 samples, denoised; set `BG_SAMPLES` to change), scipy 1.x.
- **Render settings:** QA clay at 800×600, AgX view transform, 4 point lights at 1.7 m plus a dim grey world. Workbench/Eevee are unavailable in GPU-less containers.

## Method
`camera_solve.py` minimises the reprojection error of the annotated points over:
- the parametric tray-ceiling section `W, D, ds, hlo, hbb, hb, hc, wc` and the post positions;
- one pinhole camera per photo (position, yaw/pitch/roll);
- one focal length per physical lens, with an EXIF 35 mm-equivalent prior of ±6 %;
- nuisance unknowns for opening positions.

W and D carry priors from the scan labels; **all heights are free**. A robust (soft-L1) loss is used. Annotations record the photo title, viewing note and per-point σ (pixels). Excluded views and points stay in the files with their reasons.

## Private inputs
Photos are read from `inputs/private/preview/<title>.jpg` (1600 px previews decoded from the Drive originals). `inputs/` is gitignored. Annotation pixel coordinates refer to these previews.

## Changing the model
Never hand-edit the `.blend` geometry. Change the annotations or the parameter definitions, re-solve and rebuild. The `.blend` is a build product kept for convenience (and review in the Blender GUI).
