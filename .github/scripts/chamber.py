#!/usr/bin/env python3
"""
SPECIMEN — containment chamber renderer.
Emits a self-contained animated SVG. No external fonts, no third-party
services, no JS. Every animation parameter is derived from real telemetry:
the heart beats at the subject's actual shipping rate, and the corruption
scales with real silence.
"""
import math


def _mix(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def _hex(c):
    return "#%02x%02x%02x" % c


def palette(decay):
    """Vital green -> warning amber -> necrotic red, driven by decay."""
    green = (0, 255, 156)
    amber = (255, 176, 0)
    red = (255, 46, 77)
    if decay < 50:
        c = _mix(green, amber, decay / 50.0)
    else:
        c = _mix(amber, red, (decay - 50) / 50.0)
    return _hex(c)


def ekg_path(x, y, w, bpm, decay):
    """A trace that flattens as the organism fails."""
    amp = max(4.0, 34.0 * (1.0 - decay / 115.0))
    pts = []
    beats = 6
    seg = w / float(beats)
    for b in range(beats):
        bx = x + b * seg
        # baseline -> p wave -> QRS spike -> t wave -> baseline
        pts.append((bx, y))
        pts.append((bx + seg * 0.16, y))
        pts.append((bx + seg * 0.22, y - amp * 0.20))
        pts.append((bx + seg * 0.28, y))
        pts.append((bx + seg * 0.34, y + amp * 0.28))
        pts.append((bx + seg * 0.40, y - amp))
        pts.append((bx + seg * 0.46, y + amp * 0.42))
        pts.append((bx + seg * 0.52, y))
        pts.append((bx + seg * 0.68, y - amp * 0.30))
        pts.append((bx + seg * 0.80, y))
    pts.append((x + w, y))
    return "M " + " L ".join("%.1f,%.1f" % p for p in pts)


def tendrils(cx, cy, r, count, decay, accent):
    """Limbs retract and wither as decay rises."""
    out = []
    reach = 1.0 - decay / 160.0
    for i in range(count):
        a = (2 * math.pi / count) * i - math.pi / 2
        length = r * (1.55 + 0.5 * ((i % 3) / 2.0)) * reach
        x1 = cx + math.cos(a) * r * 0.92
        y1 = cy + math.sin(a) * r * 0.92
        x2 = cx + math.cos(a) * length
        y2 = cy + math.sin(a) * length
        # curl the tip
        curl = 0.5 + (i % 4) * 0.16
        cxp = cx + math.cos(a + curl * 0.5) * length * 0.72
        cyp = cy + math.sin(a + curl * 0.5) * length * 0.72
        dur = 3.2 + (i % 5) * 0.55
        out.append(
            '<path d="M %.1f,%.1f Q %.1f,%.1f %.1f,%.1f" fill="none" '
            'stroke="%s" stroke-width="1.5" stroke-linecap="round" opacity="0.55">'
            '<animate attributeName="opacity" values="0.55;0.14;0.55" '
            'dur="%.2fs" repeatCount="indefinite"/></path>'
            % (x1, y1, cxp, cyp, x2, y2, accent, dur)
        )
    return "".join(out)


def heatmap(days, x, y, width, accent):
    """The real contribution calendar, drawn by hand — not a stats card."""
    if not days:
        return ""
    peak = max(1, max(c for _, c in days))
    cols = (len(days) + 6) // 7
    gap = 2.4
    cell = max(4.0, (width - (cols - 1) * gap) / float(cols))
    out = []
    for i, (_, c) in enumerate(days):
        row = i % 7
        col = i // 7
        px = x + col * (cell + gap)
        py = y + row * (cell + gap)
        if c == 0:
            fill, op = "#161b22", "1"
        else:
            op = "%.2f" % (0.30 + 0.70 * min(1.0, c / float(peak)))
            fill = accent
        out.append(
            '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="1.5" '
            'fill="%s" opacity="%s"/>' % (px, py, cell, cell, fill, op)
        )
    return "".join(out)


def render(v):
    decay = v["decay"]
    accent = palette(decay)
    bpm = v["bpm"]
    beat = 60.0 / max(bpm, 1)
    stage = v["stage"]
    W, H = 900, 516

    # --- layout grid ---------------------------------------------------
    PAD = 36
    RIGHT = 300           # right column origin
    RW = W - RIGHT - PAD  # right column width
    cx, cy, r = 158, 196, 38
    core_r = r * (0.50 + 0.05 * stage)

    glitch = []
    for i in range(int(decay / 9)):
        gy = 40 + (i * 137) % (H - 90)
        gw = 40 + (i * 91) % 320
        gx = (i * 213) % (W - gw)
        glitch.append(
            '<rect x="%d" y="%d" width="%d" height="%d" fill="%s" opacity="0">'
            '<animate attributeName="opacity" values="0;0.30;0" dur="%.2fs" '
            'begin="%.2fs" repeatCount="indefinite"/></rect>'
            % (gx, gy, gw, 2 + (i % 3), accent, 0.7 + (i % 6) * 0.45, (i * 0.37) % 4.0)
        )
    glitch = "".join(glitch)

    hm = heatmap(v["days"], PAD, 394, W - PAD * 2, accent)
    trace = ekg_path(RIGHT, 196, RW, bpm, decay)

    rows = [
        ("DECAY INDEX", "%d%%" % decay),
        ("INTEGRITY", "%d%%" % v["integrity"]),
        ("PULSE", "%d BPM" % bpm),
        ("SILENCE", "%dd" % v["silence"]),
    ]
    step = RW / float(len(rows))
    readout = "".join(
        '<text x="%.0f" y="286" class="lbl">%s</text>'
        '<text x="%.0f" y="310" class="val">%s</text>'
        % (RIGHT + i * step, k, RIGHT + i * step, val)
        for i, (k, val) in enumerate(rows)
    )

    bar_w = RW * (v["integrity"] / 100.0)
    login = v["user"].get("login", "?").upper()

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Specimen {v['uid']} containment chamber">
<defs>
  <radialGradient id="core" cx="50%" cy="50%">
    <stop offset="0%" stop-color="#ffffff" stop-opacity="0.95"/>
    <stop offset="45%" stop-color="{accent}" stop-opacity="0.85"/>
    <stop offset="100%" stop-color="{accent}" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="vig" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="#000" stop-opacity="0.5"/>
    <stop offset="35%" stop-color="#000" stop-opacity="0"/>
    <stop offset="100%" stop-color="#000" stop-opacity="0.6"/>
  </linearGradient>
  <pattern id="grid" width="22" height="22" patternUnits="userSpaceOnUse">
    <path d="M22 0 L0 0 0 22" fill="none" stroke="{accent}" stroke-width="0.35" opacity="0.09"/>
  </pattern>
  <clipPath id="chamber"><rect width="{W}" height="{H}" rx="10"/></clipPath>
</defs>
<style>
  .lbl {{ font-size: 9.5px; letter-spacing: 2.2px; fill: #6b7684; font-family: ui-monospace,"SF Mono",Menlo,Consolas,monospace; }}
  .val {{ font-size: 20px; font-weight: 700; fill: {accent}; font-family: ui-monospace,"SF Mono",Menlo,Consolas,monospace; }}
  .ttl {{ font-size: 16px; letter-spacing: 5.5px; fill: #e6edf3; font-weight: 700; font-family: ui-monospace,"SF Mono",Menlo,Consolas,monospace; }}
  .sub {{ font-size: 10px; letter-spacing: 2.4px; fill: #6b7684; font-family: ui-monospace,"SF Mono",Menlo,Consolas,monospace; }}
  .tiny {{ font-size: 8.5px; letter-spacing: 1.6px; fill: #59606b; font-family: ui-monospace,"SF Mono",Menlo,Consolas,monospace; }}
  .stage {{ font-size: 13px; letter-spacing: 3.4px; fill: {accent}; font-weight: 700; font-family: ui-monospace,"SF Mono",Menlo,Consolas,monospace; }}
  @keyframes sweep {{ to {{ stroke-dashoffset: -1500; }} }}
  @keyframes scan  {{ 0% {{ transform: translateY(-14px); }} 100% {{ transform: translateY({H + 14}px); }} }}
  @keyframes spin  {{ to {{ transform: rotate(360deg); }} }}
  @keyframes rspin {{ to {{ transform: rotate(-360deg); }} }}
  .trace {{ stroke-dasharray: 240 1260; animation: sweep 3.6s linear infinite; }}
  .scanline {{ animation: scan 6s linear infinite; }}
  .ring1 {{ transform-origin: {cx}px {cy}px; animation: spin 24s linear infinite; }}
  .ring2 {{ transform-origin: {cx}px {cy}px; animation: rspin 16s linear infinite; }}
</style>

<g clip-path="url(#chamber)">
  <rect width="{W}" height="{H}" fill="#08090c"/>
  <rect width="{W}" height="{H}" fill="url(#grid)"/>

  <!-- HEADER -->
  <text x="{PAD}" y="50" class="ttl">CONTAINMENT CHAMBER</text>
  <text x="{PAD}" y="72" class="sub">SUBJECT {login} · DESIGNATION {v['uid']}</text>
  <text x="{W - PAD}" y="50" class="stage" text-anchor="end">STAGE {stage} / {v['stage_label']}</text>
  <text x="{W - PAD}" y="72" class="tiny" text-anchor="end">LAST OBSERVATION {v['stamp']}</text>
  <line x1="{PAD}" y1="98" x2="{W - PAD}" y2="98" stroke="{accent}" stroke-width="0.6" opacity="0.20"/>

  <!-- ORGANISM -->
  <g class="ring1">
    <circle cx="{cx}" cy="{cy}" r="{r + 34}" fill="none" stroke="{accent}"
            stroke-width="0.9" stroke-dasharray="3 9" opacity="0.40"/>
  </g>
  <g class="ring2">
    <circle cx="{cx}" cy="{cy}" r="{r + 19}" fill="none" stroke="{accent}"
            stroke-width="0.7" stroke-dasharray="14 7" opacity="0.28"/>
  </g>
  {tendrils(cx, cy, r, stage + 4, decay, accent)}
  <circle cx="{cx}" cy="{cy}" r="{r + 8}" fill="url(#core)" opacity="0.28">
    <animate attributeName="r" values="{r + 8};{r + 22};{r + 8}" dur="{beat:.2f}s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="0.28;0.05;0.28" dur="{beat:.2f}s" repeatCount="indefinite"/>
  </circle>
  <circle cx="{cx}" cy="{cy}" r="{core_r:.1f}" fill="url(#core)">
    <animate attributeName="r" values="{core_r:.1f};{core_r * 1.22:.1f};{core_r:.1f}" dur="{beat:.2f}s" repeatCount="indefinite"/>
  </circle>
  <circle cx="{cx}" cy="{cy}" r="{core_r * 0.30:.1f}" fill="#08090c" opacity="0.85"/>
  <text x="{cx}" y="290" class="lbl" text-anchor="middle">STREAK / VELOCITY</text>
  <text x="{cx}" y="314" class="val" text-anchor="middle" style="font-size:16px">{v['streak']}d · {v['velocity']}/day</text>
  <line x1="272" y1="120" x2="272" y2="330" stroke="{accent}" stroke-width="0.6" opacity="0.16"/>

  <!-- VITAL TRACE -->
  <line x1="{RIGHT}" y1="196" x2="{W - PAD}" y2="196" stroke="{accent}" stroke-width="0.5" opacity="0.14"/>
  <path d="{trace}" fill="none" stroke="{accent}" stroke-width="1.9" stroke-linejoin="round" stroke-linecap="round" opacity="0.26"/>
  <path d="{trace}" fill="none" stroke="{accent}" stroke-width="2.4" stroke-linejoin="round" stroke-linecap="round" class="trace"/>
  <text x="{RIGHT}" y="132" class="tiny">CARDIAC TRACE — AMPLITUDE FALLS WITH SILENCE</text>

  {readout}

  <!-- INTEGRITY -->
  <rect x="{RIGHT}" y="330" width="{RW}" height="4" rx="2" fill="#161b22"/>
  <rect x="{RIGHT}" y="330" width="{bar_w:.1f}" height="4" rx="2" fill="{accent}">
    <animate attributeName="opacity" values="1;0.4;1" dur="{beat * 2:.2f}s" repeatCount="indefinite"/>
  </rect>

  <!-- SUBSTRATE -->
  <line x1="{PAD}" y1="362" x2="{W - PAD}" y2="362" stroke="{accent}" stroke-width="0.6" opacity="0.20"/>
  <text x="{PAD}" y="382" class="tiny">CELLULAR ACTIVITY — {v['total_year']} EVENTS ACROSS 52 WEEKS</text>
  <text x="{W - PAD}" y="382" class="tiny" text-anchor="end">{v['stars']} STARS ACCUMULATED · {v['living']} LIVING / {v['necrotic']} NECROTIC</text>
  {hm}

  {glitch}
  <rect width="{W}" height="1.5" fill="{accent}" opacity="0.14" class="scanline"/>
  <rect width="{W}" height="{H}" fill="url(#vig)"/>
  <rect width="{W}" height="{H}" rx="10" fill="none" stroke="{accent}" stroke-width="1" opacity="0.26"/>
</g>
</svg>"""
