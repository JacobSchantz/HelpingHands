ORCA assembled hand visualization

Original official orcahand_description v2 visual meshes and URDF transforms, all joints at zero, converted to mm. Source license is preserved in source/LICENSE (MIT). This does not change the CC BY4 license of the separate hardware CAD files.

Open view_stl.scad to see the assembled STL in OpenSCAD; assembled_hand.scad imports individually positioned source parts. build.py reproduces both using numpy and trimesh.

This is the official v2 simulation appearance reference, not a verified complete v2.1 manufacturing assembly. It omits hardware details absent from those visual meshes. The combined STL contains separate/possibly intersecting shells; use it for viewing, not as a one-piece print or mechanical fit validation. Original manufacturing parts remain under ../upstream/.
