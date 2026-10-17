"""Low-power pose holding. The servos have no brake, so a held pose costs current and heat for as
long as it is held. After a pose is reached, each servo's torque limit (SET_TOR) is lowered to the
smallest value that still holds it against its return spring, plus a margin; the next move raises it
again (engage). Each servo is told to hold where it actually settled, not the pose's target: a
servo that stalled short of its target (on the palm, a hand, another finger, a hard stop) otherwise
keeps pushing at its full torque limit forever (~2000 mA at 700). With an object in the hand
(grip.py, stall_torque set) a stalled servo keeps pushing at that fixed squeeze instead, so the
object isn't let go.

The firmware only applies SET_TOR on the next CTRL_POS, so every change resends the target. Its
torque values live in firmware RAM across scripts, which is why every move starts with engage().

Hold modes (AERO_HOLD, or --hold on pose.py / grip.py; the Mac app's Hold menu sets it):
  auto    the low-power search above (default)
  medium  every servo kept at a fixed torque that holds light objects
  firm    full torque on every servo, for tools like a hammer; the servos run hottest
"""
import os, time

MOVE_TORQUE = 700        # firmware boot default; every move runs at this
LEVELS = [450, 300, 200, 140, 100, 70, 50, 35, 25, 15, 10]  # tried in turn, high to low
DRIFT_DEG = 2.0          # actuation degrees a servo may sag before its torque counts as too low
MARGIN = 1.5             # held torque = lowest level that held x MARGIN
FLOOR = 30               # never hold below this
STALL_MA_PER_TORQUE = 1.5  # stalled servos draw ~3 mA per torque unit (2026-10-17 baseline)
STALL_ERR_DEG = 5.0
MODE_TORQUE = {"medium": 350, "firm": 1000}  # fixed hold torques; not yet measured on held objects


def mode(name=None):
    """The hold mode to use: `name`, else AERO_HOLD, else auto. Exits on an unknown mode."""
    m = (name or os.environ.get("AERO_HOLD") or "auto").strip().lower()
    if m != "auto" and m not in MODE_TORQUE:
        raise SystemExit(f"unknown hold '{m}'; use auto, medium or firm")
    return m


def _set(hand, torques):
    for i, t in enumerate(torques):
        hand.set_torque(i, int(t))


def engage(hand, torque=MOVE_TORQUE):
    """Full move torque on every servo; call before moving."""
    _set(hand, [torque] * 7)


def _target_actuations(hand, joints):
    j = hand.convert_seven_joints_to_sixteen(joints)
    j = [max(hand.joint_lower_limits[i], min(j[i], hand.joint_upper_limits[i])) for i in range(16)]
    act = hand.joints_to_actuations_model.hand_actuations(j)
    return [max(hand.actuation_lower_limits[i], min(act[i], hand.actuation_upper_limits[i])) for i in range(7)]


def _settle(hand, timeout=2.0):
    last, t0 = None, time.time()
    while time.time() - t0 < timeout:
        now = hand.get_actuations()
        if now and last and max(abs(x - y) for x, y in zip(now, last)) < 0.5:
            return now
        last = now or last
        time.sleep(0.1)
    return last


def hold(hand, joints, start=MOVE_TORQUE, stall_torque=None, how=None):
    """Lower each servo's torque to what it needs to keep `joints`; a stalled servo backs off to
    `stall_torque` when given. Medium and firm (see mode) skip that and hold every servo at a fixed
    torque, pushing on toward `joints`. Returns the torques left set."""
    m = mode(how)
    if m != "auto":
        final = [MODE_TORQUE[m]] * 7
        _set(hand, final)
        for _ in range(2):
            hand.set_joint_positions(joints)
            time.sleep(0.02)
        return final
    ref = _settle(hand)
    cur = hand.get_actuator_currents()
    if not ref or not cur:
        return [start] * 7  # can't measure, leave it as it is
    target = _target_actuations(hand, joints)
    stalled = [abs(cur[i]) > STALL_MA_PER_TORQUE * start and abs(ref[i] - target[i]) > STALL_ERR_DEG for i in range(7)]
    fixed = [s and stall_torque is not None for s in stalled]
    cmd = [target[i] if fixed[i] else ref[i] for i in range(7)]
    good, searching = [start] * 7, [not f for f in fixed]
    for level in (l for l in LEVELS if l < start):
        if not any(searching):
            break
        _set(hand, [level if searching[i] else good[i] for i in range(7)])
        hand.set_actuations(cmd)
        time.sleep(0.3)
        pos = hand.get_actuations()
        if not pos:
            break
        for i in range(7):
            if searching[i]:
                if abs(pos[i] - ref[i]) > DRIFT_DEG:
                    searching[i] = False  # sagged: the previous level was the lowest that held
                else:
                    good[i] = level
    final = [min(start, stall_torque) if fixed[i] else min(start, max(FLOOR, round(good[i] * MARGIN)))
             for i in range(7)]
    _set(hand, final)
    for _ in range(2):  # apply, and pull back anything that sagged on the last try
        hand.set_actuations(cmd)
        time.sleep(0.02)
    return final
