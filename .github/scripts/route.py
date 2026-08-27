#!/usr/bin/env python3
"""
ROUTE 1 — a pixel-art scene that never ends.

Everything is snapped to a 4px grid so it reads as real pixel art rather than
smooth vectors. The scenery scrolls in three parallax bands, each duplicated
so the seam never lands on screen. The walkers use a two-frame cycle — legs
apart, legs together — which is how the overworld sprites actually did it.
"""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pixels import (runs, PIKA_A, PIKA_B, CHAR_A, CHAR_B,  # noqa: E402
                    SQUI_A, SQUI_B, BULB_A, BULB_B)

PX = 4
CW, CH = 232, 62                      # canvas in pixels
W, H = CW * PX, CH * PX               # 928 x 248

SKY_T, SKY_B = "#8FD8F2", "#BFEAF8"
TREE_D, TREE_L = "#2C6B40", "#3E8F52"
GRASS_D, GRASS_L = "#57A860", "#6FBE72"
PATH, PATH_D = "#E4D5A0", "#CFBC86"
TRUNK = "#7A5230"

HORIZON = 22
PATH_T, PATH_B = 40, 49


def px(x, y, w, h, fill, op=None):
    o = '' if op is None else ' opacity="%s"' % op
    return '<rect x="%d" y="%d" width="%d" height="%d" fill="%s"%s/>' % (
        x * PX, y * PX, w * PX, h * PX, fill, o)


def cloud(x, y):
    return (px(x, y, 6, 2, "#FFFFFF") + px(x - 2, y + 2, 10, 2, "#FFFFFF")
            + px(x + 1, y - 2, 4, 2, "#FFFFFF"))


def tree(x, y):
    """Chunky pixel tree — dark crown, lighter cap, stubby trunk."""
    return (px(x + 3, y + 9, 3, 4, TRUNK)
            + px(x, y + 2, 9, 7, TREE_D)
            + px(x + 1, y, 7, 3, TREE_L)
            + px(x + 2, y + 3, 5, 2, TREE_L, "0.45"))


def tuft(x, y):
    return (px(x, y + 1, 5, 2, "#3F8A50") + px(x + 1, y, 1, 1, "#4E9E5E")
            + px(x + 3, y, 1, 1, "#4E9E5E"))


def ball(x, y):
    K, R, WH = "#2E2A24", "#E03B36", "#F4F4F4"
    return (px(x + 1, y, 4, 1, K) + px(x, y + 1, 6, 2, R)
            + px(x, y + 3, 6, 1, K) + px(x, y + 4, 6, 2, WH)
            + px(x + 1, y + 6, 4, 1, K)
            + px(x + 2, y + 3, 2, 1, WH))


def band(seed, maker, n, y_lo, y_hi):
    rnd = random.Random(seed)
    out = []
    for _ in range(n):
        out.append(maker(rnd.randint(0, CW - 1), rnd.randint(y_lo, y_hi)))
    return "".join(out)


def scroll(inner, dur, key):
    """Two copies a full canvas apart; the join is always off-screen."""
    return ('<g><g>%s</g><g transform="translate(%d,0)">%s</g>'
            '<animateTransform attributeName="transform" type="translate" '
            'values="0,0; -%d,0" dur="%.1fs" repeatCount="indefinite"/></g>'
            % (inner, W, inner, W, dur))


def walker(a, b, x, y, period, phase):
    """Two frames, hard-swapped. No tweening — that is the whole point."""
    fa = runs(a, PX, x * PX, y * PX)
    fb = runs(b, PX, x * PX, y * PX)
    anim = ('<animate attributeName="opacity" values="%s" keyTimes="0;0.5;0.5;1"'
            ' dur="%.2fs" begin="-%.2fs" repeatCount="indefinite"'
            ' calcMode="discrete"/>')
    return ('<g opacity="1">%s%s</g><g opacity="0">%s%s</g>'
            % (fa, anim % ("1;1;0;0", period, phase),
               fb, anim % ("0;0;1;1", period, phase)))


def render():
    sky = "".join(px(0, y, CW, 1, SKY_T if y < 10 else SKY_B)
                  for y in range(0, HORIZON))
    clouds = band(3, cloud, 9, 3, 13)
    trees = band(17, lambda x, y: tree(x, HORIZON - 12), 14, 0, 0)
    far = px(0, HORIZON - 3, CW, 3, TREE_D)

    grass_top = px(0, HORIZON, CW, PATH_T - HORIZON, GRASS_L)
    path = (px(0, PATH_T, CW, 1, PATH_D) + px(0, PATH_T + 1, CW, PATH_B - PATH_T - 1, PATH)
            + px(0, PATH_B - 1, CW, 1, PATH_D))
    grass_bot = px(0, PATH_B, CW, CH - PATH_B, GRASS_D)

    tufts_far = band(29, tuft, 26, HORIZON + 2, PATH_T - 4)
    tufts_near = band(41, tuft, 30, PATH_B + 2, CH - 4)
    stones = band(53, lambda x, y: px(x, y, 2, 1, PATH_D), 22, PATH_T + 2, PATH_B - 3)

    feet = PATH_B - 2
    cast = [
        (PIKA_A, PIKA_B, 14, feet - 19, 0.44, 0.00),
        (CHAR_A, CHAR_B, 62, feet - 18, 0.48, 0.11),
        (SQUI_A, SQUI_B, 108, feet - 17, 0.46, 0.23),
        (BULB_A, BULB_B, 154, feet - 18, 0.50, 0.07),
    ]
    walkers = "".join(walker(a, b, x, y, p, ph) for a, b, x, y, p, ph in cast)

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" shape-rendering="crispEdges" role="img" aria-label="A pixel route that never ends">
<defs><clipPath id="fr"><rect width="{W}" height="{H}"/></clipPath></defs>
<g clip-path="url(#fr)">
  {sky}
  {scroll(clouds, 52, "c")}
  {scroll(trees + far, 30, "t")}
  {grass_top}{path}{grass_bot}
  {scroll(tufts_far, 22, "g1")}
  {scroll(stones + ball(196, PATH_T + 4), 11, "st")}
  {walkers}
  {scroll(tufts_near, 8, "g2")}
</g>
</svg>'''


if __name__ == "__main__":
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    p = os.path.join(root, "assets", "route.svg")
    with open(p, "w") as f:
        f.write(render())
    print("wrote %s (%d KB)" % (p, os.path.getsize(p) // 1024))
