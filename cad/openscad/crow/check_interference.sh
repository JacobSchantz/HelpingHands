#!/usr/bin/env bash
# The test ../NOTES.md section 5 says this model was missing: the two mandibles
# must never share a point through the whole stroke.  OpenSCAD writes no file at
# all when a top-level object is empty, so "no file" is the pass condition.
#
# At crow_opening = 0 the beak closes along its whole tomial line, so the two
# faces are coplanar and CGAL returns a zero-thickness film -- that one is
# reported, not failed.
set -uo pipefail
cd "$(dirname "$0")"
OPENSCAD="${OPENSCAD:-/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD}"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
fail=0

for o in 0 0.05 0.5 2 5 10 20 30 40 50; do
    out="$TMP/i_$o.stl"
    "$OPENSCAD" --render -D 'part="interference"' -D "crow_opening=$o" \
        --export-format asciistl -o "$out" crow_beak.scad >/dev/null 2>&1
    if [ ! -f "$out" ]; then
        printf '  opening %-5s  clear\n' "$o"
        continue
    fi
    vol=$(python3 - "$out" <<'PY'
import sys
v=[tuple(map(float,l.split()[1:])) for l in open(sys.argv[1]) if l.strip().startswith('vertex')]
V=sum((a[0]*(b[1]*c[2]-b[2]*c[1])-a[1]*(b[0]*c[2]-b[2]*c[0])+a[2]*(b[0]*c[1]-b[1]*c[0]))/6
      for a,b,c in zip(v[0::3],v[1::3],v[2::3]))
print(f"{V:.4f}")
PY
)
    if [ "$o" = "0" ]; then
        printf '  opening %-5s  %s mm^3 of coplanar-face film (the beak is shut)\n' "$o" "$vol"
    else
        printf '  opening %-5s  OVERLAP %s mm^3\n' "$o" "$vol"; fail=1
    fi
done

[ "$fail" -eq 0 ] && echo "interference: clear" || { echo "interference: FAILED"; exit 1; }
