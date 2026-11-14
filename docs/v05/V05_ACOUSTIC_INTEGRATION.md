# Breakglass East v0.5: acoustic integration & salvage optimisation

**Status:** PROPOSED. This is an evolution of the **approved v0.4** "fireside + cinema" layout, not a redesign.

**Not for construction.** The existing shell is phone-LiDAR + photo reconstruction (±0.1–0.2 m). Acoustic figures are screening ranges, not predictions. An acoustician must review them and on-site measurements must confirm them before anything is fabricated.

**What v0.5 keeps from v0.4, unchanged and verified by an identical v0.4 build:**
- Envelope, roof, ceiling, posts, openings, room divisions.
- The Spectra Sonics console and both RL 901Ks, with the same listening geometry.
- The wood stove, the cinema and the architectural language.

**What v0.5 adds:**
- The owner's Clark acoustic inventory placed as real, measured objects.
- Purpose-built LF treatment where the inventory has none.
- The owner-authorised lounge correction.

## 1. Concept
The control room's acoustic problems come from the real building:
- an asymmetric tray ceiling, 4.11 m flat and 2.25–2.30 m low zones;
- glass on both side walls and the gable;
- a front wall split by the stove and a doorway.

v0.5 uses this geometry instead of fighting it:
1. **A "halo" of absorption where the first reflections actually land.** The image-source trace on the measured planes puts the strongest early reflections (+9.5 to +15 ms) on the **sloped and flat ceiling at Y ≈ 4.1–4.5 m**, not on the side walls.
   - Four burlap/Roxul GOB panels from Clark's Resident Suite go exactly there: one cloud of two panels hung 200 mm below the flat ceiling, and one panel on each slope.
2. **Deep bass control in the low side zones.** Under-sill bench traps (v0.4 intent, now specified as NEW-01) run under the windows, which stay clear. Corner traps go in the front corners, and the Clark tapered traps go in the rear corners.
3. **A quiet, absorptive front wall.**
   - The Dead Room Roxul panels (ABS-003 ×2, PAN-001 ×3) are re-hung on 200 mm wool-filled stand-off frames, effectively ~300 mm absorbers.
   - They stop > 0.9 m short of the stove.
   - The RL 901K's cardioid bass radiates little toward this wall.
4. **A scattering rear wall.** The two DIF-001 fin diffusers flank the centred entry door above the sofa. A heavy wool curtain over the door (NEW-03) catches the rear reflection between them and doubles as cinema blackout.
5. **A live room that stays a working barn.**
   - Clark's hybrid barrels, perforated panels, rustic wood wall, diffuser/trap pair and gobos turn the tray zone into a variable room.
   - The under-loft bays keep the machinery, and the aisle to the garage door stays clear.

## 2. Corrected fireside lounge (owner-authorised)
v0.4's lounge chairs faced away from the stove. In v0.5 every lounge seat faces the stove's glass door. The layout is solved by `acoustics/lounge.py`, not placed by eye.

The solver's constraints:
- 0.90 m stove clearance, a **placeholder** for the stove's listed clearances (label / WETT);
- no overlap with the speaker and cardioid clear zones, the sub, the traps, the front frames or the future Ls stand;
- the doorway route to the live room kept clear;
- a 1.0 m working space kept clear in front of the electrical cabinet on the rear (gable) wall (placeholder; electrician to confirm);
- seats behind the speaker line;
- nobody blocking anybody's view of the fire.

| Mode | Seats | Positions |
|---|---|---|
| **Fireside** | loveseat (2) + swivel armchair A (1) facing the fire; side table between | loveseat 2.53 m from the fire, armchair 1.60 m; minimum stove clearance 0.92 m |
| **Cinema** | sofa (3–4) + swivel armchairs A and B (5–6 seats, as v0.4) | armchair A rolls on glides from the fire to the rear row; B stays there. The row sits 0.40 m forward of the v0.4 cinema-chair spot so armchair B is clear of the electrical cabinet's working space; each sees the screen at 31.0° width |

**Tested and reported, not hidden:** a third seat (second armchair) does not fit around the fire behind the speaker line with these clearances.

**Honest limits:**
- The lounge sits behind the drop-down screen. It is a fireside / listen-back spot, not a cinema seat.
- There are no mechanisms, only a swivel chair on felt glides.

Drawing PR-506 and renders `cr_fireside_v05`, `cr_fire_seat_v05` and `cr_cinema_v05` show the result.

## 3. Analysis summary (reproducible: `acoustics/*.py` → `acoustics/out/`)
| Topic | Result | Confidence / what it ignores |
|---|---|---|
| Volume / target decay | 289 m³; EBU Tech 3276 T_m = **0.36 s** (±0.05 s from 200 Hz up) | shell ±0.1–0.2 m |
| Schroeder frequency | ≈ 64 Hz at 0.3 s | depends on the achieved decay time |
| Axial modes at the LP | Peaks at 30.5 Hz (2,0,0), 62.8 Hz (0,3,0) and 91.5 Hz (6,0,0); null at 83.7 Hz (0,4,0). Height series bracketed 42–76 Hz (tray ceiling spreads it) | rectangular approximation of an asymmetric room |
| SBIR (omni ¼-wave) | Front wall 2.70 m → 32 Hz; floor 1.28 m → 67 Hz (the console shadows the floor bounce); side wall ≥ 4.5 m → 19–22 Hz | RL 901K is cardioid at LF, so the front term is weaker than the omni estimate |
| First reflections (16 paths) | 11 meet v0.5 treatment; 2 floor paths console-shadowed; 1 front (L, rear radiation, wall bare between stove clearance and doorway); 3 side-wall paths are late (≥ 19.9 ms) and ≤ −10.7 dB, landing on glass or mullions → shutters NEW-04 | spherical spreading only; no diffraction |
| Decay-time ranges, control room 500 Hz | bare 1.00–2.34 s → Clark only 0.58–1.12 s → **recommended v0.5 0.39–0.68 s** | generic material-class bounds (see §5) |
| Decay-time ranges, live room 500 Hz | bright 0.98–1.85 s · neutral 0.67–1.22 s · dead 0.51–0.96 s | coupled volume, open to the middle zone |

The ranges are wide because the existing finishes, the panels' cores and backings, and the HYB and DIF behaviour are not measured. They show direction and order of magnitude.

- **Mid and high frequencies:** the treated control room's lower bound reaches the target.
- **Below 125 Hz:** even the recommended case may stay long. This is why the deep bench traps and corner traps (new build) are in the base scope. It is also why the plan keeps room to add more LF trapping after measurement, rather than relying on the reused panels.

## 4. Salvage deployment (no asset over-allocated)
The inventory is 74 counted units in 41 families (owner sheet, 13 Nov 2026).
- **Allocated: 71 units.** Control room 16, live room 34, vocal booth 11, amp booth 7, machine room 3.
- **Reserve / held: 3 units.**
  - ABS-004: tapered polygon unmeasured; a lounge-ceiling candidate.
  - ABS-006: depth unknown.
  - ABS-014: **held** as a possible duplicate of ABS-010.
- **Uncounted families:** DIF-002, ABS-002 and MAT-002 (Below Breakglass) stay in reserve until counted.

Counts are asserted in code: `acoustics/allocation.py` fails if any family is over-allocated or if ABS-014 is placed. The model asserts its unit count equals the allocation.

**Full matrix:** `acoustics/out/deployment_matrix.csv` / `.md`. It lists, per asset: inventory, allocated and reserve counts, body size, verification, room, placement, purpose, air gap, reuse mode and install requirement.

**Evidence discipline:**
- Body sizes are the owner's measurements.
- Where the sheet has no depth (the Sunny Suite ABS-005…013), the model uses a **0.05 m PROVISIONAL** depth, flagged magenta in the drawings and `depth_provisional=True` on the objects.
- DIF fin order, HYB perforation, wood-box board thickness and gobo frames are **indicative** and flagged on the objects.
- No asset gets an absorption coefficient.

## 5. Assumptions you must not over-read
- **Decay estimates** apply *generic* low/high bounds per material class (porous 75–125 mm, tapered foam, fin diffuser, perforated wood, etc.) to the *measured areas* of the allocated assets. The bounds are in `modes_sbir_rt.py:CLASS`. They are **not** data for these panels.
- **The existing finishes** (wall/ceiling lining on framing) are unknown, and they dominate the bare-room range.
- **Hidden construction** (roof void, framing for hung loads) is not inferred. Ledger X4 and the structural check (cost line 17) gate every ceiling-hung item.
- **The stove clearance (0.90 m)** is a placeholder.

## 6. Commissioning plan (what must be measured, and when)
| Step | When | What | Who |
|---|---|---|---|
| C0 | before any fabrication | Tape-verify: ABS-010 vs ABS-014; depths of ABS-005…013; ABS-004 polygon; weights of all hung items; DIF fin schedule photos | owner |
| C1 | empty room, after the Clark move | REW sweeps at the LP and 6 seats; RT60 per octave; background noise (HVAC on/off, stove fan) | owner (DIY kit) + remote acoustician |
| C2 | after bench + corner traps | repeat C1; compare with this report's ranges; decide on additional LF trapping | acoustician |
| C3 | after ceiling halo + front + rear | ETC / reflection plot at the LP (the 9–17 ms window must be ≥ 15–20 dB below direct); speaker position tuning (stands ±0.2 m) | acoustician |
| C4 | cinema calibration | 5.1 levels, sub crossover / bass management (the 30.5 and 62.8 Hz LP peaks are candidates for dual-sub placement) | owner / integrator |
| C5 | live room | RT per configuration A–D; gobo positions marked on the floor | owner |
| C6 | stove | WETT/insurer clearances: confirm the lounge, PAN-001 frame and hearth pad, or move them | WETT inspector |

## Owner decisions during v0.5 review
| Date | Decision |
|---|---|
| 13 Nov | Lounge seating must face the fire (implemented; see §2). |
| 13 Nov | Overhead immersive speaker aim corrected (erratum; see the changelog). |
| 14 Nov | **The white rectangle right of the entry is an electrical cabinet inside the barn, not a second door** (owner correction). v0.5 removes the false opening (no hole in the gable, no exterior door), models it as an interior cabinet (depth unknown, 0.25 m placeholder) and keeps 1.0 m in front of it clear. The cinema rear row moves 0.40 m forward. Acoustic results are unchanged (no traced reflection landed on it; the decay ranges did not move). Erratum in the changelog. |
| 14 Nov | **Phase 1 = Geithain stereo only.** Films play through the RL 901K pair; the 5.1 extras (centre, side surrounds, sub; $2k–8k) move to the later phase. Essential build is now $37.3k–$112.5k ($41.0k–$129.4k with contingency). Renders: `*_v05_phase1.png`. |

## 7. Files
Drive (owner): folder “v0.5 — Acoustic Integration & Salvage” in the review package, containing the presentation Doc and the workbook (Budget v0.5 / Asset deployment / New items / Open items). The v0.4 Doc and Sheet are untouched.

| Type | Files |
|---|---|
| Model | `model/breakglass_east_v05.blend`, built by `BG_VERSION=v05 python3 model/build_studio.py`. v0.4 stays the default build and `breakglass_east_v04.blend` is untouched. Collections `35_V05_CLARK_ASSETS`, `36_V05_NEW_TREATMENT`, `37_V05_LOUNGE`. |
| Drawings | `drawings/v05/PR-501…PR-512` (SVG + PNG), generated by `model/make_v05_drawings.py` |
| Renders | `renders/design/*_v05.png`, with matched v0.4/v0.5 pairs in `renders/compare_v04_v05/` |
| Photo look + exterior | `renders/design/*_v05_photo.png` (`BG_LOOK=photo`, `model/lookdev.py`: materials and lighting only; exterior trim, lawn, trees and sky are labelled presentation context). Standard/photo pairs: `renders/compare_v05_photo/` |
| Editor hand-off | `docs/v05/handoff/`: `BRIEF_FOR_EDITOR.md` (rules, fixed facts, structure) and `IMAGE_MANIFEST.md/.json` (every image pinned to a commit, with caption and provenance) |
| QA | `model/qa_v05_clashes.json`, `acoustics/out/reflection_coverage.json` |
| Costs | `acoustics/out/costs_v05.csv` |
| Changelog / open items | `docs/v05/CHANGELOG_v04_to_v05.md`, `docs/v05/UNRESOLVED.md` |
