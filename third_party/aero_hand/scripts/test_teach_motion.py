"""Regression coverage for recording compression, without touching hardware."""
import unittest
import contextlib
import io
import json
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import teach


class MotionTests(unittest.TestCase):
    def test_sequential_fingers_do_not_move_together(self):
        rows = []
        for finger in (3, 6):
            for value in [0] * 25 + list(range(0, 101, 5)) + [100] * 25 + list(range(100, -1, -5)) + [0] * 25:
                row = [0.0] * 7
                row[finger] = value
                rows.append(row)
        times = [i / teach.SEND_HZ for i in range(len(rows))]
        with patch.object(teach, 'clean', return_value=(times, rows, [False] * 3 + [True, False, False, True])):
            poses, _ = teach.key_poses([])
        self.assertTrue(all(not (p[3] > 0 and p[6] > 0) for p in poses))
        self.assertEqual(max(p[3] for p in poses), 100)
        self.assertEqual(max(p[6] for p in poses), 100)
        # Interpolated playback must pass through open between the two curls.
        index_peak = next(i for i, p in enumerate(poses) if p[3] == 100)
        pinky_onset = next(i for i, p in enumerate(poses) if p[6] > 0)
        self.assertTrue(any(p == [0] * 7 for p in poses[index_peak + 1:pinky_onset]))

    def test_every_pose_is_an_observed_simultaneous_pose(self):
        rows = [[0, 0, 0, float(i), 100 - float(i), 0, 0] for i in range(101)]
        with patch.object(teach, 'clean', return_value=(list(range(101)), rows, [True] * 7)):
            poses, _ = teach.key_poses([])
        self.assertEqual(poses, [rows[0], rows[-1]])

    def test_still_take_has_one_pose(self):
        samples = [[i / 100] + [15.] * 7 for i in range(200)]
        poses, moving = teach.key_poses(samples)
        self.assertEqual(poses, [[15.] * 7])
        self.assertFalse(any(moving))


class SmoothTrajectoryTests(unittest.TestCase):
    def test_no_stops_at_intermediate_monotone_poses(self):
        poses = [[float(x)] * 7 for x in (0, 20, 40, 60, 80, 100)]
        frames = teach.smooth_frames(poses, 100)
        increments = [b[1][0] - a[1][0] for a, b in zip(frames, frames[1:])]
        self.assertTrue(all(x > 0 for x in increments))
        middle = [(b[1][0] - a[1][0]) / (b[0] - a[0])
                  for a, b in zip(frames, frames[1:]) if 20 < a[1][0] < 80]
        self.assertGreater(min(middle), 1)

    def test_speed_acceleration_and_reversal_bounds(self):
        frames = teach.smooth_frames([[float(x)] * 7 for x in (0, 80, 100, 20, 0)], 100)
        dt = frames[1][0] - frames[0][0]
        speeds = [(b[1][0] - a[1][0]) / dt for a, b in zip(frames, frames[1:])]
        accelerations = [(b - a) / dt for a, b in zip(speeds, speeds[1:])]
        self.assertLessEqual(max(map(abs, speeds)), 100 + 1e-6)
        self.assertLessEqual(max(map(abs, accelerations)), 200 + 1e-6)
        self.assertTrue(all(-1e-8 <= row[0] <= 100 + 1e-8 for _, row in frames))
        self.assertLess(abs(speeds[0]), 200 * dt)
        self.assertLess(abs(speeds[-1]), 200 * dt)

    def test_stationary_finger_stays_stationary_until_its_turn(self):
        poses = [[0.] * 7, [0, 0, 0, 100., 0, 0, 0], [0.] * 7,
                 [0, 0, 0, 0, 0, 0, 100.], [0.] * 7]
        frames = teach.smooth_frames(poses, 100)
        self.assertTrue(all(not (row[3] > 1e-8 and row[6] > 1e-8) for _, row in frames))

    def test_initial_glide_obeys_speed_and_minimum_duration(self):
        frames = teach.smooth_frames([[0.] * 7, [300.] * 7], 50, min_duration=1.)
        self.assertGreaterEqual(frames[-1][0], 6.)
        self.assertEqual(frames[0][1], [0.] * 7)
        self.assertEqual(frames[-1][1], [300.] * 7)


class RecordingSemanticsTests(unittest.TestCase):
    def test_bottle_scale_thumb_motion_survives_cleaning(self):
        # Approximate demonstrated bottle ranges: 19° abduction, 11° flexion,
        # about 90° tendon travel. Also include 2° drift on an idle tendon.
        samples = []
        for k in range(301):
            t = k / 100
            f = max(0., 1 - abs(t - 1.75) / .75)
            samples.append([t, 100 - 19 * f, 26 + 11 * f, 35 + 70 * f,
                            23 + 99 * f, 27 + 88 * f, 36 + 85 * f, 24 + 2 * f])
        _, rows, moving = teach.clean(samples)
        self.assertTrue(moving[0])
        self.assertTrue(moving[1])
        self.assertGreater(max(r[0] for r in rows) - min(r[0] for r in rows), 15)
        self.assertGreater(max(r[1] for r in rows) - min(r[1] for r in rows), 8)
        self.assertFalse(moving[6])
        self.assertEqual(len({r[6] for r in rows}), 1)

    def test_small_thumb_noise_still_suppressed(self):
        samples = [[k / 100, 90 + (k % 2) * 2, 30 + (k % 2) * 2] + [20.] * 5
                   for k in range(201)]
        _, _, moving = teach.clean(samples)
        self.assertFalse(any(moving))

    def test_record_currents_are_bounded_separate_and_missing_samples_omitted(self):
        clock = [0.0]
        reads = []
        def sleep(seconds):
            clock[0] += max(0., seconds)
        def read_current():
            reads.append(clock[0])
            return None if len(reads) == 2 else [-6.5, 13., 0., 26., 32.5, 39., 45.5]
        hand = SimpleNamespace(ctrl_torque=lambda _: None, close=lambda: None,
                               actuation_lower_limits=[0.] * 7, actuation_upper_limits=[300.] * 7,
                               get_actuator_temperatures=lambda: [25.] * 7,
                               get_actuations=lambda: [10.] * 7,
                               get_actuator_currents=read_current)
        with tempfile.TemporaryDirectory() as directory, \
                patch.object(teach, 'TAKES', directory), patch.object(teach, 'connect', return_value=hand), \
                patch.object(teach.time, 'monotonic', side_effect=lambda: clock[0]), \
                patch.object(teach.time, 'sleep', side_effect=sleep), contextlib.redirect_stdout(io.StringIO()):
            teach.record(.36, teach.TORQUE)
            take = json.loads(next(Path(directory).glob('take-*.json')).read_text())
        self.assertGreaterEqual(len(reads), 3)
        self.assertLessEqual(len(reads), 4)
        self.assertTrue(all(b - a >= .1 - 1e-8 for a, b in zip(reads, reads[1:])))
        self.assertEqual(len(take['currents']), len(reads) - 1)
        self.assertEqual(take['currents'][0][1], -6.5)
        self.assertEqual(take['current_unit'], 'mA')
        self.assertIn('not calibrated contact force', take['current_semantics'])
        self.assertGreater(len(take['samples']), 8 * len(reads))
        # Position samples keep their old timestamp-plus-seven-values schema.
        self.assertTrue(all(len(row) == 8 for row in take['samples']))


if __name__ == '__main__':
    unittest.main()
