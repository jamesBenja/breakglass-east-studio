# Breakglass East — browser walkthrough (v0.5)

A first-person walkthrough of the v0.5 design model in the browser (three.js r160).

- `python3 model/export_walkthrough.py` re-exports `studio_v05.glb` (+ a base64 copy for artifact hosting, git-ignored) and `views.json` from `model/breakglass_east_v05.blend`.
- `index.html` is the viewer. It is written as an artifact page body (the host adds the `<html>/<head>` skeleton).
- Modes: studio / cinema (screen down, armchair A in the rear row, lights dimmed) / farm (piano on its dolly under its cover, gobos nested, backline packed away) and the later-phase immersive speakers. The farm moves mirror `model/v05_treatment.apply_scenarios`.
- Every object carries its `evidence_class`; the viewer shows it for whatever is under the crosshair.
- Lighting is simplified real-time lighting (no ray tracing). Geometry is the same as the drawings and renders. Not for construction: the shell is a phone-LiDAR + photo reconstruction (±0.1–0.2 m).
- No private property data is exported (the property terrain exists only in the private fly-through build).
