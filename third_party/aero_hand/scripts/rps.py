#!/usr/bin/env python3
"""Rock-paper-scissors against the hand, with your throw read off the webcam.

Usage: rps.py [--camera N] [--rounds N] [--dry-run]     (port auto-detected; Esc or q quits)
Run with the aero venv, or via rps.sh. Tracking is teleop.py's (MediaPipe world landmarks).

No cheating: each round the hand's throw comes from `secrets` and is committed before the
count starts — appended to LOG and shown as a sha256 on screen — so it can't depend on yours.
The hand only reveals it on "shoot", and the reveal's nonce lets anyone check the hash.
"""
import argparse, collections, glob, hashlib, json, os, secrets, subprocess, sys, time, urllib.request
import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks.python import BaseOptions, vision
from teleop import BONES, MODEL, MODEL_URL, raw_joints, wrist_frame

LOG = os.path.expanduser("~/HelpingHands-tools/aero/rps_log.jsonl")
THROWS = ["rock", "paper", "scissors"]
BEATS = {"rock": "scissors", "paper": "rock", "scissors": "paper"}
# Same joints as pose.py's fist / open / peace (pose.py runs on import, so they're copied here).
THUMB_OUT, THUMB_IN = [0.0, 0.0, 0.0], [90.0, 45.0, 60.0]
JOINTS = {
    "rock": THUMB_IN + [90.0, 90.0, 90.0, 90.0],
    "paper": THUMB_OUT + [0.0, 0.0, 0.0, 0.0],
    "scissors": THUMB_IN + [0.0, 0.0, 90.0, 90.0],
}
BEAT_S = 0.6     # between "rock", "paper", "scissors", "shoot"
READ_S = 0.8     # how long after "shoot" your throw is sampled (majority vote)
BENT = 1.4       # a finger whose pip+dip bend (radians) exceeds this counts as curled
GREEN, WHITE = (0, 255, 0), (255, 255, 255)


def classify(raw):
    """16 teleop joint angles -> 'rock' | 'paper' | 'scissors' | None, from which fingers are out."""
    up = [raw[i] + raw[i + 1] < BENT for i in (5, 8, 11, 14)]  # index, middle, ring, pinky
    if not any(up):
        return "rock"
    if all(up):
        return "paper"
    if up[0] and up[1] and not up[2] and not up[3]:
        return "scissors"
    return None


def say(text):
    subprocess.Popen(["say", text])


class Camera:
    """Webcam + MediaPipe; every read draws the preview window, so it stays live all game."""

    def __init__(self, index):
        if not os.path.exists(MODEL):
            print("downloading hand_landmarker.task …")
            urllib.request.urlretrieve(MODEL_URL, MODEL)
        self.landmarker = vision.HandLandmarker.create_from_options(vision.HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=MODEL),
            running_mode=vision.RunningMode.VIDEO, num_hands=1))
        self.cap = cv2.VideoCapture(index)
        if not self.cap.isOpened():
            sys.exit(f"camera {index} won't open (grant Helping Hands Camera access in System Settings)")
        self.t0 = time.monotonic()
        self.lines = []

    def frame(self, look=False):
        """One frame; returns your throw (or None) when look is set, raises KeyboardInterrupt on Esc/q."""
        ok, frame = self.cap.read()
        throw = None
        if ok:
            frame = cv2.flip(frame, 1)
            if look:
                image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                res = self.landmarker.detect_for_video(image, int((time.monotonic() - self.t0) * 1000))
                if res.hand_world_landmarks:
                    side = res.handedness[0][0].category_name.lower()
                    world = np.array([[-p.x, p.y, p.z] for p in res.hand_world_landmarks[0]])
                    throw = classify(raw_joints(wrist_frame(world, side)))
                    h, w = frame.shape[:2]
                    pts = [(int(p.x * w), int(p.y * h)) for p in res.hand_landmarks[0]]
                    for a, b in BONES:
                        cv2.line(frame, pts[a], pts[b], GREEN, 2)
            for i, text in enumerate(self.lines):
                cv2.putText(frame, text, (10, 30 + 30 * i), cv2.FONT_HERSHEY_SIMPLEX, 0.7, GREEN, 2)
            cv2.imshow("Rock paper scissors (Esc quits)", frame)
        if cv2.waitKey(1) & 0xFF in (27, ord("q")):
            raise KeyboardInterrupt
        return throw

    def wait(self, seconds, look=False):
        """Keep the preview live for `seconds`; returns every throw seen when look is set."""
        seen, end = [], time.monotonic() + seconds
        while time.monotonic() < end:
            throw = self.frame(look)
            if throw:
                seen.append(throw)
        return seen

    def close(self):
        self.cap.release()
        cv2.destroyAllWindows()


def commit(round_no):
    """Pick the hand's throw and write it down before anything of yours is read."""
    throw, nonce = secrets.choice(THROWS), secrets.token_hex(8)
    digest = hashlib.sha256(f"{throw}:{nonce}".encode()).hexdigest()
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with open(LOG, "a") as f:
        f.write(json.dumps({"round": round_no, "at": time.time(), "hand": throw,
                            "nonce": nonce, "sha256": digest}) + "\n")
    print(f"round {round_no}: hand committed sha256={digest[:16]}… (logged to {LOG})", flush=True)
    return throw, nonce, digest


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--camera", type=int, default=0)
    ap.add_argument("--rounds", type=int, default=0, help="stop after N rounds (0 = until Esc/Stop)")
    ap.add_argument("--dry-run", action="store_true", help="play without moving the hand")
    args = ap.parse_args()

    cam = Camera(args.camera)
    hand = None
    if not args.dry_run:
        ports = sorted(glob.glob("/dev/cu.usbmodem*"))
        if not ports:
            sys.exit("hand not connected (use --dry-run to play without it)")
        from aero_open_sdk.aero_hand import AeroHand
        import hand_speed
        hand = AeroHand(port=ports[0])
        hand_speed.limit(hand)  # 50% unless Jake asks for more
        hand.ser.write_timeout = 0.05  # SDK default 10 ms drops a frame when USB stalls briefly

    def move(throw):
        if hand:
            for _ in range(2):  # resend so a stalled frame can't leave the hand short
                hand.set_joint_positions(JOINTS[throw])
                time.sleep(0.02)

    score = collections.Counter()
    round_no = 0
    try:
        say("Let's play rock paper scissors.")
        cam.lines = ["Rock paper scissors!"]
        cam.wait(2.0)
        while not args.rounds or round_no < args.rounds:
            round_no += 1
            hand_throw, nonce, digest = commit(round_no)
            cam.lines = [f"Round {round_no}   you {score['you']} - hand {score['hand']}",
                         f"hand committed {digest[:16]}"]
            move("rock")
            for word in ("Rock", "Paper", "Scissors"):
                say(word)
                cam.lines[2:] = [word + "…"]
                cam.wait(BEAT_S)
            say("Shoot!")
            move(hand_throw)
            seen = cam.wait(READ_S, look=True)
            yours = collections.Counter(seen).most_common(1)[0][0] if seen else None
            reveal = f"hand threw {hand_throw} (nonce {nonce})"
            if yours is None:
                result, line = "none", "I couldn't see your throw. Again!"
            elif yours == hand_throw:
                result, line = "tie", f"We both threw {yours}. Tie!"
            elif BEATS[yours] == hand_throw:
                result, line = "you", f"{yours.capitalize()} beats {hand_throw}. You win!"
            else:
                result, line = "hand", f"{hand_throw.capitalize()} beats {yours}. I win!"
            if result in ("you", "hand", "tie"):
                score[result] += 1
            with open(LOG, "a") as f:
                f.write(json.dumps({"round": round_no, "you": yours, "result": result}) + "\n")
            if result == "none":
                round_no -= 1  # doesn't count; the next commit reuses the number
            tally = f"you {score['you']}, hand {score['hand']}" + (f", {score['tie']} ties" if score["tie"] else "")
            print(f"{reveal}; you threw {yours or '?'} -> {line}  [{tally}]", flush=True)
            say(f"{line} {'' if yours is None else tally}")
            cam.lines = [line, reveal, tally]
            cam.wait(3.0)
    except KeyboardInterrupt:
        pass
    finally:
        print(f"final: you {score['you']}, hand {score['hand']}, ties {score['tie']}", flush=True)
        cam.close()
        if hand:
            move("paper")
            hand.close()


if __name__ == "__main__":
    main()
