#!/usr/bin/env bash
# Regenerate everything this directory ships: measurements, parts, exports,
# drawings and the fidelity score.  Reuses the existing venv; installs nothing.
set -euo pipefail
cd "$(dirname "$0")"

PY=.venv/bin/python
[ -x "$PY" ] || { echo "no venv at $PWD/.venv — see NOTES.md"; exit 1; }

echo "== measuring the reference STEP =="
"$PY" measure_reference.py --write

echo "== building parts, exports and drawings =="
"$PY" gripper.py

echo "== fidelity against the reference =="
"$PY" fidelity_check.py --write

# macOS-only convenience: rasterise the SVG drawings so they preview in a
# browser and in GitHub.  Skipped silently anywhere else.
if command -v qlmanage >/dev/null 2>&1; then
  echo "== rasterising drawings =="
  for f in render/*.svg; do
    "$PY" - "$f" <<'PYEOF'
import re, sys
path = sys.argv[1]
svg = open(path).read()
m = re.search(r'viewBox="([-\d.e ]+)"', svg)
x, y, w, h = (float(v) for v in m.group(1).split())
side = max(w, h) * 1.06
svg = (svg[:m.start()]
       + f'viewBox="{x + w / 2 - side / 2} {y + h / 2 - side / 2} {side} {side}"'
       + svg[m.end():])
svg = re.sub(r'width="[^"]+" height="[^"]+"', 'width="1400" height="1400"',
             svg, count=1)
open(path.replace('.svg', '.square.svg'), 'w').write(svg)
PYEOF
    qlmanage -t -s 1400 -o render "${f%.svg}.square.svg" >/dev/null 2>&1 || true
    base=$(basename "${f%.svg}")
    [ -f "render/${base}.square.svg.png" ] && mv "render/${base}.square.svg.png" "render/${base}.png"
    rm -f "${f%.svg}.square.svg"
  done
fi

echo "done."
