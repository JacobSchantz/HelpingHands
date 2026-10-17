#!/usr/bin/env python3
"""Holding-power benchmark: how much current and heat each pose costs while the hand just holds it.

Usage: hold_bench.py <label> [--hold 60] [--start-c 50] [--poses fist peace can]   (port auto-detected)
For each pose it relaxes the hand, waits until every servo is at or below --start-c, runs the
real command (pose.py / grip.py, exactly what the app's buttons run), then samples current and
temperature for --hold seconds in free air. Writes ../bench/hold_<label>.json and prints a table.
Heat safety (Jake, 2026-10-17): a pose is aborted and every servo relaxed on the spot if any servo
reaches ABORT_C, and no pose starts until every servo is below MAX_START_C. Ctrl-C relaxes too.
"""
import argparse, glob, json, os, subprocess, sys, time
from aero_open_sdk.aero_hand import AeroHand

HERE = os.path.dirname(os.path.abspath(__file__))
NAMES = ["thumb_abd", "thumb_flex", "thumb_tendon", "index", "middle", "ring", "pinky"]
COMMANDS = {"fist": ["pose.py", "fist"], "peace": ["pose.py", "peace"], "can": ["grip.py", "close"]}
ABORT_C = 68      # 2 C under Jake's 70 C limit: temps read in whole degrees and climb ~1 C per 4 s
MAX_START_C = 54  # every servo below 55 C before a pose starts, whatever --start-c says

ap = argparse.ArgumentParser()
ap.add_argument("label")
ap.add_argument("--hold", type=float, default=60.0)
ap.add_argument("--start-c", type=float, default=50.0)
ap.add_argument("--poses", nargs="+", default=list(COMMANDS), choices=list(COMMANDS))
a = ap.parse_args()
a.start_c = min(a.start_c, MAX_START_C)
ports = sorted(glob.glob("/dev/cu.usbmodem*"))
if not ports:
    sys.exit("hand not connected")


def connect():
    hand = AeroHand(port=ports[0])
    hand.ser.write_timeout = 0.05
    return hand


def run(script, *args):
    subprocess.run([sys.executable, os.path.join(HERE, script), *args], check=True, cwd=HERE)


def relax_now(hand):
    for _ in range(3):
        hand.ctrl_torque([0] * 7)
        time.sleep(0.05)


def cool(limit):
    run("relax.py")
    hand, t0 = connect(), time.time()
    while True:
        temps = hand.get_actuator_temperatures()
        if temps and max(temps) <= limit:
            break
        print(f"  cooling: max {max(temps) if temps else '?'} C > {limit} C ({time.time() - t0:.0f} s)", flush=True)
        time.sleep(10)
    hand.close()
    return temps


results = {"label": a.label, "hold_s": a.hold, "start_c": a.start_c, "when": time.strftime("%Y-%m-%d %H:%M"), "poses": {}}
for pose in a.poses:
    print(f"{pose}: relax and cool to {a.start_c} C", flush=True)
    cool(a.start_c)
    run(*COMMANDS[pose])
    hand = connect()
    samples, t0, aborted = [], time.time(), False
    try:
        while time.time() - t0 < a.hold:
            cur, temp = hand.get_actuator_currents(), hand.get_actuator_temperatures()
            if cur and temp:
                samples.append((time.time() - t0, [abs(c) for c in cur], temp))
                if max(temp) >= ABORT_C:
                    relax_now(hand)
                    aborted = True
                    print(f"  ABORT: {NAMES[temp.index(max(temp))]} at {max(temp)} C, relaxed", flush=True)
                    break
            time.sleep(0.25)
    finally:
        relax_now(hand)  # also on Ctrl-C or a serial error
        hand.close()
    secs = samples[-1][0] - samples[0][0]
    mean = [sum(s[1][i] for s in samples) / len(samples) for i in range(7)]
    # temperature reads in whole degrees, so rise is end minus start over the hold
    rise = [(samples[-1][2][i] - samples[0][2][i]) * 60.0 / secs for i in range(7)]
    results["poses"][pose] = {
        "seconds": round(secs, 1), "aborted": aborted, "samples": len(samples),
        "mean_mA": [round(m) for m in mean], "total_mean_mA": round(sum(mean)),
        "start_C": samples[0][2], "end_C": samples[-1][2], "rise_C_per_min": [round(r, 1) for r in rise],
    }
    print(f"  {pose}: total {sum(mean):.0f} mA over {secs:.0f} s" + ("  (ABORTED)" if aborted else ""), flush=True)
    for i, n in enumerate(NAMES):
        print(f"    {n:13s} {mean[i]:7.0f} mA  {samples[0][2][i]:.0f}->{samples[-1][2][i]:.0f} C  {rise[i]:+.1f} C/min")

out = os.path.join(HERE, "..", "bench", f"hold_{a.label}.json")
os.makedirs(os.path.dirname(out), exist_ok=True)
with open(out, "w") as f:
    json.dump(results, f, indent=1)
print("wrote", os.path.normpath(out))
