#!/usr/bin/env python3
"""Webcam teleop: the hand copies your hand in real time.

Usage: teleop.py [--camera N] [--dry-run]     (port auto-detected; Esc or q quits)
Run with the aero venv, or via teleop.sh. Needs mediapipe + opencv-python in that venv.

Ported from upstream's ROS 2 webcam teleop (ros2/src/webcam_mocap/webcam_mocap.py and
aero_hand_open_retargeting/mediapipe_retargeting.py, commit 7bb2f23) without ROS: MediaPipe
world landmarks -> wrist frame -> joint angles -> config/normalize_default_mediapipe.yaml ranges.
"""
import argparse, glob, os, sys, time, urllib.request
import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks.python import BaseOptions, vision
from aero_open_sdk.aero_hand_constants import AeroHandConstants

MODEL = os.path.expanduser("~/HelpingHands-tools/aero/hand_landmarker.task")
MODEL_URL = ("https://storage.googleapis.com/mediapipe-models/hand_landmarker/"
             "hand_landmarker/float16/latest/hand_landmarker.task")
EMA_ALPHA = 0.7  # upstream default: weight of the newest frame

# Upstream's MediaPipe calibration (radians): valley = your relaxed angle, peak = fully bent.
# Joint order matches AeroHandConstants.joint_names.
VALLEY_PEAK = [
    (0.0, 0.705), (0.51, 0.956), (0.0, 0.70), (0.0, 0.78),  # thumb cmc_abd, cmc_flex, mcp, ip
    (0.708, 1.20), (0.02, 1.57), (0.25, 1.57),              # index mcp, pip, dip
    (0.708, 1.20), (0.02, 1.57), (0.25, 1.57),              # middle
    (0.708, 1.20), (0.02, 1.57), (0.25, 1.57),              # ring
    (0.47, 1.571), (0.005, 1.57), (0.24, 1.36),             # pinky
]
BONES = [(0, 1), (1, 2), (2, 3), (3, 4), (0, 5), (5, 6), (6, 7), (7, 8), (5, 9), (9, 10),
         (10, 11), (11, 12), (9, 13), (13, 14), (14, 15), (15, 16), (13, 17), (0, 17),
         (17, 18), (18, 19), (19, 20)]


def angle(a, b, c):
    ba, bc = a - b, c - b
    return np.arccos(np.clip(np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc)), -1, 1))


def wrist_frame(lm, side):
    """Wrist at the origin, z toward the middle finger, x across the knuckles."""
    x = lm[5] - lm[13]
    x /= np.linalg.norm(x)
    if side == "left":
        x = -x
    z = lm[9] - lm[0]
    z /= np.linalg.norm(z)
    y = np.cross(z, x)
    y /= np.linalg.norm(y)
    x = np.cross(y, z)
    return (lm - lm[0]) @ np.array([x, y, z]).T


def raw_joints(lm):
    """21 wrist-frame landmarks -> 16 human joint angles (radians)."""
    t = lm[0:5]
    cmc_abd = angle(np.array([t[2][0], t[1][1], 0]), np.array([t[1][0], t[1][1], 0]),
                    np.array([t[2][0], t[2][1], 0]))
    out = [cmc_abd] + [np.pi - angle(t[i], t[i + 1], t[i + 2]) for i in range(3)]
    for base in (5, 9, 13, 17):  # MediaPipe has no finger CMC, so the wrist stands in for it
        f = [lm[0]] + [lm[base + i] for i in range(4)]
        out += [np.pi - angle(f[i], f[i + 1], f[i + 2]) for i in range(3)]
    return out


def to_degrees(raw):
    """Map each human angle's valley..peak onto the hand's joint limits (degrees)."""
    lo, hi = AeroHandConstants.joint_lower_limits, AeroHandConstants.joint_upper_limits
    return [float(np.clip(lo[i] + (r - v) / (p - v) * (hi[i] - lo[i]), lo[i], hi[i]))
            for i, (r, (v, p)) in enumerate(zip(raw, VALLEY_PEAK))]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--camera", type=int, default=0)
    ap.add_argument("--dry-run", action="store_true", help="show tracking, don't move the hand")
    args = ap.parse_args()

    if not os.path.exists(MODEL):
        print("downloading hand_landmarker.task …")
        urllib.request.urlretrieve(MODEL_URL, MODEL)
    landmarker = vision.HandLandmarker.create_from_options(vision.HandLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=MODEL),
        running_mode=vision.RunningMode.VIDEO, num_hands=1))
    cap = cv2.VideoCapture(args.camera)
    if not cap.isOpened():
        sys.exit(f"camera {args.camera} won't open (grant this terminal Camera access in System Settings)")

    hand = None
    if not args.dry_run:
        ports = sorted(glob.glob("/dev/cu.usbmodem*"))
        if not ports:
            sys.exit("hand not connected (use --dry-run to just watch tracking)")
        from aero_open_sdk.aero_hand import AeroHand
        import hand_speed
        hand = AeroHand(port=ports[0])
        hand_speed.limit(hand)  # 50% unless Jake asks for more
        hand.ser.write_timeout = 0.05  # SDK default 10 ms drops a frame when USB stalls briefly

    smooth, t0 = None, time.monotonic()
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                continue
            frame = cv2.flip(frame, 1)  # mirror view; MediaPipe's handedness assumes it
            image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            res = landmarker.detect_for_video(image, int((time.monotonic() - t0) * 1000))
            if res.hand_world_landmarks:
                side = res.handedness[0][0].category_name.lower()
                world = np.array([[-p.x, p.y, p.z] for p in res.hand_world_landmarks[0]])  # undo mirror
                lm = wrist_frame(world, side)
                smooth = lm if smooth is None else EMA_ALPHA * lm + (1 - EMA_ALPHA) * smooth
                joints = to_degrees(raw_joints(smooth))
                if hand:
                    hand.set_joint_positions(joints)
                h, w = frame.shape[:2]
                pts = [(int(p.x * w), int(p.y * h)) for p in res.hand_landmarks[0]]
                for a, b in BONES:
                    cv2.line(frame, pts[a], pts[b], (0, 255, 0), 2)
                cv2.putText(frame, f"{side}  " + " ".join(f"{j:.0f}" for j in joints[:4] + joints[4::3]),
                            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.imshow("Aero teleop (Esc quits)", frame)
            if cv2.waitKey(1) & 0xFF in (27, ord("q")):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()
        if hand:
            hand.close()


if __name__ == "__main__":
    main()
