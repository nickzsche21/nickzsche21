#!/usr/bin/env python3
"""
THE DESCENT — the hero decides for itself.

No player, no input, no issues. A scheduled job wakes the hero every few
hours, it takes a handful of turns, and the board on the profile changes.
When it finally dies the run is sealed into the records and a fresh hero
walks through the gate. This runs unattended, forever.
"""
import sys
import os
from collections import deque

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dungeon as d  # noqa: E402

TURNS_PER_TICK = 5


def _paths(g):
    """Breadth-first flood from the hero. Returns {cell: (first_move, dist)}."""
    start = (g["x"], g["y"])
    seen = {start: (None, 0)}
    q = deque([start])
    while q:
        cur = q.popleft()
        mv0, dist = seen[cur]
        for mv, (dx, dy) in d.DIRS.items():
            nxt = (cur[0] + dx, cur[1] + dy)
            if nxt in seen or d._blocked(g, nxt[0], nxt[1]):
                continue
            seen[nxt] = (mv0 or mv, dist + 1)
            q.append(nxt)
    return seen


def _stairs(g):
    for y, row in enumerate(g["grid"]):
        if d.STAIR in row:
            return (row.index(d.STAIR), y)
    return None


def decide(g):
    """Pick one move. Fight what is in reach, heal when hurt, always descend."""
    reach = _paths(g)

    # 1. something is already breathing on us
    for m in g["monsters"]:
        if abs(m["x"] - g["x"]) + abs(m["y"] - g["y"]) == 1:
            for mv, (dx, dy) in d.DIRS.items():
                if (g["x"] + dx, g["y"] + dy) == (m["x"], m["y"]):
                    return mv, "attacking the %s" % d.KINDS[m["k"]]["name"]

    hurt = g["hp"] / float(g["maxhp"]) < 0.45

    # 2. hurt and there is medicine on this floor
    if hurt:
        best = None
        for it in g["items"]:
            if it["t"] != "potion":
                continue
            cell = reach.get((it["x"], it["y"]))
            if cell and cell[0] and (best is None or cell[1] < best[1]):
                best = (cell[0], cell[1])
        if best:
            return best[0], "wounded, going for the potion"

    # 3. loot that is genuinely on the way
    best = None
    for it in g["items"]:
        cell = reach.get((it["x"], it["y"]))
        if cell and cell[0] and cell[1] <= 7 and (best is None or cell[1] < best[1]):
            best = (cell[0], cell[1], it["t"])
    if best and not hurt:
        return best[0], "detouring for the %s" % best[2]

    # 4. weak monsters worth the gold, if close
    if not hurt:
        best = None
        for m in g["monsters"]:
            if d.KINDS[m["k"]]["hp"] > 8:
                continue
            cell = reach.get((m["x"], m["y"]))
            if cell and cell[0] and cell[1] <= 4 and (best is None or cell[1] < best[1]):
                best = (cell[0], cell[1], m["k"])
        if best:
            return best[0], "hunting the %s" % d.KINDS[best[2]]["name"]

    # 5. down
    st = _stairs(g)
    if st:
        cell = reach.get(st)
        if cell and cell[0]:
            return cell[0], "making for the stairs"

    # 6. cornered: take any opening
    for mv, (dx, dy) in d.DIRS.items():
        if not d._blocked(g, g["x"] + dx, g["y"] + dy):
            return mv, "searching"
    return "north", "trapped"


def tick(state):
    """Advance the world one scheduled wake-up. Returns log lines."""
    game = state.get("game")
    if not game:
        game = d.new_run(1)
        state["game"] = game

    lines, notable = [], []
    for _ in range(TURNS_PER_TICK):
        if not game.get("alive"):
            break
        mv, why = decide(game)
        out = d.step(game, mv, "the hero")
        for ln in out:
            if "walked into stone" in ln:
                continue
            lines.append(ln)
            if "moved" not in ln:
                notable.append(ln)

    # a chronicle of four identical footsteps is worth nobody's time
    if notable:
        game["log"] = list(reversed(notable))[:5]
    else:
        game["log"] = ["the hero pressed on — nothing stirred on floor %d"
                       % game["floor"]]

    if not game.get("alive"):
        state.setdefault("hall", []).insert(0, {
            "run": game["run"], "floor": game["floor"], "gold": game["gold"],
            "kills": game["kills"], "turns": game["turn"],
        })
        state["hall"] = state["hall"][:10]
        deepest = max((r["floor"] for r in state["hall"]), default=0)
        state["deepest"] = deepest
        lines.append("Run %02d ends. A new hero takes up the lantern."
                     % game["run"])
        state["game"] = d.new_run(game["run"] + 1)

    return lines


if __name__ == "__main__":
    import json
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..",
                     "state.json")
    st = json.load(open(p)) if os.path.exists(p) else {}
    for ln in tick(st):
        print(ln)
    json.dump(st, open(p, "w"), indent=2)
