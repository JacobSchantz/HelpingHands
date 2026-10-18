"""Durable replay evidence, separate from immutable teaching samples."""
import hashlib
import json
import os
from pathlib import Path
import time
import uuid


def atomic_json(path, value):
    temporary = path.with_suffix('.tmp')
    with temporary.open('w') as stream:
        json.dump(value, stream, indent=2)
        stream.flush()
        os.fsync(stream.fileno())
    temporary.replace(path)


class ReplayRun:
    def __init__(self, take, mode='motion', video=None):
        self.take = Path(take).expanduser().resolve()
        self.video = video
        self.id = f"replay-{time.strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:12]}"
        self.directory = self.take.parent / 'runs' / self.take.stem
        self.data = self.directory / (self.id + '.json')
        self.hand_data = self.directory / (self.id + '.hand.jsonl')
        self.metadata = dict(id=self.id, kind='replay', source_take=str(self.take),
                             source_sha256=hashlib.sha256(self.take.read_bytes()).hexdigest(),
                             mode=mode, status='running', error=None, data=str(self.data),
                             hand_data=str(self.hand_data), started_at=time.time(),
                             hand_time_origin='seconds since run started_at',
                             commanded_semantics='submitted SDK targets; not measured motion or acknowledgment',
                             measured_semantics='encoder actuator positions in degrees; missing reads stay missing',
                             extra_position_poll_hz=5)
        self.phase = 'setup'
        self.next_poll = 0.0
        self.commands = self.measurements = 0

    def __enter__(self):
        self.directory.mkdir(parents=True, exist_ok=True)
        self.metadata['started_at'] = time.time()
        self.start = time.monotonic()
        self.stream = self.hand_data.open('x')
        self.last_flush = self.start
        atomic_json(self.data, self.metadata)
        return self

    def event(self, kind, values, **fields):
        now = time.monotonic()
        self.stream.write(json.dumps(dict(kind=kind, t=round(now - self.start, 6),
                                         phase=self.phase, values=values, **fields)) + '\n')
        if now - self.last_flush >= .2:
            self.stream.flush()
            self.last_flush = now

    def wrap(self, hand):
        return ObservedHand(hand, self)

    def poll(self, hand):
        if time.monotonic() >= self.next_poll:
            hand.get_actuations()
            self.next_poll = time.monotonic() + .2

    def __exit__(self, kind, error, traceback):
        self.stream.flush()
        os.fsync(self.stream.fileno())
        self.stream.close()
        status = 'completed' if error is None else 'interrupted' if isinstance(error, KeyboardInterrupt) else 'failed'
        message = ('Replay interrupted' if isinstance(error, KeyboardInterrupt) else str(error)) if error else None
        video_path = getattr(self.video, 'video', None)
        result_path = getattr(self.video, 'result', None)
        video_path = video_path if isinstance(video_path, (str, os.PathLike)) else None
        result_path = result_path if isinstance(result_path, (str, os.PathLike)) else None
        if result_path and Path(result_path).is_file():
            try:
                capture = json.loads(Path(result_path).read_text())
                if capture.get('status') == 'failed' and not error:
                    status, message = 'failed', capture.get('error') or 'Camera capture failed'
            except (OSError, ValueError):
                pass
        self.metadata.update(status=status, error=message, finished_at=time.time(),
                             command_count=self.commands, measurement_count=self.measurements,
                             video=str(video_path) if video_path and Path(video_path).is_file() else None,
                             capture_data=str(result_path) if result_path and Path(result_path).is_file() else None)
        atomic_json(self.data, self.metadata)
        print('replay_result ' + json.dumps(summary(self.metadata, self.data)), flush=True)


class ObservedHand:
    def __init__(self, hand, run):
        self.hand, self.run = hand, run

    def __getattr__(self, name):
        return getattr(self.hand, name)

    def set_actuations(self, values):
        result = self.hand.set_actuations(values)
        self.run.event('commanded_actuations', list(values))
        self.run.commands += 1
        return result

    def set_joint_positions(self, values):
        result = self.hand.set_joint_positions(values)
        self.run.event('commanded_joint_positions', list(values))
        self.run.commands += 1
        return result

    def get_actuations(self):
        values = self.hand.get_actuations()
        self.run.event('measured_actuations', values)
        if values is not None:
            self.run.measurements += 1
        return values


def summary(data, path, kind=None):
    video = data.get('video')
    return dict(id=data.get('id', Path(path).stem), started_at=data.get('started_at') or 0,
                status=data.get('status', 'unknown'), error=(data.get('error') or 'Capture failed or was interrupted') if data.get('status') == 'failed' else data.get('error'), data=str(Path(path).resolve()),
                video=video if video and Path(video).is_file() else None, kind=kind or data.get('kind', 'replay'))


def take_runs(take):
    """Discover history without editing the original take or inventing legacy telemetry."""
    take = Path(take).expanduser().resolve()
    runs, linked = [], set()
    for path in (take.parent / 'runs' / take.stem).glob('*.json'):
        try:
            data = json.loads(path.read_text())
            runs.append(summary(data, path))
            if data.get('capture_data'):
                linked.add(str(Path(data['capture_data']).resolve()))
        except (OSError, ValueError, TypeError):
            continue
    for path in (take.parent / 'videos').glob('*.json'):
        if str(path.resolve()) in linked:
            continue
        try:
            data = json.loads(path.read_text())
            if not data.get('take') or Path(data['take']).resolve() != take:
                continue
            action = data.get('action', '')
            if action not in ('record', 'replay', 'replay-full'):
                continue
            runs.append(summary(data, path, 'record-video' if action == 'record' else 'camera-only'))
        except (OSError, ValueError, TypeError):
            continue
    return sorted(runs, key=lambda item: item['started_at'], reverse=True)


def link_record_capture(video):
    """Index record video even when its files live in a custom --video-dir."""
    take, capture = getattr(video, 'take', None), getattr(video, 'result', None)
    if not isinstance(take, (str, os.PathLike)) or not isinstance(capture, (str, os.PathLike)):
        return
    take, capture = Path(take).resolve(), Path(capture).resolve()
    if not take.is_file() or not capture.is_file():
        return
    data = json.loads(capture.read_text())
    directory = take.parent / 'runs' / take.stem
    directory.mkdir(parents=True, exist_ok=True)
    data.update(id=capture.stem, kind='record-video', source_take=str(take), capture_data=str(capture))
    atomic_json(directory / (capture.stem + '.json'), data)
