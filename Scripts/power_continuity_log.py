#!/usr/bin/env python3
"""Stage 0 of plans/wall_outlet_hop.md: did the Mac stay up when the wall plug came out?

Run this on the Mac mini while it is powered through the candidate battery/power path.
Pull the battery's wall plug by hand (it's a certified cord and outlet; nothing is
opened up), wait, plug it back, then Ctrl-C.

    python3 Scripts/power_continuity_log.py            # writes power_continuity.csv
    python3 Scripts/power_continuity_log.py --report   # summarise the last run

It writes a heartbeat every 50 ms with the kernel boot time. A reboot shows up as a
changed boot time; a brown-out that froze the machine shows up as a gap between
heartbeats. Either one fails the test. Optional --load burns CPU so the test runs
under compute load, as the plan asks.
"""
import argparse
import csv
import multiprocessing
import subprocess
import sys
import time

LOG = "power_continuity.csv"
GAP_FAIL_S = 0.5


def boot_time():
    out = subprocess.run(["sysctl", "-n", "kern.boottime"], capture_output=True, text=True)
    return out.stdout.split("sec =")[1].split(",")[0].strip() if "sec =" in out.stdout else "?"


def burn():
    while True:
        pass


def record(load):
    workers = [multiprocessing.Process(target=burn, daemon=True)
               for _ in range(multiprocessing.cpu_count() if load else 0)]
    for w in workers:
        w.start()
    boot = boot_time()
    print(f"logging to {LOG} (boot {boot}, load={'on' if load else 'off'}); pull the plug, "
          "then Ctrl-C", flush=True)
    with open(LOG, "a", newline="") as f:
        w = csv.writer(f)
        try:
            while True:
                w.writerow([f"{time.time():.3f}", boot])
                f.flush()
                time.sleep(0.05)
        except KeyboardInterrupt:
            pass


def report():
    try:
        rows = [(float(t), b) for t, b in csv.reader(open(LOG))]
    except FileNotFoundError:
        sys.exit(f"no {LOG} yet")
    boots = sorted({b for _, b in rows})
    worst = max((b[0] - a[0] for a, b in zip(rows, rows[1:])), default=0.0)
    span = rows[-1][0] - rows[0][0] if rows else 0
    ok = len(boots) == 1 and worst < GAP_FAIL_S
    print(f"{len(rows)} beats over {span:.0f}s, boots seen: {len(boots)}, "
          f"longest gap: {worst * 1000:.0f} ms -> {'PASS' if ok else 'FAIL'}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--report", action="store_true")
    p.add_argument("--load", action="store_true", help="run all cores flat out while logging")
    a = p.parse_args()
    report() if a.report else record(a.load)
