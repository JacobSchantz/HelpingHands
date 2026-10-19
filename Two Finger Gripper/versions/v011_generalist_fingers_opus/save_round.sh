#!/bin/sh
# Snapshot the current build as rounds/<name>/ (source, right.stl, renders) for the build-review loop.
set -e
cd "$(dirname "$0")"
d="rounds/$1"; mkdir -p "$d"
cp gripper.scad trace_photo.py trace_px.scad exports/print/right.stl "$d/"
cp previews/top.png previews/iso.png previews/finger.png previews/edge.png previews/jaw.png previews/photo_match.png "$d/"
