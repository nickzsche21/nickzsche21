#!/usr/bin/env python3
"""
SPECIMEN — stimulus handler.
An issue is a stimulus. The chamber responds, records the observer
permanently, and closes the aperture.
"""
import json
import os
import re
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vitals import _req, load_state, save_state, USER  # noqa: E402
import dungeon  # noqa: E402

REPO = os.environ.get("GITHUB_REPOSITORY", "%s/%s" % (USER, USER))
EVENT = os.environ.get("GITHUB_EVENT_PATH", "")

VALID = ("north", "south", "east", "west", "descend")

def event():
    if not EVENT or not os.path.exists(EVENT):
        return None
    with open(EVENT) as f:
        return json.load(f)


def parse(issue):
    blob = "%s\n%s" % (issue.get("title", ""), issue.get("body") or "")
    m = re.search(r"command\s*=\s*([a-z]+)", blob, re.I)
    if m and m.group(1).lower() in VALID:
        return m.group(1).lower()
    for c in VALID:
        if re.search(r"\b%s\b" % c, blob, re.I):
            return c
    return None


def comment(num, body):
    _req("https://api.github.com/repos/%s/issues/%d/comments" % (REPO, num),
         {"body": body})


def close(num):
    import urllib.request, ssl
    url = "https://api.github.com/repos/%s/issues/%d" % (REPO, num)
    data = json.dumps({"state": "closed", "state_reason": "completed"}).encode()
    req = urllib.request.Request(url, data=data, method="PATCH", headers={
        "Authorization": "bearer " + (os.environ.get("GH_TOKEN")
                                      or os.environ.get("GITHUB_TOKEN") or ""),
        "Accept": "application/vnd.github+json",
        "User-Agent": "specimen-observation-rig",
    })
    try:
        urllib.request.urlopen(req, context=ssl.create_default_context(), timeout=30)
    except Exception as e:
        print("close failed: %s" % e)


def main():
    ev = event()
    if not ev or "issue" not in ev:
        print("no issue payload")
        return
    issue = ev["issue"]
    num = issue["number"]
    actor = issue.get("user", {}) or {}
    login = actor.get("login", "unknown")
    avatar = actor.get("avatar_url", "")

    cmd = parse(issue)
    if not cmd:
        comment(num, "The dungeon does not understand. Move `north`, `south`, "
                     "`east` or `west` — or `descend` to begin a new run once "
                     "the hero has fallen.")
        close(num)
        return

    st = load_state()
    st.setdefault("hall", [])
    st.setdefault("players", {})
    game = st.get("game")
    if not game:
        game = dungeon.new_run(1)
        st["game"] = game

    # a fallen hero blocks every command but the next descent
    if not game.get("alive"):
        if cmd != "descend":
            comment(num, "**The hero lies dead on floor %d.**\n\nThe run is "
                         "over — no one can move a corpse. Open a `descend` "
                         "issue to send the next one down."
                         % game["floor"])
            close(num)
            return
        st["hall"].insert(0, {
            "run": game["run"], "floor": game["floor"], "gold": game["gold"],
            "kills": game["kills"], "party": game.get("party", []),
            "turns": game["turn"],
        })
        st["hall"] = st["hall"][:12]
        game = dungeon.new_run(game["run"] + 1)
        st["game"] = game
        save_state(st)
        comment(num, "**RUN %02d BEGINS.**\n\nA new hero steps through the gate "
                     "with %d hit points. The dungeon has been regenerated — "
                     "nobody has seen this floor before.\n\nMove first and the "
                     "chronicle remembers you opened it."
                % (game["run"], game["hp"]))
        close(num)
        return

    if cmd == "descend":
        comment(num, "The hero still lives. `descend` only works over a corpse — "
                     "find the stairs and walk down them instead.")
        close(num)
        return

    before_floor = game["floor"]
    out = dungeon.step(game, cmd, login)

    rec = st["players"].setdefault(login, {"avatar": avatar, "moves": 0})
    rec["avatar"] = avatar or rec.get("avatar", "")
    rec["moves"] = rec.get("moves", 0) + 1
    save_state(st)

    body = ["**%s — turn %d**" % (cmd.upper(), game["turn"]), ""]
    if out:
        body.append("```")
        body.extend(out)
        body.append("```")
    body.append("`HP %d/%d`  ·  `%d gold`  ·  `%d slain`  ·  `floor %d`"
                % (game["hp"], game["maxhp"], game["gold"], game["kills"],
                   game["floor"]))
    if game["floor"] > before_floor:
        body.append("")
        body.append("**You took the party deeper. Floor %d is untouched.**"
                    % game["floor"])
    if not game.get("alive"):
        body.append("")
        body.append("**THE HERO IS DEAD.** Run %02d ends on floor %d with %d gold "
                    "and %d kills, across %d hands. Open a `descend` issue to "
                    "start run %02d."
                    % (game["run"], game["floor"], game["gold"], game["kills"],
                       len(game.get("party", [])), game["run"] + 1))

    comment(num, "\n".join(body) +
            "\n\n<sub>The board redraws on the profile within the minute.</sub>")
    close(num)
    print("handled %s from %s" % (cmd, login))


if __name__ == "__main__":
    main()
