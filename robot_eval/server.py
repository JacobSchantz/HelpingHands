"""Policy server: run on the rented GPU, one model per process.

    python3 robot_eval/server.py --model smolvla --port 8000
    ROBOT_EVAL_TOKEN=... required; requests without it get 401.

The model name is a key of robot_eval/models.json. Stdlib HTTP, one request
at a time (a policy is not re-entrant, and the client waits anyway).
"""
import argparse
import hmac
import json
import os
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import adapters  # noqa: E402
import protocol  # noqa: E402

MODELS = Path(__file__).resolve().parent / "models.json"


def load_spec(name, path=MODELS):
    models = json.loads(Path(path).read_text())["models"]
    if name not in models:
        raise SystemExit(f"unknown model {name!r}; known: {', '.join(sorted(models))}")
    return {"name": name, **models[name]}


def make_server(adapter, token, host="0.0.0.0", port=8000):
    lock = threading.Lock()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):
            sys.stderr.write("server: " + fmt % args + "\n")

        def _reply(self, code, body):
            data = protocol.dumps(body)
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def _authorized(self):
            sent = self.headers.get("Authorization", "")
            if hmac.compare_digest(sent, f"Bearer {token}"):
                return True
            self._reply(401, {"error": "unauthorized"})
            return False

        def do_GET(self):
            if not self._authorized():
                return
            if self.path != "/info":
                return self._reply(404, {"error": "not found"})
            self._reply(200, {"protocol": protocol.PROTOCOL_VERSION, **adapter.info})

        def do_POST(self):
            if not self._authorized():
                return
            length = int(self.headers.get("Content-Length") or 0)
            try:
                body = json.loads(self.rfile.read(length) or b"{}")
            except json.JSONDecodeError:
                return self._reply(400, {"error": "body is not JSON"})
            if self.path == "/reset":
                with lock:
                    adapter.reset()
                return self._reply(200, {})
            if self.path != "/act":
                return self._reply(404, {"error": "not found"})
            try:
                instruction, state, images = protocol.validate_request(body)
            except protocol.ProtocolError as error:
                return self._reply(400, {"error": str(error)})
            start = time.perf_counter()
            with lock:
                actions = adapter.act(instruction, state, images)
            self._reply(200, {"request_id": body["request_id"], "actions": actions,
                              "model": adapter.info["model"],
                              "revision": adapter.info["revision"],
                              "inference_s": time.perf_counter() - start})

    return HTTPServer((host, port), Handler)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True)
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--host", default="0.0.0.0")
    args = parser.parse_args()
    token = os.environ.get("ROBOT_EVAL_TOKEN")
    if not token:
        raise SystemExit("set ROBOT_EVAL_TOKEN")
    spec = load_spec(args.model)
    started = time.perf_counter()
    adapter = adapters.load(spec)
    print(json.dumps({"event": "ready", "model": args.model, "port": args.port,
                      "load_s": round(time.perf_counter() - started, 1), **adapter.info}), flush=True)
    make_server(adapter, token, args.host, args.port).serve_forever()


if __name__ == "__main__":
    main()
