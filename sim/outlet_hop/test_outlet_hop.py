"""Acceptance tests for the outlet hop, run against the simulator.

    python3 -m unittest discover sim/outlet_hop

Each test is one row of the acceptance table in plans/wall_outlet_hop.md.
These are SOFTWARE proofs only; the same rows get re-run on the fixture (Stage 2).
"""
import unittest

from outlet_hop import Limits, OutletHop, SimOutlet, SimRobot


def run(outlets, **robot_kw):
    robot = SimRobot(outlets, **robot_kw)
    return robot, OutletHop(robot).hop(list(outlets))


class HappyPath(unittest.TestCase):
    def test_unplug_move_replug_confirm(self):
        robot, out = run({"kitchen": SimOutlet()})
        self.assertTrue(out.ok, out.log)
        self.assertEqual(out.outlet, "kitchen")
        self.assertTrue(robot.loads_powered())

    def test_power_continuity_under_drive_and_compute_load(self):
        # 150 W compute + 200 W drive for 10 minutes on a 1.28 kWh pack.
        robot, out = run({"far": SimOutlet()}, compute_w=150, drive_w=200, drive_s=600)
        self.assertTrue(out.ok, out.log)
        self.assertTrue(robot.loads_powered())


class Power(unittest.TestCase):
    def test_low_battery_refuses_to_leave(self):
        robot, out = run({"kitchen": SimOutlet()}, soc=0.30)
        self.assertEqual(out.state, "plugged_in_place")
        self.assertTrue(robot.plug_seated())

    def test_battery_hits_reserve_while_travelling(self):
        # Small pack, long blocked drives: must stop and ask, not drain to zero.
        outlets = {"a": SimOutlet(blocked_drives=5), "b": SimOutlet(blocked_drives=5),
                   "c": SimOutlet()}
        robot, out = run(outlets, battery_wh=100, soc=0.45, drive_s=300)
        self.assertFalse(out.ok)
        self.assertIn("reserve", out.reason)
        self.assertTrue(robot.loads_powered())

    def test_power_path_that_drops_loads_is_caught(self):
        robot, out = run({"kitchen": SimOutlet()}, power_path="dead_on_unplug")
        self.assertFalse(out.ok)
        self.assertIn("power path", out.reason)


class Unplug(unittest.TestCase):
    def test_aborted_unplug_leaves_it_charging(self):
        robot, out = run({"kitchen": SimOutlet()}, withdraw_force_n=120)
        self.assertEqual(out.state, "plugged_in_place")
        self.assertTrue(robot.plug_seated())
        self.assertTrue(robot.ac_present())


class Insertion(unittest.TestCase):
    def test_incomplete_insertion_retries_then_seats(self):
        robot, out = run({"kitchen": SimOutlet(misaligned_tries=2)})
        self.assertTrue(out.ok, out.log)

    def test_insertion_never_seats_moves_on(self):
        outlets = {"stiff": SimOutlet(insert_force_n=95), "ok": SimOutlet()}
        robot, out = run(outlets)
        self.assertTrue(out.ok, out.log)
        self.assertEqual(out.outlet, "ok")

    def test_retry_limit_is_respected(self):
        robot, out = run({"jammed": SimOutlet(misaligned_tries=99)})
        self.assertFalse(out.ok)
        tries = [l for l in out.log if "insertion attempt" in l]
        self.assertEqual(len(tries), Limits().insert_attempts)


class ChargingDetection(unittest.TestCase):
    def test_seated_in_dead_outlet_is_not_charging(self):
        outlets = {"switched_off": SimOutlet(live=False), "ok": SimOutlet()}
        robot, out = run(outlets)
        self.assertEqual(out.outlet, "ok")

    def test_current_without_mains_is_not_charging(self):
        # Solar pushing current in must not read as "plugged in and charging".
        robot, out = run({"dead": SimOutlet(live=False)}, solar_a=5.0)
        self.assertFalse(out.ok)


class Outlets(unittest.TestCase):
    def test_missing_and_occupied_outlets_are_skipped(self):
        outlets = {"gone": SimOutlet(state="missing"), "busy": SimOutlet(state="occupied"),
                   "ok": SimOutlet()}
        robot, out = run(outlets)
        self.assertEqual(out.outlet, "ok")

    def test_obstruction_retries_then_next_outlet(self):
        outlets = {"behind_couch": SimOutlet(blocked_drives=9), "ok": SimOutlet()}
        robot, out = run(outlets)
        self.assertEqual(out.outlet, "ok")
        self.assertIn("behind_couch: unreachable; next outlet", out.log)

    def test_nothing_works_halts_and_asks(self):
        robot, out = run({"busy": SimOutlet(state="occupied")})
        self.assertFalse(out.ok)
        self.assertTrue(robot.stopped)


class Cable(unittest.TestCase):
    def test_stow_failure_once_recovers(self):
        robot, out = run({"kitchen": SimOutlet()}, stow_failures=1)
        self.assertTrue(out.ok, out.log)

    def test_stow_failure_never_drives(self):
        # SimRobot.drive_to asserts if it's ever asked to drive tethered.
        robot, out = run({"kitchen": SimOutlet()}, stow_failures=9)
        self.assertFalse(out.ok)
        self.assertIn("stow", out.reason)
        self.assertEqual(robot.at, "home")


if __name__ == "__main__":
    unittest.main()
