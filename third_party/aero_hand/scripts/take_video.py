"""Camera evidence for teach.py; capture runs off the servo timing thread."""
import json
import os
from pathlib import Path
import threading
import time
import uuid


class TakeVideo:
    READ_GRACE_S = 1.0

    def _read(self, cap):
        deadline = time.monotonic() + self.READ_GRACE_S
        while not self.stop.is_set():
            ok, frame = cap.read()
            if ok:
                return ok, frame
            if time.monotonic() >= deadline:
                break
            self.stop.wait(.04)
        return False, None

    def __init__(self, directory, action, take=None, camera=0):
        self.directory = Path(directory).expanduser().resolve()
        self.action, self.take, self.camera = action, take, camera
        self.ready, self.stop = threading.Event(), threading.Event()
        self.error = None
        self.last_frame = None
        self.timestamps = []
        self.started_at = None

    def _run(self):
        cap = writer = None
        try:
            import cv2
            cap = cv2.VideoCapture(self.camera)
            if not cap.isOpened():
                raise RuntimeError(f"camera {self.camera} did not open")
            # Negotiate a known mode instead of inheriting the device's last/default
            # 1080p mode. 720p lowers USB/decode load while retaining finger detail.
            requested_width = int(os.environ.get('AERO_CAMERA_WIDTH', '1280'))
            requested_height = int(os.environ.get('AERO_CAMERA_HEIGHT', '720'))
            requested_fps = int(os.environ.get('AERO_CAMERA_FPS', '30'))
            for prop, value in ((cv2.CAP_PROP_FRAME_WIDTH, requested_width),
                                (cv2.CAP_PROP_FRAME_HEIGHT, requested_height),
                                (cv2.CAP_PROP_FPS, requested_fps)):
                cap.set(prop, value)
            ok, frame = self._read(cap)
            if not ok:
                raise RuntimeError("camera returned no frame")
            height, width = frame.shape[:2]
            self.frame_size = [width, height]
            self.capture_fps = cap.get(cv2.CAP_PROP_FPS)
            print(f"camera {self.camera}: {width}x{height}, reported {self.capture_fps} fps", flush=True)
            self.fps = 25
            writer = cv2.VideoWriter(str(self.video), cv2.VideoWriter_fourcc(*'mp4v'),
                                     self.fps, (width, height))
            if not writer.isOpened():
                raise RuntimeError("could not open video writer")
            self.started_at, start = time.time(), time.monotonic()
            while not self.stop.is_set():
                if not ok:
                    raise RuntimeError("camera stopped returning frames; capture stream lost (check USB connection/hub)")
                writer.write(frame)
                self.last_frame = time.monotonic()
                self.timestamps.append(self.last_frame - start)
                self.ready.set()
                self.stop.wait(max(0, start + len(self.timestamps) / self.fps - time.monotonic()))
                if not self.stop.is_set():
                    ok, frame = self._read(cap)
        except Exception as exc:
            self.error = str(exc)
            self.ready.set()
        finally:
            if writer is not None:
                writer.release()
            if cap is not None:
                cap.release()

    def check(self):
        if self.error:
            raise RuntimeError(f"video capture failed: {self.error}")
        if self.last_frame is None or time.monotonic() - self.last_frame > 3:
            raise RuntimeError("video capture stalled")

    def __enter__(self):
        self.directory.mkdir(parents=True, exist_ok=True)
        stem = f"{self.action}-{time.strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:8]}"
        self.video = self.directory / (stem + '.mp4')
        self.result = self.directory / (stem + '.json')
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        try:
            if not self.ready.wait(15):
                raise RuntimeError("camera startup timed out; hand not moved")
            self.check()
        except BaseException as exc:
            self.__exit__(type(exc), exc, exc.__traceback__)
            raise
        print(f"video {self.video}", flush=True)
        return self

    def __exit__(self, kind, error, traceback):
        self.stop.set()
        self.thread.join(timeout=5)
        if self.thread.is_alive():
            self.error = self.error or 'camera shutdown timed out; video may be incomplete'
        metadata = dict(action=self.action, take=self.take, camera=self.camera,
                        video=str(self.video), started_at=self.started_at,
                        fps=getattr(self, 'fps', None), frame_size=getattr(self, 'frame_size', None),
                        capture_fps=getattr(self, 'capture_fps', None), frame_times=self.timestamps,
                        status='failed' if error or self.error else 'completed',
                        error=str(error) if error else self.error)
        self.result.write_text(json.dumps(metadata, indent=2))
        print('capture_result ' + json.dumps({**metadata, 'result': str(self.result), 'frame_times': None}), flush=True)
        if self.error and error is None:
            raise RuntimeError(self.error)
