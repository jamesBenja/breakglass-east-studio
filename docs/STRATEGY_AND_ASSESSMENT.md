# Independent assessment and recommended strategy — Breakglass East

*Claude Code, session of 7 Nov 2026. Branch `claude/tender-fermi-0b6nnv`. Written after reading every repo doc, the Drive project index, enumerating all source folders, retrieving 26 original files and solving three photo camera matches. Recommendations marked **[OWNER DECISION]** change priorities or direction and need your approval before I act on them.*

> ### UPDATE v0.2: native scan received
> The owner exported the Polycam LiDAR mesh (glTF, 9.55 MB). It was transferred in three parts, reassembled byte-exact and verified. Consequences:
>
> - **The control room is 11.25 m wide, not 10.5 m.** The screenshot label was not a wall-to-wall dimension, and v0.1 inherited it as its scale. The mesh scale is cross-checked by the live-room width (11.9 m measured vs 11.81 m label).
> - **Depth 8.20 m and flat ceiling 4.11 m** confirm the v0.1 photo solve (8.10 m, 4.01 m).
> - **The section is asymmetric.** The left low zone is 2.58 m deep and the right 2.00 m. The doors, clerestory and flat ceiling share a building axis at X = 5.88 m, offset 0.26 m from the room's mid-width. This explains v0.1's systematic residual (discrepancy X1).
> - **The scan geometry fits the photographs** (fused RMS 6.8 px vs 6.3 px photo-only), so two independent capture methods agree.
> - **Loft (first read, one slice):** it is one roof-space attic about 14 m long over the intermediate zone and part of the live room. Its deck is about 2.55 m above the control-room floor, with roughly 2.0–2.5 m headroom at the ridge falling to nothing at the eaves. A full loft and live-room read is the next scan task.
> - **The live-room slab is 0.35 m below the control-room floor.**
>
> The details are in `evidence/GEOMETRY_LEDGER.md`. Sections A–E below are the original assessment; items now superseded are noted in the ledger.

---

## A. Independent project assessment

### What the existing strategy gets right
- **Existing conditions before design, and the v0.6 rejection.** v0.6's failures were *process* failures, not modelling-skill failures: it never tested geometry against a photograph. The gate structure in `ACCEPTANCE_GATES.md` is sound.
- **Evidence classes.** The SURVEYED / SCAN-LABELLED / PHOTO-INFERRED / PROPOSED / UNKNOWN split is the right discipline. I kept it and enforce it in the model through custom properties on every object and colour-coded drawings.
- **Real equipment, not stand-ins.** Correct. The photographs show this matters more than anyone realised (see below).

### What is wrong or missing

1. **The most valuable source asset hasn't been requested: the native LiDAR scan.** The six "3D scan" files are *screenshots and a screen-recording of a textured mesh* inside an iPhone LiDAR app. The app UI is visible (Ruler / Automatic / Floorplan-PRO, export and download icons). The front view also shows the ceiling was captured. Apps of this kind export OBJ/GLB/PLY/point cloud in under a minute, and nothing like that exists anywhere in Drive (I searched for obj/ply/usdz/glb/las/e57/gltf/fbx/dae/stl). Every prior version, and Assignment 01 itself, was built on reading numbers off screenshots. One export would turn the whole building — roof void, loft, intermediate rooms, openings — from inference into measured mesh geometry at roughly ±1–3 cm (phone LiDAR). **This is the single highest-leverage action in the project.** It costs the owner about five minutes.
2. **The scan already holds more measurement than was used.** The front view carries **4.07 m and 2.12 m vertical** labels plus a second width reading (**10.38 m** next to 10.51 m). v0.6 declared heights "unmeasured." My photo solve, which never used the 4.07 label, independently gives the flat ceiling at **4.01 ± 0.09 m**. The two readings of the same width differ by 0.13 m, which tells you the precision of a screenshot label (about ±1 %).
3. **The equipment is smaller than everyone assumed.** The actual Spectra Sonics is a **compact-frame console** (about three module bays with a yellow meter bridge, on a timber table base) flanked by two angled timber outboard-rack wings. The two Geithains are free-standing cabinets on floor stands, not soffit-mounted. Every prior layout and render treated the console as a large-format desk, so the control room has much more room and far more layout freedom than earlier sheets implied. The equipment models still need tape-measured dimensions before Gate 2 (see `evidence/MEASUREMENT_REQUESTS.md`).
4. **Two building facts change the design brief.**
   - **Control room ↔ live room have no line of sight.** An intermediate zone of rooms and a corridor lies between them, and no partition walls may be added or removed. Talkback, cue, video monitoring and tie-lines are therefore *core infrastructure*, not extras. This should be a stated design decision, not a surprise later.
   - **The "loft" is a floored roof void,** not a mezzanine. The photos show OSB decking over the live-room ceiling joists, exposed rafters and polythene/insulation. The joists visible under it are framed for an attic, not for habitable floor load. A bedroom there means joist reinforcement, headroom under a shallow roof, a code-compliant stair and egress, and fire separation from a room full of machinery and fuel. I'd treat the bedroom as **low-probability without major structural work** and protect only the cheap things now: don't block a future stair location, and run a spare conduit.
5. **The roof/ceiling relationship is unresolved, and it matters.** The interior sloped ceiling planes solve to roughly 47°. From outside the roof reads as a low pitch. Both can't be the roof surface, so there is very likely a **void above the control-room ceiling** (as in the live room). If confirmed, that void is the best route for quiet HVAC ducts and cable, and a possible home for low-frequency absorption — or it is a fire/insulation issue. One look through a hatch (or the native scan) answers this.
6. **Process gaps.** Assignment 01 confines work to the control room. I agree for *design*, but not for *capture*: the scan export captures the whole building at no extra cost, and the loft, roof and HVAC routes are all cross-room questions. Also, no acoustic-measurement step is planned before design. A day of measurements in the empty building (RT60 and background-noise survey, especially machinery, road and HVAC) costs very little and changes isolation decisions.
7. **What's overlooked in construction, MEP, code and logistics** (none of these is covered by the current docs):
   - **Agricultural land-use (CPTAQ)** and municipal zoning for commercial studio use. This is already in the index but must be resolved **before** design spend.
   - **Wood-stove clearances** in the control room.
   - **Electrical service size** and a dedicated technical-power distribution designed by a licensed electrical engineer/electrician, fully **bonded per the Canadian Electrical Code**. This is a star-topology technical ground that remains bonded to the building's grounding electrode, never an isolated or unbonded earth (review G1-09).
   - **Fuel and exhaust management** for machinery parked in a room with a grand piano.
   - **Humidity control** for a piano and an analog console in a rural Québec barn (winter RH below 20 %).
   - **Snow loads** if heavy acoustic ceilings are hung from existing framing.
   - **Console transport** (a compact frame is good news here).

### Should the whole building be reconstructed before individual rooms?
**Capture the whole building, design room by room.** Measured capture of the whole envelope (scan export plus a short field check) is cheap and prevents the room-to-room inconsistencies that sank v0.6. Design detail should still start with the control room, because it carries the most risk.

### Is Blender the right platform?
For this team — AI agents writing reproducible scripts, reviewed through GitHub — **yes, as the authoring and visualisation core, but not alone:**

| Need | Recommended tool | Why |
|---|---|---|
| Measured geometry | Native LiDAR export (OBJ/PLY) → CloudCompare/Blender for plane fitting | Turns inference into measurement |
| Parametric existing + proposed model | **Blender via Python (`bpy`)**, as now | Scriptable, diffable, runs here (verified: Blender 5.2.3) |
| Photo camera matching | Our own solver (this PR); fSpy is an alternative for single views | Multi-view, uncertainty-aware, reproducible |
| Final photoreal renders | **Blender Cycles on a GPU machine** | This container is CPU-only; production stills need a GPU or render farm |
| Construction drawings | Blender-generated DXF/SVG now → **the architect's Revit/ArchiCAD/AutoCAD** at permit stage | Licensed professionals will want their own tools |
| Acoustic modelling | Room-mode/SBIR calculators now; **the acoustician's tools** (e.g. EASE/ODEON-class) at design development | Not something to fake |

SketchUp or Rhino add nothing material here, and Revit is premature until a licensed architect takes the drawings.

### Should acoustics determine the control-room layout before detailed modelling?
**Yes, with a narrow scope.** Once the shell is measured, a short acoustic orientation study (room modes, speaker/listener SBIR, first reflections, symmetry against posts and openings) should choose the console axis **before** any interior modelling. My solved shell already lets me screen the options (section D). The final call belongs to a studio acoustician.

### Immersive and screening
Stereo first is correct. But an immersive (e.g. 7.1.4) plan needs **height-speaker positions** on a ceiling that is only 2.2 m at the sides and 4.0 m in the centre. That constrains the immersive layout geometrically, so **reserve the infrastructure** (conduit, rigging points, blocking) in phase 1 even though the speakers come later. A large projection screen on the front wall conflicts with free-standing Geithains on stands. An acoustically transparent screen or a retractable screen is a decision for **[OWNER DECISION]** after Gate 2.

### Is enough of the building being preserved?
The constraints already prevent invention. The bigger risk is the reverse: an isolated "room within a room" control room would hide the very tray ceiling, posts and windows you want to keep. My **working hypothesis** is that isolation can come from the envelope and door/glazing upgrades plus quiet MEP, not from new inner walls, which also respects the no-new-partitions rule. *(Review G1-09: this stays a hypothesis until a background-noise survey, an isolation target and the acoustician's review exist.)* Expected outside noise in a rural setting is low; the machinery in the live room is the real neighbour, and it is off during sessions.

### What needs licensed professionals
| Item | Who |
|---|---|
| Measured as-built survey (if the scan export is unavailable or insufficient) | Building surveyor or scanning firm |
| Loft loading, any hung acoustic ceiling, beam/post adequacy, snow load | **Structural engineer (OIQ)** |
| Change of use, egress, fire separation (machinery and fuel next to a studio), any bedroom | **Architect (OAQ)** + municipality / CPTAQ |
| Isolation targets, monitoring geometry sign-off, treatment design, HVAC noise criteria | **Studio acoustician** |
| Electrical service, technical power and grounding; HVAC design | Licensed electrical/mechanical engineers or master electrician |

---

## B. Recommended professional workflow

```
0  EVIDENCE     native scan export + field check list  ──►  measured shell (whole building)
1  SHELL        Blender parametric shell, re-solved against scan + photos (Gate 1)
2  EQUIPMENT    tape-measured console + 2 Geithains + racks modelled (Gate 2)
3  ACOUSTIC     orientation study: modes / SBIR / reflections / posts / openings
                → acoustician review → owner selects axis  [OWNER DECISION]
4  DESIGN       control room fit-out, live-room modes, MEP routes in the solved shell
5  VISUALISE    Cycles GPU renders from the SAME model (labelled APPROVED GEOMETRY vs PROPOSAL)
6  DELIVER      drawings + cost plan + survey/RFI register → architect / engineers
```

How this differs from the current plan:
1. **Step 0 is new.** Ask for the native scan before any more manual geometry work, and plan an empty-room acoustic measurement day.
2. **Camera matching is a solver, not eyeballing.** Every photo match is a least-squares solution with residuals and uncertainties (this PR), so ChatGPT or anyone else can re-run it and challenge it.
3. **Acoustic orientation study between Gate 2 and design** (step 3), with alternative orientations quantified rather than drawn.
4. **Renders are deferred to a GPU machine.** This cloud container is CPU-only. QA clay renders work here; photoreal production stills should run Cycles on a GPU (owner workstation or a render service).
5. **Whole-building capture, room-by-room design.**

---

## C. Source and tool verification (this session)

**Google Drive: working.** Tools available: `search_files`, `read_file_content`, `download_file_content`, `get_file_metadata`, plus Docs/Sheets. Search pages are capped at 5 results, so I paginated every folder.

- **Enumerated:** project index (read in full); archive root and all 6 subfolders (control room 6, live room 9, 3D-scan 6, outside/maps 8, legacy Sunny Suite 7, vibe references — first 5 of ~20 listed); the architecture folder (v0.2–v0.6 PDFs, SVGs, ZIPs, Docs).
- **Retrieved and decoded (26 files):** all 5 scan screenshots, all 6 control-room photos, all 9 live-room/loft photos, 4 exterior photos, both Sunny Suite equipment photos. HEIC decoded locally (`pillow-heif`); EXIF read (iPhone 13 Pro ultrawide 13 mm-equivalent and main 26 mm-equivalent; iPhone 15 Pro for the equipment photos). Bytes are staged only in gitignored `inputs/`.
- **Not yet retrieved:** the 41.6 MB scan-orbit `.mov`, the property maps (sensitive), the 5 Clark salvage/panel photos, the remaining vibe references, and the v0.6 ZIP (audit-only, deliberately not used as geometry). All are retrievable with the same tool; I prioritised geometry evidence.
- **Duplicate found:** `Outside view into control room.HEIC` and `Front entry to control room.HEIC` are the same file (identical size and timestamp).
- **No native 3D scan export exists in Drive** (searched by extension across the whole Drive). See item 1 above.

**Execution environment**
| Tool | Status |
|---|---|
| Blender 5.2.3 (`bpy` from PyPI) | ✅ runs headless; Cycles CPU renders work |
| Blender Workbench / Eevee | ❌ need GPU/EGL, unavailable in this container |
| download.blender.org | ❌ blocked by network policy (not needed: PyPI `bpy` works) |
| numpy / scipy / OpenCV / Pillow-HEIF | ✅ |
| Chromium/Playwright | ✅ (SVG → PNG drawing previews) |
| GPU | ❌ none: photoreal production renders should run elsewhere |

---

## D. First production milestone — delivered as this PR (draft)

My recommendation keeps your expected milestone (existing-conditions model + camera matches) but makes it **solver-based and uncertainty-carrying**. That is what makes it trustworthy enough to design on later.

**Delivered now (control room, v0.1):**
- A parametric **tray-ceiling section** solved jointly from **3 photographs** (CR1, CR2, CR3: 61 control points, RMS 6.6 px on 1600 px images, roughly 5–10 cm at room scale). Scale comes only from the scan-labelled width and depth.
- Independent agreements, none of them imposed:

| Check | Solved | Independent evidence |
|---|---|---|
| Flat ceiling height | 4.01 ± 0.09 m | scan label 4.07 m (never used in the solve) |
| Room width | 10.34 ± 0.19 m | scan labels 10.51 / 10.38 m |
| Room depth | 8.10 ± 0.19 m | scan label 7.86 m |
| Shared focal length | 590 px | 601 px predicted from EXIF (2 %) |
| Exterior door | 0.86 × 1.96 m | standard door size |
| CR1 vs CR2 camera position | agree within 4 cm | taken 5 s apart |
| CR3 camera position | lands at the partition threshold | the photo's foreground shows the hallway tile floor |
| Exterior door, clerestory, partition doorway | all on the room centreline | consistent with the symmetric exterior gable |

- **Blender file**, plan and two sections, all generated from the same solve. Camera-match panels: photo | Blender render | photo with model edges and residual vectors.
- **Recorded failures and discrepancies, not hidden:**
  - The exterior through-window match (WV) is **unsolved** (zero redundancy).
  - The beam on the X=W side shows a systematic 15–19 px residual: the room may be **asymmetric**, and the model currently assumes symmetry.
  - The posts in CR3 show 12–15 px residuals.
  - The gable-wall side windows and the X=0 wall windows are seen but **not yet solved**.

**Early layout signal from the solved shell (screening only, not a decision; updated for v0.2):**
- **Transverse axis (facing a side wall): disfavoured.** The two posts sit at mid-depth (Y ≈ 4.27 m of 8.20 m), so a transverse listening axis would put a post on or beside the axis, inside the stereo triangle. Posts cannot be removed.
- **Longitudinal axis on the building axis (X ≈ 5.88): favoured.** This is the axis shared by the doors, the clerestory and the 3.54 m-wide, 4.11 m-high flat ceiling. The posts end up beside the listener, 3.30 m and 3.37 m off-axis (nearly symmetric). The side walls are 0.52 m asymmetric about this axis (scan-measured), which treatment must equalise.
- **Remaining trade-off — which end is the front wall.**
  - Facing the partition puts the front wall on the interior side, but the centred doorway behind the speakers is the main route to the live room.
  - Facing the gable puts the exterior entry door, clerestory and daylight on the front wall.

  **[OWNER DECISION + acoustician]** after Gate 2.

**Gate 1 status (v0.2): READY FOR REVIEW — not self-certified.**
- Section geometry is now scan-measured and independently confirmed by three photo matches (6.8 px RMS).
- The asymmetry is resolved.
- Still open:
  - the remaining windows (gable side windows, X=0 wall);
  - tape checks of the post positions;
  - the void above the ceiling;
  - an independent review (ChatGPT / owner).

---

## E. Immediate next steps

| # | Action | Who | Unblocks |
|---|---|---|---|
| 1 | **Export the native scan** from the iPhone app as OBJ or GLB (with textures) *and* PLY/LAS point cloud, and drop it in the Drive "3d renderings raw" folder | Owner, ~5 min | All geometry: Gates 1 and 4, loft, roof void |
| 2 | Review the three private camera-match panels (sent to you directly, not committed) | Owner | Gate 1 |
| 3 | Tape-measure the console, both Geithains (with the model plate on the rear) and the rack wings; one photo per item from front, side and top | Owner/staff at Clark, ~30 min | Gate 2 |
| 4 | Approve or modify the workflow changes in section B | Owner | Steps 3–6 |
| 5 | On receipt of 1: fit planes to the mesh, re-run the solve with the scan as ground truth, extend to the whole building | Claude | Gate 1 |
| 6 | Extract frames from the scan-orbit video for roof-void and loft evidence (in case 1 is impossible) | Claude | Fallback |
| 7 | Confirm CPTAQ/zoning status before significant design spend | Owner + architect | Everything downstream |
