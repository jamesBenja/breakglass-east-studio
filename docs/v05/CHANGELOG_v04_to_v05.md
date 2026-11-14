# Changelog: v0.4 (approved) → v0.5

## Unchanged
These are verified: the v0.4 build with the v0.5 code produces 589 objects with identical bounding boxes.
- Building shell, openings, posts, roof, ceiling, room divisions, loft, live room shell, machinery bays and aisle.
- Console and both RL 901Ks, the listening position, ±30° geometry and the 2.70 m baffle-to-front distance.
- Wood stove + flue, the hearth pad, the cinema screen / projector / sofa, 7.1.4 positions and subs.
- Producer desk, LED coves, HVAC slots (indicative), piano, loft guard and pendants.

## Changed (v0.5 build only, `BG_VERSION=v05`)
| v0.4 element | v0.5 replacement | Why |
|---|---|---|
| Generic front absorber (300 mm, fabric box) | ABS-003 ×2 + PAN-001 ×3 (Clark Dead Room) on NEW-07 200 mm wool-filled stand-off frames | reuse actual measured assets; same depth intent |
| Generic bench traps (0.75 m, Y 0.6–7.85) | NEW-01 bench traps, same envelope, Y 1.60–7.45 (rear-corner BTRs fill the ends) | integrates the Clark tapered traps |
| Generic ceiling cloud 3.1 × 2.2 m (flat only) | GOB-004 + GOB-003 cloud (flat) + GOB-003 on each slope, positioned on the traced reflection points | the strongest reflections land on the slopes, which v0.4 missed |
| Random-slat rear "QRD-style" diffuser | DIF-001 ×2 fin diffusers flanking the entry door + NEW-03 door curtain | actual Clark assets; the rear reflection lands at the door jambs |
| — | BTR-001 ×2, BTR-002 ×2 rear corners; NEW-02 front corner traps; GOB-005 on the left wall between the windows | LF / corner and a late side reflection |
| **Lounge chairs facing away from the stove** | **Loveseat + swivel armchair facing the stove glass; armchair rolls to the rear row for films** | **owner-authorised correction** |
| Fixed cinema chairs ×2 | Swivel armchairs A/B (A doubles as the fireside seat) | fewer pieces; same seat count in cinema mode |
| Live room: 4 generic gobos + 10 generic hinged side-wall panels | Clark HYB-001 ×3, PRF-001 ×4, PRF-002 ×3, DIF-003 + BTR-002, WOOD-001…005 (11 pcs), GOB-001 ×5, GOB-002 ×2, GOB-003/006 ×4 under the loft bays | actual assets; 4 documented configurations |
| String-quartet chairs + music stands (live room) | **Band backline (indicative, generic)**: 5-piece drum kit inside the three GOB-001 drum gobos, guitar combo and bass rig behind the two GOB-002 screens, boom mic stands on kit / amps / piano, one stool + vocal and acoustic-guitar mics (`model/v05_backline.py`, collection 39) | owner request 14 Nov: the chairs read as clutter; the room is for bands, drums, amps and piano. Packed away in farm mode |
| Support rooms: none | Clark vocal-booth set + Sunny Suite panels in the vocal booth, amp booth and machine room | uses existing rooms only |

## Erratum found in owner review (13 Nov): overhead immersive speakers mis-aimed
The v0.4 model tilts each overhead speaker in its own frame *before* turning it toward the listening position, but flips the tilt sign for the rear pair:
- **Ltr / Rtr** pointed 35° *up*, 80° off the listening position.
- **Ltf / Rtf** pointed 10° off it (35° tilt where the layout calls for 45° elevation).

**v0.5** aims all four exactly at the ears: 0.0° off, tilted 45° down. An assertion in `model/build_studio.py` now fails the build if any immersive speaker is more than 2° off the listening position.

The approved v0.4 files are left as they were (owner rule: preserve v0.4). The positions were always correct (`monitoring_geometry.json`); only the rendered cabinet orientation was wrong. These are phase-P7 speakers, so nothing approved for construction depends on it.

## Erratum found in owner review (14 Nov): an invented second door on the entry gable
The model's "gable interior door" (white, right of the entry door, photo-solved outline from photo CR3) is an **electrical cabinet inside the barn**, not a door. The owner confirmed this. The barn has one entry door on this gable.

v0.4 cut it through the gable as an opening, and the exterior renders showed a second front door. The rendered siding cut also hid the right-hand control-room windows.

**v0.5 fixes:**
- **Gable wall:** no opening. `EX_CR_electrical_cabinet` is modelled inside: outline photo-solved, depth UNKNOWN (0.25 m placeholder).
- **Working space:** `QA_electrical_working_space` keeps 1.0 m clear in front of the cabinet. This is a placeholder for the CEC Rule 2-308 intent; an electrician confirms it. `qa_v05_clashes.py` now fails if anything sits in it.
- **Cinema seating:** v0.4's rear-row chair sat 0.95 m in front of the panel, inside the working space. The cinema rear row (swivel armchairs A and B) now sits 0.40 m forward (y = 1.85 m); the screen view widens from 29.8° to 31.0°.
- **Acoustics inputs:** door area 3.9 → 1.8 m². The decay ranges, first-reflection coverage and modes are unchanged.
- **Exterior siding:** now cut at the right-hand control-room windows.
- **Re-rendered:** drawings PR-501/503/505/506 and every render showing the rear wall or the rear row.

The approved v0.4 files are left as issued (v0.4 build verified identical: 589 objects). The v0.4 drawings and renders still show the false door and the closer chair.

## New files
- `acoustics/`: geometry, reflections, modes / SBIR / decay, allocation, lounge, costs, plus `out/` results.
- `model/v05_treatment.py`, `model/make_v05_drawings.py`, `model/qa_v05_clashes.py`, `model/breakglass_east_v05.blend`.
- `drawings/v05/`, `renders/design/*_v05.png`, `renders/compare_v04_v05/`, `docs/v05/`.

## Costs
- **Owner decision (14 Nov): phase 1 is Geithain stereo only.** The 5.1 cinema extras (centre, side surrounds, sub; $2k–8k) move to the later phase, and films play through the RL 901K pair in phase 1.
- **Essential build:** $37.3k–$112.5k, up from $35.3k–$109.5k (**+$2.0k / +$3.0k**).
- **With contingency:** $41.0k–$129.4k.
- **Later phase:** $15.5k–$82k (5.1 extras + 7.1.4 completion + optional live-room curtains).
- The increase is new LF traps, the door curtain, stand-off frames, shutters, a structural check of hung loads and lounge furniture.
- Detail: `acoustics/out/costs_v05.csv`.
