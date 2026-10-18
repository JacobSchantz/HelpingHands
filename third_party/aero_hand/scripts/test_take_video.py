import json
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import Mock, patch

from take_video import TakeVideo
import teach


class VideoTests(unittest.TestCase):
    def test_camera_failure_prevents_operation(self):
        with tempfile.TemporaryDirectory() as directory:
            camera = Mock()
            camera.isOpened.return_value = False
            with patch('cv2.VideoCapture', return_value=camera):
                with self.assertRaisesRegex(RuntimeError, 'did not open'):
                    with TakeVideo(directory, 'replay'):
                        self.fail('operation must not start')
            camera.release.assert_called_once()
            result = json.loads(next(Path(directory).glob('*.json')).read_text())
            self.assertEqual(result['status'], 'failed')

    def test_capture_loss_is_reported_and_resources_close(self):
        with tempfile.TemporaryDirectory() as directory:
            frame = Mock(shape=(10, 10, 3))
            camera, writer = Mock(), Mock()
            camera.get.return_value = 30.0
            camera.read.side_effect = [(True, frame), (False, None)]
            with patch('cv2.VideoCapture', return_value=camera), patch('cv2.VideoWriter', return_value=writer), patch.object(TakeVideo, 'READ_GRACE_S', 0):
                with self.assertRaisesRegex(RuntimeError, 'stopped returning frames'):
                    with TakeVideo(directory, 'replay') as video:
                        time.sleep(.1)
                        video.check()
            writer.release.assert_called_once()
            camera.release.assert_called_once()

    def test_replay_failure_relaxes_hand(self):
        hand, video = Mock(), Mock()
        hand.actuation_lower_limits = [0] * 7
        hand.actuation_upper_limits = [360] * 7
        hand.get_actuations.return_value = [0] * 7
        video.check.side_effect = RuntimeError('camera lost')
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'take.json'
            path.write_text(json.dumps({'samples': [[0] * 8, [1] + [90] * 7]}))
            with patch.object(teach, 'connect', return_value=hand), patch.object(teach.hand_speed, 'limit'):
                with self.assertRaisesRegex(RuntimeError, 'camera lost'):
                    teach.replay(str(path), False, video=video)
        hand.ctrl_torque.assert_called_once_with([0] * 7)
        hand.close.assert_called_once()
        hand.set_actuations.assert_not_called()

    def test_record_camera_loss_preserves_motion(self):
        hand, video = Mock(), Mock()
        hand.actuation_lower_limits = [0] * 7
        hand.actuation_upper_limits = [360] * 7
        hand.get_actuations.return_value = [10] * 7
        hand.get_actuator_temperatures.return_value = [25] * 7
        hand.get_actuator_currents.return_value = [0] * 7
        video.check.side_effect = [None, None, RuntimeError('camera lost')]
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(teach, 'connect', return_value=hand), patch.object(teach, 'TAKES', directory):
                with self.assertRaisesRegex(RuntimeError, 'camera lost'):
                    teach.record(5, teach.TORQUE, video)
            take = json.loads(next(Path(directory).glob('take-*.json')).read_text())
            self.assertEqual(len(take['samples']), 2)
            self.assertTrue(take['interrupted'])
            self.assertEqual(take['error'], 'camera lost')
            self.assertTrue(Path(video.take).exists())
        hand.ctrl_torque.assert_called_with([0] * 7)
        hand.close.assert_called_once()

    def test_transient_camera_read_recovers(self):
        camera = Mock()
        camera.read.side_effect = [(False, None), (True, 'fresh frame')]
        video = TakeVideo('/tmp', 'test')
        self.assertEqual(video._read(camera), (True, 'fresh frame'))

    def test_dry_run_does_not_connect(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'take.json'
            path.write_text(json.dumps({'samples': [[0] * 8, [1] + [90] * 7]}))
            with patch.object(teach, 'connect') as connect:
                teach.replay(str(path), True)
                connect.assert_not_called()


if __name__ == '__main__':
    unittest.main()
