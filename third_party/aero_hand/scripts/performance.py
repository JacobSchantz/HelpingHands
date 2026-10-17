#!/usr/bin/env python3
"""Hand performance: start the song, confirm it is playing, then run the routine.

Usage: performance.py [song]   (default: a random track from the "¿?" playlist; port auto-detected)
Run with the aero venv: ~/HelpingHands-tools/aero/venv/bin/python performance.py
"""
import glob, subprocess, sys, threading, time
from aero_open_sdk.aero_hand import AeroHand

SONG = sys.argv[1] if len(sys.argv) > 1 else None  # None: random track from the playlist below
PLAYLIST = "¿?"
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


started = threading.Event()


started = threading.Event()


def start_song(name):
    """Start the track and return once Music reports it playing (polls every 50 ms)."""
    if name:
        osa(f'tell application "Music" to play (first track of library playlist 1 whose name contains "{name}")')
    else:
        osa(f'tell application "Music" to play some track of user playlist "{PLAYLIST}"')
    for _ in range(400):  # up to 20 s
        if osa('tell application "Music" to get player state') == "playing":
            started.set()
            return
        time.sleep(0.05)


ports = sorted(glob.glob("/dev/cu.usbmodem*"))
if not ports:
    sys.exit("hand not connected; nothing played or moved")
# open the hand's port while the song starts, so neither waits on the other
song = threading.Thread(target=start_song, args=(SONG,))
song.start()
hand = AeroHand(port=ports[0])
hand.ser.write_timeout = 0.05  # SDK default 10 ms drops a frame when USB stalls briefly
song.join()
if not started.is_set():
    hand.close()
    sys.exit(f"song '{SONG}' did not start; hand not moved")
if not started.is_set():
    hand.close()
    sys.exit(f"song '{SONG}' did not start; hand not moved")
hand.run_trajectory(ROUTINE)
hand.close()
print("performance done to", osa('tell application "Music" to get name of current track'))
