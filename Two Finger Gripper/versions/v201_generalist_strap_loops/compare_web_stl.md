# Two Finger Gripper 2.1 · generalist strap loops · web vs STL

![compare](previews/compare_web_stl.png)

## Overlap

<!-- render_compare:begin -->
| View | Overlap (IoU) | Vision only px | STL only px |
|---|---|---|---|
| front | 98% | 455 | 130 |
| side | 99% | 108 | 0 |
| top | 100% | 0 | 0 |
| iso | 99% | 326 | 14 |
| exploded | 95% | 219 | 693 |

<!-- render_compare:end -->

## Differences and why

- Front 98%: the fringe along each inner edge is Gen 16's 0.4 mm grooves and edge rounding, and at the lug and slide
  corners the 1.5 / 3 mm rounding, all of which only the STL has. The concept is plain blocks and the traced outline.
- Side 99%, top 100%: both are the full 12 mm plate from base to point, as Jake asked (no taper).
- Exploded 95%: the cyan strip on each slide is its dovetail tongue. The concept leaves it out on purpose (the
  slide is drawn as a flat plate), so the STL alone shows it.

## Fix list

- None. Regenerate with `Scripts/render_compare two-finger-gripper-v201-generalist-strap-loops` after `export_models.py`.
