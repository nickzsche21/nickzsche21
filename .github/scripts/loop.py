#!/usr/bin/env python3
"""
INFINITE DESCENT — a tunnel with no bottom.

Pure declarative SVG animation. No JavaScript, no scheduled job, no server.
The loop is seamless: every ring starts at a negative offset so the stream is
already mid-flight at t=0 and never visibly restarts. It runs forever in the
viewer's browser and costs nothing to keep alive.
"""
import random

W, H = 900, 360
CX, CY = W / 2.0, H / 2.0
DUR = 7.2          # seconds for one ring to travel the whole tunnel
RINGS = 18
NEON = ["#22E5FF", "#7C5CFF", "#FF3DA6", "#FFC24B"]


def stars(n=90, seed=7):
    rnd = random.Random(seed)
    out = []
    for i in range(n):
        x, y = rnd.uniform(0, W), rnd.uniform(0, H)
        # keep the throat of the tunnel clear
        if abs(x - CX) < 90 and abs(y - CY) < 60:
            continue
        r = rnd.choice([0.6, 0.7, 0.9, 1.2])
        o = rnd.uniform(0.15, 0.6)
        dur = rnd.uniform(2.4, 6.0)
        out.append(
            '<circle cx="%.1f" cy="%.1f" r="%.1f" fill="#CFE9FF" opacity="%.2f">'
            '<animate attributeName="opacity" values="%.2f;%.2f;%.2f" dur="%.1fs"'
            ' begin="-%.1fs" repeatCount="indefinite"/></circle>'
            % (x, y, r, o, o, o * 0.2, o, dur, rnd.uniform(0, dur)))
    return "".join(out)


def tunnel():
    out = []
    for i in range(RINGS):
        delay = -(i * DUR / float(RINGS))
        col = NEON[i % len(NEON)]
        spin = 82 if i % 2 == 0 else -82
        out.append(
            '<rect x="-58" y="-58" width="116" height="116" rx="16" fill="none" '
            'stroke="%s" stroke-width="0.7" opacity="0">'
            # rushing toward the viewer
            '<animateTransform attributeName="transform" type="scale" '
            'values="0.02;9.5" dur="%.2fs" begin="%.2fs" repeatCount="indefinite" '
            'calcMode="spline" keyTimes="0;1" keySplines="0.45 0 0.9 0.6"/>'
            # and turning as it comes
            '<animateTransform attributeName="transform" type="rotate" '
            'values="0;%d" dur="%.2fs" begin="%.2fs" repeatCount="indefinite" '
            'additive="sum"/>'
            # bright in the middle distance, gone as it passes you
            '<animate attributeName="opacity" values="0;0.95;0.75;0" '
            'keyTimes="0;0.28;0.72;1" dur="%.2fs" begin="%.2fs" '
            'repeatCount="indefinite"/>'
            '</rect>'
            % (col, DUR, delay, spin, DUR, delay, DUR, delay))
    return "".join(out)


def render(name="NIKHIL", handle="nickzsche21"):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="An endless tunnel">
<defs>
  <radialGradient id="core" cx="50%" cy="50%">
    <stop offset="0%" stop-color="#FFFFFF" stop-opacity="0.95"/>
    <stop offset="30%" stop-color="#8FD8FF" stop-opacity="0.55"/>
    <stop offset="70%" stop-color="#5B6CFF" stop-opacity="0.16"/>
    <stop offset="100%" stop-color="#000000" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="vig" cx="50%" cy="50%">
    <stop offset="55%" stop-color="#000" stop-opacity="0"/>
    <stop offset="100%" stop-color="#000" stop-opacity="0.85"/>
  </radialGradient>
  <clipPath id="frame"><rect width="{W}" height="{H}" rx="12"/></clipPath>
</defs>
<style>
  .id {{ font-family: ui-monospace,'SF Mono',Menlo,Consolas,monospace;
         font-size: 10px; letter-spacing: 4.2px; fill: #8FA6C4; }}
</style>

<g clip-path="url(#frame)">
  <rect width="{W}" height="{H}" fill="#04060D"/>
  {stars()}

  <!-- the throat -->
  <circle cx="{CX}" cy="{CY}" r="120" fill="url(#core)">
    <animate attributeName="opacity" values="0.75;1;0.75" dur="3.6s"
             repeatCount="indefinite"/>
  </circle>

  <g transform="translate({CX},{CY})">
    {tunnel()}
  </g>

  <circle cx="{CX}" cy="{CY}" r="2.6" fill="#FFFFFF">
    <animate attributeName="r" values="2;4.2;2" dur="2.2s" repeatCount="indefinite"/>
  </circle>

  <rect width="{W}" height="{H}" fill="url(#vig)"/>
  <text x="28" y="{H - 22}" class="id">{name}</text>
  <text x="{W - 28}" y="{H - 22}" class="id" text-anchor="end">{handle.upper()}</text>
  <rect width="{W}" height="{H}" rx="12" fill="none" stroke="#1B2740" stroke-width="1"/>
</g>
</svg>'''


if __name__ == "__main__":
    import os
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    os.makedirs(os.path.join(root, "assets"), exist_ok=True)
    p = os.path.join(root, "assets", "loop.svg")
    with open(p, "w") as f:
        f.write(render())
    print("wrote %s (%d bytes)" % (p, os.path.getsize(p)))
