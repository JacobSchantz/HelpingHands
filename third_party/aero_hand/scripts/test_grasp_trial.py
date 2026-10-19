import json
import tempfile
from pathlib import Path
import unittest
from unittest.mock import Mock, patch
import grasp_trial as trial


class GraspTests(unittest.TestCase):
    def hand(self):
        h=Mock()
        h.get_actuations.return_value=[10]*7
        h.get_actuator_currents.return_value=[100]*7
        h.get_actuator_temperatures.return_value=[40]*7
        return h

    def test_missing_telemetry_aborts(self):
        h=self.hand();h.get_actuator_currents.return_value=None
        with self.assertRaisesRegex(RuntimeError,'missing'):
            trial.feedback(h)

    def test_overcurrent_and_temperature_abort(self):
        h=self.hand();h.get_actuator_currents.return_value=[-1800]+[100]*6
        with self.assertRaisesRegex(RuntimeError,'current cutoff'):
            trial.feedback(h)
        h=self.hand();h.get_actuator_temperatures.return_value=[40]*6+[55]
        with self.assertRaisesRegex(RuntimeError,'temperature cutoff'):
            trial.feedback(h)

    def test_posture_squeeze_preserves_thumb_opposition_and_original(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'take.json'
            data={'samples':[[0,85,30,100,110,110,110,110],[1,85,30,100,110,110,110,110]]}
            p.write_text(json.dumps(data));original=p.read_text()
            base,_=trial.recorded_target(str(p),.5,0)
            squeezed,source=trial.recorded_target(str(p),.5,20)
            self.assertEqual(squeezed[0],base[0])
            for i in range(3,7):self.assertAlmostEqual(squeezed[i]-base[i],20)
            self.assertEqual(p.read_text(),original)
            with self.assertRaisesRegex(ValueError,'within'):
                trial.recorded_target(str(p),2,20)

    def test_camera_fault_relaxes_before_video_finalizes(self):
        h=self.hand()
        h.actuation_lower_limits=[0]*7
        h.actuation_upper_limits=[360]*7
        video=Mock()
        video.__enter__=Mock(return_value=video)
        video.__exit__=Mock(return_value=False)
        video.video='test.mp4'
        video.check.side_effect=RuntimeError('camera lost')
        events=[]
        h.ctrl_torque.side_effect=lambda _:events.append('relax')
        video.__exit__.side_effect=lambda *args:events.append('finalize')
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(trial.teach,'TAKES',directory), patch.object(trial,'TakeVideo',return_value=video), patch.object(trial.teach,'connect',return_value=h), patch.object(trial.hold,'_target_actuations',return_value=[100]*7), patch.object(trial.hold,'engage'), patch.object(trial.hand_speed,'limit'):
                with self.assertRaisesRegex(RuntimeError,'camera lost'):
                    trial.run(200,5)
            result=json.loads(next(Path(directory).glob('grasp-trials/trial-*.json')).read_text())
            self.assertEqual(result['status'],'failed')
        self.assertEqual(events,['relax','finalize'])
        h.close.assert_called_once()

    def test_unbounded_trials_rejected_before_hardware(self):
        for torque, seconds in [(501,5),(200,11),(200,-1)]:
            with self.assertRaises(ValueError):trial.run(torque,seconds)

if __name__=='__main__':unittest.main()
