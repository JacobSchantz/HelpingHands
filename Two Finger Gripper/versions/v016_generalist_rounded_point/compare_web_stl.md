# Two Finger Gripper gen 16 · generalist rounded point · web vs STL

![compare](previews/compare_web_stl.png)

## Overlap

<!-- render_compare:begin -->
| View | Overlap (IoU) | Vision only px | STL only px |
|---|---|---|---|
| front | 97% | 432 | 28 |
| side | 100% | 60 | 0 |
| top | 100% | 2 | 0 |
| iso | 99% | 180 | 5 |
| exploded | 99% | 139 | 6 |

<!-- render_compare:end -->

## Differences and why

- Front 97%: the fringe along each inner edge is the 0.4 mm grooves and the 0.5 mm / 1.2 mm edge rounding, which only the
  STL has. The concept is the bare traced outline and holes; this is the expected gap.
- Side, top 100%: Gen 9's eased taper to the 0.5 mm point matches; the STL's 0.25 mm nub at the very point is below a pixel.

## Fix list

- None. Regenerate with `Scripts/render_compare two-finger-gripper-v016-generalist-rounded-point` after `export_models.py`.
