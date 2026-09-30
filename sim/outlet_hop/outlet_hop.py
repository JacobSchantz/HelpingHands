"""Outlet hop: unplug -> stay powered on battery -> drive -> replug -> confirm charging.

This is the controller for the first Helping Hands milestone (plans/wall_outlet_hop.md)
plus a simulated robot with fault injection, so every failure path in the plan can be
exercised before any hardware exists. The controller only talks to the `Robot`
interface; the real robot implements the same methods later.

Everything here is SIMULATED. Passing tests prove the logic, not the hardware.
"""
from dataclasses import dataclass, field


# ---------------------------------------------------------------- limits

@dataclass
class Limits:
    leave_soc: float = 0.40          # won't unplug below this state of charge
    reserve_soc: float = 0.15        # travelling below this = stop and ask for help
    max_withdraw_n: float = 70.0     # stop pulling if the plug needs more than this
    max_insert_n: float = 60.0       # stop pushing before this (UL 498 withdrawal is 3-15 lbf)
    insert_depth_mm: float = 16.0    # NEMA 5-15 blade engagement, face-to-face
    step_mm: float = 2.0
    insert_attempts: int = 3         # per outlet
    drive_attempts: int = 2          # per outlet
    stow_attempts: int = 2
    charge_min_a: float = 1.0        # battery current that counts as charging
    charge_confirm_samples: int = 5  # consecutive samples of AC present + current in


# ---------------------------------------------------------------- the robot interface

class Robot:
    """What the controller needs from hardware. The simulator below implements it."""
    def soc(self): ...                      # 0..1, from the battery shunt
    def loads_powered(self): ...            # Mac, iPad, controllers, radio all up
    def ac_present(self): ...               # mains detected at the charger input
    def battery_current_a(self): ...        # + = into the battery
    def plug_seated(self): ...              # face switch on the plug holder closed
    def cable_stowed(self): ...             # pigtail back in its channel
    def force_n(self): ...                  # axial force on the plug holder
    def move_plug(self, mm): ...            # + = toward the wall; returns False if stopped
    def stow_cable(self): ...               # returns True when stowed
    def drive_to(self, outlet): ...         # returns "arrived" | "blocked"
    def inspect(self, outlet): ...          # returns "free" | "occupied" | "missing"
    def tick(self, seconds): ...            # let time pass (sensor sampling)
    def stop(self): ...                     # all motion off, brakes on


# ---------------------------------------------------------------- the controller

@dataclass
class Outcome:
    ok: bool
    state: str                   # where it ended: "charging", "plugged_in_place", "halted"
    reason: str = ""
    outlet: str | None = None
    log: list = field(default_factory=list)


class OutletHop:
    def __init__(self, robot, limits=None):
        self.r = robot
        self.lim = limits or Limits()
        self.log = []

    def note(self, msg):
        self.log.append(msg)

    def halt(self, reason, state="halted"):
        self.r.stop()
        self.note(f"HALT: {reason}")
        return Outcome(False, state, reason, log=self.log)

    # -- public

    def hop(self, outlets):
        """Leave the current outlet and end up charging at one of `outlets` (in order)."""
        lim = self.lim
        if self.r.soc() < lim.leave_soc:
            return Outcome(False, "plugged_in_place", "battery too low to leave", log=self.log)

        unplugged = self.unplug()
        if unplugged is not None:
            return unplugged

        for outlet in outlets:
            if self.r.soc() < lim.reserve_soc:
                return self.halt("battery at reserve while travelling; need help")
            result = self.try_outlet(outlet)
            if result == "charging":
                return Outcome(True, "charging", outlet=outlet, log=self.log)
            if result.startswith("halt:"):
                return self.halt(result[5:])
            self.note(f"{outlet}: {result}; next outlet")
        return self.halt("no outlet worked; need help")

    # -- steps

    def unplug(self):
        """Pull straight back. Returns None on success, an Outcome if it must stop."""
        lim = self.lim
        pulled = 0.0
        while self.r.plug_seated() or pulled < lim.insert_depth_mm:
            if not self.r.move_plug(-lim.step_mm) or self.r.force_n() > lim.max_withdraw_n:
                # Aborted unplug: push back in so it is still charging, and stop.
                self.r.move_plug(pulled)
                return self.halt("plug would not come out within force limit",
                                 state="plugged_in_place")
            pulled += lim.step_mm
            if not self.r.loads_powered():
                return self.halt("loads lost power during unplug (power path failed)")
        self.r.tick(1)
        if self.r.ac_present():
            return self.halt("still seeing mains after unplug")
        if not self.r.loads_powered():
            return self.halt("loads lost power after unplug (power path failed)")
        self.note("unplugged; loads stayed up on battery")
        return self.stow()

    def stow(self):
        for attempt in range(self.lim.stow_attempts):
            if self.r.stow_cable() and self.r.cable_stowed():
                self.note("cable stowed")
                return None
            self.note(f"stow attempt {attempt + 1} failed")
        return self.halt("cable would not stow; not driving with a loose cord")

    def try_outlet(self, outlet):
        lim = self.lim
        # Interlock: never drive with mains attached or a cord out.
        if self.r.ac_present() or not self.r.cable_stowed():
            return "halt:drive interlock (mains present or cable out)"
        for attempt in range(lim.drive_attempts):
            if self.r.drive_to(outlet) == "arrived":
                break
            self.note(f"{outlet}: blocked (drive attempt {attempt + 1})")
            if self.r.soc() < lim.reserve_soc:
                return "halt:battery at reserve while travelling; need help"
        else:
            return "unreachable"

        seen = self.r.inspect(outlet)
        if seen != "free":
            return seen

        for attempt in range(lim.insert_attempts):
            if self.insert():
                if self.confirm_charging():
                    self.note(f"{outlet}: charging")
                    return "charging"
                self.note(f"{outlet}: seated but not charging (dead/switched outlet?)")
                self.back_out()
                if self.stow() is not None:
                    return "halt:cable would not stow after a dead outlet"
                return "no power"
            self.note(f"{outlet}: insertion attempt {attempt + 1} failed")
            self.back_out()
        if self.stow() is not None:
            return "halt:cable would not stow after failed insertion"
        return "would not seat"

    def insert(self):
        lim = self.lim
        pushed = 0.0
        while pushed < lim.insert_depth_mm:
            if not self.r.move_plug(lim.step_mm) or self.r.force_n() > lim.max_insert_n:
                return False
            pushed += lim.step_mm
        return self.r.plug_seated()

    def back_out(self):
        self.r.move_plug(-self.lim.insert_depth_mm - self.lim.step_mm)

    def confirm_charging(self):
        """Mains present AND current into the battery, several samples in a row.
        Current alone is not proof (solar or regen can push current too)."""
        good = 0
        for _ in range(self.lim.charge_confirm_samples * 3):
            self.r.tick(1)
            if self.r.ac_present() and self.r.battery_current_a() > self.lim.charge_min_a:
                good += 1
                if good >= self.lim.charge_confirm_samples:
                    return True
            else:
                good = 0
        return False


# ---------------------------------------------------------------- simulator

@dataclass
class SimOutlet:
    state: str = "free"              # free | occupied | missing
    live: bool = True                # False = dead or wall-switched off
    insert_force_n: float = 35.0     # force to push the plug fully home
    blocked_drives: int = 0          # how many drive attempts hit an obstacle
    misaligned_tries: int = 0        # insert attempts that jam on the cover plate


class SimRobot(Robot):
    """Energy + contact model with fault injection. Units: Wh, W, mm, N, s."""

    def __init__(self, outlets, battery_wh=1280.0, soc=0.9, compute_w=70.0,
                 drive_w=60.0, drive_s=120.0, withdraw_force_n=40.0,
                 power_path="online", stow_failures=0, solar_a=0.0):
        self.outlets = outlets
        self.cap_wh = battery_wh
        self.wh = battery_wh * soc
        self.compute_w, self.drive_w, self.drive_s = compute_w, drive_w, drive_s
        self.withdraw_force_n = withdraw_force_n
        self.power_path = power_path          # "online" | "dead_on_unplug"
        self.stow_failures = stow_failures
        self.solar_a = solar_a
        self.at = "home"                      # starts plugged in at home
        self.depth = 16.0                     # mm of blade engagement
        self.cable_out = True
        self.powered = True
        self.force = 0.0
        self.jams = {}
        self.stopped = False

    # sensors
    def soc(self): return self.wh / self.cap_wh
    def loads_powered(self): return self.powered
    def force_n(self): return self.force
    def plug_seated(self): return self.depth >= 16.0
    def cable_stowed(self): return not self.cable_out

    def _mains(self):
        o = self.outlets.get(self.at)
        return self.plug_seated() and (self.at == "home" or (o is not None and o.live))

    def ac_present(self): return self._mains()

    def battery_current_a(self):
        return (15.0 if self._mains() else 0.0) + self.solar_a

    # actuators
    def move_plug(self, mm):
        self.stopped = False
        if mm < 0:
            self.force = self.withdraw_force_n if self.depth > 0 else 0.0
            if self.force > 70.0:
                return False
            self.depth = max(0.0, self.depth + mm)
            if self.depth == 0 and self.power_path == "dead_on_unplug":
                self.powered = False
            return True
        self.cable_out = True
        o = self.outlets.get(self.at)
        jam_left = self.jams.setdefault(self.at, o.misaligned_tries if o else 0)
        if jam_left > 0 and self.depth + mm > 2.0:
            self.force = 90.0                # blade on the cover plate
            self.jams[self.at] = jam_left - 1
            return False
        self.force = o.insert_force_n if o and self.depth > 4 else 5.0
        self.depth = min(16.0, self.depth + mm)
        return True

    def stow_cable(self):
        if self.depth > 0:
            return False
        if self.stow_failures > 0:
            self.stow_failures -= 1
            return False
        self.cable_out = False
        return True

    def drive_to(self, outlet):
        assert not self._mains() and not self.cable_out, "drove while tethered"
        o = self.outlets[outlet]
        self._spend(self.compute_w + self.drive_w, self.drive_s)
        if o.blocked_drives > 0:
            o.blocked_drives -= 1
            return "blocked"
        self.at = outlet
        return "arrived"

    def inspect(self, outlet):
        return self.outlets[outlet].state

    def tick(self, seconds):
        self._spend(self.compute_w, seconds)
        if self._mains():
            self.wh = min(self.cap_wh, self.wh + 15.0 * 12.8 * seconds / 3600)

    def stop(self):
        self.stopped = True
        self.force = 0.0

    def _spend(self, watts, seconds):
        self.wh -= watts * seconds / 3600
        if self.wh <= 0:
            self.wh, self.powered = 0.0, False
