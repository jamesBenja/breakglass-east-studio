# Equipment reference — actual Breakglass monitoring and console

Status (v0.3, 2026-11-08): **modelled** in `model/build_studio.py` from the owner's tape measurements, the manufacturer's data and the photos. The owner instructed modelling to proceed while Gate 1 revisions are reviewed.

## Main monitors: 2 × Musikelectronic Geithain **RL 901K** (model confirmed by owner, 2026-11-08)

| Property | Value | Class / source |
|---|---|---|
| Type | Active 3-way **coaxial** main monitor with cardioid (directional) low-frequency radiation | MANUFACTURER-PUBLISHED |
| Cabinet H × W × D | **550 × 500 × 430 mm** | MANUFACTURER-PUBLISHED (datasheet, as quoted by search results and Bonedo review) |
| ~~Alternative figure~~ | ~~561 × 500 × 441 mm, 49 kg~~ | **Removed:** these are the **ME 901K** (a different, related model), as the independent review pointed out (finding G1-08) |
| **Owner tape (2026-11-08)** | **W 19.7″ (500 mm) × D 16.7″ (424 mm) × H 21.4″ (544 mm)**; top of cabinet on its stand **61″ (1549 mm)** above the floor | TAPE: matches the published RL 901K size → **RL 901K confirmed** |
| Manufacturer placement | ≥ 20 cm clearance from walls and furniture | MANUFACTURER (per independent review, official manual pp. 7–8) |
| Weight | **48 kg each** (96 kg per pair) | MANUFACTURER-PUBLISHED |
| Drivers | 400 mm woofer; 130 mm midrange (some sources say 125 mm) + 25 mm dome tweeter, mounted coaxially | MANUFACTURER-PUBLISHED |
| Crossover | 550 Hz / 2.8 kHz | MANUFACTURER-PUBLISHED |
| Frequency range | 25 Hz – 20 kHz ±3 dB | MANUFACTURER-PUBLISHED |
| Max SPL | 116–122 dB (100 Hz–6 kHz, 1 m) | MANUFACTURER-PUBLISHED |
| Designed listening distance | **2–4 m** | MANUFACTURER-PUBLISHED |
| Acoustic centre on baffle | Coaxial MF/HF bar across the centre of the 400 mm woofer (owner photo); modelled at cabinet mid-height = **1.277 m** on the current stands | PHOTO-INFERRED |
| Current installation (Sunny Suite) | Free-standing on floor stands, upright, toed in, flanking a compact console | PHOTO-OBSERVED (Legacy sunny suite 1/2) |
| Photo consistency | Cabinet H:W ≈ 1.0–1.1 in the Sunny Suite photo vs 1.10 published | consistent |

Primary sources to read when network access allows (blocked in the current cloud session):
- [Geithain RL 901K installation manual (PDF)](https://www.me-geithain.de/en/assets/media/products/studio/RL901K/en/RL901K%20BDA%20ENV17_Web.pdf)
- [Geithain RL 901K product page](https://www.me-geithain.de/en/rl-901k2.html)
- [Bonedo review](https://www.bonedo.de/artikel/me-geithain-rl-901k/)

### Design implications (to be confirmed by the acoustician)
- **Listening distance.** The 2–4 m design distance fits the control room comfortably (8.20 m deep, 11.25 m wide). Space is not the constraint; reflection and low-frequency behaviour are.
- **Weight and stands.** At 48 kg per cabinet, the stands need to be rigid and decoupled, and the floor build-up under them matters. The existing control-room floor sits 0.35 m above the live-room slab, so its construction is UNKNOWN and needs inspection.
- **Front-wall placement.** Cardioid low-frequency radiation reduces, but does not remove, the front-wall boundary interaction (SBIR). It allows a closer-to-wall placement than conventional boxes, but the distance must be chosen from the room's actual modes, not assumed. The 4.11 m flat ceiling only 3.54 m wide and the 0.52 m side-wall asymmetry about the building axis are the conditions to analyse.
- **A future projection screen** in front of free-standing 550 mm-tall cabinets needs either an acoustically transparent screen or a screen that clears the cabinets' top. This is an [OWNER DECISION].

### Still to confirm (low effort)
1. The serial plate on the rear of each cabinet: model and any variant suffix, plus any rear-panel low-frequency/room settings currently in use (photograph the rear panels).
2. ~~One tape measurement of a cabinet~~: **done** (owner, 2026-11-08).
3. ~~Current stand height~~: **done** (top of cabinet at 61″). Toe-in angle in the old room: still open (not needed for the new layout).

## Console: Spectra Sonics (legacy, compact frame)
**Owner tape (2026-11-08):** width **62.4″ (1585 mm)**, depth **47″ (1194 mm)**, height at the front (armrest) **31″ (787 mm)**, height at the top (meter bridge) **41″ (1041 mm)**.

The owner's 3-D scan `Spectra Sonics console.glb` (7.1 MB) exceeds the Drive connector limit; split it like the building scan to use it. The model currently uses tape + photo.

From the owner photo (PHOTO-OBSERVED):
- 16 input strips in two banks of 8 with long-throw faders.
- A blank centre section.
- A master section with 6 faders.
- 12 VU meters on a brass/walnut bridge.
- A TT patchbay well at the right.
- A walnut frame with black steel T-legs.

Previously observed:
- About three module bays with a yellow VU meter bridge.
- A dedicated timber table/frame.
- Two angled timber outboard-rack wings forming a horseshoe.
- Operator facing the monitor wall.

The model and exact module count are to be confirmed from the console itself.
