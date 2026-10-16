"""The one policy-server contract every model is tried through.

Stdlib only, so the Mac client (lerobot conda env) and any GPU server image
import the same file. See plans/robot_model_scouting.md.

    POST /act    {instruction, state, images, request_id, sent_at}
              -> {request_id, actions, model, revision, inference_s}
    GET  /info  -> {model, revision, adapter, action_dim, chunk, camera_map}
    POST /reset -> {}   (start of a new episode)

Images are the two eye-height stereo views, keys "left" and "right", each a
base64 JPEG. Nothing else: no wrist camera exists in the human-mirror setup.
State and actions are SO-101 joint positions in LeRobot units, in JOINTS order,
six per arm. Actions are a chunk: a list of rows, each the same width as state.
"""
import base64
import json
import math
import time
import uuid

PROTOCOL_VERSION = 1
CAMERAS = ("left", "right")
JOINTS = ("shoulder_pan", "shoulder_lift", "elbow_flex",
          "wrist_flex", "wrist_roll", "gripper")
MAX_IMAGE_BYTES = 2_000_000
MAX_CHUNK = 256


class ProtocolError(ValueError):
    """A request or response that must not reach a model or a motor."""


def encode_jpeg(data):
    return base64.b64encode(data).decode("ascii")


def decode_jpeg(text):
    try:
        data = base64.b64decode(text, validate=True)
    except (ValueError, TypeError) as error:
        raise ProtocolError(f"image is not base64: {error}") from None
    if not data.startswith(b"\xff\xd8"):
        raise ProtocolError("image is not a JPEG")
    if len(data) > MAX_IMAGE_BYTES:
        raise ProtocolError(f"image is {len(data)} bytes, max {MAX_IMAGE_BYTES}")
    return data


def _finite_row(row, width, what):
    if not isinstance(row, list) or len(row) != width:
        raise ProtocolError(f"{what} must be a list of {width} numbers")
    for value in row:
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            raise ProtocolError(f"{what} has a non-finite or non-numeric value: {value!r}")
    return [float(v) for v in row]


def make_request(instruction, state, images, now=None):
    request = {
        "protocol": PROTOCOL_VERSION,
        "request_id": uuid.uuid4().hex,
        "sent_at": time.time() if now is None else now,
        "instruction": instruction,
        "state": list(state),
        "images": {k: encode_jpeg(v) for k, v in images.items()},
    }
    validate_request(request)
    return request


def validate_request(request):
    """Return (instruction, state, {camera: jpeg bytes}) or raise ProtocolError."""
    if not isinstance(request, dict) or request.get("protocol") != PROTOCOL_VERSION:
        raise ProtocolError(f"protocol must be {PROTOCOL_VERSION}")
    instruction = request.get("instruction")
    if not isinstance(instruction, str) or not instruction.strip():
        raise ProtocolError("instruction must be a non-empty string")
    state = request.get("state")
    if not isinstance(state, list) or not state or len(state) % len(JOINTS):
        raise ProtocolError(f"state must be {len(JOINTS)} joints per arm")
    state = _finite_row(state, len(state), "state")
    images = request.get("images")
    if not isinstance(images, dict) or set(images) != set(CAMERAS):
        raise ProtocolError(f"images must be exactly {CAMERAS}; got {sorted(images or {})}")
    if not isinstance(request.get("request_id"), str):
        raise ProtocolError("request_id must be a string")
    return instruction, state, {k: decode_jpeg(images[k]) for k in CAMERAS}


def validate_response(response, request, action_dim, max_age_s, now=None):
    """Return the action chunk as a list of rows, or raise ProtocolError.

    Rejects a reply to a different request (late/out-of-order), a reply older
    than max_age_s since the observation was taken, and any malformed row.
    """
    if not isinstance(response, dict):
        raise ProtocolError("response must be an object")
    if response.get("request_id") != request["request_id"]:
        raise ProtocolError("response answers a different request")
    age = (time.time() if now is None else now) - request["sent_at"]
    if age > max_age_s:
        raise ProtocolError(f"response is stale: {age:.2f}s > {max_age_s:.2f}s")
    actions = response.get("actions")
    if not isinstance(actions, list) or not 0 < len(actions) <= MAX_CHUNK:
        raise ProtocolError(f"actions must be 1..{MAX_CHUNK} rows")
    return [_finite_row(row, action_dim, f"action row {i}") for i, row in enumerate(actions)]


def limit_step(previous, target, max_step):
    """Clamp each joint's move from previous toward target to at most max_step."""
    return [p + max(-max_step, min(max_step, t - p)) for p, t in zip(previous, target)]


def dumps(obj):
    return json.dumps(obj, separators=(",", ":")).encode()
