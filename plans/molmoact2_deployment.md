# MolmoAct2: one deployment plan

Updated 2026-09-30. This is the authoritative implementation plan. It replaces
previous camera shopping, binocular-head-first and Mac-port proposals.

## Goal

Run MolmoAct2 on rented NVIDIA compute, with the existing Mac capturing USB
camera images and controlling one existing SO-101 arm. Prove the complete
connection using the camera Jake already owns, then add a matching camera
above/beside the workspace. Minimize hardware changes and reuse the official
checkpoint and inference code.

## What Jake needs to provide

1. **Cloud access:** configure a GPU-provider API token locally and enable
   billing/compute credit. Default to the existing Hugging Face account, with
   Jobs and artifact-bucket write permissions; its present token is read-only.
   RunPod is an alternative if Jake already has an account. Never paste the
   key into chat or commit it. Tell the agent when access is configured.
2. **Camera access:** plug the existing Arducam day/night USB camera into the
   Mac, and obtain one matching second camera for the later two-view trial.
   The new-camera budget is below $100. Confirm its exact SKU before ordering:
   the desktop title identified the product family, not the exact revision.
   The second camera is not a blocker for software or the one-camera test.
3. **Physical setup when needed:** power/connect the SO-101, mount the cameras
   and be present for the first moving-robot tests. Jake is building the body;
   the final mobile body is not required for a tabletop trial. If macOS asks
   for camera permission, Jake must grant it locally.

Everything else in this plan is agent-owned: environment setup, cloud launch,
capture/client/server code, integration, automated tests, logs, latency
measurements, and a clear run/stop procedure. Ask only for missing access or
physical actions that cannot be performed remotely.

## One data path

USB camera(s) → Mac capture + timestamped joint state + task instruction →
authenticated GPU endpoint → predicted joint-action chunk → Mac validation →
local arm controller (disabled until the physical-test stage).

The Mac shows live camera views and request status. The server returns action
predictions and timing/identifiers, not a generated future video. A diagnostic
mode may echo the exact images received to verify the path. Keep recording
formats portable: timestamped images, joint states, actions, task labels,
checkpoint revision and camera configuration.

## Build and verify in order

### 1. Cloud model check, with no camera or motors required

Use `Scripts/molmoact2_cloud_smoke.py`: pinned SO100/101 checkpoint, published
sample images and recorded sample joint state, bf16 NVIDIA inference. Check
finite output with six joint dimensions, memory use and warm inference time.
Choose the existing prepared Hugging Face L4 24 GB configuration first.
The last observed price was $0.80/hour; verify before launching. Cap the first
job at 30 minutes (about $0.40 hardware time at that price). No always-on
rental while waiting for hardware. Larger training rentals are a later step.

Prepared command, run from the repository root after cloud access is fixed:

```sh
uvx --from huggingface_hub hf jobs uv run \
  --flavor l4x1 --timeout 30m --python 3.11 \
  --name helpinghands-molmoact2-smoke --detach \
  Scripts/molmoact2_cloud_smoke.py
```

Inspect the returned job ID and its logs. A submitted job is not a passed test.

### 2. Complete the live path using the existing single camera

Build the authenticated inference endpoint and Mac client. Enumerate/select
cameras reliably, capture in normal daylight color mode and display locally.
Send the same captured image as both model image inputs, explicitly marked
`single_camera_diagnostic`. This tests transport and inference; it does not
reproduce the two-view setup or prove manipulation quality.

Use read-only measured arm state if the arm is connected. Otherwise use a
clearly marked recorded state for pipeline checks only. Display predicted
actions; do not execute predictions derived from recorded state on hardware.
Measure capture age, upload time, GPU inference and end-to-end response time.

### 3. Add the second camera and reproduce top/side viewpoints

Mount both cameras rigidly on the robot frame or its mast: one above the
workspace looking down, the other to the side looking diagonally across it.
Both should see the target area and gripper throughout the motion. Their
spacing need not match human eyes; this is multi-view RGB, not a calibrated
binocular depth rig. Use timestamps to pair nearby frames and reject stale or
missing views. Do not silently substitute duplicate frames after camera loss.

Start with 640×480 at 30 fps if supported and check actual negotiated modes,
USB bandwidth, exposure and sharpness. The matching B0205 guide lists focus
from 1 metre: test the existing unit at the proposed distances before fixing
mount positions. Keep lighting sufficient for normal color mode; infrared
night images differ from the reference. Do not assume the exact SKU or
close-focus performance from the generic product title.

### 4. Supervised robot trial

Verify current calibration, joint order, units, sign/offset conventions and
limits against the chosen checkpoint/processor. Apply convention conversion
once. Start with bounded single-arm motion and one short pick-and-place task.
Keep motor limits, stop control and watchdog on the Mac. Disconnects, stale
observations, late/out-of-order responses and interrupts must stop further
action execution. Reconnection must not replay queued actions automatically.

### 5. Improve the specific task with demonstrations

Record successful teleoperated demonstrations in this exact camera/gripper
setup. Vary object pose, lighting and target location, and collect successful
recoveries for common failures. Fine-tune the existing checkpoint on rented
compute rather than training from scratch. Select LoRA/full/action-expert-only
training based on the measured failure and dataset, then evaluate on held-out
episodes and object arrangements. A proposed 50–100 episode starting batch is
an experiment budget, not a guaranteed data requirement. Keep the best prior
checkpoint and check retained tasks after each update.

## Required evidence

Automated checks cover request/response schemas; malformed/nonfinite/wrong-size
actions; authentication; camera loss and stale frame pairs; timeout, duplicate
and out-of-order responses; reconnect behavior; joint convention fixtures;
and stop/watchdog behavior with a fake controller. Also test one-camera mode
is explicit and cannot be mistaken for the two-camera evaluation.

Integration evidence must include a real GPU prediction, a real Mac camera
round trip, measured latency, stable two-camera capture and supervised task
success/failure counts. Mocks and the official sample do not establish robot
success. Do not call the rollout complete until these hardware checks pass.

## Current status

- Prepared and committed: GPU smoke script; syntax and launch dry-run passed.
- Blocked: actual launch received HTTP 403 because the saved HF token cannot
  create the Jobs artifact bucket. Compute credit is unverified.
- Not yet implemented/verified: live endpoint, Mac camera client, latency,
  controller integration, physical test and fine-tuning. No GPU job is running.

## Later, after the first working loop

Keep binocular head cameras, shared human/robot glasses and glove sensing,
human-held New Caledonian crow grippers, SO-101 attachment, and portable human
training data as the longer-term roadmap in `gripper_bet.md`. Bimanual control
requires a suitable policy/adaptation; the current checkpoint is single-arm.
Solar, mobile battery power and autonomous outlet connection remain separate
hardware workstreams. None blocks this first trial. No ZED or Waveshare stereo
camera purchase is currently required; no Mac Studio or Mac model port needed.

## References

- Model and sample: https://huggingface.co/allenai/MolmoAct2-SO100_101
- Official integration: https://huggingface.co/docs/lerobot/main/en/molmoact2
- Training code/data: https://github.com/allenai/molmoact2
- Cloud billing: https://huggingface.co/docs/hub/jobs-pricing
- Camera-family guide (confirm SKU): https://www.uctronics.com/download/Amazon/B0205.pdf
