import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

import teach
from replay_run import ReplayRun, take_runs, link_record_capture


class ReplayHistoryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.take = Path(self.tmp.name) / 'take-20261017-170553.json'
        self.take.write_text(json.dumps({'samples': [[0.] * 8, [1.] + [90.] * 7]}))
        self.original = self.take.read_bytes()
        self.output = contextlib.redirect_stdout(io.StringIO())
        self.output.__enter__()
        self.addCleanup(self.output.__exit__, None, None, None)

    def test_multiple_runs_keep_original_and_distinguish_commands_measurements(self):
        ids = []
        for _ in range(2):
            with ReplayRun(self.take) as run:
                hand = Mock()
                hand.get_actuations.return_value = [3.] * 7
                wrapped = run.wrap(hand)
                wrapped.set_actuations([9.] * 7)
                wrapped.get_actuations()
                hand.get_actuations.return_value = None
                wrapped.get_actuations()
            ids.append(run.id)
            manifest = json.loads(run.data.read_text())
            rows = [json.loads(line) for line in run.hand_data.read_text().splitlines()]
            self.assertEqual([r['kind'] for r in rows], ['commanded_actuations', 'measured_actuations', 'measured_actuations'])
            self.assertEqual(rows[0]['values'], [9.] * 7)
            self.assertEqual(rows[1]['values'], [3.] * 7)
            self.assertIsNone(rows[2]['values'])
            self.assertEqual(manifest['measurement_count'], 1)
            self.assertEqual(manifest['status'], 'completed')
            self.assertIsNone(manifest['video'])
        self.assertNotEqual(*ids)
        self.assertEqual(len(take_runs(self.take)), 2)
        self.assertEqual(self.take.read_bytes(), self.original)

    def test_camera_startup_failure_retains_empty_failed_run(self):
        camera = Mock()
        camera.__enter__ = Mock(side_effect=RuntimeError('camera did not open'))
        camera.__exit__ = Mock()
        with self.assertRaisesRegex(RuntimeError, 'camera did not open'):
            with ReplayRun(self.take, video=camera) as run:
                with camera:
                    self.fail('must never start hand')
        manifest = json.loads(run.data.read_text())
        self.assertEqual(manifest['status'], 'failed')
        self.assertIn('camera did not open', manifest['error'])
        self.assertEqual(run.hand_data.read_text(), '')

    def test_interrupt_keeps_partial_evidence_and_nonempty_error(self):
        with self.assertRaises(KeyboardInterrupt):
            with ReplayRun(self.take) as run:
                run.event('commanded_actuations', [7.] * 7)
                raise KeyboardInterrupt()
        manifest = json.loads(run.data.read_text())
        self.assertEqual(manifest['status'], 'interrupted')
        self.assertTrue(manifest['error'])
        self.assertEqual(len(run.hand_data.read_text().splitlines()), 1)

    def test_record_custom_directory_and_legacy_capture_discovery(self):
        custom = Path(self.tmp.name) / 'custom-camera'
        custom.mkdir()
        video = custom / 'record.mp4'
        video.touch()
        capture = custom / 'record.json'
        capture.write_text(json.dumps(dict(take=str(self.take), video=str(video), action='record',
                                          started_at=1., status='completed')))
        link_record_capture(SimpleNamespace(take=self.take, result=capture))
        old = self.take.parent / 'videos'
        old.mkdir()
        (old / 'old.json').write_text(json.dumps(dict(take=str(self.take), action='replay',
                                                    started_at=2., status='failed', error='')))
        rows = take_runs(self.take)
        self.assertEqual([r['kind'] for r in rows], ['camera-only', 'record-video'])
        self.assertTrue(rows[0]['error'])
        self.assertEqual(rows[1]['video'], str(video))

    def test_camera_manifest_deduplicated_and_shutdown_failure_not_success(self):
        directory = self.take.parent / 'videos'
        directory.mkdir()
        capture = directory / 'run.json'
        video = directory / 'run.mp4'
        video.touch()
        with ReplayRun(self.take, video=SimpleNamespace(video=video, result=capture)) as run:
            capture.write_text(json.dumps(dict(take=str(self.take), action='replay', status='failed',
                                               error='camera shutdown failed', video=str(video))))
        rows = take_runs(self.take)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['status'], 'failed')
        self.assertEqual(rows[0]['kind'], 'replay')

    def test_extra_measurements_never_poll_faster_than_five_hz(self):
        with ReplayRun(self.take) as run:
            hand = Mock()
            with patch('replay_run.time.monotonic', side_effect=[0., 0., .1, .19, .2, .2, .3]):
                for _ in range(5):
                    run.poll(hand)
            self.assertEqual(hand.get_actuations.call_count, 2)

    def test_logging_failure_relaxes_and_closes_hand(self):
        hand = Mock()
        hand.actuation_lower_limits, hand.actuation_upper_limits = [0.] * 7, [300.] * 7
        hand.get_actuations.return_value = [0.] * 7
        hand.get_actuator_temperatures.return_value = [25.] * 7
        with self.assertRaisesRegex(OSError, 'disk full'):
            with ReplayRun(self.take) as run:
                original_event = run.event
                def event(kind, values, **fields):
                    if kind == 'commanded_actuations':
                        raise OSError('disk full')
                    return original_event(kind, values, **fields)
                with patch.object(run, 'event', side_effect=event), patch.object(teach, 'connect', return_value=hand), \
                        patch.object(teach.hand_speed, 'limit'), patch.object(teach.time, 'sleep'):
                    teach.replay(str(self.take), False, run=run)
        hand.set_actuations.assert_called_once()
        hand.ctrl_torque.assert_called_once_with([0] * 7)
        hand.close.assert_called_once()
        self.assertEqual(json.loads(run.data.read_text())['status'], 'failed')


if __name__ == '__main__':
    unittest.main()
