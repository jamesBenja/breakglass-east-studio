"""Build the presentation hand-off pack for a second editor (e.g. ChatGPT): an image manifest pinned to a
commit, with captions and provenance, so the layout can be rebuilt without re-describing or regenerating images.
Usage: python3 docs/v05/handoff/make_handoff.py <commit-sha>   (the commit that contains the images)"""
import json, os, sys
SHA = sys.argv[1]
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
RAW = f"https://raw.githubusercontent.com/jamesBenja/breakglass-east-studio/{SHA}/"
SHELL = "Existing shell: phone-LiDAR + photo reconstruction, ±0.1–0.2 m (not a certified survey)."
LOOK = "Photo look pass: materials + lighting only on the unchanged v0.5 model (model/lookdev.py)."
EXT = ("Building geometry from the model; cladding/roof/trim type and colour from the owner's site photos (approximate). "
       "Lawn, grass, trees, sky and the entry-lamp glow are indicative context, not surveyed.")
I = []
def add(path, section, title, caption, kind, notes, hero=False):
    assert os.path.exists(os.path.join(ROOT, path)), path
    I.append(dict(path=path, url=RAW + path, section=section, title=title, caption=caption, kind=kind, provenance=notes, hero=hero))

# 1 exterior
add("renders/design/ext_entry_v05_photo.png", "01 Site & building", "The barn from the entry gable",
    "Existing barn at Ways Mills: control-room entry gable and the long east wall. Nothing on the exterior changes in v0.5.", "render-photo", f"{EXT} {SHELL}", True)
add("renders/design/ext_live_gable_v05_photo.png", "01 Site & building", "Live-room gable and machinery door",
    "The live-room end keeps its large door for farm machinery; the studio works inside the existing envelope.", "render-photo", f"{EXT} {SHELL} Door shown open as modelled.")
add("renders/design/ext_aerial_v05_photo.png", "01 Site & building", "Aerial view",
    "One continuous roof over control room, middle rooms and live room — no raised roof, no new primary partitions.", "render-photo", f"{EXT} {SHELL}")
add("renders/design/ext_entry_dusk_v05_photo.png", "01 Site & building", "Dusk",
    "The control room lit from inside at dusk.", "render-photo", f"{EXT} Interior lighting is design intent.")
add("renders/design/axo_cutaway_v05.png", "01 Site & building", "Cut-away axonometric",
    "Roof and near walls removed to show the room sequence: control room, middle rooms, live room with loft.", "render-standard", SHELL)
# 2 control room
for f, t, c in (
 ("cr_front_v05_photo", "Control room — mix position", "Spectra Sonics console and both Geithain RL 901Ks on the ±30° stereo triangle; ceiling halo and front Dead-Room panels above and behind."),
 ("cr_overview_rear_v05_photo", "Control room — looking back to the entry", "High view over the console to the sofa, armchairs, rear diffusers and the curtained entry door."),
 ("cr_overview_rear_L_v05_photo", "Control room — rear left", "The fireside side of the room from above the left speaker."),
 ("cr_console_v05_photo", "The console", "The actual Spectra Sonics console, modelled from photographs and measured dimensions."),
 ("cr_fireside_v05_photo", "Fireside lounge (corrected)", "Owner-authorised correction: the loveseat and swivel armchair now face the stove glass."),
 ("cr_fire_seat_v05_photo", "From the fireside seat", "The view a guest has from the lounge: fire, console and monitors."),
 ("cr_cinema_v05_photo", "Cinema mode", "Screen down, armchair A rolled to the rear row; phase 1 plays films through the RL 901K pair."),
):
    add(f"renders/design/{f}.png", "02 Control room", t, c, "render-photo", f"{LOOK} {SHELL}", f == "cr_front_v05_photo")
for f, t, c in (
 ("cr_front_v05_phase1", "Phase 1 — Geithain stereo only", "Owner decision 14 Nov: phase 1 is the RL 901K pair only; immersive speakers and subs are later-phase."),
 ("cr_overview_rear_v05_phase1", "Phase 1 — open room", "The same room without the immersive array: more open, fewer objects."),
 ("cr_ceiling_v05", "Ceiling halo", "GOB panels hung where the traced first reflections land: flat-ceiling cloud plus one panel on each slope."),
):
    add(f"renders/design/{f}.png", "02 Control room", t, c, "render-standard", SHELL)
# 3 live room
for f, t, c in (
 ("live_piano_v05_photo", "Live room — piano and ensemble", "Grand piano with a mic pair, the band set-up (drums in the gobo booth, amps behind half-height screens) and Clark gobos under the existing tray ceiling. Backline is generic and indicative."),
 ("live_drums_v05_photo", "Live room — drums under the loft", "Drum kit inside three wheeled gobos, amps behind the half-height screens; machinery bays and aisle untouched. Backline is generic and indicative."),
 ("live_farm_v05_farm_photo", "Farm mode", "Piano covered on its dolly against the west wall, gobos nested, aisle clear for machinery."),
):
    add(f"renders/design/{f}.png", "03 Live room", t, c, "render-photo", f"{LOOK} {SHELL}", f.startswith("live_piano"))
add("renders/design/loft_overlook_v05_farm.png", "03 Live room", "Farm mode from the loft", "Looking down from the existing loft with the room cleared for farm use.", "render-standard", SHELL)
# 4 drawings
for f, t in (("PR-501_control_room_treatment_plan", "Control-room treatment plan"), ("PR-502_control_room_RCP", "Reflected ceiling plan"),
             ("PR-503_control_room_elevations", "Elevations"), ("PR-504_control_room_sections", "Sections"),
             ("PR-505_monitoring_reflections", "Monitoring geometry and first reflections"), ("PR-506_lounge_two_modes", "Lounge: fireside and cinema modes"),
             ("PR-511_live_room_treatment_configs", "Live-room configurations A–D"), ("PR-512_support_rooms_treatment", "Support rooms")):
    add(f"drawings/v05/{f}.png", "04 Drawings", t, f"{t} (v0.5, not for construction).", "drawing", "Generated from the same model (model/make_v05_drawings.py). Magenta = provisional depth.")
# 5 comparisons
for f in sorted(os.listdir(os.path.join(ROOT, "renders/compare_v05_photo"))):
    add(f"renders/compare_v05_photo/{f}", "05 Comparisons", "Standard vs photo look", "Same camera, same geometry; only materials and lighting differ.", "comparison", LOOK)
for f in ("cr_front", "cr_fireside", "cr_rear", "live_piano"):
    add(f"renders/compare_v04_v05/{f}.jpg", "05 Comparisons", f"v0.4 → v0.5: {f}", "Matched cameras: approved v0.4 on the left, v0.5 on the right.", "comparison", SHELL)

out = os.path.dirname(os.path.abspath(__file__))
json.dump(dict(commit=SHA, images=I), open(os.path.join(out, "IMAGE_MANIFEST.json"), "w"), indent=1, ensure_ascii=False)
with open(os.path.join(out, "IMAGE_MANIFEST.md"), "w") as f:
    f.write(f"# v0.5 image manifest (pinned to commit `{SHA[:10]}`)\n\nUse these files unchanged. Captions may be edited for length; provenance may not be dropped.\n\n")
    sec = None
    for i in I:
        if i["section"] != sec: sec = i["section"]; f.write(f"\n## {sec}\n\n| # | Image | Caption | Kind / provenance |\n|---|---|---|---|\n")
        f.write(f"| {I.index(i)+1}{' ★' if i['hero'] else ''} | [{i['title']}]({i['url']}) | {i['caption']} | {i['kind']}: {i['provenance']} |\n")
print(len(I), "images")
