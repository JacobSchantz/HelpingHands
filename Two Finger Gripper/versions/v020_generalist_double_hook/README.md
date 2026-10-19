# Generalist Gripper · Version 1.20: double hook

voice-483f28b9. Jake: *"The gripper should have a hook at both the bottom AND the top along the flat face, so the handle piece
slides in and is held by both hooks."*

Builds on 1.19 (`v019_generalist_wide_beak`, voice-13bdab11). Everything in 1.19 is the same here: the wide beak, the
flat-bottom taper, the holes, the grooves and the tip-only contact.

## What changed from 1.19

- **A top hook.** The finger's straight outer edge (the flat face) already ended in the base J-hook. `trace_photo.py`
  `top_hook()` copies that hook's outline (`PATCHES[1]`), flips it end for end about u = 8.5 mm along the edge (`RAIL`,
  `TOP_HOOK`), and splices it onto the top of the same edge. A short ramp joins the back of the copy to the edge.
  - The two notches face each other.
  - Their floors are 39.8 mm apart (u -11.4 and 28.4, `trace_px.scad` `hook_floor_u`).
  - The top hook ends before the edge bends toward the root (u 36.5).
- **A handle blank (black, one per finger).** It's a 3.5 mm plate, as thick in Y as the finger (12 mm), lying against the
  outer edge with a 0.2 mm gap. It's trimmed by the finger outline grown by that 0.2 mm, so each end becomes a foot that fills
  one notch.
  - **How it goes on.** The hooks face each other, so the blank can't drop in along the edge. It slides in sideways, across
    the finger's thickness, from either face.
  - **What holds it.** Seated, the notch floors stop it along the edge, and both prongs stop it pulling outboard.
  - It's a fit blank, not a strap handle. The 1.x line is gripper only, so the strap slots stay in 2.x.
- `trace_photo.py` `RDP_SPLIT` pins the point where the outline's simplification is split to 1.19's. Otherwise the extra hook
  points shift that split, and the re-picked beak vertices left a non-manifold edge in the 15° pose.

## Parts

| Part | STL (assembled pose / print) |
|---|---|
| Right finger | `exports/parts/right.stl` / `exports/print/right.stl` |
| Left finger (mirror) | `exports/parts/left.stl` / `exports/print/left.stl` |
| Right handle blank | `exports/parts/right_handle.stl` / `exports/print/right_handle.stl` |
| Left handle blank | `exports/parts/left_handle.stl` / `exports/print/left_handle.stl` |

`gripper.scad` `part=` takes `assembly`, `fingers`, `handles`, `right`, `left`, `right_handle`, `left_handle`, `handle_in`
(with `handle_slide` = mm still to slide in) and `collision`. Print the fingers flat on the ventral face, as in 1.18. The
hooks are plan-view shapes cut straight through the thickness, so they need no supports. Print the blank on its long side.

## Checks (all pass)

Run `python3 trace_photo.py && python3 export_models.py && python3 genus.py && python3 check_geometry.py`. Every 1.19 check
passes, plus these:

- **Clearance:** the seated blank clears the finger.
- **Slides in:** it moves out across the finger's thickness, in 2 mm steps to 12 mm, without touching it.
- **Held:**
  - Pushed 0.5 mm outboard, it hits both prongs (overlap at both ends, z 2.5 and 40.9). Even 0.3 mm catches.
  - Pushed 0.5 mm toward either hook, it hits that notch's floor.
- **Hole count:** 33 through-holes, the same as 1.19.

Previews:

- `previews/hooks.png`: the two hooks.
- `previews/handle_in.png`: the blank seated.
- `previews/handle_sliding.png`: the blank 9 mm from home, sliding in.
- `compare_web_stl.md`: the web render against the STL.

## Not verified

Nothing has been printed. Only friction keeps the blank from sliding back out across the finger. The 0.2 mm clearance is
nominal. The prongs are the base hook's size (about 2.2 mm deep along the edge) and haven't been pull-tested.
