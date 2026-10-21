# YUBI and the UMI-family grippers: most data, smallest size

voice-7b719c5b, 2026-10-21. Research only, no CAD changed.

Jake heard about "UB, an open platform for large-scale robotics collection". It is almost
certainly **YUBI** ("you-bee"), the *Yielding Universal Bidigital Interface*
([arXiv 2606.10244](https://arxiv.org/abs/2606.10244), [yubi.airoa.io](https://yubi.airoa.io/)).
Toyota's Frontier Research Center and AIRoA (the AI Robot Association, Japan) built it.
They release the gripper hardware, the collection software and the dataset as one stack,
and AIRoA runs the CoRL 2026 "UMI Arena" around it
([umi-arena.airoa.io](https://umi-arena.airoa.io)). `handheld_gripper.md` §1a already
lists it. This note answers the two new questions.

## 1. The gripper designs inside YUBI

YUBI publishes **one** finger-aligned design with a handful of variants. The bounding boxes
below are my measurements of the published SolidWorks STEP assemblies
([toyota/yubi-hw](https://github.com/toyota/yubi-hw), CERN-OHL-W v2), using OCCT
(`cad/blender/.venv`).

| Variant (repo file) | What it is | Bounding box (measured) | Mass |
| --- | --- | --- | --- |
| **YUBI Glove ver2** (`YUBI Glove Assy_ver2_R/L`) | The handheld collector. The thumb drives one jaw and the index and middle fingers drive the other, with a support grip for the other fingers. It has an ELP 180° fisheye wrist camera, an AS5601 encoder on an ESP32-C6, and a Quest Touch Plus controller for 6-DoF tracking. | **105 × 188 × 198 mm** with the Quest controller | ≈200 g + 119 g controller = **≈319 g** (paper) |
| Glove ver2 **opt1** | The same glove with the `FINGER ATTACHMENT_Glove` option and t20/t30 pads (the controller is not in this assembly) | 105 × 167 × 198 mm | not stated |
| Glove ver2 **opt2** | opt1 with the v2 pads and a TPU "Fin" | 105 × 167 × 202 mm | not stated |
| **YUBI Gripper ver2** (`YUBI Gripper Assy_Dynamixel_ver2`) | The robot-side twin. One Dynamixel XM430-W350-R drives two z30 spur gears, with the same fisheye camera and the same pads, so the data transfers. Flanges are provided for UR5e, Franka, OpenArm and Unitree G1. | **92 × 117 × 150 mm** including the UR5e flange | not stated (XM430 alone is 82 g) |
| Pads t20 / t30 (L/R, v1/v2) | Swappable finger pads: t20 is the inner pad and t30 the outer pad | n/a | n/a |

Every hour in YUBI's dataset comes from the Glove; the paper does not break data down by
variant. Data totals are 8,434 h, 1.20M episodes, 119 tasks, 179 operators and 22 desks,
collected 24/7 over two months. The license is CC-BY-NC-SA-4.0. Only about 580 h has been
released so far, and only to UMI Arena teams who sign a data agreement. The target is
20,000 h.

Because YUBI has a single design, I ranked it against the other handheld gripper platforms
in the same family, which is what the question is really about.

## 2. Ranked by how much data was collected

| # | Gripper | Data | Open? | Source |
| --- | --- | --- | --- | --- |
| 1 | **RDT2's rebuilt UMI** (≈100 devices, stronger materials, IR tracking) | **≈10,000 h**, 100+ homes, in the wild | Paper calls it open; only an example set is on HF (Apache-2.0), and I could not find the full corpus | [arXiv 2602.03310](https://arxiv.org/abs/2602.03310), [project](https://rdt-robotics.github.io/rdt2/) |
| 2 | **YUBI Glove** | **8,434 h, 1.20M episodes, 119 tasks** | Hardware CERN-OHL-W, software Apache-2.0, data NC and gated (≈580 h out) | [arXiv 2606.10244](https://arxiv.org/abs/2606.10244) |
| 3 | **HiFi-UMI** (Simple AI; head-mounted stereo SLAM, two fisheyes per hand) | 2,000 h public (HiFi-UMI-2K) + 4,000 h internal pretraining | Dataset on HF, license not stated; no hardware repo | [arXiv 2607.25895](https://arxiv.org/abs/2607.25895), [HF](https://huggingface.co/datasets/simple-world-lab/HiFi-UMI-2K) |
| 4 | **XRZero-G0** (X-Square; VR + "dual specialized grippers") | 2,000 h robot-free | Repo exists, license not stated | [arXiv 2604.13001](https://arxiv.org/abs/2604.13001) |
| 5 | **FastUMI** (T265 tracking) | FastUMI-100K: 100k+ trajectories ≈ 600 h, 54 tasks; FastUMI: 10k demos, 22 tasks | License not found; T265 is end-of-life | [arXiv 2510.08022](https://arxiv.org/abs/2510.08022), [2409.19499](https://arxiv.org/abs/2409.19499) |
| 6 | PrimeBot UMI subset | ≈205 h | CC BY-SA 4.0, LeRobot v3 | `robot_datasets.md` |
| 7 | **UMI** (original, Chi et al.) | ≈12 h, 4–5 tasks (cup set 1,400 demos) | Code MIT | [arXiv 2402.10329](https://arxiv.org/abs/2402.10329) |
| 8 | ActiveUMI, exUMI, UMI-3D, DexUMI | Task-sized sets (6 tasks / 1M tactile frames / 3,500 demos) | Varies | §1a of `handheld_gripper.md` |

Closed systems with more data are not ranked because we cannot get them:
Generalist GEN-0 (UMI-style pincers) and Xiaomi-Robotics-1 (100k+ h). See `handheld_gripper.md`.

## 3. Ranked by size (smallest first)

| # | Gripper | Size | Mass | Source |
| --- | --- | --- | --- | --- |
| 1 | **YUBI Glove** | 105 × 167–188 × 198 mm (measured from the STEP) | **≈319 g** with tracker | STEP + paper |
| — | YUBI robot gripper (robot side, not handheld) | 92 × 117 × 150 mm (measured) | XM430 82 g + print | STEP |
| 2 | FastUMI Pro | 270 × 162 × 215 mm | ≈600 g | [retailer](https://aifitlab.com/products/lumos-fastumi-pro) (secondary) |
| 3 | UMI original | not stated | ≈780 g; >900 g with a VR controller | UMI paper; YUBI Table 1 |
| 4 | FastUMI Go | ≤300 × 170 × 250 mm | ≤800 g | [retailer](https://aifitlab.com/products/lumos-fastumi-go) |
| — | RDT2, HiFi-UMI, XRZero-G0, ActiveUMI, exUMI | not published | not published | |

For scale: our Aero Hand is 198 × 95 × 53.5 mm and under 400 g (`aero_hand_on_b601.md`),
about the same length and weight as the YUBI Glove.

**Answer:** YUBI is the smallest gripper and ranks second for data. Of the corpora that have started to
release, it is the largest in total hours, though only ≈580 h is out (gated), and HiFi-UMI-2K's 2,000 h is the biggest fully public set. RDT2's UMI has slightly more hours, but I could not
confirm its full release, and it is a heavier pistol grip.

## 4. What fits Helping Hands

- **For the Aero Hand: YUBI's grip is the closest human-to-robot mapping in the family.** The
  thumb drives one jaw and the index and middle fingers drive the other, which is the Aero
  Hand's thumb-to-two-finger pinch. A YUBI episode's aperture could drive that pinch
  synergy. This is a retargeting idea and has not been tried.
- **For a VLA / MolmoAct2 zero-shot direction:** RDT2 is the paper that shows zero-shot
  cross-embodiment from UMI data. YUBI shows one π0.5 policy running on UR, Franka and ELEY.
  Both need the robot to carry the *same* fisheye wrist camera and jaw geometry as the
  collector, so an Aero Hand would see a different image than any of this data.
- **To pretrain or fine-tune on it:** YUBI (NC, gated; ≈580 h through UMI Arena; policy
  submissions close Nov 2) and HiFi-UMI-2K (public on HF) are the obtainable ones.
  YUBI's NC license rules out commercial use.
- **The YUBI robot gripper does not bolt on as-is.** It is a Dynamixel XM430 with UR5e, Franka,
  OpenArm and G1 flanges. Putting it on the reBot would need a Mount 1 tool plate for its
  case. I did not check that interface.
