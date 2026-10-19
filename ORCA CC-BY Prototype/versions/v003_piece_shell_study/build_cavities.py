#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy==2.5.4", "trimesh==5.1.1", "vtk==9.6.2", "manifold3d==3.5.4", "networkx==3.7"]
# ///
"""Derive inward-distance cavities while retaining the exact source exterior.
ORCA source hardware: ORCA Dexterity, Inc., CC BY 4.0. See LICENSE.
This script and generated geometry are modifications in this independent study.
"""
from pathlib import Path
import hashlib
import json
import time
import numpy as np
import trimesh
import vtk

ROOT = Path(__file__).resolve().parent
PARTS = ["I-AP-R", "I-PP", "I-IP"]
THICKNESSES = [1.0, 1.5, 2.0]
PITCH = 0.20
COMMIT = "37b71dc03d3f11e48b920cbf54562b33c025bc8c"
EXPECTED = {
    "I-AP-R": "dcb079b42627e2b72fabb00a623293d587e9c22d8a0b58bd194ba27e60c315cb",
    "I-PP": "326697b792080363c007674953f84799ead7e5a4d886942435171a12bffce8cf",
    "I-IP": "f265a451fba256522035f0d1e7dd932bf6da9653844da720eeb520e02a8ebb11",
}

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def vtk_mesh(poly):
    from vtk.util.numpy_support import vtk_to_numpy
    vertices = vtk_to_numpy(poly.GetPoints().GetData()).copy()
    faces = vtk_to_numpy(poly.GetPolys().GetConnectivityArray()).reshape(-1, 3).copy()
    result = trimesh.Trimesh(vertices=vertices, faces=faces, process=True)
    result.fix_normals(multibody=True)
    return result


def build():
    (ROOT / "generated").mkdir(exist_ok=True)
    report = {
        "source_repository": "https://github.com/orcahand/orcahand_hardware",
        "source_commit": COMMIT,
        "license": "CC-BY-4.0",
        "attribution": "ORCA Hand, Copyright (c) 2026 ORCA Dexterity, Inc.",
        "source_units": "millimeters",
        "method": "Signed Euclidean distance from the closed source triangle mesh, sampled on a regular grid; negative isosurfaces extracted by vtkFlyingEdges3D. Subtract each cavity from the unchanged source exterior in OpenSCAD.",
        "maximum_grid_pitch_mm": PITCH,
        "grid_origin_shift_mm": [0.013071, 0.019137, 0.029513],
        "tiny_cavity_filter": "Exclude an entire disconnected cavity island only when its largest bounding-box extent is below 1 mm AND its bounding-box volume is below 0.01 mm3. This preserves solid material in those locations; no hole filling or smoothing is performed.",
        "nominal_offset_presets_mm_at_1x": THICKNESSES,
        "measurement_limit": "Surface clearance is sampled at every cavity vertex and triangle centroid; it is not a certified minimum over all points. Original narrow features remain solid and may already be thinner than the selected offset.",
        "part_results": [],
    }
    for name in PARTS:
        source = ROOT / "source" / (name + ".stl")
        assert digest(source) == EXPECTED[name], f"Source hash mismatch: {name}"
        original = trimesh.load(source, force="mesh")
        assert original.is_watertight and original.is_winding_consistent
        reader = vtk.vtkSTLReader()
        reader.SetFileName(str(source))
        reader.Update()
        sdf = vtk.vtkImplicitPolyDataDistance()
        sdf.SetInput(reader.GetOutput())
        bounds = np.array(reader.GetOutput().GetBounds()).reshape(3, 2)
        # Avoid an isosurface falling exactly on a grid plane through an
        # axis-aligned face: exact coincidences can produce zero-area triangles.
        # Both limits are displaced by the same small deterministic vector.
        grid_shift = np.array([0.013071, 0.019137, 0.029513])
        bounds[:, 0] -= PITCH * 2
        bounds[:, 1] += PITCH * 2
        bounds += grid_shift[:, None]
        dims = np.ceil(np.diff(bounds, axis=1).ravel() / PITCH).astype(int) + 1
        sample = vtk.vtkSampleFunction()
        sample.SetImplicitFunction(sdf)
        sample.SetModelBounds(*bounds.ravel())
        sample.SetSampleDimensions(*dims)
        sample.ComputeNormalsOff()
        start = time.monotonic()
        sample.Update()
        print(f"{name}: distance field {tuple(dims)}, {time.monotonic()-start:.1f}s", flush=True)
        record = {
            "id": name,
            "source_path": str(source.relative_to(ROOT)),
            "source_sha256": digest(source),
            "source_bounds_mm": original.bounds.tolist(),
            "source_volume_mm3": float(original.volume),
            "source_connected_boundary_components": len(original.split()),
            "grid_dimensions": dims.tolist(),
            "grid_spacing_mm": list(sample.GetOutput().GetSpacing()),
            "maximum_sampled_interior_distance_mm": -sample.GetOutput().GetScalarRange()[0],
            "cavities": [],
        }
        for thickness in THICKNESSES:
            iso = vtk.vtkFlyingEdges3D()
            iso.SetInputConnection(sample.GetOutputPort())
            iso.SetValue(0, -thickness)
            iso.ComputeNormalsOff()
            iso.Update()
            raw_cavity = vtk_mesh(iso.GetOutput())
            groups = trimesh.graph.connected_components(
                raw_cavity.face_adjacency, nodes=np.arange(len(raw_cavity.faces)))
            islands = trimesh.util.submesh(raw_cavity, groups, repair=False)
            retained, excluded = [], []
            for island in islands:
                if max(island.extents) < 1.0 and np.prod(island.extents) < 0.01:
                    excluded.append({
                        "triangle_count": len(island.faces),
                        "bounds_mm": island.bounds.tolist(),
                        "bounding_box_volume_mm3": float(np.prod(island.extents)),
                        "was_watertight": bool(island.is_watertight),
                    })
                else:
                    retained.append(island)
            cavity = trimesh.util.concatenate(retained)
            assert cavity.is_watertight and cavity.is_winding_consistent
            outside = trimesh.boolean.difference([cavity, original], engine="manifold")
            assert len(outside.faces) == 0, (name, thickness, "Cavity exits source solid")
            cavity_path = ROOT / "generated" / f"{name}_cavity_{thickness:.1f}mm.stl"
            cavity.export(cavity_path)
            hollow = trimesh.boolean.difference([original, cavity], engine="manifold")
            assert hollow.is_watertight and hollow.is_winding_consistent
            # Closed void boundaries have NEGATIVE signed volume in a material mesh;
            # counting every disconnected boundary as a loose part would be wrong.
            boundary_volumes = [float(p.volume) for p in hollow.split(only_watertight=False)]
            positive_boundaries = [v for v in boundary_volumes if v > 1e-5]
            negative_boundaries = [v for v in boundary_volumes if v < -1e-5]
            points = np.concatenate([cavity.vertices, cavity.triangles_center])
            clearances = np.array([-sdf.EvaluateFunction(p) for p in points])
            entry = {
                "nominal_offset_mm_at_1x": thickness,
                "path": str(cavity_path.relative_to(ROOT)),
                "sha256": digest(cavity_path),
                "triangle_count": len(cavity.faces),
                "watertight": bool(cavity.is_watertight),
                "excluded_tiny_cavity_islands": excluded,
                "outside_source_triangle_count": len(outside.faces),
                "outside_source_volume_mm3": 0.0,
                "cavity_volume_mm3": float(cavity.volume),
                "material_removed_percent": float(100 * (1 - hollow.volume / original.volume)),
                "remaining_material_volume_mm3": float(hollow.volume),
                "remaining_positive_boundary_components": len(positive_boundaries),
                "closed_void_boundaries": len(negative_boundaries),
                "hollow_watertight": bool(hollow.is_watertight),
                "sampled_clearance_mm": {
                    "minimum": float(clearances.min()),
                    "maximum": float(clearances.max()),
                    "median": float(np.median(clearances)),
                    "sample_count": len(points),
                    "sample_locations": "Every cavity vertex and triangle centroid",
                },
            }
            assert len(positive_boundaries) == 1, (name, thickness, boundary_volumes)
            assert clearances.min() > thickness - PITCH, (name, thickness, clearances.min())
            record["cavities"].append(entry)
            print(f"  {thickness:.1f}mm: {entry['material_removed_percent']:.1f}% removed; {len(positive_boundaries)} material body; sampled clearance {clearances.min():.3f}–{clearances.max():.3f}mm", flush=True)
        report["part_results"].append(record)
        (ROOT / "cavity_audit.json").write_text(json.dumps(report, indent=2) + "\n")
    print("Completed cavity_audit.json", flush=True)

if __name__ == "__main__":
    build()
