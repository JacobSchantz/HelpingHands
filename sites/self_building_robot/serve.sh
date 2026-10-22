#!/bin/sh
# Serve the self-building robot mock-up at http://localhost:8790
cd "$(dirname "$0")" && exec python3 -m http.server "${PORT:-8790}" --bind 127.0.0.1
