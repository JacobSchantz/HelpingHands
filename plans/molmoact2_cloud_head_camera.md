# MolmoAct2 cloud trial and binocular robot head

Status (2026-09-30): Jake authorized renting compute and preparing the trial.
He will buy the camera and build the robot body. No camera purchased here.
GPU launch attempted but rejected: the saved Hugging Face token has read
access, not permission to create the Jobs artifact bucket. No GPU job or
inference endpoint is running. Compute balance has not been verified.

This is the current first milestone, superseding the fixed top/side camera
purchase and Mac-port experiment. Preserve those as comparison options.

## Camera to order

**Stereolabs ZED Mini USB stereo camera**, listed at **US $399**, with dispatch
in 1–2 weeks when checked. Purchase link:
https://www.stereolabs.com/store/products/zed-mini

Two color views, 63 mm baseline, USB capture, and a 60 g body make it our
preferred head-camera experiment. This is an engineering selection, not a
measured claim that it produces better MolmoAct2 task success. OAK-D Lite/S2
offer useful onboard depth, but their stereo pair is monochrome plus a
separate central RGB sensor. ZED Mini gives the desired pair of color eyes.

Body envelope: **124.5 × 30.5 × 26.5 mm**, excluding cable clearance and mount.
Use an adjustable, rigid, removable head bracket tilted down so both grippers
and the entire manipulation region remain visible. Leave USB cable clearance
and strain relief. Keep the head fixed during the first dataset/trial so its
pose does not vary unpredictably. Final fastener locations must come from the
manufacturer drawing/CAD, not inferred from the envelope:
https://www.stereolabs.com/3dmodels

Capture the side-by-side color stream on the Mac through UVC/OpenCV, then
split it into left and right RGB frames. Vendor confirms basic capture works
on macOS without CUDA. The full vendor depth/tracking SDK has separate
platform requirements; this plan does not promise that SDK runs on the Mac.
https://support.stereolabs.com/articles/7166665108-can-i-use-the-zed-without-cuda

Do not substitute a ZED X Mini: it has a different host interface. This is an
indoor prototype camera choice, not a weatherproof outdoor deployment choice.
Keep lens protection/weatherproofing as later work.

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
