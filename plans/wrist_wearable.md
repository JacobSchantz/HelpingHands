# Wristlog — an all-day wearable that saves hand demonstrations on a gesture

Plan only (pebble voice-b3454864, 2026-10-17). Nothing bought, built or flashed.

Jake's ask: wear a camera (and maybe something on the hands) all day, every
day. It records into a local rolling buffer and throws everything away unless
he makes a deliberate gesture (Spider-Man sign, pointing). On the trigger it
keeps the last N seconds plus the next M seconds as a labeled episode, which
becomes training data for the Aero Hand on the reBot arm.

## Verdict in five lines

1. **First prototype: "Wristlog v0" = the Apple Watch Jake already wears +
   a ~$40 camera pod on its strap** (Seeed XIAO ESP32-S3 Sense + small LiPo),
   aimed at the fingers. The pod keeps a 60 s ring buffer on microSD; the
   Watch is the trigger and the status light. Detail in §7.
2. **The v0 trigger is the Watch's own pinch / double-tap gesture, not the
   Spider-Man sign.** A camera-based sign detector has to run continuously
   on the pod, which costs battery, and the false-trigger rate is unknown.
   The Spider-Man sign becomes the v1 trigger once v0 shows what the buffer
   really sees (§4).
3. **All-day battery is the hard limit, not storage.** Continuous video on
   a wrist costs ~0.5 W, so 12 h needs ~6 Wh, which is too heavy for a strap.
   v0 targets ~5 h per charge and gates the camera on wrist motion to stretch
   it. Measure it before designing the band (§3).
4. **Tension with "mirror a human" (`plans/hand_1_0.md`):** that principle
   says no wrist cameras; the robot sees only through two eye-height cameras.
   This plan resolves it by treating the wrist camera as a **finger-pose
   sensor (the action label), not the policy's eyes.** The eye-height camera
   is added in v1 for observations (§6). **Jake to confirm.**
5. **Honest volume check:** one person won't match the big labs on hours
   (Generalist reports +10k h/week). ~100 episodes/day ≈ 1 h/day ≈ 350 h/year.
   The advantage is relevance: Jake's own tasks, with the robot's own hand
   in mind, labeled at the moment he does them.

---

## 1. Prior art (what to copy)

| System | What it is | What we take |
|---|---|---|
| **UMI** (Chi et al., 2024) | Handheld gripper + GoPro fisheye on the gripper, SLAM for pose | Wrist-view data trains policies when the robot has the *same* view. Ours won't, so we can't copy it directly |
| **DexCap** (Wang et al., 2024) | Mocap gloves + chest LiDAR camera, retargeted to a robot hand | Finger pose from gloves beats vision for labels. v2 option (§2) |
| **Generalist GEN-0/1** | 270k → 500k+ h from "low-cost wearable devices on humans"; proprietary | Proof that human wearable data at scale pretrains manipulation. See `plans/handheld_gripper.md` §0 |
| **Meta Project Aria / Aria Gen 2** | Research glasses: eye-height RGB + SLAM cams + hand tracking | Eye-height egocentric view = our "mirror a human" observation |
| **EgoDex** (Apple, ICLR 2026) | 829 h, 194 tabletop tasks, Vision Pro with 3D hand + head tracking at capture time; [public](https://github.com/apple/ml-egodex) | Free pretraining data in the same format we'd produce. Download before collecting our own hours |
| **Ego4D / EPIC-KITCHENS / HOT3D** | Large egocentric video sets, some with hand pose | More free egocentric pretraining data |
| **EgoMimic** (2024) | Aria glasses human data co-trained with robot data | The training recipe for §6: human data + a little robot data |
| **Digits** (Microsoft, 2012), FingerTrak | Wrist-worn sensors aimed at the hand that reconstruct finger pose | Evidence that a camera on the wrist can see enough of the fingers |

Takeaway: the big wins came from **cheap devices, worn a lot, with hand pose
recorded at capture time**. Nobody has published an *always-on,
gesture-saved* buffer. That part is new, and it's the part that makes daily
wear free of effort.

## 2. Hardware options

| Option | Cost | Rolling buffer + custom trigger? | All-day? | Verdict |
|---|---|---|---|---|
| **Insta360 GO 3S** on a wrist strap | ~$400 | Has *Pre-Rec* (buffers before a button press). Button only, no gesture, no API for a custom trigger | No: ~38 min alone, ~140 min with the Action Pod; reviews mention heat | Good footage, wrong product. Fine for a one-afternoon look at what a wrist view sees |
| **GoPro HERO** with HindSight | ~$300–400 + wrist mount | HindSight keeps up to 30 s before the press. Button / voice only | No, ~1–1.5 h of recording | Same as above, and too bulky to wear daily |
| **Smartwatch with a camera** | — | Apple Watch has no camera. Camera watches are kids' phones with closed firmware | — | Dead end. The Watch's value is the trigger, IMU and haptics |
| **XIAO ESP32-S3 Sense pod on the Watch strap** | ~$15 board + ~$10 battery + microSD + 3D-printed clip | Full control: our firmware, our buffer, BLE trigger | ~5 h on 1000 mAh (§3); longer with motion gating | **Recommended v0.** Weak sensor, rolling shutter, but we own every byte |
| **Custom camera band** (better sensor, e.g. OV5640/global shutter, flex PCB, band-integrated battery) | $100s + weeks | Yes | Designed for it | v2, only after v0 data shows it's worth it |
| **Glove sensors** (flex/IMU glove, e.g. DexCap-style or Rokoko/Manus) | $50 DIY – $1000s | Feeds the same buffer | Gloves aren't wearable all day (heat, touch, washing hands) | Calibration tool only (§6), not daily wear |
| **Ray-Ban Meta glasses** via Meta's Wearables Device Access Toolkit | ~$300 | Camera stream to a phone app, 720p30 max over Bluetooth | A few hours, and the phone has to stay awake | v1 eye-height camera candidate (§6) |

## 3. Battery, storage and sync (v0 numbers to verify)

**Power.** Seeed's own figures for the XIAO ESP32-S3 Sense running a webcam:
~154 mA at 3.8 V on battery (≈0.59 W), modem-sleep ~45 mA, light-sleep
~5 mA. Writing to SD with Wi-Fi off should be a bit below the webcam figure;
**to be measured.**

- 1000 mAh LiPo (~20 g, roughly a watch face in size) → ~5–6 h continuous.
- **Motion gating:** the Watch already knows when the wrist is still (desk,
  driving, sleep). The pod light-sleeps (~5 mA) until the Watch says "hands
  moving", then buffers. If the hands are busy 40% of a waking day, 1000 mAh
  covers ~12 h. This is the lever that makes all-day possible.
- Charging: the pod and Watch both go on the charger at night; that is also
  when sync happens.

**Storage.** VGA (640×480) MJPEG at 10 fps ≈ 25–40 KB/frame → ~18 MB/min.
- Ring buffer: one preallocated 60 s file on microSD, overwritten in place.
  Nothing else is ever written without a trigger.
- Episode: last **N = 20 s** + next **M = 20 s** (both configurable) ≈ 12 MB.
  100 a day ≈ 1.2 GB; a 64 GB card holds weeks.
- Why SD and not PSRAM: 8 MB of PSRAM holds only ~25 s of VGA. Keep PSRAM
  as a write cache.

**Sync to the Mac.** On the charger, the pod joins home Wi-Fi and POSTs each
saved episode to a small receiver on the Mac (`wristlog_receiver.py`, writes to
`~/HelpingHands-tools/wristlog/raw/`). It deletes an episode from SD only
after the Mac returns its checksum. Fallback: pull the card. The Watch sends
its side (trigger time, IMU, label) through the iPhone app to the same
receiver.

## 4. Gesture trigger

| Trigger | Where it runs | Cost | False triggers | Plan |
|---|---|---|---|---|
| **Watch double-tap / pinch** (watchOS `handGestureShortcut`, Series 9 / Ultra 2 and later) | Watch, already always on | ~0 extra | Low: it's a deliberate pinch Apple already tuned | **v0** |
| Watch IMU custom gesture (e.g. two wrist flicks) | Watch, CoreMotion | Low | Unknown; needs a small classifier and real-day testing | v0 fallback if the double-tap is taken by the system |
| **Spider-Man sign / point**, seen by the wrist camera | Pod (ESP-DL tiny classifier on 96×96 grey) | Runs on every frame; costs battery | Unknown, and pointing is a common everyday pose | **v1**: train it on v0's saved clips; require holding it for ~1 s |
| Spider-Man sign seen by the head camera | Phone (Apple Vision hand pose) | Phone battery | Lower: full-hand view | v1 once a head camera exists |

On every trigger: the Watch gives a **haptic tap**, the pod blinks its LED
(also the bystander signal, §5), and the Watch offers an *optional* one-tap or
dictated label ("dishes", "soldering", "skip"). The label becomes the
LeRobot `task` string, and VLA training needs one. A second double-tap within
the save window cancels it ("oops").

## 5. Privacy

- **Nothing leaves the buffer untriggered.** The ring file is overwritten in
  place; the firmware has no code path that uploads it. It is the only thing
  written without a trigger.
- **No audio, ever.** The pod has a mic; the firmware never opens it. This
  avoids two-party consent laws and is most of the privacy risk.
- **Bystanders:** a camera aimed at Jake's own fingers mostly sees the hand
  and the object. Even so: the LED is on while saving; faces are blurred on
  the Mac before anything enters a dataset; no saving in bathrooms, at work
  in someone else's space, or near kids who aren't his. A physical lens
  shutter on the clip for those times.
- Episodes stay on the Mac; nothing goes to a cloud unless Jake chooses to
  publish a cleaned dataset.

## 6. From episodes to Aero Hand + reBot training data

**Pipeline (on the Mac, overnight, per episode):**
1. Decode MJPEG, blur faces, attach Watch IMU and label.
2. Finger pose per frame: MediaPipe Hands for a fast pass, WiLoR/HaMeR (3D
   MANO) for quality. The camera is fixed to the forearm, so this gives finger
   angles relative to the wrist directly, which is exactly what the hand needs.
3. **Retarget to the Aero Hand's 7 actuations** (thumb abd, thumb flex, thumb
   tendon, index, middle, ring, pinky). Calibrate it with paired data: Jake
   wears the pod while doing glove teaching (`plans/aero-hand-glove-teaching.md`).
   The camera sees his fingers while the hand records its own actuations, which
   gives (wrist image → actuation) pairs. That lets us learn the mapping instead
   of hand-tuning it.
4. Write a LeRobot dataset (`wristlog_human`): `observation.images.wrist`,
   `observation.state` = estimated actuations, `action` = next-step actuations,
   `task` = label, plus a `human: true` flag.

**What it can and can't train (be clear-eyed):**
- **Can:** pretrain and co-train the *hand* part of a policy (grasp shapes,
  timing, which finger does what), and give a gesture/task vocabulary. Human
  data + ~1 h robot data is the recipe GEN-1 and EgoMimic report.
- **Can't (yet):** drive the reBot arm. The wrist camera gives no 6-DoF wrist
  trajectory. That needs a head camera with hand tracking, or SLAM.
- **View mismatch:** the robot has no wrist camera (mirror-a-human), so a
  policy trained on wrist images won't see that view on the robot. Hence the
  split: wrist camera = **labels**; eye-height camera = **observations**.

**Pairing with the eye-height cameras (v1).** Yes, but only for triggered
episodes, not as an all-day buffer: a head camera all day is a bigger
privacy and battery problem than a wrist one. Candidates: Ray-Ban Meta via
the Device Access Toolkit (mono, 720p30, the phone app holds a short buffer
and the same Watch trigger saves both), or the ELP stereo board from
`plans/shared_stereo_glasses.md` for sessions at the bench. The head camera
also gives the wrist's 3D path, which unlocks the reBot arm.

**Decision for Jake:** (A) keep mirror-a-human; the wrist camera is labels only
and v1 adds the eye-height camera; or (B) relax it and put a matching wrist
camera on the robot so wrist-view data trains directly (UMI-style). This plan
assumes **A**.

## 7. Recommended first prototype: Wristlog v0

**Parts (~$40 + owned Watch/iPhone/Mac):** XIAO ESP32-S3 Sense; 1000 mAh LiPo
with protection; 64 GB microSD; a printed clip that slides onto the Watch band
on the inside of the wrist with the lens aimed at the fingers (try the back of
the wrist too, see step 1); a short USB-C pigtail for charging.

**Build order (each step is a go/no-go):**
1. **Look first (1 evening):** pod streams to the Mac; wear it for an hour of
   real chores. Do the fingers stay in frame, and is the blur tolerable at
   10 fps? Run MediaPipe on it. If finger pose fails more than ~30% of the time,
   stop and rethink placement before anything else.
2. **Power (1 day):** log current with the camera + SD writing; wear it until
   it dies. That's the real hours-per-charge.
3. **Firmware:** ring buffer on SD, BLE "save" characteristic, N/M windows,
   LED, light-sleep on "hands still".
4. **Watch app** (HelpingHands already has a watch target, `build_watch.sh`):
   double-tap → BLE save → haptic → optional label; streams "hands moving" to
   the pod.
5. **Mac receiver + pipeline**: §3 sync and §6 steps 1–4, ending in a
   `wristlog_human` LeRobot dataset that the app can browse.
6. **One honest week of wear.** Count: episodes/day, hours/charge, false or
   missed triggers, pose-quality rate, and "did I take it off, and why".

**v0 is done when:** a week of wear gives ≥300 episodes with usable finger
pose, the battery lasts a workday with motion gating (or ~5 h without), and
Jake still wants to put it on in the morning.

## 8. Why wear it daily, beyond data

This decides whether the volume ever happens, so it's a real requirement:
- **It's already a watch.** The pod rides on the band Jake wears anyway; no new
  device to remember.
- **"How did I do that?"**: saved clips are a personal how-to library (the
  wiring, the knot, the repair), searchable by label.
- **A daily count on the watch face:** episodes today and a streak. Data
  collection as a habit (a natural BuyAHabit tie-in).
- **Robot replay:** each night, the Aero Hand plays back one of the day's
  grasps. Watching the robot do what you did that morning is the fun loop.

## 9. Open questions

- Inside or outside of the wrist for the lens? (Step 1 answers it.)
- Is the Watch double-tap free for apps on Jake's Watch model, or does it need
  the IMU fallback?
- Does XIAO's current camera module (OV2640 vs OV3660) give enough detail for
  WiLoR? *(unverified)*
- Decision A vs B in §6.

Sources: Insta360 GO 3S runtime/Pre-Rec ([Maison du Drone review](https://www.maisondudrone.com/en/insta360-go-3s-full-review-the-4k-version-of-the-go-3/),
[Airpoints listing](https://www.airpointsstore.co.nz/product/insta360-go-3s-standard-edition--128gb-69703578574-par));
XIAO ESP32-S3 Sense current and price ([Core Electronics](https://core-electronics.com.au/seeed-studio-xiao-esp32s3-54467.html.md),
[The Pi Hut](https://thepihut.com/products/seeed-studio-xiao-esp32s3-sense));
Meta Device Access Toolkit ([FAQ](https://developers.meta.com/wearables/faq),
[UploadVR](https://www.uploadvr.com/meta-wearables-device-access-toolkit-public-preview/));
EgoDex ([Apple ML](https://machinelearning.apple.com/research/egodex-learning-dexterous-manipulation),
[arXiv 2505.11709](https://arxiv.org/abs/2505.11709)); Generalist figures from
`plans/handheld_gripper.md` §0. UMI, DexCap, Aria, EgoMimic, Digits are cited
from memory and not re-checked this pass.
