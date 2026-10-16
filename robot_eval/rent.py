"""Rent the cheapest suitable GPU on RunPod Community Cloud and start one model's server.

    export RUNPOD_API_KEY=...            # never commit it
    python3 robot_eval/rent.py up smolvla_base
    python3 robot_eval/rent.py status
    python3 robot_eval/rent.py down      # ends billing; always run when finished

`up` picks the GPU from the model's min_vram_gb, clones this public repo on
the pod, installs the model's `pip` line, starts robot_eval/server.py on a
direct TCP port and waits until /info answers. It writes robot_eval/.pod.json
(gitignored) with the URL and a fresh bearer token; client.py and try.sh read
it. Prices are what was seen on 2026-10-16; RunPod shows the live price.
"""
import json
import os
import secrets
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import server  # noqa: E402

API = "https://rest.runpod.io/v1"
STATE = HERE / ".pod.json"
REPO_URL = "https://github.com/JacobSchantz/HelpingHands"
IMAGE = "runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04"
# (max VRAM GB, RunPod gpu type ids in preference order, $/h seen 2026-10-16)
GPUS = [
    (24, ["NVIDIA GeForce RTX 4090", "NVIDIA L4"], 0.34),
    (48, ["NVIDIA RTX A6000", "NVIDIA L40S"], 0.33),
    (80, ["NVIDIA A100 80GB PCIe", "NVIDIA H100 PCIe"], 1.19),
]


def pick_gpu(min_vram_gb):
    for vram, ids, price in GPUS:
        if min_vram_gb <= vram:
            return ids, price
    raise SystemExit(f"no rental GPU has {min_vram_gb} GB")


def start_command(name, spec, port=8000):
    pip = spec.get("pip", "")
    return " && ".join(filter(None, [
        f"git clone --depth 1 {REPO_URL} /app",
        f"pip install -q {pip}" if pip else "",
        f"python /app/robot_eval/server.py --model {name} --port {port}",
    ]))


def api(method, path, body=None):
    key = os.environ.get("RUNPOD_API_KEY") or sys.exit("set RUNPOD_API_KEY (RunPod > Settings > API Keys)")
    request = urllib.request.Request(API + path, method=method,
                                     data=None if body is None else json.dumps(body).encode(),
                                     headers={"Authorization": f"Bearer {key}",
                                              "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            text = response.read()
            return json.loads(text) if text else {}
    except urllib.error.HTTPError as error:
        sys.exit(f"RunPod {method} {path}: HTTP {error.code} {error.read().decode()[:500]}")


def address(pod, port=8000):
    """Public http URL of the pod's direct TCP port, or None while it starts."""
    ip, mapped = pod.get("publicIp"), (pod.get("portMappings") or {}).get(str(port))
    return f"http://{ip}:{mapped}" if ip and mapped else None


def up(name, wait_s=1800):
    if STATE.exists():
        sys.exit(f"a pod is already recorded in {STATE}; run `rent.py down` first")
    spec = server.load_spec(name)
    gpu_ids, price = pick_gpu(spec["min_vram_gb"])
    token = secrets.token_urlsafe(24)
    pod = api("POST", "/pods", {
        "name": f"helpinghands-{name}", "imageName": IMAGE, "cloudType": "COMMUNITY",
        "gpuTypeIds": gpu_ids, "gpuCount": 1, "supportPublicIp": True,
        "ports": ["8000/tcp"], "containerDiskInGb": int(spec.get("disk_gb", 60)),
        "env": {"ROBOT_EVAL_TOKEN": token, "HF_TOKEN": os.environ.get("HF_TOKEN", "")},
        "dockerEntrypoint": ["bash", "-lc"], "dockerStartCmd": [start_command(name, spec)],
    })
    record = {"pod_id": pod["id"], "model": name, "token": token, "gpu": gpu_ids[0],
              "price_seen_per_h": price, "started": time.time(), "url": None}
    STATE.write_text(json.dumps(record, indent=2))
    print(f"pod {pod['id']} on {gpu_ids} (~${price}/h when seen); loading {name}...", flush=True)
    deadline = time.time() + wait_s
    while time.time() < deadline:
        url = address(api("GET", f"/pods/{pod['id']}"))
        if url:
            try:
                with urllib.request.urlopen(urllib.request.Request(
                        url + "/info", headers={"Authorization": f"Bearer {token}"}), timeout=5) as r:
                    info = json.loads(r.read())
                record["url"] = url
                STATE.write_text(json.dumps(record, indent=2))
                print(f"ready: {url}  model {info['model']} @ {info['revision']}")
                return record
            except (urllib.error.URLError, OSError, ValueError):
                pass
        time.sleep(10)
    print("server not ready in time; check RunPod logs, then `rent.py down`", file=sys.stderr)
    sys.exit(1)


def status():
    if not STATE.exists():
        return print("no pod recorded")
    record = json.loads(STATE.read_text())
    pod = api("GET", f"/pods/{record['pod_id']}")
    hours = (time.time() - record["started"]) / 3600
    print(f"{record['pod_id']} {record['model']} {pod.get('desiredStatus')} {record['url']}"
          f" — up {hours:.2f} h, ~${hours * record['price_seen_per_h']:.2f}")


def down():
    if not STATE.exists():
        return print("no pod recorded")
    record = json.loads(STATE.read_text())
    api("DELETE", f"/pods/{record['pod_id']}")
    STATE.unlink()
    print(f"deleted pod {record['pod_id']}; billing ended")


def main():
    command = sys.argv[1] if len(sys.argv) > 1 else ""
    if command == "up" and len(sys.argv) == 3:
        up(sys.argv[2])
    elif command in ("status", "down") and len(sys.argv) == 2:
        {"status": status, "down": down}[command]()
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
