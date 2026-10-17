#!/usr/bin/env python3
"""Hand outline (mm) from one top-down photo, for the glove shell.

Photo rules: hand spread fully flat on plain WHITE paper (or any plain surface
that contrasts with skin), fingers pointing to the top of the photo, wrist
toward the bottom edge, camera straight above (not at an angle). A credit card
(85.6 x 54 mm) lies flat on the same surface, not touching the hand. The card
is the scale: the script finds it as the second-largest blob and reads its
long side. Pass --mm-per-px instead if there is no card.

--tape: the hand on a wood bench (or any surface that is not skin-coloured)
next to a yellow tape measure, shot from eye height at a slant. The tape is the
scale AND the perspective: the mm-tick spacing along its edge is measured row
by row, a pitched pinhole camera (focal length from an iPhone 1x lens unless
--focal-px) is fitted to how that spacing grows toward the bottom of the
photo, and the hand mask is re-projected onto the bench plane, lifted --lift
mm (where the hand's outline edge sits). Skin is found by colour (green/blue
< 1.2: skin is pink, wood and the tape are yellow). The wrist cut is
perpendicular to the forearm, which may enter at any angle.

  python3 outline_from_photo.py ~/Downloads/hand.jpg          # writes hand_outline.scad + outline_preview.png
  python3 outline_from_photo.py --tape ../../glove_hand/refs/jake_left_hand_spread_top.jpg
  python3 outline_from_photo.py --placeholder                  # synthetic large left hand (no photo yet)
  python3 outline_from_photo.py --self-test                    # extract the synthetic photo, check the scale

Writes hand_outline.scad (hand_outline = [[x,y],...] in mm, wrist edge at
y=0, fingers toward +y; hand_source = where it came from) next to this file.
No CAD build, no app build.
"""
import argparse
import math
from pathlib import Path
import contourpy
import numpy as np
from PIL import Image, ImageDraw, ImageOps
from scipy import ndimage

HERE = Path(__file__).resolve().parent
CARD_MM = (85.60, 53.98)

def masks(gray):
    """Foreground = the Otsu class that touches the image border least."""
    hist = np.bincount(gray.ravel(), minlength=256).astype(float)
    p = hist / hist.sum()
    w = np.cumsum(p); mu = np.cumsum(p * np.arange(256))
    between = (mu[-1] * w - mu) ** 2 / np.maximum(w * (1 - w), 1e-12)
    fg = gray <= int(np.argmax(between))
    border = np.concatenate([fg[0], fg[-1], fg[:, 0], fg[:, -1]]).mean()
    if border > 0.5:
        fg = ~fg
    fg = ndimage.binary_opening(fg, iterations=2)
    labels, n = ndimage.label(fg)
    sizes = ndimage.sum(fg, labels, range(1, n + 1))
    order = np.argsort(sizes)[::-1] + 1
    hand = ndimage.binary_fill_holes(labels == order[0])
    card = ndimage.binary_fill_holes(labels == order[1]) if n > 1 else None
    return hand, card

def card_long_side_px(card):
    ys, xs = np.nonzero(card)
    pts = np.stack([xs, ys], 1).astype(float)
    pts -= pts.mean(0)
    _, vecs = np.linalg.eigh(np.cov(pts.T))
    proj = pts @ vecs
    sides = sorted(proj.max(0) - proj.min(0) + 1)
    ratio = sides[1] / sides[0]
    if not 1.35 < ratio < 1.85:   # a card is 1.59; anything else is not the card
        raise SystemExit(f'second blob is not a card (side ratio {ratio:.2f}); retake or pass --mm-per-px')
    return sides[1]

def skin_mask(rgb, rule='gb'):
    a = ndimage.uniform_filter(rgb.astype(float), (5, 5, 1))
    g_b = a[..., 1] / np.maximum(a[..., 2], 1)
    if rule == 'rg':   # warm light: skin G/B rises to ~1.25, but R/G stays ~1.4 (wood 1.2, laptop 1.0)
        m = (a[..., 0] / np.maximum(a[..., 1], 1) > 1.3) & (g_b < 1.35) & (a[..., 0] > 100)
    else:
        m = (g_b < 1.2) & (a[..., 0] > 120)
    m = ndimage.binary_closing(ndimage.binary_opening(m, iterations=2), iterations=3)
    labels, n = ndimage.label(m)
    sizes = ndimage.sum(m, labels, range(1, n + 1))
    return ndimage.binary_fill_holes(labels == np.argmax(sizes) + 1)

def tape_px_per_mm(rgb):
    """[(row, px per mm)] from the mm ticks along the tape's left edge."""
    a = rgb.astype(float)
    yellow = (a[..., 0] > 150) & (a[..., 1] > 130) & (a[..., 2] < 90)
    labels, n = ndimage.label(yellow)
    tape = labels == np.argmax(ndimage.sum(yellow, labels, range(1, n + 1))) + 1
    rows = np.nonzero(tape.sum(1) > 20)[0]
    left = np.array([np.nonzero(tape[r])[0].min() for r in rows])
    keep = np.abs(left - np.median(left - np.polyval(np.polyfit(rows, left, 1), rows))
                  - np.polyval(np.polyfit(rows, left, 1), rows)) < 4
    edge = np.polyfit(rows[keep], left[keep], 1)
    gray = a.mean(2)
    ys = np.arange(rows[0], rows[-1])
    prof = np.array([gray[y, int(np.polyval(edge, y)) + 2:int(np.polyval(edge, y)) + 7].mean() for y in ys])
    prof -= np.convolve(prof, np.ones(31) / 31, 'same')
    out = []
    for c in range(ys[0] + 60, ys[-1] - 60, 20):
        w = prof[(ys >= c - 50) & (ys < c + 50)]
        f = np.fft.rfftfreq(8192)
        sp = np.abs(np.fft.rfft((w - w.mean()) * np.hanning(len(w)), n=8192)) * ((f > 1 / 6) & (f < 1 / 1.8))
        out.append((c, 1 / f[np.argmax(sp)]))
    out = np.array(out)
    med = ndimage.median_filter(out[:, 1], 7, mode='nearest')
    return out[np.abs(out[:, 1] - med) < 0.05 * med]   # number labels and the hook give stray periods

class Camera:
    """Pinhole camera pitched `pitch` rad from straight down, `height` mm above the bench, no roll.
    Bench coords: X right, Y away from the camera (up the photo)."""
    def __init__(self, w, h, focal):
        self.cx, self.cy, self.f = w / 2, h / 2, focal

    def fit(self, ticks):
        from scipy.optimize import least_squares
        r = least_squares(lambda p: self.px_per_mm(ticks[:, 0], *p) - ticks[:, 1], [500, 0.3])
        self.height, self.pitch = r.x
        self.rms = float(np.sqrt(np.mean(r.fun ** 2)))
        return self

    def px_per_mm(self, v, height, pitch):   # along the photo's vertical, on the bench
        phi = np.arctan((v - self.cy) / self.f)
        return self.f * np.cos(pitch - phi) ** 2 / (height * np.cos(phi) ** 2)

    def to_bench(self, u, v, lift=0.0):
        h, phi = self.height - lift, np.arctan((v - self.cy) / self.f)
        beta = self.pitch - phi
        return (u - self.cx) * h * np.cos(phi) / np.cos(beta) / self.f, h * np.tan(beta)

    def to_px(self, X, Y, lift=0.0):
        h = self.height - lift
        beta = np.arctan(Y / h); phi = self.pitch - beta
        return self.cx + X * self.f * np.cos(beta) / (h * np.cos(phi)), self.cy + self.f * np.tan(phi)

def rectify(hand, cam, lift, res=0.25):
    """Hand mask resampled onto the bench plane at `res` mm/px, rotated so the forearm points
    straight down. Returns (mask, wrist row, mm->photo px function)."""
    H, W = hand.shape
    edge = np.ones_like(hand); edge[8:-8, 8:-8] = False   # opening/closing eat the outermost px
    ev, eu = np.nonzero(hand & edge)
    if not len(ev):
        raise SystemExit('the forearm does not reach the photo edge; cannot find its direction')
    entry = np.array(cam.to_bench(eu.mean(), ev.mean(), lift))
    # Palm centre: the deepest point of the mask's far half (from where the arm enters). The
    # forearm near the camera is wider in px than the palm, so the whole-mask maximum is on it.
    vv, uu = np.nonzero(hand)
    far = np.hypot(*(np.array(cam.to_bench(uu, vv, lift)) - entry[:, None]))
    dist = ndimage.distance_transform_edt(np.pad(hand, 1))[1:-1, 1:-1]
    i = np.argmax(np.where(far > far.max() / 2, dist[vv, uu], 0))
    palm = np.array(cam.to_bench(uu[i], vv[i], lift))
    up = (palm - entry) / np.linalg.norm(palm - entry); right = np.array([up[1], -up[0]])
    xs = np.arange(-150, 150, res); ys = np.arange(160, -160, -res)   # rows top (fingers) -> bottom (arm)
    gx, gy = np.meshgrid(xs, ys)
    def to_px(x, y):
        b = palm.reshape(2, *[1] * np.ndim(x))
        X, Y = b[0] + x * right[0] + y * up[0], b[1] + x * right[1] + y * up[1]
        return cam.to_px(X, Y, lift)
    u, v = to_px(gx, gy)
    rect = ndimage.gaussian_filter(ndimage.map_coordinates(hand.astype(float), [v, u], order=1, cval=0), 1 / res) > 0.5   # 1 mm: skin-edge jitter
    inside = (u >= 8) & (u < W - 9) & (v >= 8) & (v < H - 9)
    labels, _ = ndimage.label(rect)
    palm_row, axis = int(np.argmin(np.abs(ys))), int(np.argmin(np.abs(xs)))
    rect = labels == labels[palm_row, axis]
    # Narrowest crossing of the forearm below the palm centre, before it runs off the photo.
    best, cut = None, None
    for r in range(palm_row + 10, len(ys)):
        run = rect[r]
        if not run[axis]:
            break
        lo, hi = axis, axis
        while lo > 0 and run[lo - 1]: lo -= 1
        while hi < len(run) - 1 and run[hi + 1]: hi += 1
        if not (inside[r, lo - 1] and inside[r, hi + 1]):
            break
        if best is None or hi - lo < best:
            best, cut = hi - lo, r
    if cut is None:
        raise SystemExit('no wrist found below the palm')
    # mm (outline frame: wrist at y=0, x centred on the hand) -> photo px, for the preview
    rows = np.nonzero(rect[:cut].any(1))[0]
    cols = np.nonzero(rect[:cut].any(0))[0]
    x0 = (xs[cols.min()] + xs[cols.max()]) / 2; y0 = ys[cut] + res / 2
    return rect, cut, lambda x, y: to_px(np.asarray(x) + x0, np.asarray(y) + y0)

def wrist_row(hand):
    """Narrowest row in the bottom 40% of the hand: where the palm meets the forearm."""
    rows = np.nonzero(hand.any(1))[0]
    top, bottom = rows[0], rows[-1]
    width = hand.sum(1)
    lo = int(bottom - 0.4 * (bottom - top))
    band = np.arange(lo, bottom - 2)
    return int(band[np.argmin(width[band])])

def rdp(pts, eps):
    if len(pts) < 3:
        return pts
    a, b = pts[0], pts[-1]
    u, v = b - a, pts - a
    d = np.abs(u[0] * v[:, 1] - u[1] * v[:, 0]) / max(np.linalg.norm(u), 1e-9)
    i = int(np.argmax(d))
    if d[i] <= eps:
        return np.array([a, b])
    return np.vstack([rdp(pts[:i + 1], eps)[:-1], rdp(pts[i:], eps)])

def outline(hand, mm_per_px, cut=None):
    cut = wrist_row(hand) if cut is None else cut
    hand = hand.copy(); hand[cut:] = False
    hand = np.pad(hand, 2)
    lines = contourpy.contour_generator(z=hand.astype(float)).lines(0.5)
    ring = max(lines, key=len)
    mm = (ring - 2) * mm_per_px
    mm[:, 1] = (cut - 0.5) * mm_per_px - mm[:, 1]   # image y down -> CAD y up, wrist at y=0
    mm[:, 0] -= (mm[:, 0].max() + mm[:, 0].min()) / 2
    if np.allclose(mm[0], mm[-1]):
        mm = mm[:-1]
    far = int(np.argmax(np.linalg.norm(mm - mm[0], axis=1)))   # split the ring so RDP has two real ends
    mm = np.vstack([rdp(mm[:far + 1], 0.3)[:-1], rdp(np.vstack([mm[far:], mm[:1]]), 0.3)[:-1]])
    x, y = mm[:, 0], mm[:, 1]
    if (x * np.roll(y, -1) - np.roll(x, -1) * y).sum() < 0:   # counter-clockwise for OpenSCAD
        mm = mm[::-1]
    return mm

def write(mm, source, out='hand_outline'):
    pts = ',\n '.join(f'[{x:.2f},{y:.2f}]' for x, y in mm)
    w, h = np.ptp(mm, 0)
    src = 'hand_source' if out == 'hand_outline' else f'{out}_source'
    (HERE / f'{out}.scad').write_text(
        f'// Generated by outline_from_photo.py. Do not hand-edit; re-run the script.\n'
        f'// Source: {source}\n// Width {w:.1f} mm, wrist-to-tip {h:.1f} mm, {len(mm)} points.\n'
        f'{src} = "{source}";\n{out} = [\n {pts}\n];\n')
    return w, h

def preview(img, mm, to_px, out='hand_outline'):
    rgb = img.convert('RGB')
    d = ImageDraw.Draw(rgb)
    # Redraw the CAD outline back onto the photo so a bad extraction is obvious.
    px = [tuple(map(float, to_px(x, y))) for x, y in mm]
    d.line(px + px[:1], fill=(230, 40, 40), width=max(2, rgb.width // 400))
    d.line([tuple(map(float, to_px(x, 0))) for x in (-80, 80)], fill=(40, 120, 230), width=3)
    rgb.thumbnail((1200, 1200))
    rgb.save(HERE / ('outline_preview.png' if out == 'hand_outline' else f'{out}_preview.png'))

def synthetic(px_per_mm=4.0):
    """A large adult LEFT hand, palm down, fully spread, seen from above
    (thumb on the right), plus a credit card. Sizes are a ~95th-percentile
    male guess, NOT Jake's hand: hand breadth 95 mm, middle tip 205 mm from wrist."""
    W, H = 320, 300   # mm canvas
    img = Image.new('L', (int(W * px_per_mm), int(H * px_per_mm)), 245)
    d = ImageDraw.Draw(img)
    s = lambda x, y: (x * px_per_mm, (H - y) * px_per_mm)   # mm, y up -> px
    ox, oy = 150, 40   # wrist centre
    d.rectangle([s(ox - 33, oy), s(ox + 33, 0)], fill=90)                       # forearm
    d.polygon([s(ox - 33, oy), s(ox - 30, oy + 18), s(ox - 50, oy + 100), s(ox - 45, oy + 112),
               s(ox + 45, oy + 112), s(ox + 50, oy + 70), s(ox + 33, oy + 15), s(ox + 33, oy)], fill=90)
    # [base x, base y, angle from +y (deg, + toward thumb), length, width]
    for bx, by, ang, ln, wd in [(-36, 102, -24, 66, 16.5), (-14, 108, -8, 86, 18.5),
                                (8, 110, 4, 92, 20), (30, 106, 16, 82, 19), (40, 32, 58, 76, 23)]:
        x0, y0 = ox + bx, oy + by
        x1, y1 = x0 + ln * math.sin(math.radians(ang)), y0 + ln * math.cos(math.radians(ang))
        d.line([s(x0, y0), s(x1, y1)], fill=90, width=int(wd * px_per_mm))
        r = wd / 2 * px_per_mm
        for x, y in [(x0, y0), (x1, y1)]:
            cx, cy = s(x, y); d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=90)
    card = Image.new('L', (int(CARD_MM[0] * px_per_mm), int(CARD_MM[1] * px_per_mm)), 40)
    card = card.rotate(7, expand=True, fillcolor=0)
    img.paste(card, (int(225 * px_per_mm), int(20 * px_per_mm)), card.point(lambda v: 255 if v else 0))
    return img

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('photo', nargs='?')
    ap.add_argument('--mm-per-px', type=float)
    ap.add_argument('--tape', action='store_true', help='scale + perspective from a tape measure (see above)')
    ap.add_argument('--focal-px', type=float, help='default: iPhone 1x, 26 mm-equivalent')
    ap.add_argument('--lift', type=float, default=10.0, help='mm above the bench where the outline edge sits')
    ap.add_argument('--skin', choices=['gb', 'rg'], default='gb', help="skin colour rule; 'rg' for warm-lit photos")
    ap.add_argument('--out', default='hand_outline', help='output stem: <out>.scad defines <out> = [...]')
    ap.add_argument('--placeholder', action='store_true')
    ap.add_argument('--self-test', action='store_true')
    a = ap.parse_args()
    if a.placeholder or a.self_test:
        img, source = synthetic(), 'PLACEHOLDER synthetic large left hand, not measured'
    elif a.photo:
        img, source = ImageOps.exif_transpose(Image.open(a.photo)), Path(a.photo).name
    else:
        ap.error('give a photo, --placeholder or --self-test')
    if a.tape:
        rgb = np.asarray(img.convert('RGB'))
        cam = Camera(img.width, img.height, a.focal_px or math.hypot(*img.size) * 26 / 43.27)
        cam.fit(tape_px_per_mm(rgb))
        rect, cut, to_px = rectify(skin_mask(rgb, a.skin), cam, a.lift)
        mm = outline(rect, 0.25, cut)
        w, h = write(mm, f'{source} (tape, perspective-corrected)', a.out)
        preview(img, mm, to_px, a.out)
        print(f'{source}: camera {cam.height:.0f} mm up, pitched {math.degrees(cam.pitch):.1f} deg '
              f'(tick fit rms {cam.rms:.3f} px/mm); outline {w:.1f} mm wide x {h:.1f} mm wrist-to-tip, '
              f'{len(mm)} points -> {a.out}.scad')
        return
    gray = np.asarray(img.convert('L'))
    hand, card = masks(gray)
    if a.mm_per_px:
        mm_per_px = a.mm_per_px
    elif card is not None:
        mm_per_px = CARD_MM[0] / card_long_side_px(card)
    else:
        raise SystemExit('no card found; pass --mm-per-px')
    mm = outline(hand, mm_per_px)
    if a.self_test:
        err = abs(mm_per_px - 0.25) / 0.25
        w, h = np.ptp(mm, 0)
        assert err < 0.01, f'card scale off by {err:.1%}'
        assert 170 < w < 200 and 185 < h < 215, (w, h)
        print(f'self-test ok: scale error {err:.2%}, outline {w:.1f} x {h:.1f} mm, {len(mm)} points')
        return
    w, h = write(mm, source)
    cut = wrist_row(hand)
    cx = (lambda c: (c.max() + c.min()) / 2)(np.nonzero(hand.any(0))[0])
    preview(img, mm, lambda x, y: (x / mm_per_px + cx, cut - y / mm_per_px))
    print(f'{source}: {mm_per_px:.4f} mm/px, outline {w:.1f} mm wide x {h:.1f} mm wrist-to-tip, '
          f'{len(mm)} points -> hand_outline.scad, outline_preview.png')

if __name__ == '__main__':
    main()
