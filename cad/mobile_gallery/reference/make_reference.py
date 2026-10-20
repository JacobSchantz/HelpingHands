#!/usr/bin/env python3
"""Stage the reference photos the live preview's photo toggle shows beside a family's views (voice-c68a1812).

actual_top.png is the left-hand device of cad/reference/generalist_gripper_gen6_two_hands.png
resampled into gripper CAD millimetres (X across, Z along the fingers, viewed from +Y), using
the same photo->mm frame Gens 9-11 traced their fingers in (gripper.scad: mm_per_px, px_pivot,
axis_deg, and the right hinge pivot), spanning BOUNDS. The other photos are copied downscaled.
photos.js maps each design family to its photos; a family with none still gets the toggle, greyed out.
Re-run after changing the frame or adding photos: python3 cad/mobile_gallery/reference/make_reference.py"""
from pathlib import Path
import json, math
from PIL import Image

HERE = Path(__file__).resolve().parent
REF = HERE.parents[2] / 'cad/reference'
MM_PER_PX, PX_PIVOT, AXIS_DEG, PIVOT_X = 0.2, (337, 395), 36.5, 27.672   # v011b gripper.scad / poses.js
BOUNDS = (-75, 75, -45, 125)   # X0, X1, Z0, Z1 in mm
K = 0.125                      # output mm per pixel
OTHERS = {'top': 'Top, around a bowl', 'two_hands': 'Both hands, top', 'side': 'Side', 'closed': 'Closed',
          'cup': 'Holding a cup', 'robot': 'On the robot', 'camera': 'Camera', 'target': 'Target'}


def main():
    x0, x1, z0, z1 = BOUNDS
    s, c = math.sin(math.radians(AXIS_DEG)), math.cos(math.radians(AXIS_DEG))
    # output (col,row) -> CAD X = x0 + col*K, Z = z1 - row*K -> finger frame u = (X-pivot)/mm, w = Z/mm
    # -> photo dx = -u s + w c, dy = u c + w s (inverse of px() in gripper.scad)
    # One output column is du = a, one row is dw = -a.
    a = K / MM_PER_PX
    u0, w0 = (x0 - PIVOT_X) / MM_PER_PX, z1 / MM_PER_PX
    coeffs = (-a * s, -a * c, PX_PIVOT[0] - u0 * s + w0 * c,
              a * c, -a * s, PX_PIVOT[1] + u0 * c + w0 * s)
    size = (round((x1 - x0) / K), round((z1 - z0) / K))
    photo = Image.open(REF / 'generalist_gripper_gen6_two_hands.png').convert('RGBA')
    photo.transform(size, Image.Transform.AFFINE, coeffs, Image.Resampling.BICUBIC,
                    fillcolor=(0, 0, 0, 0)).save(HERE / 'actual_top.png', optimize=True)
    photos = [dict(id='aligned', label='Top (aligned)', src='reference/actual_top.png', bounds=BOUNDS)]
    for key, label in OTHERS.items():
        image = Image.open(REF / f'generalist_gripper_gen6_{key}.png').convert('RGB')
        image.thumbnail((1000, 1000))
        image.save(HERE / f'{key}.png', optimize=True)
        photos.append(dict(id=key, label=label, src=f'reference/{key}.png'))
    families = {'Generalist Gripper': photos}
    (HERE / 'photos.js').write_text('// Written by make_reference.py: design family -> its reference photos.\nexport default ' + json.dumps(families, indent=1) + ';\n')


if __name__ == '__main__':
    main()
