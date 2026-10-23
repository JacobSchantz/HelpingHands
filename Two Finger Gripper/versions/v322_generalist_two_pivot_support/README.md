# Base 21 + Gripper 25 — two local pivots, all connecting support overhead

**Base 21 builds on Base 20. Gripper 25 is unchanged.** Latest voice-550038ca clarification minimizes support material within the finger slab; jaw solids are explicitly excluded. Historic versions remain untouched. This continues the compact, hand-held HLS3606M-C001 branch; there is no SO-101/Mount 2 bracket or legacy Handle interface.

![Actual same-scale top/side comparison](previews/comparison.png)

The broad lower retaining plate and both rear pillars are deleted. Only two 3 mm OD smooth printed pivot sleeves cross the Y=-3..3 mm finger band. Each is bored 2.2 mm for a steel M2×25 bolt. A separate **5×2.2×0.5 mm washer** beneath each finger prevents axial escape; the bolt clamps washer/sleeve/base against an **M2 nut above the overhead base**. The steel bolt reinforces the thin sleeve; the finger runs on the printed outside, not the bolt threads. Six printed parts remain: two unchanged fingers, two unchanged gears, pinion, base.

The motor, purchased spline plate, sector gears and keyed finger bosses retain Base 20's placement and actual size. Teeth begin at Y=3.8 mm, **0.8 mm above** the 6 mm finger slab. Thumb/index still approach opposing outside jaw faces; there are no handles, straps or palm fixture. No jaw surface was shrunk to reduce the support metric.

| CAD measurement | Base 20 | Base 21 |
| --- | ---: | ---: |
| Projected support material within Y=-3..3, jaws excluded | 103.808 mm² | 12.799 mm² |
| Conservative outer-disc footprint of remaining journals | — | 14.114 mm² |
| Broad lower plate | present | absent |
| Local retainer projected material below slab | broad cap | 39.207 mm² |
| Gear-to-finger gap | 0.8 mm | 0.8 mm |
| Overall swept X/Y/Z, including cable reserve | 70.032 / 53.200 / 114.514 mm | 70.032 / 52.600 / 106.764 mm |

The support number is a **projection of the union of real stationary material clipped to the slab**, including bolt cores; holes are not counted as material. It is not total surface area or a strength-qualified global minimum. The enclosing two 3 mm discs are also reported so hollowing cannot disguise the occupied footprint. Washers/head material is counted separately below the slab. The actual band remains -3..3 for the working blades; short torque bosses extend above it as before.

## Retention, hardware and assembly

The washer extends **0.75 mm radially past the 3.5 mm finger bore**. Its top is Y=-3.2 mm, leaving **0.2 mm lower clearance**. Together with the inherited 0.3 mm upper gear clearance, the stack can float up to **0.5 mm**, retaining at least **2.0 mm key engagement**. Moving either finger downward by 1 mm intentionally intersects its washer (~4.999 mm³): a positive escape-stop control, not a force calculation.

Use two M2×25 ISO 4762 bolts, two M2 DIN 934 nuts (4 mm across flats, 1.6 mm high) and two M2 washers (dimensions above). M2 head envelope is 3.8×2 mm, 1.5 mm hex drive; dimensions from [Westfield ISO 4762 drawing](https://www.westfieldfasteners.co.uk/Datasheets/ScrewBolt_SHCap_M.pdf) and [Accu's M2 dimensional listing](https://www.accu.co.uk/metric-cap-head-screws/653179-SSC-M2-20-TI5-R360). The Accu listing is for the same head family at 20 mm length, not the specified 25 mm bolt. Verify purchased hardware before fabrication. Nut/washer dimensions are nominal prototype assumptions, not measured parts. Explicit envelope meshes omit thread forms; nut bore clears the nominal bolt core rather than intersecting it as real threads do.

Bolt tip reaches Y=21.3 mm; nut occupies Y=15.8..17.4 mm, giving the full 1.6 mm engagement and **3.9 mm exposed thread overhead**. No extra lower fastening plate is required. Install motor/stock plate/pinion first as in Base 20, seat fingers/gears over sleeves, then washers/bolts and nuts. The 6 mm hollow nut-driver envelope and 2.5 mm lower hex-driver shaft clear in CAD. The two original motor-ear screws still need a 10° driver tilt; actual PH0 engagement and tool handles remain unverified.

**Do not treat retention as strength certification:** sleeve wall is only **0.4 mm**, compressed between washer and base. Bolt bending/shear, sleeve crushing, nut loosening/locking method, bearing friction/wear, key strength, resin tolerances, thread fit, supports and cable bend need physical investigation. No motor was actuated and no load/grip force is claimed.

## Acceptance evidence — mechanical checks pass, human fit fails

`check_geometry.py` passes twelve watertight single-body print/part meshes, genus, 121 motion poses ×105 pairs = **12,705** intersections (no pair exclusions), driver paths, actual hardware seating/phase controls and local retention controls. Stroke remains 0–30° per jaw, 37.5° servo travel. Collision checks are sampled, not a continuous proof.

The additional tests in `Scripts/test_finger_plane_constraints.py` first reproduce Base 20's excessive support footprint, preserve an earlier rejected four-post cap study, and verify this version removes off-pivot material without changing the jaws. All new dimensions live in `params.json`; Tune still regenerates real geometry.

**The whole-hand acceptance screen fails.** Complete WebXR reference skin, palm, wrist and all digits are animated using the same `fingerContacts`/fixed-wrist solver as the live preview. At the 50% outside-contact station, reference hand lengths 181.1 and 193.3 mm miss contact by about 12 mm at worst; skin vertices intersect CAD at 5/13 and 7/13 poses. This may reflect pose/solver assumptions as well as genuine interference; it is not accepted ergonomics. The generic hand is narrow (~78 mm breadth at 187.2 mm length) and is not Jake's measured hand.

Open `two_pivot_acceptance.html` from the published gallery for full motion and Copy fit report. Saved frames, whole-skin screening, reproduction commands, rejected candidate and coordination contract are in `../../../cad/validation/voice-550038ca/README.md`. The separate voice-3f6ae8e1 hand study owns subsequent anatomical solver changes; this CAD task shares the same meshes and pose definition.
