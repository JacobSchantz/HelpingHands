#!/usr/bin/env python3
"""Hand performance: start the song, confirm it is playing, then run the routine.

Usage: performance.py [song]   (default "Violin the Trap"; port auto-detected)
Run with the aero venv: ~/HelpingHands-tools/aero/venv/bin/python performance.py
"""
import glob, subprocess, sys, time
from aero_open_sdk.aero_hand import AeroHand

SONG = sys.argv[1] if len(sys.argv) > 1 else "Violin the Trap"
OPEN = [0.0] * 7

ROUTINE = [
    (OPEN, 1.0),
    # pinch each finger to the thumb
    ([100.0, 35.0, 23.0, 0.0, 0.0, 0.0, 50.0], 0.5), ([100.0, 35.0, 23.0, 0.0, 0.0, 0.0, 50.0], 0.25),
    ([100.0, 42.0, 23.0, 0.0, 0.0, 52.0, 0.0], 0.5), ([100.0, 42.0, 23.0, 0.0, 0.0, 52.0, 0.0], 0.25),
    ([83.0, 42.0, 23.0, 0.0, 50.0, 0.0, 0.0], 0.5), ([83.0, 42.0, 23.0, 0.0, 50.0, 0.0, 0.0], 0.25),
    ([75.0, 25.0, 30.0, 50.0, 0.0, 0.0, 0.0], 0.5), ([75.0, 25.0, 30.0, 50.0, 0.0, 0.0, 0.0], 0.25),
    (OPEN, 0.5), (OPEN, 0.5),
    # finger wave, index to pinky and back
    ([0.0, 0.0, 0.0, 90.0, 0.0, 0.0, 0.0], 0.3), ([0.0, 0.0, 0.0, 0.0, 90.0, 0.0, 0.0], 0.3),
    ([0.0, 0.0, 0.0, 0.0, 0.0, 90.0, 0.0], 0.3), ([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 90.0], 0.3),
    ([0.0, 0.0, 0.0, 0.0, 0.0, 90.0, 0.0], 0.3), ([0.0, 0.0, 0.0, 0.0, 90.0, 0.0, 0.0], 0.3),
    ([0.0, 0.0, 0.0, 90.0, 0.0, 0.0, 0.0], 0.3), (OPEN, 0.5),
    # peace sign
    ([90.0, 0.0, 0.0, 0.0, 0.0, 90.0, 90.0], 0.5), ([90.0, 45.0, 60.0, 0.0, 0.0, 90.0, 90.0], 0.5),
    ([90.0, 45.0, 60.0, 0.0, 0.0, 90.0, 90.0], 1.0), (OPEN, 0.5), (OPEN, 0.5),
    # rock on
    ([0.0, 0.0, 0.0, 0.0, 90.0, 90.0, 0.0], 0.5), ([0.0, 0.0, 0.0, 0.0, 90.0, 90.0, 0.0], 1.0),
    # fist, then open to finish
    ([90.0, 45.0, 60.0, 90.0, 90.0, 90.0, 90.0], 0.8), ([90.0, 45.0, 60.0, 90.0, 90.0, 90.0, 90.0], 1.0),
    (OPEN, 1.0),
]


def osa(script):
    return subprocess.run(["osascript", "-e", script], capture_output=True, text=True).stdout.strip()


def start_song(name):
    osa(f'tell application "Music" to play (first track of library playlist 1 whose name contains "{name}")')
    for _ in range(50):  # up to 5 s
        if osa('tell application "Music" to get player state') == "playing" and \
           name.lower() in osa('tell application "Music" to get name of current track').lower():
            return
        time.sleep(0.1)
    sys.exit(f"song '{name}' did not start; hand not moved")


ports = sorted(glob.glob("/dev/cu.usbmodem*"))
if not ports:
    sys.exit("hand not connected; nothing played or moved")
hand = AeroHand(port=ports[0])
start_song(SONG)
time.sleep(1.0)
hand.run_trajectory(ROUTINE)
hand.close()
print(f"performance done to '{SONG}'")
