#!/usr/bin/env python3
"""Read exact dimensions out of the SO-101 reference STEP files.

Blender has no STEP importer, so OCCT (via the `cadquery-ocp` wheel, installed
into cad/blender/.venv/ -- gitignored) is used here purely as a *measuring
instrument*: it loads the analytic B-rep and prints face types, cylinder radii
and axes, planar face positions and the solid bounding box.  Nothing is
authored here and cad/build123d/reference/ is only ever opened for reading.

  cad/blender/.venv/bin/python cad/blender/measure_step_ocp.py <file.step>
"""
import sys
from collections import defaultdict

from OCP.STEPControl import STEPControl_Reader
from OCP.TopAbs import TopAbs_FACE, TopAbs_SOLID
from OCP.TopExp import TopExp_Explorer
from OCP.BRep import BRep_Tool
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import (GeomAbs_Plane, GeomAbs_Cylinder, GeomAbs_Cone,
                         GeomAbs_Sphere, GeomAbs_Torus, GeomAbs_BSplineSurface)
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
from OCP.TopoDS import TopoDS

KIND = {GeomAbs_Plane: "plane", GeomAbs_Cylinder: "cylinder",
        GeomAbs_Cone: "cone", GeomAbs_Sphere: "sphere",
        GeomAbs_Torus: "torus", GeomAbs_BSplineSurface: "bspline"}


def read(path):
    r = STEPControl_Reader()
    r.ReadFile(path)
    r.TransferRoots()
    return r.OneShape()


def bbox(shape):
    b = Bnd_Box()
    b.SetGap(0.0)
    BRepBndLib.AddOptimal_s(shape, b, True, False)
    return (b.CornerMin().X(), b.CornerMin().Y(), b.CornerMin().Z(),
            b.CornerMax().X(), b.CornerMax().Y(), b.CornerMax().Z())


def v3(p):
    return f"({p.X():8.3f},{p.Y():8.3f},{p.Z():8.3f})"


def report(path):
    shape = read(path)
    print("=" * 78)
    print(path)
    print("=" * 78)

    xm, ym, zm, xM, yM, zM = bbox(shape)
    print(f"bbox  X {xm:8.3f} .. {xM:8.3f}   ({xM-xm:7.3f} mm)")
    print(f"      Y {ym:8.3f} .. {yM:8.3f}   ({yM-ym:7.3f} mm)")
    print(f"      Z {zm:8.3f} .. {zM:8.3f}   ({zM-zm:7.3f} mm)")

    props = GProp_GProps()
    BRepGProp.VolumeProperties_s(shape, props)
    c = props.CentreOfMass()
    print(f"volume {props.Mass():.1f} mm^3   centre of mass {v3(c)}")

    nsolid = 0
    ex = TopExp_Explorer(shape, TopAbs_SOLID)
    while ex.More():
        nsolid += 1
        ex.Next()
    print(f"solids {nsolid}")

    cyls, planes, cones, tori, kinds = [], defaultdict(list), [], [], defaultdict(int)
    ex = TopExp_Explorer(shape, TopAbs_FACE)
    while ex.More():
        f = TopoDS.Face(ex.Current())
        ad = BRepAdaptor_Surface(f)
        k = ad.GetType()
        kinds[KIND.get(k, str(k))] += 1
        g = GProp_GProps()
        BRepGProp.SurfaceProperties_s(f, g)
        area = g.Mass()
        if k == GeomAbs_Cylinder:
            cy = ad.Cylinder()
            ax = cy.Axis()
            # face extent along the cylinder axis
            fb = Bnd_Box()
            fb.SetGap(0.0)
            BRepBndLib.AddOptimal_s(f, fb, True, False)
            ext = (fb.CornerMin().X(), fb.CornerMin().Y(), fb.CornerMin().Z(),
                   fb.CornerMax().X(), fb.CornerMax().Y(), fb.CornerMax().Z())
            cyls.append((cy.Radius(), ax.Location(), ax.Direction(), area, ext))
        elif k == GeomAbs_Plane:
            pl = ad.Plane()
            n = pl.Axis().Direction()
            o = pl.Location()
            key = (round(n.X(), 3), round(n.Y(), 3), round(n.Z(), 3))
            d = o.X() * n.X() + o.Y() * n.Y() + o.Z() * n.Z()
            planes[key].append((round(d, 3), area))
        elif k == GeomAbs_Cone:
            co = ad.Cone()
            import math
            cones.append((co.RefRadius(), math.degrees(co.SemiAngle()),
                          co.Axis().Location()))
        elif k == GeomAbs_Torus:
            to = ad.Torus()
            tori.append((to.MajorRadius(), to.MinorRadius(), to.Axis().Location()))
        ex.Next()

    print("faces: " + ", ".join(f"{k}={n}" for k, n in sorted(kinds.items())))

    print("\nCYLINDRICAL FACES (radius, dia, axis, axis point, axial extent, area)")
    for r, loc, d, area, bb in sorted(cyls, key=lambda t: t[0]):
        x0, y0, z0, x1, y1, z1 = bb
        span = [x1 - x0, y1 - y0, z1 - z0]
        ax = max(range(3), key=lambda i: abs((d.X(), d.Y(), d.Z())[i]))
        print(f"  r={r:7.3f} d={2*r:7.3f} axis=({d.X():5.2f},{d.Y():5.2f},"
              f"{d.Z():5.2f}) at {v3(loc)} len~{span[ax]:7.3f} area={area:8.2f}")

    print("\nPLANAR FACES grouped by normal -> signed offsets (mm) and areas")
    for n, lst in sorted(planes.items()):
        agg = defaultdict(float)
        for d, a in lst:
            agg[d] += a
        items = ", ".join(f"{d}(A={a:.0f})" for d, a in sorted(agg.items()))
        print(f"  n={n}: {items}")

    if cones:
        print("\nCONICAL FACES (ref radius, half-angle deg, apex-ref point)")
        for r, a, loc in sorted(cones):
            print(f"  r={r:7.3f} half-angle={a:6.2f} at {v3(loc)}")
    if tori:
        print("\nTOROIDAL FACES (major, minor -> fillet radius)")
        for R, r, loc in sorted(tori, key=lambda t: (t[0], t[1])):
            print(f"  major={R:7.3f} minor={r:7.3f} at {v3(loc)}")
    print()


if __name__ == "__main__":
    for p in sys.argv[1:]:
        report(p)
