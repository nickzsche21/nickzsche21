#!/usr/bin/env python3
"""
THE CHASE — an endless runner drawn from scratch in SVG.

Original vector interpretations, animated declaratively. The scenery scrolls
in two parallax layers, each duplicated so the seam never lands on screen;
the runners bob in place with alternating legs. No JavaScript, no scheduler.
"""
import random

W, H = 900, 270
GROUND = 205


def bob(dur, phase, lift=5):
    return ('<animateTransform attributeName="transform" type="translate" '
            'values="0,0; 0,-%d; 0,0" dur="%.2fs" begin="-%.2fs" '
            'repeatCount="indefinite" additive="sum"/>' % (lift, dur, phase))


def legs(dur, phase, col, x1=-9, x2=7, y=-6, rx=6, ry=8):
    """Two feet trading places — reads as a run at any size."""
    a = ('<ellipse cx="%d" cy="%d" rx="%d" ry="%d" fill="%s">'
         '<animateTransform attributeName="transform" type="translate" '
         'values="0,0; -3,-7; 0,0" dur="%.2fs" begin="-%.2fs" '
         'repeatCount="indefinite"/></ellipse>' % (x1, y, rx, ry, col, dur, phase))
    b = ('<ellipse cx="%d" cy="%d" rx="%d" ry="%d" fill="%s">'
         '<animateTransform attributeName="transform" type="translate" '
         'values="0,-7; 3,0; 0,-7" dur="%.2fs" begin="-%.2fs" '
         'repeatCount="indefinite"/></ellipse>' % (x2, y, rx, ry, col, dur, phase))
    return a + b


def eye(cx, cy, r=4.6):
    return ('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="#2A2622"/>'
            '<circle cx="%.1f" cy="%.1f" r="%.1f" fill="#fff"/>'
            % (cx, cy, r, cx + r * 0.34, cy - r * 0.38, r * 0.36))


# ------------------------------------------------------------------ the cast
def pikachu(dur, phase):
    Y, D, BLK, RED = "#F7D02C", "#E0A81C", "#2A2622", "#E3423C"
    return f'''<g>{bob(dur, phase, 7)}
  <g>
    <path d="M 22,-40 L 40,-56 L 33,-52 L 52,-74 L 40,-70 L 54,-92
             L 46,-88 L 50,-104 L 30,-78 L 36,-80 L 22,-58 Z"
          fill="{Y}" stroke="{D}" stroke-width="1.5" stroke-linejoin="round">
      <animateTransform attributeName="transform" type="rotate"
        values="-8 22 -40; 10 22 -40; -8 22 -40" dur="{dur:.2f}s"
        begin="-{phase:.2f}s" repeatCount="indefinite"/>
    </path>
    {legs(dur, phase, D)}
    <ellipse cx="0" cy="-30" rx="20" ry="19" fill="{Y}"/>
    <path d="M -14,-40 q 8,6 16,0" stroke="{D}" stroke-width="3"
          fill="none" stroke-linecap="round"/>
    <g>
      <path d="M -12,-52 L -22,-88 L -6,-60 Z" fill="{Y}" stroke="{D}" stroke-width="1.2"/>
      <path d="M -22,-88 L -18,-77 L -14,-79 Z" fill="{BLK}"/>
      <path d="M 10,-54 L 14,-92 L 22,-60 Z" fill="{Y}" stroke="{D}" stroke-width="1.2"/>
      <path d="M 14,-92 L 19,-81 L 21,-84 Z" fill="{BLK}"/>
      <ellipse cx="0" cy="-56" rx="21" ry="19" fill="{Y}"/>
      <circle cx="-13" cy="-49" r="5.4" fill="{RED}"/>
      <circle cx="13" cy="-49" r="5.4" fill="{RED}"/>
      {eye(-7, -60)}{eye(10, -60)}
      <path d="M 0,-54 l -2.5,-2.5 l 5,0 Z" fill="{BLK}"/>
      <path d="M -4,-50 q 4,4 8,0" stroke="{BLK}" stroke-width="1.6" fill="none"
            stroke-linecap="round"/>
      <animateTransform attributeName="transform" type="rotate"
        values="-3 0 -40; 3 0 -40; -3 0 -40" dur="{dur:.2f}s"
        begin="-{phase:.2f}s" repeatCount="indefinite"/>
    </g>
    <g opacity="0">
      <path d="M 20,-52 l 9,-5 l -4,7 l 9,-3 l -12,11 l 3,-8 Z" fill="#FFF07A"/>
      <path d="M -20,-52 l -9,-5 l 4,7 l -9,-3 l 12,11 l -3,-8 Z" fill="#FFF07A"/>
      <animate attributeName="opacity" values="0;0;1;0;0" keyTimes="0;0.6;0.7;0.8;1"
               dur="2.4s" repeatCount="indefinite"/>
    </g>
  </g>
</g>'''


def charmander(dur, phase):
    O, D, C = "#F0894A", "#D2703A", "#FBD9A5"
    return f'''<g>{bob(dur, phase)}
  <g>
    <path d="M 18,-26 q 22,-4 26,-22" stroke="{O}" stroke-width="9" fill="none"
          stroke-linecap="round"/>
    <g>
      <path d="M 44,-50 q 9,-9 3,-19 q 10,10 3,22 Z" fill="#FF9B3D"/>
      <path d="M 45,-50 q 5,-6 2,-12 q 6,7 2,14 Z" fill="#FFDA5E"/>
      <animateTransform attributeName="transform" type="rotate"
        values="-9 44 -46; 9 44 -46; -9 44 -46" dur="0.9s" repeatCount="indefinite"/>
    </g>
    {legs(dur, phase, D)}
    <ellipse cx="0" cy="-28" rx="17" ry="18" fill="{O}"/>
    <ellipse cx="2" cy="-24" rx="10" ry="12" fill="{C}"/>
    <ellipse cx="2" cy="-52" rx="17" ry="15" fill="{O}"/>
    <ellipse cx="12" cy="-48" rx="6" ry="4" fill="{C}" opacity="0.55"/>
    {eye(-3, -56, 4.2)}{eye(11, -56, 4.2)}
    <path d="M 2,-46 q 7,4 13,0" stroke="#B4562A" stroke-width="1.6" fill="none"
          stroke-linecap="round"/>
  </g>
</g>'''


def squirtle(dur, phase):
    B, D, SH, C = "#7BC8E8", "#4E9DC4", "#C98A4B", "#F6E3B8"
    return f'''<g>{bob(dur, phase)}
  <g>
    <path d="M 16,-24 q 16,-6 14,-18" stroke="{B}" stroke-width="8" fill="none"
          stroke-linecap="round"/>
    {legs(dur, phase, D)}
    <ellipse cx="0" cy="-28" rx="19" ry="18" fill="{SH}"/>
    <ellipse cx="0" cy="-28" rx="13" ry="12" fill="#E0A868"/>
    <path d="M -13,-28 h 26 M 0,-40 v 24" stroke="{SH}" stroke-width="2"/>
    <ellipse cx="4" cy="-24" rx="11" ry="13" fill="{C}"/>
    <ellipse cx="3" cy="-52" rx="17" ry="15" fill="{B}"/>
    {eye(-2, -56, 4.4)}{eye(12, -56, 4.4)}
    <path d="M 3,-46 q 6,4 11,0" stroke="{D}" stroke-width="1.6" fill="none"
          stroke-linecap="round"/>
  </g>
</g>'''


def bulbasaur(dur, phase):
    G, D, BULB = "#8FD1A6", "#5FA47C", "#77C48E"
    return f'''<g>{bob(dur, phase)}
  <g>
    {legs(dur, phase, D)}
    <ellipse cx="-4" cy="-30" rx="20" ry="17" fill="{G}"/>
    <circle cx="-12" cy="-44" r="13" fill="{BULB}"/>
    <path d="M -20,-50 q 8,-9 16,-2" stroke="#4E8C68" stroke-width="2" fill="none"/>
    <ellipse cx="-14" cy="-33" rx="7" ry="4" fill="#6FAF86" opacity="0.6"/>
    <ellipse cx="8" cy="-46" rx="16" ry="14" fill="{G}"/>
    {eye(4, -50, 4.2)}{eye(17, -50, 4.2)}
    <path d="M 6,-40 q 7,4 13,0" stroke="#4E8C68" stroke-width="1.6" fill="none"
          stroke-linecap="round"/>
    <ellipse cx="-4" cy="-26" rx="5" ry="3" fill="#6FAF86" opacity="0.5"/>
  </g>
</g>'''


def jigglypuff(dur, phase):
    P, D = "#F5B8CE", "#DE8FAE"
    return f'''<g>{bob(dur, phase, 8)}
  <g>
    {legs(dur, phase, D, -7, 6, -5, 5, 6)}
    <circle cx="0" cy="-34" r="24" fill="{P}"/>
    <path d="M -20,-48 q 6,-12 17,-8 q -9,3 -9,10 Z" fill="{P}" stroke="{D}"
          stroke-width="1.2"/>
    <ellipse cx="-14" cy="-28" rx="6" ry="4" fill="#F09BBB" opacity="0.7"/>
    <ellipse cx="14" cy="-28" rx="6" ry="4" fill="#F09BBB" opacity="0.7"/>
    {eye(-6, -38, 6)}{eye(11, -38, 6)}
    <path d="M 0,-28 q 4,4 8,0" stroke="#B5687F" stroke-width="1.6" fill="none"
          stroke-linecap="round"/>
  </g>
</g>'''


def psyduck(dur, phase):
    Y, D, BILL = "#F6DE7A", "#D9BC4E", "#E8B85C"
    return f'''<g>{bob(dur, phase)}
  <g>
    {legs(dur, phase, BILL)}
    <ellipse cx="0" cy="-28" rx="17" ry="17" fill="{Y}"/>
    <ellipse cx="2" cy="-50" rx="17" ry="16" fill="{Y}"/>
    <ellipse cx="14" cy="-45" rx="9" ry="6" fill="{BILL}"/>
    <path d="M -10,-64 q 3,-7 5,-1 M -3,-66 q 3,-8 5,-1 M 4,-65 q 3,-7 5,-1"
          stroke="{D}" stroke-width="2" fill="none" stroke-linecap="round"/>
    <circle cx="-1" cy="-53" r="4" fill="#2A2622"/>
    <circle cx="9" cy="-53" r="4" fill="#2A2622"/>
    <g stroke="{D}" stroke-width="6" fill="none" stroke-linecap="round">
      <path d="M -14,-38 q -8,-8 -3,-16">
        <animateTransform attributeName="transform" type="rotate"
          values="-6 -14 -38; 8 -14 -38; -6 -14 -38" dur="{dur:.2f}s"
          begin="-{phase:.2f}s" repeatCount="indefinite"/>
      </path>
    </g>
  </g>
</g>'''


# --------------------------------------------------------------- the scenery
def hills(seed, col, base, amp, step):
    rnd = random.Random(seed)
    pts = []
    x = -40
    while x < W + 120:
        pts.append("%d,%d" % (x, base - rnd.randint(0, amp)))
        x += step
    return ('<polygon points="-40,%d %s %d,%d" fill="%s"/>'
            % (H, " ".join(pts), W + 120, H, col))


def clouds(seed):
    rnd = random.Random(seed)
    out = []
    for _ in range(7):
        x, y = rnd.uniform(0, W), rnd.uniform(18, 92)
        s = rnd.uniform(0.6, 1.25)
        out.append(
            '<g transform="translate(%.0f,%.0f) scale(%.2f)" opacity="0.92">'
            '<ellipse cx="0" cy="0" rx="26" ry="14" fill="#fff"/>'
            '<ellipse cx="-18" cy="5" rx="18" ry="11" fill="#fff"/>'
            '<ellipse cx="18" cy="5" rx="20" ry="12" fill="#fff"/></g>'
            % (x, y, s))
    return "".join(out)


def scroll(inner, dur):
    """Two copies side by side, translated a full width — the seam never shows."""
    return ('<g><g>%s</g><g transform="translate(%d,0)">%s</g>'
            '<animateTransform attributeName="transform" type="translate" '
            'values="0,0; -%d,0" dur="%.1fs" repeatCount="indefinite"/></g>'
            % (inner, W, inner, W, dur))


def grass(seed):
    rnd = random.Random(seed)
    out = []
    for _ in range(44):
        x = rnd.uniform(0, W)
        h = rnd.uniform(5, 12)
        out.append('<path d="M %.0f,%d q 2,-%.0f 4,0" stroke="#4E9E5E" '
                   'stroke-width="2" fill="none" stroke-linecap="round"/>'
                   % (x, GROUND + 6, h))
    for _ in range(9):
        x, y = rnd.uniform(0, W), rnd.uniform(GROUND + 22, H - 8)
        out.append('<ellipse cx="%.0f" cy="%.0f" rx="%.0f" ry="2.5" '
                   'fill="#3F8A50" opacity="0.5"/>' % (x, y, rnd.uniform(6, 16)))
    return "".join(out)


def render():
    cast = [
        (pikachu, 150, 1.0, 0.52, 0.00),
        (charmander, 300, 0.88, 0.56, 0.14),
        (squirtle, 430, 0.86, 0.54, 0.27),
        (bulbasaur, 560, 0.86, 0.58, 0.09),
        (jigglypuff, 690, 0.78, 0.50, 0.33),
        (psyduck, 810, 0.84, 0.60, 0.21),
    ]
    runners = []
    for fn, x, sc, dur, ph in cast:
        runners.append('<g transform="translate(%d,%d) scale(%.2f)">%s</g>'
                       % (x, GROUND, sc, fn(dur, ph)))

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="A line of creatures running forever">
<defs>
  <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="#5FC4F0"/>
    <stop offset="62%" stop-color="#AEE7FA"/>
    <stop offset="100%" stop-color="#DFF6E4"/>
  </linearGradient>
  <linearGradient id="dirt" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="#6FBE72"/>
    <stop offset="100%" stop-color="#4E9457"/>
  </linearGradient>
  <clipPath id="fr"><rect width="{W}" height="{H}" rx="12"/></clipPath>
</defs>
<g clip-path="url(#fr)">
  <rect width="{W}" height="{H}" fill="url(#sky)"/>
  <circle cx="792" cy="52" r="30" fill="#FFE973" opacity="0.95"/>
  <circle cx="792" cy="52" r="44" fill="#FFE973" opacity="0.22"/>

  {scroll(clouds(4), 46)}
  {scroll(hills(11, "#7FCB93", GROUND + 6, 46, 58), 26)}
  {scroll(hills(29, "#66B77C", GROUND + 16, 26, 44), 16)}

  <rect x="0" y="{GROUND + 8}" width="{W}" height="{H - GROUND}" fill="url(#dirt)"/>
  <line x1="0" y1="{GROUND + 8}" x2="{W}" y2="{GROUND + 8}" stroke="#3F8A50" stroke-width="2"/>
  {scroll(grass(5), 7)}

  {"".join(runners)}

  <rect width="{W}" height="{H}" rx="12" fill="none" stroke="#3F8A50" stroke-width="1.5" opacity="0.35"/>
</g>
</svg>'''


if __name__ == "__main__":
    import os
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    p = os.path.join(root, "assets", "chase.svg")
    with open(p, "w") as f:
        f.write(render())
    print("wrote %s (%d bytes)" % (p, os.path.getsize(p)))
