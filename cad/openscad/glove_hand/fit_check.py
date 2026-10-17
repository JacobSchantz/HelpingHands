#!/usr/bin/env python3
"""Does jake_hand.scad match the photo? Its top view over the fingers-together trace.

Exports the model's top-down silhouette (OpenSCAD projection -> SVG), slides
and turns it onto hand_outline_together.scad until they overlap best (the
photo's frame follows the forearm, which is not the hand's axis), and draws
both on fit_check.png: grey = both, red = photo only (the model is too small
there), blue = model only (too big). The overlap (IoU) is printed. Only the
part above the photo's wrist cut counts. Thickness is not checked: it needs
the side photo.

    python3 fit_check.py
"""
import re
import subprocess
import tempfile
from pathlib import Path

import numpy as np
from matplotlib.path import Path as Poly
from PIL import Image
from scipy.optimize import minimize

HERE = Path(__file__).resolve().parent
SCAD = '/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD'
RES = 0.5   # mm per raster cell


def trace():
    text = (HERE / 'hand_outline_together.scad').read_text()
    body = text.split('hand_outline_together = [')[1]
    return np.array([[float(a), float(b)] for a, b in re.findall(r'\[(-?[\d.]+),(-?[\d.]+)\]', body)])


def model():
    """Every closed ring of the projected model, in mm."""
    with tempfile.TemporaryDirectory() as tmp:
        stub, svg = Path(tmp) / 'top.scad', Path(tmp) / 'top.svg'
        stub.write_text(f'use <{HERE / "jake_hand.scad"}>\nprojection() jake_hand();\n')
        subprocess.run([SCAD, '--backend', 'Manifold', '-o', str(svg), str(stub)], check=True, capture_output=True)
        d = svg.read_text()
    rings = []
    for path in re.findall(r' d="([^"]+)"', d):
        for part in re.split(r'[zZ]', path):
            nums = [float(v) for v in re.findall(r'-?[\d.]+(?:e-?\d+)?', part)]
            if len(nums) >= 6:
                p = np.array(nums).reshape(-1, 2)
                p[:, 1] *= -1   # SVG y points down
                rings.append(p)
    return rings


def raster(rings, grid):
    inside = np.zeros(len(grid), bool)
    for r in rings:
        inside ^= Poly(r).contains_points(grid)   # even-odd, so holes stay holes
    return inside


def main():
    photo = trace()
    rings = model()
    xs = np.arange(-120, 120, RES); ys = np.arange(-20, 220, RES)
    gx, gy = np.meshgrid(xs, ys)
    grid = np.c_[gx.ravel(), gy.ravel()]
    target = Poly(photo).contains_points(grid)
    above = gy.ravel() > 0.5   # the photo's own wrist cut

    def placed(p):
        a = np.radians(p[0]); c, s = np.cos(a), np.sin(a)
        return [r @ np.array([[c, s], [-s, c]]) + p[1:] for r in rings]

    def iou(p):
        m = raster(placed(p), grid) & above
        return (m & target).sum() / max((m | target).sum(), 1)

    # start: model wrist at the photo's wrist-cut middle, turned to the photo's tip direction
    cut = photo[np.abs(photo[:, 1]) < 0.5]
    mid = np.array([(cut[:, 0].min() + cut[:, 0].max()) / 2, 0])
    tip = photo[np.argmax(np.linalg.norm(photo - mid, axis=1))]
    start = [np.degrees(np.arctan2(tip[0] - mid[0], tip[1] - mid[1])), *mid]
    best = max((minimize(lambda p: -iou(p), [start[0] + d, start[1], start[2] + dy], method='Nelder-Mead',
                         options=dict(initial_simplex=None, xatol=0.2, fatol=1e-4, maxiter=300))
                for d in (-8, 0, 8) for dy in (-10, 0, 10)), key=lambda r: -r.fun)
    m = raster(placed(best.x), grid) & above
    both, photo_only, model_only = m & target, target & ~m, m & ~target
    img = np.full(gx.shape + (3,), 255, np.uint8)
    for mask, colour in ((both, (170, 170, 170)), (photo_only, (220, 50, 50)), (model_only, (50, 90, 220))):
        img.reshape(-1, 3)[mask] = colour
    Image.fromarray(img[::-1]).save(HERE / 'fit_check.png')
    print(f'overlap {-best.fun:.1%} (turned {best.x[0]:.1f} deg); photo only {photo_only.sum() * RES ** 2:.0f} mm2, '
          f'model only {model_only.sum() * RES ** 2:.0f} mm2 -> fit_check.png')


if __name__ == '__main__':
    main()
