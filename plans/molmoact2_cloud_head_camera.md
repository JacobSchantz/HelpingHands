# MolmoAct2 cloud trial and binocular robot head

Status (2026-09-30): Jake authorized renting compute and preparing the trial.
He will buy the camera and build the robot body. No camera purchased here.
GPU launch attempted but rejected: the saved Hugging Face token has read
access, not permission to create the Jobs artifact bucket. No GPU job or
inference endpoint is running. Compute balance has not been verified.

This is the current first milestone, superseding the fixed top/side camera
purchase and Mac-port experiment. Preserve those as comparison options.

## Camera to order — budget corrected to under $100

Jake set a hard camera budget below $100. The previous $399 ZED Mini choice
is withdrawn. Current trial choice: **Waveshare OS02G10 Stereo USB Camera (A),
SKU 32639**, listed at **$56.99 before shipping/tax** when checked.
https://www.waveshare.com/product/raspberry-pi/cameras/os02g10-stereo-usb-camera-a.htm

Vendor specifies synchronized stereo output, USB 2.0 Type-C, 62 mm baseline,
fixed-focus lenses, rolling shutter, and MJPEG 2560×720 at 30 fps. Capture
and verify the side-by-side color frames on the actual Mac before relying on
that mode; this is a purchase recommendation, not a tested camera/model pair.
The camera does not provide a turnkey calibrated depth/tracking SDK. Preserve
raw pairs and perform stereo calibration if we later need metric depth.

**Updated body envelope: 100 × 22 × 17.72 mm**, plus USB cable clearance and
mounting hardware. Do not build to the earlier ZED dimensions. Use a rigid,
adjustable, removable head bracket pointing toward the manipulation area.
Keep the head fixed for the first trial, provide strain relief and a protective
housing for the exposed board. Verify the vendor mechanical drawing before
placing mounting holes. Confirm shipping/tax keep the delivered total below
$100 before ordering; no purchase has been made here.

Test exposure, focus at gripper distance, simultaneous left/right visibility,
frame synchronization and motion artifacts on receipt. Rolling shutter makes
fast head movement a particular limitation. Camera/head placement remains a
new distribution for MolmoAct2, requiring measured evaluation and possibly
fine-tuning. This is an indoor prototype, not a weatherproof camera.

## Cloud trial prepared

`Scripts/molmoact2_cloud_smoke.py` pins the official SO100/101 checkpoint
revision and tests its published top/side sample before introducing our head
camera. It loads bf16 on NVIDIA, checks finite six-joint action output and
prints warm inference timings and peak GPU memory. It never sends motor
commands. Python syntax and launch configuration were checked locally;
actual dependency installation, GPU loading and inference remain untested
because launch was denied.

Chosen first rental: Hugging Face Jobs **l4x1**, 24 GB GPU memory, listed at
$0.80/hour by `hf jobs hardware`. Each launch is capped at **30 minutes**,
approximately $0.40 of hardware time at that rate. No automatically recurring
job or continuously billed endpoint is configured. Public checkpoint/sample
assets only; no household video is uploaded by this test.

After configuring an appropriately scoped token locally (Jobs and artifact
bucket write access) and funding compute credit:

```sh
uvx --from huggingface_hub hf jobs uv run \
  --flavor l4x1 --timeout 30m --python 3.11 \
  --name helpinghands-molmoact2-smoke --detach \
  Scripts/molmoact2_cloud_smoke.py
```

The launcher uploads only this script. Do not put token values in the repo,
command line, or chat. Use `hf jobs logs JOB_ID` and `hf jobs inspect JOB_ID`
(via the same uvx prefix) to check execution and completion. A successful
submission is not a passed inference test.

## After the sample passes

1. Add an authenticated on-demand inference endpoint. Keep motor control,
   limits, stop behavior and timeout enforcement on the Mac. Measure complete
   camera-to-action latency; cloud compute time alone is insufficient.
2. Validate the camera's actual frame dimensions, left/right split, color
   order, timestamps and visibility, and record synchronized joint state.
3. Test a single SO-101 first: this checkpoint outputs one arm's six joints.
   A second arm requires an appropriate bimanual policy or adaptation; three
   camera streams do not make the single-arm checkpoint bimanual.
4. Treat head stereo as a new camera distribution. Adjacent RGB views are not
   the published top/side reference. Compare outcomes before relying on it.
5. Collect teleoperated demonstrations with this mounted camera and current
   gripper, then fine-tune on rented compute as needed. Preserve raw stereo
   recordings, calibration and timestamps for future models. Evaluate on
   held-out tasks/placements; do not promise a fixed demonstration count.
6. Only enable supervised, bounded motor execution after joint convention,
   stale-input rejection, connection-loss stop and interrupt behavior pass.

Model reference: https://huggingface.co/allenai/MolmoAct2-SO100_101
Training code/data: https://github.com/allenai/molmoact2
Cloud billing: https://huggingface.co/docs/hub/jobs-pricing
