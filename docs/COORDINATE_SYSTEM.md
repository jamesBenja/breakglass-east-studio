# Model coordinate system and conventions

- **Units:** metres. Blender scene unit system METRIC, length unit METERS.
- **Origin (0,0,0):** control-room finished floor at the interior corner formed by the gable-end wall and the side wall on your **left** when standing in the gable entry door looking in.
- **+X:** across the building, toward the side wall with the long ribbon window seen in CR1 (right-hand side from the entry).
- **+Y:** along the building, from the control-room gable wall toward the interior partition, intermediate zone and live room.
- **+Z:** up.
- Interior faces are modelled; wall, roof and floor thicknesses are UNKNOWN until surveyed.
- Compass orientation: UNKNOWN (no site north established from the evidence yet). Do not infer sun paths.

## Blender collections
| Collection | Contents |
|---|---|
| `10_SCAN_LABELLED` | floor rectangle (extents from scan labels, adjusted by the solve) |
| `20_PHOTO_SOLVED` | walls, ceiling section, beams, posts |
| `30_PHOTO_INFERRED` | (empty in v0.1) |
| `40_OPENINGS` | doors and windows as dark panels 10 mm proud of the wall |
| `90_CAMERAS` | `CAM_CR1/2/3` solved photo cameras; `CAM_AXO_review` |

Every object has custom properties `evidence_class`, `source`, `sigma_m` and `note` (Blender: Object Properties → Custom Properties).

## Existing vs proposed
Existing-conditions files are named `existing_*`. Proposed design will live in separate `proposed_*` files or collections that *link* the existing shell and never edit it.
