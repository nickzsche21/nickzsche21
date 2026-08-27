#!/usr/bin/env python3
"""
SPECIMEN — observation report renderer.
Writes assets/specimen.svg and README.md from live telemetry.
"""
import os
import random
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vitals import fetch, derive, USER, load_state, save_state  # noqa: E402
import chamber  # noqa: E402
import letterhead  # noqa: E402

STYLE = os.environ.get("SPECIMEN_STYLE", "letterhead")

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

GLITCH = "▓▒░█▄▀╳╱╲┼╬※#@%&"

# Three morphologies. Corruption is applied on top, driven by real decay.
FORM_HEALTHY = r"""
              \    |    /
               \   |   /
          ╭─────────────────╮
      ────┤   ◜  (( ● ))  ◝   ├────
          ╰─────────────────╯
               /   |   \
              /    |    \
"""

FORM_FADING = r"""
               '   |   ,
                \  |  /
          ╭─────────────────╮
      ─ ──┤   ·   ( ◉ )   ·   ├── ─
          ╰─────────────────╯
                /  |  \
               ,   |   '
"""

FORM_DEAD = r"""
                   .
          ╭─────────────────╮
       ·  ┆       ( ○ )       ┆  ·
          ╰─ ─ ─ ─ ─ ─ ─ ─ ─╯
                   .
"""


def corrupt(art, decay, seed):
    """Eat the organism in proportion to real silence."""
    if decay < 20:
        return art
    rnd = random.Random(seed)
    rate = (decay - 20) / 100.0 * 0.34
    out = []
    for ch in art:
        if ch not in " \n" and rnd.random() < rate:
            out.append(rnd.choice(GLITCH))
        else:
            out.append(ch)
    return "".join(out)


def organism(v):
    if v["stage"] >= 4:
        art = FORM_HEALTHY
    elif v["stage"] >= 2:
        art = FORM_FADING
    else:
        art = FORM_DEAD
    return corrupt(art, v["decay"], v["decay"] * 7 + v["stage"]).rstrip("\n")


def bar(pct, width=28, full="█", empty="░"):
    n = int(round(width * pct / 100.0))
    return full * n + empty * (width - n)


def sparkline(days, n=30):
    ramp = "▁▁▂▃▄▅▆▇█"
    tail = [c for _, c in days[-n:]]
    if not tail:
        return ""
    peak = max(tail) or 1
    return "".join(ramp[min(8, int(round(c / peak * 8)))] for c in tail)


def issue_link(repo, cmd, title, body):
    import urllib.parse

    q = urllib.parse.urlencode({"title": title, "body": body})
    return "https://github.com/%s/issues/new?%s" % (repo, q)


def observer_block(st):
    log = (st or {}).get("log", [])
    obs = (st or {}).get("observers", {})
    if not log:
        return ("> **THE LOG IS EMPTY.** No one has touched the chamber yet.\n>\n"
                "> The first observer gets the first line, permanently.")

    faces = []
    seen = []
    for e in log:
        if e["who"] not in seen:
            seen.append(e["who"])
    for who in seen[:18]:
        av = obs.get(who, {}).get("avatar", "")
        if av:
            faces.append(
                '<a href="https://github.com/%s" title="%s — %d stimulus(es)">'
                '<img src="%s&s=52" width="42" height="42" alt="%s" /></a>'
                % (who, who, obs.get(who, {}).get("n", 1), av, who))
    face_row = "".join(faces)

    rows = []
    for e in log[:10]:
        rows.append("| `%s` | **%s** | [@%s](https://github.com/%s) |"
                    % (e["ts"], e["cmd"].upper(), e["who"], e["who"]))

    hostile = sorted(
        [(w, d.get("provokes", 0)) for w, d in obs.items() if d.get("provokes", 0)],
        key=lambda x: -x[1])[:5]
    hostile_line = ""
    if hostile:
        hostile_line = "\n**HOSTILE OBSERVERS.** " + ", ".join(
            "[@%s](https://github.com/%s) ×%d" % (w, w, n) for w, n in hostile) + "\n"

    return f"""<div align="center">

{face_row}

**{len(obs)} observer(s) on record · {len(log)} logged stimulus(es) · {st.get('nutrients', 0)} nutrient unit(s) in reserve**

</div>
{hostile_line}
| WHEN | STIMULUS | OBSERVER |
|:--|:--|:--|
{chr(10).join(rows)}
"""


def render_readme(v, st):
    stamp = str(int(time.time()))
    login = v["user"].get("login", USER)
    pool = [o for o in v["organs"] if o["name"].lower() != login.lower()]
    named = [o for o in pool if o["desc"] or o["stars"]][:3] or pool[:3]
    links = " · ".join("[%s](%s)" % (o["name"], o["url"]) for o in named)

    return f"""<div align="center">

<img src="assets/card.svg?v={stamp}" alt="{v['user'].get('name', login)} — statement of record" width="100%" />

<sub>{links}</sub>

</div>
"""


def main():
    st = load_state()
    v = derive(fetch(), st)
    # nutrients evaporate one unit per observation cycle
    if int(st.get("nutrients", 0)) > 0:
        st["nutrients"] = int(st["nutrients"]) - 1
        save_state(st)
    os.makedirs(os.path.join(ROOT, "assets"), exist_ok=True)
    art = letterhead if STYLE == "letterhead" else chamber
    name = "card.svg" if STYLE == "letterhead" else "specimen.svg"
    with open(os.path.join(ROOT, "assets", name), "w") as f:
        f.write(art.render(v))

    readme_path = os.path.join(ROOT, "README.md")
    with open(readme_path, "w") as f:
        f.write(render_readme(v, st))
    print("rendered :: stage=%d decay=%d bpm=%d silence=%dd"
          % (v["stage"], v["decay"], v["bpm"], v["silence"]))


if __name__ == "__main__":
    main()
