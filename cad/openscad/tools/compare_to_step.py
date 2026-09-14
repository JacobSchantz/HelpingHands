#!/usr/bin/env python3
"""Overlay the OpenSCAD model on the reference STEP, projection by projection.

This is the fidelity check behind NOTES.md: it draws the reference solid and
the exported STL in the same frame and the same three orthographic views, so
where the rebuild drifts is visible rather than asserted.

Unlike tools/measure_step.py this one is NOT dependency-free -- reading a STEP
solid needs a kernel:

    python3 -m venv .venv && .venv/bin/pip install cadquery-ocp matplotlib
    .venv/bin/python tools/compare_to_step.py

Writes render/fidelity_check.png.
"""
import os
import struct
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
REF = os.path.join(ROOT, "..", "build123d", "reference")


def step_tris(path):
    from OCP.STEPControl import STEPControl_Reader
    from OCP.BRepMesh import BRepMesh_IncrementalMesh
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopAbs import TopAbs_FACE
    from OCP.TopoDS import TopoDS
    from OCP.BRep import BRep_Tool
    from OCP.TopLoc import TopLoc_Location

    reader = STEPControl_Reader()
    reader.ReadFile(path)
    reader.TransferRoots()
    shape = reader.OneShape()
    BRepMesh_IncrementalMesh(shape, 0.2, False, 0.3, True)
    tris = []
    exp = TopExp_Explorer(shape, TopAbs_FACE)
    while exp.More():
        face = TopoDS.Face(exp.Current())
        loc = TopLoc_Location()
        tri = BRep_Tool.Triangulation_s(face, loc)
        if tri is not None:
            trsf = loc.Transformation()
            pts = []
            for i in range(1, tri.NbNodes() + 1):
                p = tri.Node(i).Transformed(trsf)
                pts.append((p.X(), p.Y(), p.Z()))
            for i in range(1, tri.NbTriangles() + 1):
                a, b, c = tri.Triangle(i).Get()
                tris.append((pts[a - 1], pts[b - 1], pts[c - 1]))
        exp.Next()
    return np.array(tris)


def stl_tris(path):
    with open(path, "rb") as fh:
        fh.read(80)
        n = struct.unpack("<I", fh.read(4))[0]
        out = np.empty((n, 3, 3))
        for i in range(n):
            data = struct.unpack("<12fH", fh.read(50))
            out[i] = np.array(data[3:12]).reshape(3, 3)
    return out


def draw(ax, tris, colour, alpha, title, i, j):
    ax.add_collection(PolyCollection(tris[:, :, [i, j]], facecolors=colour,
                                     alpha=alpha, edgecolors="none"))
    ax.set_title(title)
    ax.set_aspect("equal")
    ax.grid(True, lw=0.3, alpha=0.6)
    ax.set_xlabel("XYZ"[i])
    ax.set_ylabel("XYZ"[j])


def panel(axes, ref, mine, label):
    for ax, (i, j) in zip(axes, [(0, 1), (0, 2), (1, 2)]):
        draw(ax, ref, "#1f77b4", 0.35, "%s  %s%s" % (label, "XYZ"[i], "XYZ"[j]), i, j)
        draw(ax, mine, "#d62728", 0.35, "%s  %s%s" % (label, "XYZ"[i], "XYZ"[j]), i, j)
        allpts = np.vstack([ref.reshape(-1, 3), mine.reshape(-1, 3)])
        ax.set_xlim(allpts[:, i].min() - 4, allpts[:, i].max() + 4)
        ax.set_ylim(allpts[:, j].min() - 4, allpts[:, j].max() + 4)


def main():
    pairs = [("Moving_Jaw_SO101.step", "moving_jaw.stl", "moving jaw"),
             ("Wrist_Roll_Follower_SO101.step", "fixed_jaw.stl", "fixed jaw")]
    fig, axs = plt.subplots(2, 3, figsize=(19, 15))
    for row, (step, stl, label) in enumerate(pairs):
        panel(axs[row], step_tris(os.path.join(REF, step)),
              stl_tris(os.path.join(ROOT, "export", stl)), label)
    fig.suptitle("blue = reference STEP     red = OpenSCAD rebuild", fontsize=15)
    plt.tight_layout()
    out = os.path.join(ROOT, "render", "fidelity_check.png")
    plt.savefig(out, dpi=95)
    print("wrote", out)


if __name__ == "__main__":
    sys.exit(main())
