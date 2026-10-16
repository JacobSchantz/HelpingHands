#!/bin/bash
# One command to try a model on our arm:
#   bash robot_eval/try.sh <model> <task> <trial> --stereo-device 0 [--execute] [client args...]
# Rents a GPU for <model> if none is up (robot_eval/rent.py), runs one scored
# trial (robot_eval/client.py), then asks whether to keep the pod for the next
# trial. The default answer deletes it so billing never runs on unnoticed.
# Run in native Terminal.app (see teleop.sh). Needs RUNPOD_API_KEY.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
MODEL="$1"; TASK="$2"; TRIAL="$3"; shift 3
source ~/miniforge3/etc/profile.d/conda.sh
conda activate lerobot

if [ -f "$HERE/.pod.json" ] && [ "$(python3 -c "import json;print(json.load(open('$HERE/.pod.json'))['model'])")" != "$MODEL" ]; then
  python3 "$HERE/rent.py" down
fi
[ -f "$HERE/.pod.json" ] || python3 "$HERE/rent.py" up "$MODEL"

read -r URL TOKEN GPU < <(python3 -c "import json;p=json.load(open('$HERE/.pod.json'));print(p['url'],p['token'],p['gpu'].replace(' ','_'))")
ROBOT_EVAL_TOKEN="$TOKEN" ROBOT_EVAL_GPU="$GPU" python3 "$HERE/client.py" \
  --server "$URL" --task "$TASK" --trial "$TRIAL" "$@" || true

read -r -p "Keep the GPU for another trial? [y/N] " KEEP
[ "$KEEP" = "y" ] || python3 "$HERE/rent.py" down
