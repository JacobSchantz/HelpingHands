# Generalist Gripper · Generation 6

Built on Generation 5 (voice-650be16a). Two changes, both from Jake's note:

1. **Everything but the fingers moves up above the hand.** The gears, the servo
   and the housing now sit on the back of the hand (+Y, 13–59 mm above the
   finger plane). The only things left in the thumb–index web are the two
   pivot columns (Ø10 mm, Ø14 mm shoulder) climbing out of the plane. Gen 5's
   hub floor, both hub cheeks, the in-plane gears and the motor are gone from
   the web.
2. **Fingers redrawn to copy Generalist's.** Each finger is a flat 10 mm plate
   with hexagon honeycomb through-cutouts inside a 2.2 mm solid rim. It has an
   outer knuckle bump at about 55% of its length, a small inner step opposite
   the bump, and a lower blade that swings inward to a black pointed TPU tip.
   Two grey-dot pockets hold 4×2 mm disc magnets, matching the dots in the
   photos.

References used: `references/generalist/ziptie_1.jpg` (clearest view of the
finger outline and honeycomb), `screwhand_1.jpg`, `human_jar_01.png` (the
human-worn device). The outline is traced **by eye** from these photos. No
dimension was measured from a real part, and no Generalist CAD exists or was
used. Treat "identical" as "as close as photos allow".

## Parts (8)

| Part | Print | Notes |
|---|---|---|
| `housing_base` | PLA/PETG | Floor + wall over the back of the hand; strap slots in the rear tongue |
| `housing_lid` | PLA/PETG | Holds the left axle pin; right drive passes through to the servo |
| `left`, `right` | PLA/PETG (yellow) | Mirror images from one `jaw()` source; print flat |
| `left_gear`, `right_gear` | PLA/PETG | 24T m1.2, keyed on an 8 mm hex; left is half-tooth indexed, right carries the servo hub |
| `left_tip`, `right_tip` | TPU (black) | Slide over the jaw tongue, 0.15 mm seating gap |
| servo | — | 36×38×30 envelope only, shaft down into the right gear; **unselected** |

Not modeled: two Ø4 mm steel axle pins, three M2 self-tapping lid screws,
the servo horn/adapter, the magnets, and the straps (finger straps go
through the slots near each plate's outer edge; a palm strap goes through
the housing's rear slots).

## How it moves

ONE servo turns the right gear and right finger. The right gear drives the
left gear, so both fingers counter-rotate 1:1 through 0–22°. Each jaw rides on
its Ø10 column in the housing floor and on its pin in the lid, two supports
spaced 20 mm apart along the axle. The Ø14 shoulder stops the jaw rising and the
gear on its hex stops it dropping. Tips are 1.2 mm apart closed and about 87 mm
apart at 22°.

## What changed vs Gen 5, honestly

- **Cantilever:** the fingers now hang 13 mm below the housing floor on their
  columns instead of being sandwiched between cheeks. Stiffness and pin bending
  are not analysed.
- **No hard travel stops:** Gen 5's stop tabs are gone; the servo limits
  travel.
- **No finger channel:** Gen 5's deep outer groove for the human finger can't
  coexist with a honeycomb plate. Fingers attach by straps through the slots
  instead. Fit is untested.
- The stack is taller (the servo sits on the lid, about 60 mm above the
  finger plane).

## Checks

- `python3 check_geometry.py` sweeps 45 poses (0–22° every 0.5°). It checks
  that no rigid parts collide and that **nothing occupies the thumb–index
  web** (hand-plane band |Y| ≤ 12 mm behind the pivots), with a positive
  control. It also checks that the gears have no material overlap and still
  engage at ±1° misphase, and that the tips don't touch when closed.
- `python3 export_models.py` exports `exports/print/*.stl` (print
  orientation as modeled), `exports/parts/*.stl` (assembled, for the
  viewer), `exports/assembly.stl`, and closed-mesh/winding checks.

These are bounded CAD checks only. Strength, print quality, comfort and
backdrive are all unvalidated, and no hardware was operated.
