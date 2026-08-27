#!/usr/bin/env python3
"""
A terminal that types itself, forever.

Pure SVG. Each command is revealed by a clip rectangle that widens one
character at a time (calcMode="discrete", so it steps rather than slides —
that is what makes it read as typing rather than a wipe). Text is forced to
an exact advance with textLength, so the clip math lands on glyph boundaries.
No JavaScript, no recording, nothing to schedule.
"""
import os

CW = 8.62          # character advance at 14.5px monospace
LH = 25            # line height
PAD_X, TOP = 30, 62
FS = 14.5

BG, BAR, EDGE = "#0B0E14", "#141A24", "#222B39"
GREEN, WHITE, GREY = "#7EE787", "#E6EDF3", "#7D8792"
CYAN, GOLD, VIOLET = "#79C0FF", "#F2CC60", "#D2A8FF"
AMBER, RED, DIM = "#E3A008", "#F8514A", "#4A525C"

# (kind, text, colour, flicker, hold-after)
SCRIPT = [
    ("cmd", "whoami", WHITE, 0, 0.40),
    ("out", "nikhil", GREY, 0, 0.30),
    ("gap", "", None, 0, 0),
    ("cmd", "who", WHITE, 0, 0.45),
    ("out", "nikhil    console    since tuesday", GREY, 0, 0.34),
    ("out", "?         ttys001    since ????", AMBER, 1, 1.30),
    ("gap", "", None, 0, 0),
    ("cmd", "kill -9 ?", WHITE, 0, 0.70),
    ("out", "kill: ?: no such process", GREY, 0, 1.05),
    ("gap", "", None, 0, 0),
    ("cmd", "ls /dev/thoughts", WHITE, 0, 0.45),
    ("out", "racing   looping   3am", VIOLET, 0, 1.10),
    ("gap", "", None, 0, 0),
    ("cmd", "exit", WHITE, 0, 0.95),
    ("out", "exit: you don't get to.", RED, 1, 3.00),
]

TYPE = 0.052       # seconds per character
HOLD_CMD = 0.42    # pause after a command lands
HOLD_OUT = 0.30
TAIL = 1.4         # blinking prompt before the screen clears


def build():
    t = 0.4
    events = []
    for kind, text, col, flick, hold in SCRIPT:
        if kind == "gap":
            t += 0.18
            events.append((kind, text, col, t, 0.0, flick))
            continue
        dur = len(text) * TYPE if kind == "cmd" else 0.0
        events.append((kind, text, col, t, dur, flick))
        t += dur + hold
    total = t + TAIL
    return events, total


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def render():
    events, total = build()
    rows = len(events)
    # size the window to its longest line instead of leaving dead space
    widest = max((len(t) + (2 if k == "cmd" else 0)) for k, t, _c, _s, _d, _f in events)
    # a terminal that is taller than it is wide reads as a phone, not a shell
    W = max(600, int(PAD_X * 2 + widest * CW + 18))
    H = TOP + rows * LH + 34

    body, clips = [], []
    y = TOP
    for i, (kind, text, col, start, dur, flick) in enumerate(events):
        if kind == "gap":
            y += LH
            continue

        s = start / total
        clear = (total - 0.34) / total
        px = PAD_X
        if kind == "cmd":
            px = PAD_X + 2 * CW
            body.append(
                '<g opacity="0"><animate attributeName="opacity" '
                'values="0;1;1;0;0" keyTimes="0;%.4f;%.4f;%.4f;1" dur="%.2fs" '
                'repeatCount="indefinite" calcMode="discrete"/>'
                '<text x="%.1f" y="%d" class="m" fill="%s">$</text></g>'
                % (s, clear, clear, total, PAD_X, y, GREEN))

        n = max(1, len(text))
        full = n * CW
        if kind == "cmd":
            kt = [0.0, s] + [(start + dur * k / n) / total for k in range(1, n + 1)]
            vs = [0.0, 0.0] + [k * CW for k in range(1, n + 1)]
            kt.append(1.0)
            vs.append(full)
            clips.append(
                '<clipPath id="c%d"><rect x="%.1f" y="%d" width="0" height="%d">'
                '<animate attributeName="width" values="%s" keyTimes="%s" '
                'dur="%.2fs" repeatCount="indefinite" calcMode="discrete"/>'
                '</rect></clipPath>'
                % (i, px, y - LH + 6, LH,
                   ";".join("%.1f" % v for v in vs),
                   ";".join("%.4f" % k for k in kt), total))
            body.append(
                '<g clip-path="url(#c%d)" opacity="0">'
                '<animate attributeName="opacity" values="0;1;1;0;0" '
                'keyTimes="0;%.4f;%.4f;%.4f;1" dur="%.2fs" repeatCount="indefinite" '
                'calcMode="discrete"/>'
                '<text x="%.1f" y="%d" class="m" fill="%s" textLength="%.1f" '
                'lengthAdjust="spacing">%s</text></g>'
                % (i, s, clear, clear, total, px, y, col, full, esc(text)))
            # the caret rides the clip edge
            ckt = [0.0, s] + [(start + dur * k / n) / total for k in range(1, n + 1)]
            cvs = [px, px] + [px + k * CW for k in range(1, n + 1)]
            ckt.append(1.0)
            cvs.append(px + full)
            body.append(
                '<rect y="%d" width="%.1f" height="16" fill="%s" opacity="0">'
                '<animate attributeName="x" values="%s" keyTimes="%s" dur="%.2fs" '
                'repeatCount="indefinite" calcMode="discrete"/>'
                '<animate attributeName="opacity" values="0;0.9;0;0" '
                'keyTimes="0;%.4f;%.4f;1" dur="%.2fs" repeatCount="indefinite" '
                'calcMode="discrete"/></rect>'
                % (y - 12, CW, WHITE,
                   ";".join("%.1f" % v for v in cvs),
                   ";".join("%.4f" % k for k in ckt), total,
                   s, (start + dur) / total, total))
        else:
            inner = ('<text x="%.1f" y="%d" class="m" fill="%s" textLength="%.1f" '
                     'lengthAdjust="spacing">%s</text>'
                     % (px, y, col, full, esc(text)))
            if flick:
                inner = ('<g>%s<animate attributeName="opacity" '
                         'values="1;0.15;1;0.55;1;1;0.3;1" dur="2.7s" '
                         'repeatCount="indefinite" calcMode="discrete"/></g>'
                         % inner)
            body.append(
                '<g opacity="0"><animate attributeName="opacity" '
                'values="0;1;1;0;0" keyTimes="0;%.4f;%.4f;%.4f;1" dur="%.2fs" '
                'repeatCount="indefinite" calcMode="discrete"/>%s</g>'
                % (s, clear, clear, total, inner))
        y += LH

    tail = ""

    dots = "".join('<circle cx="%d" cy="21" r="5.5" fill="%s"/>' % (x, c)
                   for x, c in ((26, "#FF5F57"), (46, "#FEBC2E"), (66, "#28C840")))

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="A terminal typing itself">
<defs>{"".join(clips)}</defs>
<style>
  .m {{ font-family: ui-monospace,'SF Mono',SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace;
        font-size: {FS}px; letter-spacing: 0; white-space: pre; }}
  .t {{ font-family: ui-monospace,'SF Mono',Menlo,Consolas,monospace;
        font-size: 11.5px; letter-spacing: 1.6px; fill: #6B7480; }}
</style>
<rect width="{W}" height="{H}" rx="10" fill="{BG}"/>
<path d="M0,10 a10,10 0 0 1 10,-10 h{W - 20} a10,10 0 0 1 10,10 v32 h-{W} Z" fill="{BAR}"/>
<line x1="0" y1="42" x2="{W}" y2="42" stroke="{EDGE}" stroke-width="1"/>
{dots}
<text x="{W / 2}" y="26" class="t" text-anchor="middle">nikhil@bangalore — zsh</text>
{"".join(body)}
{tail}
<rect width="{W}" height="{H}" rx="10" fill="none" stroke="{EDGE}" stroke-width="1"/>
</svg>'''


if __name__ == "__main__":
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    p = os.path.join(root, "assets", "term.svg")
    with open(p, "w") as f:
        f.write(render())
    ev, tot = build()
    print("wrote %s (%d KB) — loop %.1fs" % (p, os.path.getsize(p) // 1024, tot))
