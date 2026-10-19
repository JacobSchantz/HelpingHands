import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import curate_take
import teach


class CuratedTakeTests(unittest.TestCase):
    def prepared(self):
        rows = [[0.] * 7, [20., 10., 30., 0., 0., 0., 0.], [30., 20., 100., 0., 0., 0., 0.]]
        for finger in range(3, 7):
            row = [0.] * 7
            row[finger] = 200.
            rows.append(row)
        source = {'name': 'synthetic', 'samples': [[i] + row for i, row in enumerate(rows)]}
        original = json.dumps(source)
        with patch.object(teach, 'clean', return_value=(list(range(len(rows))), rows, [True] * 7)):
            result = curate_take.prepare(source, [0, 1, 2])
        self.assertEqual(json.dumps(source), original)
        return result

    def test_exactly_one_close_and_release_each_with_no_overlap(self):
        take = self.prepared()
        samples = take['samples']
        for i in range(1, 8):
            signs = []
            for a, b in zip(samples, samples[1:]):
                delta = b[i] - a[i]
                if abs(delta) > 1e-7:
                    sign = 1 if delta > 0 else -1
                    if not signs or signs[-1] != sign:
                        signs.append(sign)
            self.assertEqual(signs, [1, -1])
        self.assertTrue(all(sum(v > 1e-6 for v in row[4:]) <= 1 for row in samples))
        peaks = [max(range(len(samples)), key=lambda k: samples[k][i]) for i in range(3, 8)]
        self.assertEqual(peaks, sorted(peaks))
        self.assertTrue(take['derivation']['generated'])
        self.assertFalse(take['derivation']['measured'])

    def test_prepared_default_replay_bypasses_sensor_processing(self):
        take = self.prepared()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'take.json'
            path.write_text(json.dumps(take))
            with patch.object(teach, 'clean', side_effect=AssertionError('must not denoise authored trajectory')), \
                    patch.object(teach, 'connect', side_effect=AssertionError('dry-run must not connect')), \
                    contextlib.redirect_stdout(io.StringIO()) as output:
                teach.replay(str(path), True)
            self.assertIn('replay prepared', output.getvalue())

    def test_prepared_samples_obey_speed_and_acceleration_bounds(self):
        take = self.prepared()
        samples = take['samples']
        for i in range(1, 8):
            speed = [(b[i] - a[i]) / (b[0] - a[0]) for a, b in zip(samples, samples[1:])]
            dt = samples[1][0] - samples[0][0]
            accel = [(b - a) / dt for a, b in zip(speed, speed[1:])]
            self.assertLessEqual(max(map(abs, speed)), take['derivation']['speed_cap_deg_s'] + .1)
            self.assertLessEqual(max(map(abs, accel)), take['derivation']['acceleration_cap_deg_s2'] + .1)


if __name__ == '__main__':
    unittest.main()
