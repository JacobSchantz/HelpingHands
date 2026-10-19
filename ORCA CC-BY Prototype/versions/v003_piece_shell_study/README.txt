v003 — ORCA pieces with an inward wall and separated cutaway

Open index.scad in OpenSCAD. Default: original 1× outer size, three pieces
separated side by side, 1.5 mm nominal inward offset, half-section facing you.
AP (blue) is the abduction/base part. PP (gray) is the proximal part. IP (orange)
is the intermediate segment with its fixed distal tip, not a separate DIP joint.

Controls
  part: all, AP, PP, or IP.
  geometry: shell = original minus cavity; original = unchanged source shape;
            cavity = the removed interior volume by itself.
  section: half exposes the interior; whole shows the complete component.
  wall_offset: 1.0, 1.5, or 2.0 mm, measured in the original 1× model.
  outer_scale: 1 or 2. Scaling doubles ALL dimensions, including the wall offset,
               hardware openings and segment length. It does not establish fit.
  section_y: slide the inspection plane through the component in source mm.
  show_labels: preview-only labels; labels are omitted from STL exports.

The view is separated for inspection. It is not an assembly position or a print
layout. For the intact original assembled finger, open ../v002_clean_index.
Versions v001 and v002 have not been modified: all 52 prior snapshot hashes
were checked. See inspection_audit.json.

How the inner wall is made
The outer boundary is the exact original manufacturing STL. The subtraction is
an inward Euclidean-distance isosurface of that mesh, sampled on a grid no
coarser than 0.20 mm. The cavity follows distance to the source surfaces rather than uniform scaling.
OpenSCAD subtracts the generated cavity mesh from the original on demand.
The sampling grid has a small fixed origin shift to avoid degenerate triangles
where offset levels coincide exactly with grid planes. A disconnected cavity
island is omitted only if its largest bounding-box extent is below 1 mm AND its
bounding-box volume is below 0.01 mm3. This leaves original solid material in
that location. Every omitted island is recorded; no holes are filled and no
surfaces are smoothed. An exact mesh Boolean check verifies that each retained
cavity has no geometry outside the original source solid.

The requested offset is measured from every original boundary, including
existing holes and recesses. Areas too narrow for an interior cavity remain
solid, and the original thin webs are preserved. Wall thickness is therefore
not uniform everywhere. The cavity surface is an approximation; measured
clearance ranges and volumes are in cavity_audit.json. Those measurements
sample every cavity vertex and triangle centroid, not every possible point.

Only 1.0, 1.5 and 2.0 mm presets are supplied. A 2.5 mm trial produced a
non-watertight cavity near vanishing pockets in the AP/base and was excluded.


These are closed internal cavities. The inspection half-section is only a
viewing cut; it is not a proposed assembly seam. No finger-sized opening,
wearable fit, joint redesign, tendon rerouting, access/drain holes, retention,
load rating or print-support strategy has been established. Removing internal
material can weaken bearing and tendon supports even when their surfaces are
preserved. This is a geometry study, not a validated printable mechanism.

Geometry checks at the default 1.5 mm offset
  Part        Original material removed     Whole material bodies remaining
  AP/base               11.5%                             1
  PP/proximal           20.7%                             1
  IP/distal             34.6%                             1
Every supplied cavity preset is closed and lies inside its source part. The
sampled default inner clearance is 1.491–1.600 mm across all three parts.
All three whole shells export from OpenSCAD as watertight, consistently oriented
geometry. The 1 mm and 2 mm wall presets, 2× scale, and original-IP control were
also exported and checked. Internal closed void surfaces are not loose parts.
The half-section is a viewing cut and can sever features visible in that slice.

Reproduction
Use the three original files in source/ and the precomputed offsets in
generated/. Files in generated/ are subtraction volumes, not printable shells. OpenSCAD is sufficient to inspect and change all supplied controls.
To regenerate the offsets and numerical audit, run:
  uv run build_cavities.py
The script pins its Python dependencies, verifies source SHA-256 hashes,
extracts the inward offsets, checks closed meshes, and records their geometry.

Attribution and changes
ORCA Hand — Copyright (c) 2026 ORCA Dexterity, Inc. — CC BY 4.0. See LICENSE.
Original manufacturing source:
https://github.com/orcahand/orcahand_hardware/tree/37b71dc03d3f11e48b920cbf54562b33c025bc8c/orca_v2/base/01_Fingers
Pinned commit: 37b71dc03d3f11e48b920cbf54562b33c025bc8c

source/I-AP-R.stl, source/I-PP.stl and source/I-IP.stl are byte-for-byte copies
of the original sources retained in v002. Modified material in this independent
study: derived inward-offset cavities, subtraction, display placements,
section controls and documentation. Original geometry and this geometry study
are distributed under CC BY 4.0. No ORCA endorsement is implied.
