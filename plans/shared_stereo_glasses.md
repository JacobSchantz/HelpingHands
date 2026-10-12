# Shared stereo camera glasses — one camera for Jake and the robot

Plan only (pebble voice-d3e2cdc1, 2026-10-12). Nothing is bought, turned on,
mounted or wired to the arm by this document. It is the HelpingHands half of a
shared decision; the BuyAHabit half is `~/buyahabit/plans/056_camera_glasses.md`
(pebble voice-71659c51), which did the product survey. This plan reuses that
survey rather than repeating it, and adds the robot side.

## Verdict

**No glasses under $100 have two outward-facing scene cameras that a program
can read.** BuyAHabit 056 checked the cheap field (Bapick B0HHR9Y8V3, the
HeyCyan family, OpenGlass) and every one is a single camera; the only glasses
that ever had a real stereo pair (Snap Spectacles 3) are discontinued, cap
clips at seconds and have no API. Products sold as "binocular" glasses in this
price band mean two display lenses, or one camera plus a second sensor; none
of them gives two readable image streams.

The closest thing that *is* verified stereo and in budget is a bare board:
**ELP 960P synchronized dual-lens USB module**,
[B0CCXRVV48](https://www.amazon.com/dp/B0CCXRVV48), $84 when 056 checked on
2026-10-06 (the listing still resolves today under that title; the price was
not re-confirmed because Amazon's page did not return it). It can be clipped
into a glasses-shaped frame. It is a robot camera a person can wear on a
cable, not habit glasses.

**Recommendation: buy nothing for this yet.** One purchase *can* be shared,
and if Jake wants one it is the ELP board. But the robot's next camera is not
this one (see "The conflict" below), and the board gives BuyAHabit only a
tethered bench test. Nothing the budget buys today does both jobs well.

## What the two cameras on the ELP board actually are

| Requirement | ELP 960P (B0CCXRVV48) | Evidence |
|---|---|---|
| Two scene cameras, not displays/lens marketing | Yes, two OV9750 sensors on one board | listing, [review](https://summet.com/blog/2023/11/17/elp-synchronized-stereo-camera-module-elp-usb960p2cam-v90) |
| Access to both streams | Yes: one UVC device, one 2560×960 side-by-side frame, split in half | review (Linux, OpenCV) |
| Synchronization | Shared shutter, both eyes in the same frame, so one timestamp covers both | listing claim + review's description; **no measured skew published** |
| Resolution / frame rate | 1280×960 per eye; 60 fps claimed | listing; review does not report achieved fps |
| Baseline / overlap | **Not published.** Board is 80×16.5 mm, so baseline is under 80 mm, probably ~60 mm. Measured during calibration | 056 |
| Shutter | Rolling (a global shutter sibling, [B0D9793XZN](https://www.amazon.com/dp/B0D9793XZN), $96.99, 120° lenses, has no independent review) | 056 |
| Low light | Unknown; untested | — |
| SDK / protocol | None needed: standard UVC webcam, OpenCV / AVFoundation / LeRobot `OpenCVCamera` | — |
| Depth | **Not established.** The review ran uncalibrated StereoBM and reported no numbers. Two cameras on one board are necessary, not sufficient | review |
| Power / runtime | USB bus powered, no battery, no storage. Runs as long as the host does | — |
| Capture blocked when not worn? | No wear sensor, no app pairing, no vendor cloud | — |
| Thermal | Unknown; tested in the soak run below | — |
| iPhone | **Cannot read it.** Apple allows external USB cameras on iPad only ([Apple forum](https://developer.apple.com/forums/thread/775883)); Android reads it over USB OTG | 056 |

Expected depth precision, as a back-of-envelope to judge the test against:
with ~90° lenses the focal length is roughly 640 px per eye, so with a 60 mm
baseline the depth error is about z² × 0.25 px ÷ (640 × 60 mm) for quarter-pixel
matching: ≈ 2 mm at 0.5 m, ≈ 7 mm at 1 m, ≈ 26 mm at 2 m, ≈ 60 mm at 3 m. Good
enough for tabletop reach; poor for room-scale distances.

## The conflict with the robot's current plan

`molmoact2_deployment.md` step 3 needs a **second camera at a different
viewpoint**: one above the workspace, one to the side, "multi-view RGB, not a
calibrated binocular depth rig", matching the existing Arducam, budget under
$100. A stereo board's two eyes sit ~6 cm apart looking the same way; it
cannot stand in for the top/side pair. So buying the ELP board now would spend
the robot's camera money on the later roadmap item (`gripper_bet.md`, "Shared
sensing roadmap") while the first milestone still needs the matching Arducam.

Order of operations this implies:

1. Robot milestone 1 keeps its plan: existing Arducam + one matching Arducam.
2. Shared stereo glasses come after the MolmoAct2 loop works, as the
   `gripper_bet.md` sensing roadmap already says.
3. When that time comes, the ELP board is the first thing to buy, and both
   projects buy that one board, not two devices.

## The compromise, compared honestly

Since no stereo glasses exist in budget, the two real options are:

**A. ELP dual-camera module in a printed glasses frame (~$92 all in).**
Robot: good. Stereo, synchronized, external power, rigid mount, LeRobot reads
it today. Jake wearing it: tethered by a USB cable to a Mac (or an Android
phone); a MacBook in a backpack (`iBackpack.md`) makes that walkable for
demonstrations, but it is not all-day habit evidence, and it never works with
an iPhone. Weight on the face is the board plus cable strain; untested.

**B. Monocular glasses (Bapick ~$57, or OpenGlass ~$25).**
BuyAHabit: closer to a real wearable, with batteries and storage, though 056
found neither records all day and HeyCyan access is an unlicensed community
SDK. Robot: poor. No live stream on HeyCyan (photos and clips pulled over a
Wi-Fi hotspot), clip caps, a pairing step per transfer; OpenGlass streams
small low-resolution stills over Bluetooth. No depth at all, and monocular
depth from a model would be a guess, not a measurement.

Neither silently raises the budget or needs a second pair. A is the only one
that serves the robot; B is the only one that is a wearable. If one pair must
serve both, it is A, with BuyAHabit's use limited to a tethered experiment.

## One capture interface for both projects

The camera never talks to either app directly. A small capture process on the
host (Mac mini on the robot, Jake's Mac or an Android phone when worn) owns it:

- Opens the board by its stable device id (AVFoundation `uniqueID` on macOS,
  `/dev/v4l/by-id` on Linux), never by index, so a replug finds the same camera.
- Reads the side-by-side frame, stamps it with the host's monotonic clock and a
  frame counter, and splits it into `left` / `right`. One stamp covers both
  halves because they were exposed together.
- Applies the stored rectification (below) on request.
- Publishes two consumers from the same frames:
  - **Robot:** LeRobot observation keys `observation.images.left` / `.right`
    (and optionally a depth map), paired with joint state by timestamp exactly
    as `molmoact2_deployment.md` pairs its views.
  - **BuyAHabit:** a still every N seconds (left eye only is enough) with the
    capture time, dropped into the evidence flow 056 already defines
    (thresholds, review list, one completion per evidence id, seven-day local
    retention, pause control).
- On device loss it marks a gap, retries the open every second, and resumes
  with a new frame counter epoch. It never repeats the last frame to fill the
  gap (the same rule MolmoAct2 step 3 sets).

Compute is on the host: OpenCV `StereoSGBM` on the Mac mini at 640×480 per
eye is the starting point; nothing runs on the glasses.

## Calibration and repeatable mounting

Calibration belongs to the board, not the mount: the two lenses share a rigid
PCB, so the intrinsics and the left-right extrinsics survive moving the board
between Jake's frame and the robot. What changes on each move is only where
the board sits relative to the robot, which matters for manipulation, not for
depth.

- Store `stereo_calib/<board-serial>.yaml` (intrinsics, distortion, R, T,
  rectification maps, the measured baseline, date, reprojection error).
- One printed carrier holds the board; the glasses frame and a robot-mast
  plate both take that carrier on a dovetail with two dowel pins, so it seats
  the same way every time.
- After every remount: show the checkerboard once and check rectified
  epipolar error (rows line up within ~0.5 px). If not, recalibrate; if the
  board itself flexed, the frame is too thin.
- For the robot, the board-to-arm transform is a separate step (hand-eye
  calibration against the gripper, as `crow_gripper.md` plans for the wrist
  camera). Without it, depth is in camera coordinates only.

## Prototype test — only after milestone 1, only if bought

About two hours on the Mac mini, arm unpowered:

1. **Enumerate.** Confirm the Mac opens it and which modes it actually
   negotiates (2560×960 at what fps, MJPEG vs YUYV). Log achieved fps.
2. **Calibrate.** 20–30 checkerboard views, OpenCV `stereoCalibrate`.
   Record the baseline and reprojection error (target < 0.5 px).
3. **Known distances.** A flat target at 0.5, 1, 2 and 3 m by tape measure.
   Pass: within 2% at 0.5 m and 5% at 1 m; record 2 m and 3 m as found.
4. **Moving objects.** A hand and a swinging weighted string crossing the
   view. Check both halves show the same phase of motion (sync) and how much
   rolling-shutter skew bends straight edges. A phone stopwatch filmed in both
   halves gives the inter-eye skew directly.
5. **Latency.** Film a millisecond timer on screen; capture-to-host latency
   = displayed time minus frame time. Then unplug and replug mid-run; confirm
   the gap is logged and capture resumes on the same device id.
6. **Soak.** Two hours on USB power: dropped frames, achieved fps over time,
   board temperature by touch/IR thermometer.
7. **Low light.** One run at evening room lighting; note where matching fails.
8. **Worn.** Clip the carrier into the frame, wear it tethered to the
   MacBook while reading, and run the stills through BuyAHabit's flow (056's
   reading test). This is the only BuyAHabit check possible with this board.

## What this does and does not give the robot

A calibrated stereo pair gives the robot a depth image of what is in front of
it. That is basic perception: distances to surfaces in view, under decent
light, within a couple of metres. It is **not** safe navigation (no obstacle
policy, no coverage behind or beside it, no failure handling), and it is not
validated manipulation (that needs the camera-to-arm transform, a policy
trained or adapted on these views, and supervised task trials). The prototype
above proves the camera, nothing more.

## Open questions for Jake

- Is it acceptable that the shared device is a wired robot camera, with
  BuyAHabit limited to a tethered test, or should BuyAHabit keep a separate
  monocular wearable path later (which would mean two devices)?
- Hold the stereo purchase until MolmoAct2 milestone 1 works, as above?
