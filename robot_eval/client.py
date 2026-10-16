"""Mac side of one scored trial: stereo head cameras + SO-101 -> policy server -> arm.

Run in the lerobot conda env, in native Terminal.app (see teleop.sh):

    python robot_eval/client.py --server http://HOST:PORT --task pick_block --trial 1
    python robot_eval/client.py ... --execute        # actually move the arm

Without --execute the arm is only read and the predicted actions are printed
(dry run). Ctrl+C stops at once; torque is released on disconnect. Every
trial ends with a score prompt and a row appended to robot_eval/scores.csv.
"""
import argparse
import csv
import json
import os
import statistics
import sys
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import protocol  # noqa: E402

REPO = HERE.parent
FOLLOWER_RIGHT_PORT = "/dev/tty.usbmodem5AA90242401"  # robot_config.md
SCORE_FIELDS = ["date", "model", "revision", "adapter", "camera_map", "task", "trial",
                "arm", "end_effector", "executed", "score", "max_score", "success",
                "median_round_trip_s", "median_inference_s", "requests", "gpu", "notes"]


class Server:
    def __init__(self, url, token, timeout_s):
        self.url, self.token, self.timeout_s = url.rstrip("/"), token, timeout_s

    def call(self, path, body=None):
        request = urllib.request.Request(
            self.url + path, data=None if body is None else protocol.dumps(body),
            headers={"Authorization": f"Bearer {self.token}",
                     "Content-Type": "application/json"})
        with urllib.request.urlopen(request, timeout=self.timeout_s) as response:
            return json.loads(response.read())


class StereoCameras:
    """Two eye-height views: one side-by-side stereo device, or two devices."""

    def __init__(self, stereo=None, left=None, right=None, width=1280, height=480):
        import cv2
        self.cv2 = cv2
        self.split = stereo is not None
        indices = [stereo] if self.split else [left, right]
        self.caps = []
        for index in indices:
            cap = cv2.VideoCapture(index)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, width if self.split else width // 2)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            if not cap.isOpened():
                raise SystemExit(f"camera {index} did not open (camera permission?)")
            self.caps.append(cap)

    def read(self):
        frames = []
        for cap in self.caps:
            ok, frame = cap.read()
            if not ok:
                raise RuntimeError("camera frame missing; stopping (never reuse an old frame)")
            frames.append(frame)
        if self.split:
            half = frames[0].shape[1] // 2
            frames = [frames[0][:, :half], frames[0][:, half:]]
        jpegs = [self.cv2.imencode(".jpg", f, [self.cv2.IMWRITE_JPEG_QUALITY, 85])[1].tobytes()
                 for f in frames]
        return dict(zip(protocol.CAMERAS, jpegs))

    def close(self):
        for cap in self.caps:
            cap.release()


class Arm:
    def __init__(self, port, arm_id, use_degrees, execute):
        from lerobot.robots.so_follower.config_so_follower import SOFollowerRobotConfig
        from lerobot.robots.so_follower.so_follower import SOFollower
        self.execute = execute
        self.robot = SOFollower(SOFollowerRobotConfig(
            port=port, id=arm_id, calibration_dir=REPO / "lerobot_calibration",
            use_degrees=use_degrees, disable_torque_on_disconnect=True))
        self.robot.connect()

    def state(self):
        obs = self.robot.get_observation()
        return [float(obs[f"{j}.pos"]) for j in protocol.JOINTS]

    def move(self, row):
        if self.execute:
            self.robot.send_action({f"{j}.pos": v for j, v in zip(protocol.JOINTS, row)})

    def close(self):
        self.robot.disconnect()


def run_episode(server, cameras, arm, instruction, seconds, fps, steps_per_chunk,
                max_step, max_age_s, max_jump=25.0, log=print, clock=time.monotonic,
                sleep=time.sleep):
    """Observe -> predict -> execute up to steps_per_chunk rows, until time is up.

    Returns timing stats. Any bad response, camera loss or exception ends the
    episode without executing that chunk; nothing is retried or replayed. A
    chunk whose first row is more than max_jump from the current pose means
    the model speaks different units or joint conventions: it is refused.
    """
    round_trips, inference = [], []
    end = clock() + seconds
    server.call("/reset", {})
    while clock() < end:
        state = arm.state()
        request = protocol.make_request(instruction, state, cameras.read())
        sent = time.perf_counter()
        response = server.call("/act", request)
        round_trips.append(time.perf_counter() - sent)
        inference.append(float(response.get("inference_s", 0)))
        chunk = protocol.validate_response(response, request, len(state), max_age_s)
        jump = max(abs(a - b) for a, b in zip(chunk[0], state))
        if jump > max_jump:
            raise protocol.ProtocolError(
                f"first action is {jump:.1f} from the current pose (> {max_jump}); "
                "check the model's units / joint signs before executing")
        log(f"chunk {len(round_trips)}: {len(chunk)} rows, first {[round(v, 1) for v in chunk[0]]},"
            f" round trip {round_trips[-1]:.3f}s")
        previous = state
        for row in chunk[:steps_per_chunk]:
            if clock() >= end:
                break
            previous = protocol.limit_step(previous, row, max_step)
            arm.move(previous)
            sleep(1 / fps)
    return {"requests": len(round_trips),
            "median_round_trip_s": round(statistics.median(round_trips), 3) if round_trips else "",
            "median_inference_s": round(statistics.median(inference), 3) if inference else ""}


def append_score(path, row):
    new = not Path(path).exists()
    with open(path, "a", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=SCORE_FIELDS)
        if new:
            writer.writeheader()
        writer.writerow({k: row.get(k, "") for k in SCORE_FIELDS})


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--server", required=True)
    p.add_argument("--task", required=True, help="id from robot_eval/tasks.json")
    p.add_argument("--trial", type=int, required=True)
    p.add_argument("--execute", action="store_true", help="move the arm (default: dry run)")
    p.add_argument("--stereo-device", type=int, help="one side-by-side stereo camera (e.g. ELP)")
    p.add_argument("--left", type=int, help="left eye camera index (two-device rig)")
    p.add_argument("--right", type=int, help="right eye camera index (two-device rig)")
    p.add_argument("--arm", default="follower_right")
    p.add_argument("--port", default=FOLLOWER_RIGHT_PORT)
    p.add_argument("--end-effector", default="so101_stock_jaw", help="e.g. hand_gen_01")
    p.add_argument("--fps", type=float, default=30)
    p.add_argument("--steps-per-chunk", type=int, default=15)
    p.add_argument("--max-step", type=float, default=3.0, help="max joint change per control step")
    p.add_argument("--max-jump", type=float, default=25.0,
                   help="refuse a chunk starting this far from the current pose")
    p.add_argument("--max-age", type=float, default=1.5, help="drop replies older than this (s)")
    p.add_argument("--gpu", default=os.environ.get("ROBOT_EVAL_GPU", ""))
    p.add_argument("--scores", default=str(HERE / "scores.csv"))
    args = p.parse_args()
    if (args.stereo_device is None) == (args.left is None or args.right is None):
        p.error("give --stereo-device, or both --left and --right")
    tasks = {t["id"]: t for t in json.loads((HERE / "tasks.json").read_text())["tasks"]}
    task = tasks.get(args.task) or p.error(f"unknown task; known: {', '.join(tasks)}")

    server = Server(args.server, os.environ["ROBOT_EVAL_TOKEN"], timeout_s=args.max_age)
    info = server.call("/info")
    print(f"model {info['model']} @ {info['revision']} via {info['adapter']}")
    print(f"task {task['id']}: {task['instruction']}\nsetup: {task['setup']}")
    input("Reset the scene, then press Enter to start (Ctrl+C stops at any time) ")
    cameras = StereoCameras(args.stereo_device, args.left, args.right)
    arm = Arm(args.port, args.arm, info.get("units") == "degrees", args.execute)
    stats, notes = {}, ""
    try:
        stats = run_episode(server, cameras, arm, task["instruction"], task["seconds"], args.fps,
                            args.steps_per_chunk, args.max_step, args.max_age, args.max_jump)
    except KeyboardInterrupt:
        notes = "stopped by operator"
    except Exception as error:  # noqa: BLE001 - any failure ends the trial safely
        notes = f"aborted: {error}"
    finally:
        arm.close()
        cameras.close()
    print(notes or "time up")
    print("Rubric:\n" + "\n".join(f"  {i + 1}. {s}" for i, s in enumerate(task["rubric"])))
    score = int(input(f"Points earned 0-{len(task['rubric'])}: "))
    notes = " / ".join(x for x in (notes, input("Notes: ").strip()) if x)
    append_score(args.scores, {
        "date": time.strftime("%Y-%m-%d %H:%M"), "model": info["model"], "revision": info["revision"],
        "adapter": info["adapter"], "camera_map": json.dumps(info.get("camera_map") or info.get("camera_order")),
        "task": task["id"], "trial": args.trial, "arm": args.arm, "end_effector": args.end_effector,
        "executed": args.execute, "score": score, "max_score": len(task["rubric"]),
        "success": score == len(task["rubric"]), "gpu": args.gpu, "notes": notes, **stats})
    print(f"saved to {args.scores}")


if __name__ == "__main__":
    main()
