#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=2", "trimesh>=4", "scipy>=1.11", "manifold3d>=3"]
# ///
"""Reproduce the original placement and default carve's geometry audit."""
import hashlib
import json
from pathlib import Path
import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parent
SOURCES = ROOT.parent / "upstream/orca_v2/base/01_Fingers"


def main():
    manifest = json.loads((ROOT.parent / "manifest.json").read_text())
    for entry in manifest["files"]:
        if Path(entry["path"]).stem in {"I-AP-R", "I-PP", "I-IP"}:
            data = (ROOT.parent / entry["path"]).read_bytes()
            assert hashlib.sha256(data).hexdigest() == entry["sha256"], entry["path"]
    channel = trimesh.creation.cylinder(radius=1, height=280, sections=128)
    channel.apply_scale([11, 12, 1])
    channel.apply_translation([0, 0, 60])
    original = {}
    results = []
    for name in ["I-AP-R", "I-PP", "I-IP"]:
        mesh = trimesh.load(SOURCES / (name + ".stl"), process=True)
        assert mesh.is_watertight and mesh.is_winding_consistent
        if name == "I-AP-R":
            mesh.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2, [0, 1, 0]))
        if name == "I-IP":
            mesh.apply_translation([1.5, 0, 37])
        original[name] = mesh.copy()
        mesh.apply_scale(2)
        cut = trimesh.boolean.difference([mesh, channel], engine="manifold")
        components = cut.split(only_watertight=False)
        results.append({
            "part": name, "uncut_volume_mm3": float(mesh.volume),
            "remaining_volume_mm3": float(cut.volume),
            "removed_percent": float((1-cut.volume/mesh.volume)*100),
            "remaining_connected_components": len(components),
            "component_volumes_mm3": [float(c.volume) for c in components],
            "watertight": bool(cut.is_watertight), "bounds_mm": cut.bounds.tolist(),
        })
    intersections = {}
    for a, b in [("I-AP-R", "I-PP"), ("I-PP", "I-IP"), ("I-AP-R", "I-IP")]:
        common = trimesh.boolean.intersection([original[a], original[b]], engine="manifold")
        volume = float(common.volume) if len(common.faces) else 0.0
        intersections[f"{a} vs {b}"] = volume
        assert volume < 1e-6, (a, b, volume)
    exported = trimesh.load(ROOT / "export/index_2x_carved_concept.stl", process=True)
    report = {
        "parameters": {"enlargement": 2, "longitudinal_scale": 2,
                       "channel_width_mm": 24, "channel_depth_mm": 22, "channel_center_xy_mm": [0, 0]},
        "source_hashes_match": True,
        "original_neutral_intersection_mm3": intersections,
        "parts": results,
        "saved_openscad_stl": {
            "triangles": len(exported.faces), "watertight": bool(exported.is_watertight),
            "consistent_winding": bool(exported.is_winding_consistent),
            "connected_components": len(exported.split(only_watertight=False)),
            "volume_mm3": float(exported.volume),
            "sha256": hashlib.sha256((ROOT / "export/index_2x_carved_concept.stl").read_bytes()).hexdigest(),
        },
        "scope": "Geometry only. Disconnected remnants are retained and reported. No force, pin retention, tendon routing, motion range or wearable-fit validation.",
    }
    (ROOT / "cut_audit.json").write_text(json.dumps(report, indent=2) + "\n")
    for row in results:
        print(f'{row["part"]}: {row["removed_percent"]:.1f}% removed, {row["remaining_connected_components"]} remaining solids')
    print('Neutral original intersections:', intersections)
    print('Saved concept:', report['saved_openscad_stl'])


if __name__ == "__main__":
    main()
