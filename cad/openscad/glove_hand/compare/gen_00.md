# Robot Glove Hand gen 00 · flat-hand fit tray · web vs STL

![compare](../render/compare_gen_00.png)

## Overlap

<!-- render_compare:begin -->
| View | Overlap (IoU) | Vision only px | STL only px |
|---|---|---|---|
| front | 29% | 14202 | 0 |
| side | 26% | 16513 | 0 |
| top | 98% | 600 | 490 |
| iso | 78% | 5143 | 1 |
| exploded | 45% | 14665 | 1923 |

<!-- render_compare:end -->

## Differences and why

- **Outline (top IoU 98%).** The concept glove is extruded from the same `hand_outline.scad` the tray uses, so from above they match except the wrist cuff. This confirms the photo outline drives both.
- **Height (front 29%, side 26%).** Expected: gen_00 prints only the bottom of the glove, a 0.8 mm TPU pad with an 8 mm wall. The vision is the whole thing: a 22 mm hollow shell, servo pack and tendons on the back, a wrist cuff. Everything magenta is step 2, not a defect.
- **Wall (iso, exploded cyan).** The tray wall stands 1.5 mm outside the outline (clearance + wall); the vision's shell bevel sits inside it. Fine for a fit check.

## Fix list

- Step 2 (gen_01): thickness. Needs a side photo of the flat hand or calipers at each knuckle and the palm; the vision's 22 mm is a guess.
- Concept: once thickness is measured, make the shell a real hollow (outer minus inner) so the diff measures wall thickness, and put the tendon guides where the print will put them.
- Fix nothing in gen_00: it is a fit test and its outline already matches the vision.
