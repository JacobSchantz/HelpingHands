"""Servo speed limiter for every script that drives the hand.

Default is 50% of full speed (Jake, 2026-10-17); go faster only when he explicitly asks
(set AERO_SPEED_PCT=80 or 100). Measured 2026-10-17: full speed peaks ~130 RPM; the
firmware's SET_SPE value is in Feetech units of 0.732 RPM, so 100% = 182 and 50% = 91
(verified: peak 67-72 RPM). The firmware keeps it in RAM, so apply it on every connect.
"""
import os

FULL = 182
DEFAULT_PCT = 50


def limit(hand, pct=None):
    pct = float(os.environ.get("AERO_SPEED_PCT", DEFAULT_PCT) if pct is None else pct)
    value = max(1, min(32766 if pct >= 100 else FULL, round(FULL * pct / 100)))
    for servo in range(7):
        hand.set_speed(servo, value)
    return pct
