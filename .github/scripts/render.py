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
import dungeon  # noqa: E402

STYLE = os.environ.get("SPECIMEN_STYLE", "game")

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


def hall_block(st):
    hall = (st or {}).get("hall", [])
    if not hall:
        return ""
    rows = ["| RUN | DEPTH | GOLD | SLAIN | TURNS | HANDS ON THE BLADE |",
            "|--:|--:|--:|--:|--:|:--|"]
    for r in hall[:8]:
        who = r.get("party", [])
        names = ", ".join("@%s" % w for w in who[:5])
        if len(who) > 5:
            names += " +%d" % (len(who) - 5)
        rows.append("| %02d | %d | %d | %d | %d | %s |"
                    % (r["run"], r["floor"], r["gold"], r["kills"],
                       r.get("turns", 0), names or "—"))
    return "\n### HALL OF RECORDS\n\n" + "\n".join(rows) + "\n"


def party_block(st):
    game = (st or {}).get("game", {}) or {}
    players = (st or {}).get("players", {})
    party = game.get("party", [])
    if not party:
        return ""
    faces = []
    for who in party[:20]:
        av = players.get(who, {}).get("avatar", "")
        if av:
            faces.append('<a href="https://github.com/%s" title="%s — %d move(s)">'
                         '<img src="%s&s=48" width="34" height="34" alt="%s"/></a>'
                         % (who, who, players.get(who, {}).get("moves", 1), av, who))
    if not faces:
        return ""
    return "\n<div align=\"center\">\n\n%s\n\n<sub>hands on the blade this run</sub>\n\n</div>\n" % "".join(faces)


def render_readme(v, st):
    repo = "%s/%s" % (USER, USER)
    stamp = str(int(time.time()))
    game = st.get("game", {}) or {}
    alive = game.get("alive", True)

    def mv(slug, label):
        return "[%s](%s)" % (label, issue_link(
            repo, slug, "descent: %s" % slug, "command=%s" % slug))

    if alive:
        controls = ("| %s | %s | %s | %s |\n|:--:|:--:|:--:|:--:|\n"
                    "| move up | move down | move left | move right |"
                    % (mv("north", "**NORTH**"), mv("south", "**SOUTH**"),
                       mv("west", "**WEST**"), mv("east", "**EAST**")))
        state_line = ("**HP %d/%d** · **%d gold** · **%d slain** · **floor %d** · turn %d"
                      % (game.get("hp", 0), game.get("maxhp", 0), game.get("gold", 0),
                         game.get("kills", 0), game.get("floor", 1), game.get("turn", 0)))
    else:
        controls = "### %s\n\nThe hero is dead. Send the next one down." % mv(
            "descend", "**BEGIN RUN %02d**" % (game.get("run", 1) + 1))
        state_line = "**THE HERO FELL ON FLOOR %d** — run %02d is over." % (
            game.get("floor", 1), game.get("run", 1))

    chron = ""
    if game.get("log"):
        chron = "\n> " + "\n> ".join(game["log"][:3]) + "\n"

    return f"""<div align="center">

<img src="assets/descent.svg?v={stamp}" alt="The Descent — run {game.get('run', 1)}, floor {game.get('floor', 1)}" width="100%" />

{state_line}

</div>

## TAKE THE NEXT TURN

One hero. One dungeon. **Everyone plays the same run.** Click a direction — it
opens a pre-filled issue, a machine moves the hero, fights whatever is standing
there, and redraws the board above. Walk into a monster to attack it. Find the
stairs to go deeper. When the hero dies, the run is over for everybody and the
dungeon regenerates.

{controls}
{chron}{party_block(st)}{hall_block(st)}
---

<sub>Built by [{USER}](https://github.com/{USER}) — {", ".join("[%s](%s)" % (o["name"], o["url"]) for o in [o for o in v["organs"] if o["name"].lower() != USER.lower() and (o["desc"] or o["stars"])][:3])}</sub>
"""


def main():
    st = load_state()
    v = derive(fetch(), st)
    # nutrients evaporate one unit per observation cycle
    if int(st.get("nutrients", 0)) > 0:
        st["nutrients"] = int(st["nutrients"]) - 1
        save_state(st)
    os.makedirs(os.path.join(ROOT, "assets"), exist_ok=True)
    if STYLE == "game":
        if not st.get("game"):
            st["game"] = dungeon.new_run(1)
            save_state(st)
        svg, name = dungeon.render_svg(st["game"]), "descent.svg"
    elif STYLE == "letterhead":
        svg, name = letterhead.render(v), "card.svg"
    else:
        svg, name = chamber.render(v), "specimen.svg"
    with open(os.path.join(ROOT, "assets", name), "w") as f:
        f.write(svg)

    readme_path = os.path.join(ROOT, "README.md")
    with open(readme_path, "w") as f:
        f.write(render_readme(v, st))
    print("rendered :: stage=%d decay=%d bpm=%d silence=%dd"
          % (v["stage"], v["decay"], v["bpm"], v["silence"]))


if __name__ == "__main__":
    main()
