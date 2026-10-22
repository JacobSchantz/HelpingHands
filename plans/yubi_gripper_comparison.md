# YUBI and the UMI-family grippers: most data, smallest size

voice-7b719c5b, 2026-10-21 (second pass adds Aug–Oct 2026 releases). Research only, no CAD changed.

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
collected 24/7 over two months (paper, June 2026). Since then it has grown to ≈17,854 h in five
gated Hugging Face parts, open only to UMI Arena teams (§2). The target is 20,000 h.

Because YUBI has a single design, I ranked it against the other handheld gripper platforms
in the same family, which is what the question is really about.

## 2. Ranked by how much data was collected (updated 2026-10-21, second pass)

Jake was right that the first pass was stale. Its newest dataset was FastUMI-100K from Oct 2025, and
it missed everything released from August to October 2026. The biggest change: **YUBI's full
corpus is now on Hugging Face**. It comes in five gated parts (terms dated Aug 31 2026), and the
parts add up to more than the paper's 8,434 h. Hours below come straight from each dataset card.

| YUBI part (HF `airoa-org/…`) | Hours | Episodes | Tasks |
| --- | --- | --- | --- |
| `yubi-corl2026-umi-arena` (initial, Aug) | 579.9 | 336,543 | n/a |
| `…-01-6k6` | 6,588.1 | 3,089,390 | 5,377 |
| `…-02-2k1` | 2,075.4 | 1,672,464 | 921 |
| `…-03-2k0` | 2,013.2 | 961,059 | 805 |
| `…-04-3k9` | 3,934.7 | 1,940,597 | 1,358 |
| `…-05-3k2` | 3,242.3 | 1,237,274 | 5,849 |
| **Parts 1–5 total** | **≈17,854** | **≈8.9M** | |

Access: only for UMI Arena competition teams that sign the NDA; for competition use only; no
redistribution; copies must be deleted afterwards. The Arena site still says the full release
(≈20,000 h) is "ongoing". So the data exists, but we cannot pretrain on it for our own work.

Every handheld-gripper corpus, newest numbers:

| # | Gripper (device) | Collected | Publicly downloadable | License | Date | Source |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | **NeoteAI TacUMI** (visuotactile UMI, 2 gel cams per gripper) | **30,000+ h** NeoData across 6 embodiments (UMI is one of them), 450 tasks | **5,000+ h** OpenNeoData, 200k+ traj., 257 tasks (gated: share email) | CC BY-NC-SA 4.0 | Aug 30 2026 | [arXiv 2608.29601](https://arxiv.org/abs/2608.29601), [HF](https://huggingface.co/datasets/NeoteAIEmbodied/OpenNeoData) |
| 2 | **YUBI Glove** (Toyota/AIRoA) | **≈17,854 h** across 5 HF parts, target 20,000 h | none: gated to UMI Arena teams | AIRoA limited-access ToU | Aug 31 2026 | HF cards above, [arXiv 2606.10244](https://arxiv.org/abs/2606.10244) |
| 3 | **GenRobot RealOmni** | 10,000+ h, 1M+ clips, 3,000 homes, 10 tasks | gated HF (`genrobot2025/10Kh-RealOmin-OpenData`) | check the card | Jan 2026 | [HF](https://huggingface.co/genrobot2025/datasets) |
| 4 | **Daimon DM-DataClaw** (+DataDex; TacClaw is the tactile deploy gripper) | 10,000+ h, 1M episodes, 1,000+ task types | **1,000 h** (Daimon-Infinity, first slice) | CC BY-NC-SA 4.0 | Oct 14 2026 | [arXiv 2610.20320](https://arxiv.org/abs/2610.20320), [HF](https://huggingface.co/datasets/daimonrobotics/Daimon-Infinity) |
| 5 | **Tencent fingertip UMI** (optical mocap) | 10,000+ h | **2,163 h**, 250,304 episodes, 70+ tasks | **CC BY 4.0** | Jun 12 2026 | [HF](https://huggingface.co/datasets/tencent/Hy-Embodied-0.5-VLA-Data) |
| 6 | **RDT2's rebuilt UMI** | 10,000+ h, 100+ scenes | example set only | Apache-2.0 (example) | Feb 2026 | [arXiv 2602.03310](https://arxiv.org/abs/2602.03310) |
| 7 | **HiFi-UMI** (Simple AI) | 6,000 h (2k public + 4k internal) | **2,000 h**, 6 views | **CC BY 4.0** | Jul 28 2026 | [arXiv 2607.25895](https://arxiv.org/abs/2607.25895), [HF](https://huggingface.co/datasets/simple-world-lab/HiFi-UMI-2K) |
| 8 | XRZero-G0 / QUANXTA Zero-G1 (X Square; headband + 2 grippers) | 2,000 h (G0) | not stated | commercial | Apr / Jul 2026 | [arXiv 2604.13001](https://arxiv.org/abs/2604.13001), [Zero-G1](https://x2robot.com/en/news/6a46341cc7feadddbc603a33) |
| 9 | FastUMI | ≈600 h (FastUMI-100K) | yes | not found | Oct 2025 | [arXiv 2510.08022](https://arxiv.org/abs/2510.08022) |
| 10 | Original UMI | ≈12 h | yes | MIT code | Feb 2024 | [arXiv 2402.10329](https://arxiv.org/abs/2402.10329) |

Not ranked because the data is closed: Xiaomi-Robotics-1 (100k+ h of UMI trajectories; only the
model is open) and Generalist GEN-0.

New hardware from Jun–Oct 2026 that has no big dataset yet: **PolyUMI** (Northwestern, Sep 24;
wireless handheld with tactile and contact audio; open code), **KIWI** (Autel, Sep 19; two Insta360 X5
cameras, chopstick fingers, open hardware), **UMI ver.2** (穹明智能, Jul; AGPL-3.0, low-cost rebuild),
**iPhUMI** (Stanford, Jun 29; iPhone as the tracker and camera), and **WT-UMI** (Georgia Tech, Jun).
Most of the October AIRoA papers (YUBI-STAG, RoboPace, YUBI-Real2Sim) are policies and benchmarks
trained on YUBI data, not new grippers.

## 3. Ranked by size (smallest first)

| # | Gripper | Size | Mass | Source |
| --- | --- | --- | --- | --- |
| 1 | **YUBI Glove ver2** | 105 × 167–188 × 198 mm (measured from the STEP) | **≈319 g** with Quest tracker (≈200 g without) | STEP + paper |
| — | YUBI robot gripper (robot side, not handheld) | 92 × 117 × 150 mm (measured) | XM430 82 g + print | STEP |
| 2 | **Daimon DM-DataClaw** | 215 × 124 × 172 mm | ≈388 g per gripper; 0–100 mm stroke | [retailer](https://aifitlab.com/products/daimon-robotics-dm-dataclaw-gripper) (secondary, $13.6k) |
| 3 | FastUMI Pro | 270 × 162 × 215 mm | ≈600 g | [retailer](https://aifitlab.com/products/lumos-fastumi-pro) (secondary) |
| 4 | UMI original | not stated | ≈780 g; >900 g with a VR controller | UMI paper; YUBI Table 1 |
| 5 | FastUMI Go | ≤300 × 170 × 250 mm | ≤800 g | [retailer](https://aifitlab.com/products/lumos-fastumi-go) |
| — | TacUMI, Tencent fingertip UMI, RDT2, HiFi-UMI, Zero-G1, PolyUMI ("lightweight"), KIWI | not published | not published | |

On the yubi-hw repo, the newest commit (Sep 21 2026, PR #34 "update YUBI v2") refreshed the ver2 files.
Its other changes since June add Franka, OpenArm and Unitree G1 flanges. It has no ver3 and no tagged releases.

For scale: our Aero Hand is 198 × 95 × 53.5 mm and under 400 g (`aero_hand_on_b601.md`),
about the same length and weight as the YUBI Glove.

**Answer (updated):** YUBI is still the smallest gripper. With ≈17,850 h it is now the
**second-largest corpus** that exists, behind TacUMI's 30k h (which is multi-embodiment, not UMI
only). We cannot use YUBI's data outside the competition. The largest sets we can actually
download are **OpenNeoData, 5,000 h** (NC, visuotactile) and **Tencent Hy-Embodied, 2,163 h**,
plus **HiFi-UMI-2K, 2,000 h**; the last two are CC BY 4.0, so they also allow commercial use.

## 4. What fits Helping Hands

- **For the Aero Hand: YUBI's grip is the closest human-to-robot mapping in the family.** The
  thumb drives one jaw and the index and middle fingers drive the other, which is the Aero
  Hand's thumb-to-two-finger pinch. A YUBI episode's aperture could drive that pinch
  synergy. This is a retargeting idea and has not been tried.
- **For a VLA / MolmoAct2 zero-shot direction:** RDT2 is the paper that shows zero-shot
  cross-embodiment from UMI data. YUBI shows one π0.5 policy running on UR, Franka and ELEY.
  Both need the robot to carry the *same* fisheye wrist camera and jaw geometry as the
  collector, so an Aero Hand would see a different image than any of this data.
- **To pretrain or fine-tune on it:** YUBI's ≈17,850 h is limited to competition use (policy
  submissions close Nov 2). The open options are HiFi-UMI-2K and Tencent Hy-Embodied (CC BY 4.0, ≈4,160 h together)
  and OpenNeoData (5,000 h, NC, with tactile) and Daimon-Infinity (1,000 h, NC).
- **The YUBI robot gripper does not bolt on as-is.** It is a Dynamixel XM430 with UR5e, Franka,
  OpenArm and G1 flanges. Putting it on the reBot would need a Mount 1 tool plate for its
  case. I did not check that interface.
