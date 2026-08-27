#!/usr/bin/env python3
"""
Wake the hero, let it act, redraw the profile.
One scheduled job calls this. There is nothing to click and nothing to answer.
"""
import json
import os
import ssl
import sys
import time
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bot        # noqa: E402
import dungeon    # noqa: E402
import store      # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
USER = os.environ.get("SPECIMEN_USER", "nickzsche21")
TOKEN = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN") or ""


def top_repos(n=3):
    """A quiet footer of real work. Never fatal if the network says no."""
    url = ("https://api.github.com/users/%s/repos?per_page=100&sort=pushed"
           % USER)
    h = {"Accept": "application/vnd.github+json", "User-Agent": "descent"}
    if TOKEN:
        h["Authorization"] = "bearer " + TOKEN
    try:
        req = urllib.request.Request(url, headers=h)
        with urllib.request.urlopen(req, context=ssl.create_default_context(),
                                    timeout=20) as r:
            repos = json.loads(r.read().decode())
    except Exception as e:
        print("repo fetch skipped: %s" % e)
        return []
    repos = [r for r in repos
             if not r.get("fork") and r["name"].lower() != USER.lower()
             and (r.get("description") or r.get("stargazers_count"))]
    repos.sort(key=lambda r: -r.get("stargazers_count", 0))
    return repos[:n]


def records(st):
    hall = st.get("hall", [])
    if not hall:
        return ""
    rows = ["| RUN | REACHED | GOLD | SLAIN | TURNS |",
            "|--:|:--|--:|--:|--:|"]
    for r in hall[:8]:
        rows.append("| %02d | floor %d | %d | %d | %d |"
                    % (r["run"], r["floor"], r["gold"], r["kills"],
                       r.get("turns", 0)))
    return ("\n## RECORDS\n\nEvery hero so far, and how deep they got before "
            "the dungeon took them.\n\n" + "\n".join(rows) + "\n")


def readme(st, repos):
    g = st["game"]
    stamp = str(int(time.time()))
    deepest = st.get("deepest", 0)

    chronicle = ""
    if g.get("log"):
        chronicle = "> " + "\n> ".join(g["log"][:3]) + "\n"

    foot = " · ".join("[%s](%s)" % (r["name"], r["html_url"]) for r in repos)
    foot = ("\n<sub>Built by [%s](https://github.com/%s)%s</sub>"
            % (USER, USER, " — " + foot if foot else ""))

    deep = ""
    if deepest:
        deep = " · deepest ever **floor %d**" % deepest

    return f"""<div align="center">

<img src="assets/descent.svg?v={stamp}" alt="The Descent — run {g['run']}, floor {g['floor']}" width="100%" />

**RUN {g['run']:02d}** · floor **{g['floor']}** · **{g['hp']}/{g['maxhp']}** hp · **{g['gold']}** gold · **{g['kills']}** slain{deep}

</div>

## THE DESCENT

A hero is walking down through a dungeon that generates itself. Nobody is
driving it — it reads the floor, fights what is in the way, drinks when it is
hurt, and looks for the stairs. It wakes every three hours, takes five turns,
and the board above is redrawn from wherever it ended up.

It has never come back up. When it dies the run is sealed into the records
below and a new hero walks through the gate with a dungeon nobody has seen.

{chronicle}{records(st)}
---
{foot}
"""


def main():
    st = store.load()
    lines = bot.tick(st)
    store.save(st)

    os.makedirs(os.path.join(ROOT, "assets"), exist_ok=True)
    with open(os.path.join(ROOT, "assets", "descent.svg"), "w") as f:
        f.write(dungeon.render_svg(st["game"]))
    with open(os.path.join(ROOT, "README.md"), "w") as f:
        f.write(readme(st, top_repos()))

    g = st["game"]
    print("run %d floor %d hp %d/%d gold %d"
          % (g["run"], g["floor"], g["hp"], g["maxhp"], g["gold"]))
    for ln in lines:
        print("  " + ln)


if __name__ == "__main__":
    main()
