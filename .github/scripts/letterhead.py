#!/usr/bin/env python3
"""
Letterhead — the restrained rendering.
A statement of record, not a dashboard. Swiss grid, warm neutrals, one
metallic accent, and a single hairline that draws itself once on open.
Everything is still. The numbers are stated, not celebrated.
"""

BG = "#0A0A0B"
RULE = "#23221F"
PRIMARY = "#EDEAE4"
SECOND = "#A29B90"
MUTED = "#57534D"
BRASS = "#B08D57"

SERIF = "Georgia,'Times New Roman',Times,serif"
SANS = "'Helvetica Neue',Helvetica,Arial,sans-serif"

MONTHS = ("JANUARY", "FEBRUARY", "MARCH", "APRIL", "MAY", "JUNE", "JULY",
          "AUGUST", "SEPTEMBER", "OCTOBER", "NOVEMBER", "DECEMBER")


def _long_date(now):
    return "%d %s %d" % (now.day, MONTHS[now.month - 1], now.year)


def _thin(n):
    """Hair space between thousands reads quieter than a comma."""
    s = str(n)
    if len(s) <= 3:
        return s
    out = []
    while len(s) > 3:
        out.insert(0, s[-3:])
        s = s[:-3]
    out.insert(0, s)
    return " ".join(out)


def render(v):
    W, H = 1000, 480
    L, R = 64, 936          # content margins
    MID = 560               # right column origin

    user = v.get("user", {}) or {}
    login = user.get("login", "")
    display = (user.get("name") or login).strip() or login

    pool = [o for o in v["organs"] if o["name"].lower() != login.lower()]
    named = [o for o in pool if o["desc"] or o["stars"]]
    picks = (named or pool)[:3]

    work = []
    y = 302
    for i, o in enumerate(picks):
        work.append(
            '<text x="%d" y="%d" class="idx">%02d</text>'
            '<text x="%d" y="%d" class="work">%s</text>'
            '<text x="%d" y="%d" class="year">%s</text>'
            % (L, y, i + 1, L + 40, y, o["name"], 480, y, o.get("year", ""))
        )
        if i < len(picks) - 1:
            work.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" '
                        'stroke-width="1"/>' % (L, y + 18, 480, y + 18, RULE))
        y += 46
    work = "".join(work)

    figures = [
        ("REPOSITORIES", str(user.get("public_repos", len(v["organs"])))),
        ("STARS", _thin(v["stars"])),
        ("CONTRIBUTIONS", _thin(v["total_year"])),
    ]
    figs = []
    y = 302
    for i, (k, val) in enumerate(figures):
        figs.append(
            '<text x="%d" y="%d" class="fkey">%s</text>'
            '<text x="%d" y="%d" class="fval">%s</text>' % (MID, y, k, R, y, val)
        )
        if i < len(figures) - 1:
            figs.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" '
                        'stroke-width="1"/>' % (MID, y + 18, R, y + 18, RULE))
        y += 46
    figs = "".join(figs)

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{display} — statement of record">
<style>
  text {{ fill: {PRIMARY}; }}
  .name  {{ font-family: {SERIF}; font-size: 44px; letter-spacing: 7px; fill: {PRIMARY}; }}
  .meta  {{ font-family: {SANS}; font-size: 9px; letter-spacing: 3.4px; fill: {MUTED}; }}
  .lede  {{ font-family: {SERIF}; font-size: 19px; letter-spacing: 0.2px; fill: {SECOND}; }}
  .eyebrow {{ font-family: {SANS}; font-size: 9px; letter-spacing: 3.4px; fill: {MUTED}; }}
  .idx   {{ font-family: {SANS}; font-size: 10px; letter-spacing: 1.5px; fill: {BRASS}; }}
  .work  {{ font-family: {SERIF}; font-size: 19px; letter-spacing: 0.3px; fill: {PRIMARY}; }}
  .year  {{ font-family: {SANS}; font-size: 10px; letter-spacing: 2px; fill: {MUTED}; text-anchor: end; }}
  .fkey  {{ font-family: {SANS}; font-size: 10px; letter-spacing: 2.6px; fill: {SECOND}; }}
  .fval  {{ font-family: {SERIF}; font-size: 22px; fill: {PRIMARY}; text-anchor: end; }}
  .foot  {{ font-family: {SANS}; font-size: 9px; letter-spacing: 3px; fill: {MUTED}; }}
  @keyframes draw {{ to {{ stroke-dashoffset: 0; }} }}
  .accent {{ stroke-dasharray: 96; stroke-dashoffset: 96;
             animation: draw 1.3s cubic-bezier(.22,.61,.36,1) .25s forwards; }}
</style>

<rect width="{W}" height="{H}" fill="{BG}"/>

<!-- MASTHEAD -->
<text x="{L}" y="96" class="name">{display.upper()}</text>
<text x="{R}" y="78" class="meta" text-anchor="end">INDEPENDENT</text>
<text x="{R}" y="98" class="meta" text-anchor="end">BANGALORE · INDIA</text>
<line x1="{L}" y1="120" x2="{L + 96}" y2="120" stroke="{BRASS}" stroke-width="1.4" class="accent"/>

<!-- POSITION -->
<text x="{L}" y="166" class="lede">Builds systems that survive contact with</text>
<text x="{L}" y="194" class="lede">real institutions.</text>

<line x1="{L}" y1="238" x2="{R}" y2="238" stroke="{RULE}" stroke-width="1"/>

<!-- COLUMNS -->
<text x="{L}" y="266" class="eyebrow">SELECTED WORK</text>
<text x="{MID}" y="266" class="eyebrow">RECORD</text>
{work}
{figs}

<line x1="{L}" y1="432" x2="{R}" y2="432" stroke="{RULE}" stroke-width="1"/>
<text x="{L}" y="456" class="foot">LAST ACTIVITY — {_long_date(v['now'])}</text>
<text x="{R}" y="456" class="foot" text-anchor="end">GITHUB.COM/{login.upper()}</text>
</svg>'''
