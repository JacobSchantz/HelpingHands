#!/usr/bin/env python3
"""Wrist budget for the crow cartridge: mass and moment, measured off the STLs.

Printed parts are measured (volume and centroid by a signed-tetrahedron sum over
export/*.stl).  Bought parts are [GUESS] numbers, listed below so they can be
replaced by a kitchen scale.  Everything is in the follower (cartridge) frame,
and the moment arm is measured along Z from the wrist_roll horn face -- the
same datum plans/crow_gripper.md section 3 used, so the numbers compare.

Fails (exit 1) if the arm-side mass breaks the budget in
plans/handheld_gripper.md section 2 (<= 250 g at the wrist for gripper + camera,
itself unverified).  Stdlib only.

    python3 check_budget.py            # after ./build.sh
"""
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PLA = 1.24            # g/cm^3
INFILL = 0.45         # effective solid fraction at ~40 % infill + 3 perimeters
PIVOT_Z = 23.375      # ../params.scad jaw_pivot_z
DOCK_LIFT = 9.05      # crow_params.scad: dock_puck_h - fj_flange_z0
HORN_Z = 0.95 - 10.0  # horn face in the cartridge frame
TIP_Z = 105.375
THROAT_Z = 67.5
BUDGET_G = 250.0
LOAD_KG = 0.5         # voice-3c221288's payload figure, inherited


def stl(path):
    with open(path, "rb") as f:
        data = f.read()
    if data[:5] == b"solid" and b"facet" in data[:400]:
        v = [tuple(map(float, l.split()[1:4])) for l in data.decode().splitlines()
             if l.strip().startswith("vertex")]
        tris = list(zip(v[0::3], v[1::3], v[2::3]))
    else:
        n = struct.unpack("<I", data[80:84])[0]
        tris = []
        for i in range(n):
            f = struct.unpack("<12f", data[84 + 50 * i: 84 + 50 * i + 48])
            tris.append((f[3:6], f[6:9], f[9:12]))
    vol = cx = cy = cz = 0.0
    for a, b, c in tris:
        d = (a[0] * (b[1] * c[2] - b[2] * c[1]) - a[1] * (b[0] * c[2] - b[2] * c[0])
             + a[2] * (b[0] * c[1] - b[1] * c[0])) / 6.0
        vol += d
        cx += d * (a[0] + b[0] + c[0]) / 4
        cy += d * (a[1] + b[1] + c[1]) / 4
        cz += d * (a[2] + b[2] + c[2]) / 4
    return vol / 1000.0, (cx / vol, cy / vol, cz / vol)   # cm^3, mm


def printed(name, frame="follower"):
    vol, c = stl(os.path.join(HERE, "export", name + ".stl"))
    z = c[2] if frame == "follower" else PIVOT_Z - c[1]   # jaw frame -> follower
    return vol * PLA * INFILL, z, f"{vol:6.2f} cm^3 printed"


# name: (grams, z in the cartridge frame, note)
BOUGHT = {
    "gripper servo STS3215 (ID 6)": (55.0, 24.0, "[GUESS] datasheet-ish, in the cradle"),
    "UVC camera board + lens":      (12.0, 44.0, "[GUESS] at cam_pos"),
    "M3 screws, inserts, cross-pin": (8.0, 5.0, "[GUESS]"),
    "cable pigtail to the dock":    (10.0, 10.0, "[GUESS]"),
}


def main():
    arm = {
        "upper mandible + body": printed("upper"),
        "lower mandible":        printed("lower", frame="jaw"),
        "camera mount":          printed("camera_mount"),
        "wrist puck":            printed("puck"),
    }
    arm.update({k: (m, z, n) for k, (m, z, n) in BOUGHT.items()})

    print("ARM SIDE (what the SO-101 wrist carries)")
    tot = mom = 0.0
    for k, (m, z, n) in arm.items():
        arm_mm = z - HORN_Z
        tot += m
        mom += m * arm_mm
        print(f"  {k:32s} {m:6.1f} g   CG {arm_mm:6.1f} mm out   {n}")
    cg = mom / tot
    print(f"  {'total':32s} {tot:6.1f} g   CG {cg:6.1f} mm out   budget {BUDGET_G:.0f} g")

    # the stock pair, same method, for the comparison that matters
    sf = printed_stock("fixed_jaw")
    sm = printed_stock("moving_jaw", frame="jaw")
    s_tot = sf[0] + sm[0] + 55.0
    s_mom = sf[0] * (sf[1] + 0.05) + sm[0] * (sm[1] + 0.05) + 55.0 * (24.0 + 0.05)
    print(f"  stock gripper (no camera)        {s_tot:6.1f} g   CG {s_mom / s_tot:6.1f} mm out")
    print(f"  -> +{tot - s_tot:.1f} g and {mom / 1000 - s_mom / 1000:+.2f} g.m of self-moment vs stock")

    tip = TIP_Z - HORN_Z
    thr = THROAT_Z - HORN_Z
    print(f"\nLOAD ({LOAD_KG} kg): at the tip {tip:.1f} mm out -> {LOAD_KG * 9.81 * tip / 1000:.3f} N.m;"
          f" in the throat {thr:.1f} mm -> {LOAD_KG * 9.81 * thr / 1000:.3f} N.m"
          f" ({100 * (1 - thr / tip):.0f} % less)")
    print(f"  the dock's {DOCK_LIFT} mm of puck adds {LOAD_KG * 9.81 * DOCK_LIFT / 1000:.3f} N.m at full load"
          f" ({100 * DOCK_LIFT / (TIP_Z + 0.05):.1f} % on a tip load)")

    hand = {
        "cartridge (as above, no puck)": (tot - arm["wrist puck"][0], None, ""),
        "handle": printed("handle"),
        "trigger lever": printed("trigger"),
        "trigger servo STS3215": (55.0, None, "[GUESS]"),
        "iPhone": (200.0, None, "[GUESS] 170-230 g by model"),
        "screws": (6.0, None, "[GUESS]"),
    }
    h_tot = sum(v[0] for v in hand.values())
    print(f"\nHANDHELD (what the demonstrator holds, battery pack on the belt): {h_tot:.0f} g"
          f"  -- UMI's is 780 g")

    if tot > BUDGET_G:
        print(f"\nFAIL: {tot:.1f} g at the wrist is over the {BUDGET_G:.0f} g budget")
        return 1
    print("\nbudget: ok")
    return 0


def printed_stock(name, frame="follower"):
    vol, c = stl(os.path.join(HERE, "..", "export", name + ".stl"))
    z = c[2] if frame == "follower" else PIVOT_Z - c[1]
    return vol * PLA * INFILL, z


if __name__ == "__main__":
    sys.exit(main())
