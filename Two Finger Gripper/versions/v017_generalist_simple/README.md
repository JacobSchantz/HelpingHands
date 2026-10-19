# Gen 17 — simple handheld gripper (voice-258bb62c)

A stripped-down sibling of the old printable Gen 15. That Gen 15 was deleted later (voice-8673a6b6; it is in git at
97850a1) and the number reused for the long-jaw fingers. Gen 17 copied everything it needed, so it stands alone.
Renumbered Gen 16 → Gen 17 (voice-1fc7e062, folder `v016_generalist_simple` → `v017_generalist_simple`); the geometry did not change.

Jake: "Focus on significant simplicity. It doesn't need that whole arm attachment bit … It just needs a flat piece on
the side that I can put my fingers in, my thumb on the other side, and a strap that goes over. We don't need to
actually draw the straps."

## What it is

Three printed parts:

- **Right finger + thumb side pad** and **left finger + index side pad**: Gen 15's printable Gen 14 finger (2.0 mm tip,
  0.8 mm walls, same closed tip contact) fused to a flat 9 mm pad on its back face. The pad runs outboard over the
  digit, has one 4 × 22 mm strap / zip-tie slot, and holds the M4 pivot nut. It replaces Gen 15's separate carrier
  and its two M3 bolts.
- **Pivot plate + camera cradle**: both pivots at ±27.137 mm and the Insta360 X4/X5 cradle on top, one print. It
  replaces Gen 15's pivot plate, hand frame and camera mount.

Gone from Gen 15: the hand frame, the wrist strap, the separate carriers and camera mount, every M3 screw and insert.
Straps are not modelled. Everything sits above the hand; the thumb-index web stays empty over the full swing.

Parts and assembly: `BOM.md`. Print files: `exports/print/`.

## Checks (all pass)

- `check_geometry.py`: the fingers still contact like Gen 14 (closed gap within 0.081 mm of target, 6.9° included at the point).
- `check_device.py`: over 0–30° neither finger hits the plate, camera or the other side; the web stays empty; the camera
  sits in its cradle; a nominal 22.5 mm digit fits under each pad clear of the finger; walls ≥ 0.8 mm.
- `genus.py`: the printed finger has exactly its 36 designed through-holes.
- `export_models.py`: every STL is one watertight, consistently wound body.

Rebuild: `python3 export_models.py && python3 check_geometry.py && python3 check_device.py && python3 genus.py`.

## Not verified

Nothing is printed yet. Pad size, slot position and the digit size are nominal, not measured on Jake's hand.
