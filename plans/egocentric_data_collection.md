# Open egocentric data collection: glasses, what buyers pay for, and a minimum spec

Status: RESEARCH (2026-10-20, voice-2a989d97). Nothing bought, nothing built.

Jake's plan: an open-source data collection system. People wear **camera
glasses** and work with the **handheld gripper** (Base 11's STS3215 logs the
finger angle, `Two Finger Gripper/versions/v311_generalist_motor_choice/record_grip.py`),
or they wear the glasses alone. The hardware is sold cheaply or given away, and
the **data is sold**.

This doc answers three questions: (a) which glasses work, (b) what data buyers
look for and pay, and (c) which prior art to learn from. It ends with a
recommendation. It builds on, and doesn't repeat:

- `egocentric_datasets.md`: the open egocentric datasets (EgoLive, Open-AoE, EgoDex, Ego4D …) and their license traps.
- `robot_datasets.md`: the open robot datasets, including handheld-gripper data (GenRobot, FastUMI, PrimeBot UMI).
- `handheld_gripper.md`: UMI, Grabette, YUBI, UMI-3D and the other handheld systems, plus the retargeting pilot.
- `shared_stereo_glasses.md`: why no cheap consumer glasses have a readable stereo pair, and the ELP stereo board.
- `hand_1_0.md` §3: **Decided (Jake, 2026-10-16)**: the only cameras are a stereo pair at eye height. The demonstrator wears it, and the robot carries the same pair at head height.

Source quality: product specs come from vendor pages or launch coverage as of
today. **Prices and pay rates come mostly from vendor and marketplace blogs**
that have a stake in the market, so treat them as ranges rather than quotes.
Anything I couldn't confirm is marked *(unverified)*.

---

## 0. Answer in one paragraph

**No glasses you can buy meet the spec.** The consumer glasses (Ray-Ban Meta,
Mentra Live, Brilliant Halo) are mono, rolling-shutter and phone-tethered, and
none exports synchronized IMU data. Ray-Ban Meta's developer stream is capped at
720p30 over Bluetooth. The glasses with real sensors (Aria Gen 2, Snap Specs,
Pupil Neon) either can't be bought, lock capture inside a vendor sandbox, or
cost $2–6k. A head-mounted GoPro is UMI's proven answer, but it is mono with a
rolling shutter, so it can't be the same camera the robot uses.
**Recommendation: build our own head rig in the Ego-OSCAR pattern.** That means
a hardware-synced global-shutter stereo USB module, an IMU and a small Linux
board on a visor or glasses frame, at about $200 of parts with Apache-2.0
software. The same stereo module goes on the robot's head, which is the
`hand_1_0.md` §3 decision. **Record MCAP as the master copy and ship LeRobot v3
as the sales format.** Buyers pay roughly **$15–40 per accepted hour** for
egocentric video today, with listed prices up to ~$135. What raises the price
is exactly what our rig adds over phone or glasses footage: calibrated stereo,
measured time sync, real action labels from the gripper, and a clean
commercial consent chain. Supply is growing fast and per-hour prices are
falling, so **plain video is a commodity. Synchronized stereo plus gripper
actions is not.**

---

## 1. Camera glasses: which ones work

What the job needs, from §4's spec: **two** scene cameras at eye height with a
known baseline, global shutter (or at least a fast rolling shutter), ≥110° FOV
so both hands stay in view, an IMU on the same clock, **raw files we own**
pulled off over USB or Wi-Fi with no vendor cloud, ≥2 h runtime, and a price
we can afford to give away.

| Device | Cameras (scene) | Raw access / lock-in | IMU, depth, eyes | Battery | Price / availability | Verdict |
|---|---|---|---|---|---|---|
| **Meta Aria Gen 2** | 1 RGB (Sony IMX681, 12 MP, reported 4032×3024 @ 24 fps, 133°×99° *(single source)*) + 4 global-shutter CV/SLAM cams, 80° stereo overlap | Full raw VRS files + `projectaria_tools`; on-device VIO, hand and eye tracking | IMU, eye tracking (2 ET cams), PPG, contact mic | 6–8 h | **Not for sale.** Rolling application (academic or corporate forms); broad rollout targeted Q2 2026. Data released by Meta is CC BY-NC | Best sensors in a glasses form. But it's research-only, you can't give it away, and the RGB is mono (the SLAM cams are monochrome). It doesn't fit a product that sells data. **Use it as a reference, not a product.** |
| **Ray-Ban Meta (Gen 2)** | 1 RGB; on-device recording 3K@30 / 1200p@60, **vertical**, clips ≤3 min | Device Access Toolkit (iOS/Android, developer preview): stream **≤720p @ 30 fps over Bluetooth**, quality drops when bandwidth is short. Publishing apps targeted for 2026 | IMU not exposed; no depth, no eye tracking | ~8 h | ~$379+ *(unverified)*; buyable | Mono, short clips, a throttled stream, and the vendor app sits in the path. **Glasses-only tier at best.** |
| **Mentra Live** | 1 RGB 12 MP, 1080p video, ~112–119° FOV | Open SDK (BLE) to drive the camera from our own phone app. Sources disagree on whether MentraOS is open source | No IMU export found, mono | 12+ h claimed | $299 at launch, $449 now (Sep 2026 guide) | **The most open consumer glasses**, and wide-angle. Still mono. The candidate if we ever want a cheap, normal-looking glasses-only tier (§4). |
| **Brilliant Labs Halo** | A "low-power optical sensor", not a video camera; resolution unstated | Open source (Zephyr + Lua on GitHub), but **stores no rich media** by design | 6-axis IMU | 14 h | $299 | **Can't record video.** Out. |
| **Snap Specs (consumer, 2026)** / Spectacles 5 | Two color cameras (left, right). Camera Module API: a lower-res continuous stream, stills fixed at 3200×2400 | Lens Studio sandbox (JS/TS), no APK sideloading; camera API marked **experimental**; using internet modules restricts camera access | Stereo pair, 6DoF tracking | 4 h (+20 h case) | $2,195, shipping fall 2026 | The only real stereo glasses on sale, but capture is sandboxed and battery-short at 10× our budget. **Out.** |
| **Xreal (Air/One + Eye)** | 1 RGB add-on | SDK 3.0 (Unity XR plugin) can use it as a video source; the LED and shutter sound can't be turned off | No IMU export documented for capture | — | — | Built as an AR display, not a recorder. **Out.** |
| **Pupil Labs Neon** | 1 scene cam 1600×1200 @ 30 Hz, 103°×77° | "All raw, intermediate and final data, no licenses required" | 9-axis IMU, research-grade **eye tracking** | — | from €5,950 | Open and honest, but the price covers eye tracking we don't need. **Out** unless a buyer specifically pays for gaze. |
| **Head-mounted GoPro** (UMI's camera, HERO12/13 + Max Lens Mod 2.0) | 1 RGB, up to 4K60, 155–177° fisheye | Plain MP4 on SD card; GPMF telemetry carries the IMU (UMI's ORB-SLAM3 reads it) | IMU via GPMF; mono, **rolling shutter** | ~1–1.5 h *(unverified for 4K60)* | ~$400 + $95 lens mod | **Proven** (UMI, FastUMI, PrimeBot's UMI subset). But it's mono and rolling-shutter, so it breaks the "same stereo pair on the robot" rule, and the GoPro has to be retired when it isn't sold anymore. |
| **Ego-OSCAR** (FPV Labs, arXiv 2608.08285, Aug 2026) | **Hardware-synced global-shutter stereo** (Dexcin UVC module, 2 OmniVision sensors), 1280×720 per eye @ 30 fps, **126°** per sensor, **42 mm** baseline | Our own files: V4L2 + FFmpeg on a Radxa SBC, segmented video + IMU CSV + `calibration.json` to SD (~16–18 h), upload daemon to S3/GCS/NAS | ICM-20948 IMU @ 120 Hz, timed by an ESP32-S3 off the camera's start-of-exposure pin; **measured 700 µs cam–IMU residual** (Kalibr); stereo depth via SGBM/RAFT-Stereo | 5–6 h on a hot-swap 10 Ah power bank | **~US$200 BOM**, all off-the-shelf; software Apache-2.0, CAD + BOM + firmware released | **The only open device that matches the job.** Proven in the field: 1,462 sessions, ~550 h per camera, 25 contributors, 96% of sessions usable. Weak points: ~280 g on a sport visor (not glasses), thermal shutdown above 35 °C past 90 min (fixed by adding a heatsink), and a cable-strain failure (fixed by reinforcing the connector). |

Two notes the table can't hold:

- **Stereo from consumer glasses is still not available.** `shared_stereo_glasses.md`
  reached that conclusion on 2026-10-12 for anything under $100, and
  today's sweep extends it to every price point except Snap's sandboxed
  $2,195 Specs and Meta's not-for-sale Aria.
- **The ELP 960P board** from `shared_stereo_glasses.md` ($84, rolling shutter,
  no published skew) is the cheaper sibling of Ego-OSCAR's Dexcin module. The
  global-shutter part matters here. People move their heads fast while working,
  and with a rolling shutter each row is exposed at a different time, which
  corrupts visual-inertial tracking. Ego-OSCAR picked global shutter for
  exactly that reason.

---

## 2. What data buyers look for

### 2a. Who's buying

- **Frontier labs, robot-model companies, and world-model/video companies**
  are the three buyer types named in a 2026 market essay. There are **many
  sellers and a handful of buyers**. On the model side, the companies already
  scaling human wearable data (see `handheld_gripper.md` §0) are Generalist
  (GEN-1: ">500k h" from "low-cost wearable devices on humans"), Sunday, Skild
  and Xiaomi. NVIDIA's EgoScale and the EgoVerse consortium are research
  buyers.
- **Brokers and collectors in between**, which are our competitors as much as
  our channel:
  - Scale AI's Physical AI engine includes "Scale Harness", a *robotless
    egocentric* collection platform. Scale claims >1,000 h/day and 100–150k h
    delivered in 2025.
  - Data-ops firms: Encord, Objectways, Appen, Labellerr.
  - Egocentric specialists and marketplaces: Lightwheel (EgoSuite, ships
    LeRobot v3 + MCAP), Build AI (Egocentric-100K), JD Cloud's robot-data
    market (EgoLive), truelabel, claru, roboticscenter.ai.
  - Gig apps that pay individuals to record: micro1, Waffle, Atlas Capture,
    Human Archive, and Kled AI for general data.

### 2b. What they pay, and what contributors are paid

| Price point | Range | Source (all vendor or press, unverified) |
|---|---|---|
| Raw egocentric capture, sold | **$15–22 / finished hour** | Dexset, egxodata (seller-reported) |
| Fully annotated egocentric, sold | **$30–40 / hour**; $30–49 per *accepted* hour | Dexset, egxodata |
| Wearable capture, buyer rate | $25–60 / collected hour | teahose |
| Marketplace list price | $90–135 / hour, 10 h minimum | roboticscenter.ai |
| Per episode (custom capture) | $50–500 / episode | truelabel |
| Teleop robot data, for contrast | >$100 / hour | Stellaris VP |
| Contributor pay, India | $1–4.20 / hour; **fell ~30% Jan→Jun 2026** as suppliers piled in | TechCrunch, StartupFeed |
| Contributor pay, US/global apps | $3–10 typical, $18–30 on some missions | ABC, remowork |

What this means for the business:

1. **Plain mono chore video is a commodity**, and its price is falling.
   Competing on hours of it means competing with gig workers paid $1–4/h.
2. **Buyers price "per accepted hour against a spec."** Truelabel says there's
   no flat per-hour rate without a spec. Rejected hours earn nothing, so
   automated QA (§4) is part of the product, not an extra.
3. **Teleop robot data costs >$100/h.** Data with real action labels sits
   between teleop and plain video. Our gripper encoder supplies those action
   labels, so that's the gap we can price into.

### 2c. What they check: format, fidelity, rights

**Format.** No single standard exists yet. Sellers ship LeRobot (parquet +
MP4), MCAP/ROS 2 bags, raw MP4 + sensor JSON, HDF5 and RLDS. Lightwheel ships
**LeRobot v3 + MCAP**, and Ego-OSCAR ships segmented video + IMU CSV +
calibration JSON. Buyer guides warn that **naming a format isn't enough**: the
spec has to pin the exact version, fields, episode semantics, video encoding
and timestamp convention. Two gaps to know about:

- **LeRobot v3 doesn't officially support depth yet.** Depth would have to be a
  custom extension, so we ship stereo plus calibration and let the buyer
  compute depth.
- **Hand-pose fields differ across LeRobot datasets.** Some use 21 joints × 6
  DoF, others use keypoints + finger angles.

**Fidelity** (buyer guides, cross-checked against what the strong datasets ship):

| Item | What buyers ask for |
|---|---|
| Time sync | A shared timebase, a **measured** residual (not a "synced: yes" flag), a sync event at the start and end of each session, and skew under half a frame period (~16 ms at 30 fps), tighter for contact-rich tasks |
| Calibration | Intrinsics + extrinsics per **device, mount and session**, each with a validity interval. A session that drifts out of tolerance ships as mono footage, not as metric 3D |
| Resolution / fps | 30 fps is the floor in every 2026 set we reviewed. 720p per eye is accepted (Ego-OSCAR, EgoLive downsamples for training); 1080p+ is preferred for hand pose |
| Actions / proprio | Ego camera trajectory (6-DoF head pose), 3D hand pose or **gripper width + EE pose**. This is what separates "action data" from "video" in price |
| Depth | Stereo or RGB-D increasingly expected (EgoLive, HiFi-UMI, Ego-OSCAR) |
| Language | Episode instruction + dense segment captions. Ego-OSCAR has ~380 labeled segments per hour. VLM-written captions with human review are acceptable (EgoLive) |
| Diversity | Many environments, many wearers, long-tail tasks. EgoVerse found gains scale only when the data is **aligned with the target task**, so diversity *within* a task family beats random hours |
| Hands in view | Ego-OSCAR reports 94% of frames with a detected hand at 126° FOV. A narrower lens loses hands |

**Rights, consent, PII.**

- **Consent artifact per session.** Truelabel ships one with every session,
  covering commercial training use, plus a location release where needed.
  Ego-OSCAR got informed consent from the wearer *and* the environment owner.
- **Bystander faces and screens blurred before anyone annotates.** Meta's
  **EgoBlur** model is the standard tool. Wearer consent gets planned and
  bystander consent gets forgotten, so plan both.
- **Keep the consent chain clean.** Public corpora are mostly NC or
  research-only (`egocentric_datasets.md` §3), so a clean commercial chain is
  itself a selling point.
- **Legal flags, not legal advice.** BIPA (Illinois) covers face geometry, so
  never compute or store face embeddings. GDPR treats bystander images as
  personal data, and blurring may not count as anonymisation. Exclude minors.
  Get a lawyer's read before the first sale.

---

## 3. Prior art to learn from

`handheld_gripper.md` §1/§1a already covers UMI, FastUMI, Grabette, YUBI,
UMI-3D, HiFi-UMI and PolyUMI, and `egocentric_datasets.md` §4 covers EgoScale,
HumanEgo, Ego2Robot and H2R. Below are the ones that add something about
**glasses + collection at scale**.

| Project | What to copy | What not to copy |
|---|---|---|
| **UMI** (Chi et al. 2024) | Method: action = end-effector pose + gripper width, filtered against the target robot's kinematics so the data stays robot-agnostic; fiducials on the fingers to read width; IMU fused into SLAM | The camera lives on the gripper (our rule forbids that); mono fisheye + mirrors as fake stereo; the GoPro dependency |
| **DexUMI** (2025) | The exoskeleton matches the robot hand's kinematics, and the human hand is **inpainted out and replaced by the robot hand** in video. That's a Hand 2.0 idea | Dexterous-hand specific; the hardware license wasn't confirmed in this sweep |
| **EgoMimic** (GT/Stanford, Aria) | Co-training on human + robot data gave **+34–228%** over robot-only. It uses the side SLAM cams to track hands outside the RGB view, so wide FOV matters | It's built on Aria, which we can't buy or give away |
| **EgoZero** (Aria) | A morphology-agnostic 3D state-action space; 70% zero-shot on a Franka from **20 min of human data per task**. Strong evidence that glasses-only data carries action signal | Research-scale; Aria again |
| **Ego-OSCAR** (FPV Labs, 2026) | **Our hardware template.** Off-the-shelf parts, no custom PCB; an LED that flashes on the 60th exposure pulse pins IMU time to video frames; a watchdog with a buzzer when recording stops; an upload daemon; a 6-month field deployment through a contributor network in India; consent + environment-owner release; faces and screens blurred; ships annotated, not raw | Visor mount at ~280 g; 720p only; no action labels (it's a glasses-only system) |
| **EgoVerse** / EgoDB | Its tooling for ingesting, QA'ing and browsing many contributors' data is worth reading before we write our own. Also its finding that gains come from task-aligned data | — |
| **Grabette / Gripette** (Pollen, Apache-2.0) | Post-processing straight to LeRobot; the same STS3215 servo on both handheld and robot ends | OAK-D on the gripper as its tracker |
| **Generalist / Sunday / Build AI / Human Archive** | Proof that the business exists: wearables on many people, data sold or used in-house | All closed. Their hardware details are press-only |

The gap none of them fill: **an open rig whose glasses camera is the robot's
camera, plus a cheap gripper whose encoder is the robot's gripper motor.**
Ego-OSCAR is open stereo glasses with no actions. UMI and Grabette are open
grippers with the camera in the wrong place. Our system combines the two.

---

## 4. Recommendation

### Glasses

**Build an Ego-OSCAR-derived head rig. Don't buy consumer glasses.**

1. Start from Ego-OSCAR's BOM and firmware (Apache-2.0): the Dexcin
   global-shutter stereo UVC module (126°, 42 mm), an ICM-20948 IMU, an ESP32-S3
   for exposure-pulse timing and the watchdog, and a Radxa SBC with hardware
   H.264, powered from a USB-PD power bank.
2. **Add the gripper to the same box.** The STS3215 sits on the same Feetech
   bus the SO-101 uses. The Radxa reads it alongside the cameras (the
   `record_grip.py` logic, timestamped on the same host clock), so the gripper
   log and the video share one timebase. The sync event is a hard close of the
   jaws at the start and end of each session, visible in video and sharp in
   the encoder.
3. **Put the identical module on the robot's head.** That's the
   `hand_1_0.md` §3 decision, and it's why we can't use any consumer glasses.
   The 42 mm baseline is narrower than a human's ~63 mm, but every recording
   and every robot run use the same baseline, which is what matters.
4. Mount it on a glasses frame or a light headband instead of a visor if the
   weight allows. That's the first CAD job, and it's a new part.
5. **Glasses-only tier:** the *same* rig without the gripper. Don't add a
   second, mono, consumer-glasses product. It would split the pipeline and sell
   at the commodity price. Revisit Mentra Live only if comfort turns out to be
   why contributors quit.

How to get the gripper's 6-DoF pose without a camera on the gripper (still
open): an AprilTag/ArUco cube on the handle, tracked by the head stereo pair,
chained with the head's own visual-inertial pose. This is UMI's
fiducial idea, moved to the head camera. It needs a pilot. Grabette's OAK-D
tracker is the fallback, but it puts a camera on the gripper.

### Data format

- **Master copy: MCAP**, one file per session. It holds every stream with its
  own timestamps (stereo H.264, IMU, gripper encoder, sync events) plus the
  calibration and consent records as attachments. Nothing gets resampled, and
  buyers who want raw get exactly this.
- **Sales/training format: LeRobot v3** exported from MCAP:
  - `observation.images.left/right` (MP4)
  - `observation.state`: head pose (7) + gripper finger angle
  - `action`: next gripper pose (7) + finger angle
  - the episode instruction as `task`, and segment captions as an extra field
  - a calibration JSON per episode

  It's the format our own training already uses (`training_pipeline.md`), and
  it's what Hugging Face, Lightwheel and PrimeBot ship.
- **RLDS / HDF5:** write a converter only when a buyer asks.
- Publish a frozen schema doc (fields, units, frames, timestamp convention,
  version) next to the exporter, because buyers reject "LeRobot" without one.

### Minimum spec (a session that misses any line is rejected automatically)

| # | Item | Minimum |
|---|---|---|
| 1 | Scene cameras | Hardware-synced **stereo, global shutter**, ≥1280×720 per eye, **≥30 fps** constant, ≥110° HFOV, fixed baseline identical to the robot head's |
| 2 | IMU | ≥100 Hz, timestamped on the camera's clock domain; **measured cam–IMU residual ≤1 ms** (Ego-OSCAR: 0.7 ms) |
| 3 | Gripper | STS3215 finger angle at **≥30 Hz** (aim for 100 Hz) on the same host clock; jaw-snap sync event at start and end; residual **≤16 ms** (half a frame) |
| 4 | Calibration | Stereo intrinsics + extrinsics per device and session, reprojection error **<0.3 px** (Ego-OSCAR reports <0.03); cam–IMU extrinsics (Kalibr); a validity interval. A session that fails ships as mono at a lower tier, or not at all |
| 5 | Pose | Head 6-DoF trajectory from stereo-inertial SLAM, plus per-frame tracking-valid flags |
| 6 | Coverage | A hand or the gripper in view in **≥90%** of task frames (Ego-OSCAR: 94% at 126°) |
| 7 | Session | ≥2 h runtime; a watchdog that buzzes if recording stops; no dropped frames >1% |
| 8 | Labels | One instruction per episode; segment captions (VLM draft + human check); success/fail flag |
| 9 | Rights | Signed wearer consent (commercial training, resale, retention) + environment-owner release per session; no minors; **faces and screens blurred (EgoBlur) before annotation**; no face embeddings stored |
| 10 | Format | MCAP master + LeRobot v3 export conforming to our published schema version |

### Business notes

- **Price tiers follow the spec.** Glasses-only stereo + IMU + captions sits
  at about the annotated-egocentric band ($30–40/h). Adding gripper actions +
  calibrated pose is the product nobody else sells cheaply, priced between
  that and teleop (>$100/h). Neither number is validated. Get one buyer quote
  on a sample before building more than a handful of rigs.
- **Open hardware, sold data, and the tension between them.** If the raw data
  were open it would compete with itself. Ego-OSCAR's answer was to open the
  hardware plus one annotated sample set. Copy that: open the rig, the
  exporter, the schema and a free sample, and sell the bulk under commercial
  license, with a revenue share to contributors.
- **The market is crowded and getting cheaper.** Contributor pay fell 30% in
  six months in India. Our edge is fidelity per hour, not hours.

---

## 5. Suggested next steps (not started)

1. **Order one Ego-OSCAR BOM (~$200)** and build it as published. Re-measure
   the 0.7 ms residual and the hands-in-view rate on our own tabletop tasks.
2. **Add the STS3215 read** to its recorder on the same clock, and verify the
   jaw-snap sync against video (target ≤16 ms).
3. **Pilot the gripper-pose tag cube** against the head stereo. Report pose
   error on a ruler-and-tape test before committing.
4. **Write the MCAP → LeRobot v3 exporter and the schema doc.** Check that
   `training_pipeline.md` can train on one exported episode.
5. **Record ~5 h, cut a sample, ask two brokers for a price** (e.g. truelabel
   and Lightwheel, or a direct robot-model company). That turns §4's price
   tiers from guesses into quotes.
6. Lawyer read on consent + BIPA/GDPR before the first paid hour.

## Sources

- Aria Gen 2: https://www.projectaria.com/glasses/ · https://ai.meta.com/blog/aria-gen-2-research-glasses-under-the-hood-reality-labs/ · Gen 2 pilot dataset (CC BY-NC) https://www.projectaria.com/datasets/gen2pilot/ · availability https://roadtovr.com/?p=173142 · RGB spec (single source) https://www.cloudspress.com/?p=616108
- Ray-Ban Meta Gen 2: https://about.fb.com/news/2025/09/ray-ban-meta-gen-2/ · Device Access Toolkit https://developers.meta.com/wearables/faq · https://www.uploadvr.com/meta-wearables-device-access-toolkit-public-preview/
- Mentra Live: https://9to5google.com/2026/01/15/mentra-live-smart-glasses-youtube-livestream/ · https://idevice.com/guide-text/mentra-live.md
- Brilliant Labs Halo: https://roadtovr.com/brilliant-labs-halo-smart-glasses-price-release-date/ · https://heise.de/-10506039
- Snap Specs: https://ppc.land/snap-specs-ar-glasses-set-for-fall-2026-launch-at-2-500/ · https://aiweekly.co/alerts/snap-launches-2195-specs-ar-glasses-at-awe-2026 · Camera Module https://developers.snap.com/spectacles/about-spectacles-features/apis/camera-module
- Xreal Eye: https://av.watch.impress.co.jp/docs/news/2013691.html
- Pupil Labs Neon: https://pupil-labs.com/products/neon/hardware
- GoPro Max Lens Mod 2.0: https://gopro.com/en/au/shop/mounts-accessories/max-lens-mod-2/ADWAL-002.html
- Ego-OSCAR: https://arxiv.org/abs/2608.08285 · https://github.com/fpv-labs/ego-oscar · dataset https://huggingface.co/datasets/fpvlabs/stereo-550
- Prices and pay: https://dexset.ai/blogs/egocentric-data-collection-robotics/ · https://egxodata.com/resources/egocentric-dataset-price · https://www.teahose.com/guides/robotics-training-data · https://www.roboticscenter.ai/marketplace · https://truelabel.ai/blog/best-egocentric-video-data-providers · https://techcrunch.com/2026/05/26/human-archive-taps-into-indias-services-startups-to-collect-data-for-physical-ai/ · https://www.abc.net.au/news/2026-09-20/egocentric-training-gig-workers-helping-robots-learn-tasks/107135216 · https://startupfeed.in/egocentric-data-india-robot-training-boom/ · https://remowork.life/blog/get-paid-to-record-household-chores-egocentric-ai-data-platforms-2026 · https://www.stellarisvp.com/blog/physical-ai-has-a-massive-data-problem
- Buyers: https://varunnair191587.substack.com/p/embodied-data-scale-up · https://scale.com/physical-ai · https://www.therobotreport.com/5-physical-ai-infrastructure-platforms-shaping-robotics-in-2026/ · https://encord.com/blog/best-data-collection-services/
- Spec and format guides: https://truelabel.ai/robot-training-data-marketplace · https://www.dataxpower.com/blog/stereo-camera-egocentric-data-collection · https://egxodata.com/resources/egocentric-dataset-specification-template · https://mcap.dev/
- Privacy: EgoBlur https://www.deepai.org/publication/egoblur-responsible-innovation-in-aria · https://www.cloudpano.com/blog/egocentric-video-privacy-bystander-consent
- Prior art: UMI https://arxiv.org/abs/2402.10329 · FastUMI https://arxiv.org/abs/2409.19499 · DexUMI https://arxiv.org/abs/2505.21864 · EgoMimic https://arxiv.org/abs/2410.24221 · EgoZero https://arxiv.org/abs/2505.20290 · EgoVerse https://arxiv.org/abs/2604.07607
