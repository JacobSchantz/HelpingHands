"""Behavioral checks for the harness. Stdlib only: python3 -m unittest robot_eval/test_robot_eval.py"""
import csv
import json
import sys
import tempfile
import threading
import unittest
import urllib.error
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import adapters  # noqa: E402
import client  # noqa: E402
import leaderboard  # noqa: E402
import protocol  # noqa: E402
import rent  # noqa: E402
import server  # noqa: E402

JPEG = b"\xff\xd8\xff\xe0fake"
STATE = [0.0, -10.0, 20.0, 5.0, 0.0, 30.0]
IMAGES = {"left": JPEG, "right": JPEG}


class Protocol(unittest.TestCase):
    def test_round_trip(self):
        request = protocol.make_request("Pick up the red block.", STATE, IMAGES)
        instruction, state, images = protocol.validate_request(json.loads(protocol.dumps(request)))
        self.assertEqual((instruction, state, images), ("Pick up the red block.", STATE, IMAGES))

    def test_rejects_wrist_camera_and_missing_eye(self):
        for images in ({"left": JPEG}, {**IMAGES, "wrist": JPEG}):
            with self.assertRaises(protocol.ProtocolError):
                protocol.make_request("go", STATE, images)

    def test_rejects_bad_state(self):
        for state in ([], STATE[:5], STATE[:5] + [float("nan")], STATE[:5] + [True]):
            with self.assertRaises(protocol.ProtocolError):
                protocol.make_request("go", state, IMAGES)

    def test_response_checks(self):
        request = protocol.make_request("go", STATE, IMAGES, now=100.0)
        good = {"request_id": request["request_id"], "actions": [STATE, STATE]}
        self.assertEqual(protocol.validate_response(good, request, 6, 1.0, now=100.5), [STATE, STATE])
        bad = [
            ({**good, "request_id": "other"}, 100.5),          # out of order / late
            (good, 102.0),                                      # stale
            ({**good, "actions": [STATE[:5]]}, 100.5),          # wrong width
            ({**good, "actions": [STATE[:5] + [float("inf")]]}, 100.5),
            ({**good, "actions": []}, 100.5),
        ]
        for response, now in bad:
            with self.assertRaises(protocol.ProtocolError):
                protocol.validate_response(response, request, 6, 1.0, now=now)

    def test_limit_step(self):
        self.assertEqual(protocol.limit_step([0, 0, 10], [10, -1, 10], 3), [3, -1, 10])


class Server(unittest.TestCase):
    def setUp(self):
        self.httpd = server.make_server(adapters.MockAdapter({"chunk": 4}), "secret", "127.0.0.1", 0)
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()
        self.url = f"http://127.0.0.1:{self.httpd.server_port}"

    def tearDown(self):
        self.httpd.shutdown()
        self.httpd.server_close()

    def test_act_over_http(self):
        api = client.Server(self.url, "secret", 5)
        self.assertEqual(api.call("/info")["adapter"], "mock")
        request = protocol.make_request("go", STATE, IMAGES)
        chunk = protocol.validate_response(api.call("/act", request), request, 6, 5)
        self.assertEqual(chunk, [STATE] * 4)

    def test_wrong_token_is_401(self):
        with self.assertRaises(urllib.error.HTTPError) as caught:
            client.Server(self.url, "wrong", 5).call("/info")
        self.assertEqual(caught.exception.code, 401)
        caught.exception.close()

    def test_malformed_request_is_400(self):
        with self.assertRaises(urllib.error.HTTPError) as caught:
            client.Server(self.url, "secret", 5).call("/act", {"protocol": 1, "state": STATE})
        self.assertEqual(caught.exception.code, 400)
        caught.exception.close()


class FakeArm:
    def __init__(self):
        self.moves = []

    def state(self):
        return self.moves[-1] if self.moves else list(STATE)

    def move(self, row):
        self.moves.append(row)


class FakeCameras:
    def __init__(self, fail_after=None):
        self.reads, self.fail_after = 0, fail_after

    def read(self):
        self.reads += 1
        if self.fail_after is not None and self.reads > self.fail_after:
            raise RuntimeError("camera frame missing")
        return IMAGES


class FakeServer:
    def __init__(self, target, corrupt=False):
        self.target, self.corrupt = target, corrupt

    def call(self, path, body=None):
        if path != "/act":
            return {}
        rid = "nope" if self.corrupt else body["request_id"]
        return {"request_id": rid, "actions": [self.target] * 5, "inference_s": 0.01}


class Episode(unittest.TestCase):
    def run_for(self, ticks, api, cameras, arm):
        clock = iter(range(ticks + 100))
        return client.run_episode(api, cameras, arm, "go", seconds=ticks, fps=30, steps_per_chunk=5,
                                  max_step=2.0, max_age_s=1e9, log=lambda *_: None,
                                  clock=lambda: next(clock), sleep=lambda _: None)

    def test_moves_are_rate_limited_toward_target(self):
        arm, target = FakeArm(), [s + 10 for s in STATE]
        stats = self.run_for(20, FakeServer(target), FakeCameras(), arm)
        self.assertEqual(arm.moves[0], [s + 2 for s in STATE])
        self.assertEqual(arm.moves[-1], target)
        self.assertGreater(stats["requests"], 1)

    def test_bad_reply_moves_nothing(self):
        arm = FakeArm()
        with self.assertRaises(protocol.ProtocolError):
            self.run_for(20, FakeServer(STATE, corrupt=True), FakeCameras(), arm)
        self.assertEqual(arm.moves, [])

    def test_far_first_action_is_refused(self):
        arm = FakeArm()
        with self.assertRaises(protocol.ProtocolError):
            self.run_for(20, FakeServer([s + 90 for s in STATE]), FakeCameras(), arm)
        self.assertEqual(arm.moves, [])

    def test_camera_loss_stops_without_reusing_frames(self):
        arm = FakeArm()
        with self.assertRaises(RuntimeError):
            self.run_for(100, FakeServer([s + 1 for s in STATE]), FakeCameras(fail_after=1), arm)
        self.assertEqual(len(arm.moves), 5)  # only the first chunk ran


class Rent(unittest.TestCase):
    def test_cheapest_gpu_that_fits(self):
        self.assertEqual(rent.pick_gpu(8)[0][0], "NVIDIA GeForce RTX 4090")
        self.assertEqual(rent.pick_gpu(32)[0][0], "NVIDIA RTX A6000")
        with self.assertRaises(SystemExit):
            rent.pick_gpu(200)

    def test_every_model_fits_a_gpu_and_starts_its_server(self):
        for name, spec in json.loads((HERE / "models.json").read_text())["models"].items():
            rent.pick_gpu(spec["min_vram_gb"])
            self.assertIn(f"server.py --model {name} ", rent.start_command(name, spec))

    def test_address_waits_for_mapping(self):
        self.assertIsNone(rent.address({"publicIp": "1.2.3.4", "portMappings": {}}))
        self.assertEqual(rent.address({"publicIp": "1.2.3.4", "portMappings": {"8000": 40123}}),
                         "http://1.2.3.4:40123")


class Files(unittest.TestCase):
    def test_models_registry(self):
        models = json.loads((HERE / "models.json").read_text())["models"]
        for name, spec in models.items():
            self.assertIn(spec["adapter"], adapters.ADAPTERS, name)
            self.assertIsInstance(spec["min_vram_gb"], (int, float), name)
            self.assertIn(spec.get("units", "range"), ("range", "degrees"), name)
            if spec["adapter"] == "lerobot":
                self.assertTrue(set(spec["camera_map"].values()) <= {*protocol.CAMERAS, "blank"}, name)
                self.assertIn("pip", spec, name)

    def test_tasks(self):
        tasks = json.loads((HERE / "tasks.json").read_text())["tasks"]
        self.assertEqual(len({t["id"] for t in tasks}), len(tasks))
        for task in tasks:
            self.assertTrue(task["instruction"] and task["rubric"] and task["seconds"] > 0)

    def test_leaderboard_counts_only_executed_trials(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "scores.csv"
            base = {"revision": "abcdef1234", "end_effector": "hand_gen_01", "max_score": 3,
                    "median_round_trip_s": 0.4, "task": "pick_block"}
            client.append_score(path, {**base, "model": "a", "executed": True, "score": 3, "success": True})
            client.append_score(path, {**base, "model": "a", "executed": True, "score": 0, "success": False})
            client.append_score(path, {**base, "model": "b", "executed": True, "score": 2, "success": False})
            client.append_score(path, {**base, "model": "c", "executed": False, "score": 3, "success": True})
            with open(path, newline="") as handle:
                text = leaderboard.table(list(csv.DictReader(handle)))
        lines = text.splitlines()
        self.assertIn("| 1 | b |", lines[2])
        self.assertIn("67%", lines[2])
        self.assertIn("| 2 | a |", lines[3])
        self.assertIn("1/2", lines[3])
        self.assertNotIn("| c |", text)


if __name__ == "__main__":
    unittest.main()
