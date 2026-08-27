#!/usr/bin/env python3
"""
THE DESCENT — a roguelike played by everyone at once.

One hero. One dungeon. Shared hit points. Anyone on GitHub may take the
next turn, and the consequences are permanent for every player after them.
Generation and combat are seeded, so any run can be replayed and audited.
"""
import random

W, H = 25, 13
WALL, FLOOR, STAIR = "#", ".", ">"

KINDS = {
    "rat":    {"g": "r", "hp": 3,  "dmg": 1, "gold": 2,  "name": "sewer rat"},
    "goblin": {"g": "g", "hp": 6,  "dmg": 2, "gold": 5,  "name": "goblin"},
    "orc":    {"g": "o", "hp": 10, "dmg": 3, "gold": 11, "name": "orc"},
    "wraith": {"g": "w", "hp": 15, "dmg": 5, "gold": 24, "name": "wraith"},
}
LADDER = ["rat", "goblin", "orc", "wraith"]

DIRS = {"north": (0, -1), "south": (0, 1), "west": (-1, 0), "east": (1, 0)}


# ---------------------------------------------------------------- generation
def _rooms(rnd):
    rooms = []
    for _ in range(60):
        if len(rooms) >= 5:
            break
        rw, rh = rnd.randint(4, 6), rnd.randint(3, 4)
        rx, ry = rnd.randint(1, W - rw - 2), rnd.randint(1, H - rh - 2)
        box = (rx, ry, rw, rh)
        if any(not (rx + rw + 1 < o[0] or o[0] + o[2] + 1 < rx or
                    ry + rh + 1 < o[1] or o[1] + o[3] + 1 < ry) for o in rooms):
            continue
        rooms.append(box)
    return rooms


def _centre(r):
    return (r[0] + r[2] // 2, r[1] + r[3] // 2)


def generate(run, floor):
    # keep reseeding until the cave is worth entering
    rooms, rnd, salt = [], None, 0
    while len(rooms) < 4 and salt < 40:
        rnd = random.Random(run * 977 + floor * 31 + salt * 7)
        rooms = _rooms(rnd)
        salt += 1
    grid = [[WALL] * W for _ in range(H)]

    for (rx, ry, rw, rh) in rooms:
        for y in range(ry, ry + rh):
            for x in range(rx, rx + rw):
                grid[y][x] = FLOOR

    for a, b in zip(rooms, rooms[1:]):
        (x1, y1), (x2, y2) = _centre(a), _centre(b)
        for x in range(min(x1, x2), max(x1, x2) + 1):
            grid[y1][x] = FLOOR
        for y in range(min(y1, y2), max(y1, y2) + 1):
            grid[y][x2] = FLOOR

    hx, hy = _centre(rooms[0])
    sx, sy = _centre(rooms[-1])
    grid[sy][sx] = STAIR

    # inhabitants scale with depth
    tier = min(3, floor // 3)
    monsters = []
    for r in rooms[1:]:
        for _ in range(rnd.randint(1, 2)):
            k = LADDER[max(0, min(3, rnd.randint(max(0, tier - 1), tier)))]
            mx = rnd.randint(r[0], r[0] + r[2] - 1)
            my = rnd.randint(r[1], r[1] + r[3] - 1)
            if (mx, my) in ((hx, hy), (sx, sy)):
                continue
            monsters.append({"k": k, "x": mx, "y": my, "hp": KINDS[k]["hp"]})

    items = []
    for r in rooms[1:]:
        if rnd.random() < 0.55:
            items.append({"t": "gold", "x": rnd.randint(r[0], r[0] + r[2] - 1),
                          "y": rnd.randint(r[1], r[1] + r[3] - 1),
                          "v": rnd.randint(3, 12)})
        if rnd.random() < 0.32:
            items.append({"t": "potion", "x": rnd.randint(r[0], r[0] + r[2] - 1),
                          "y": rnd.randint(r[1], r[1] + r[3] - 1), "v": 6})

    return {"grid": ["".join(row) for row in grid], "hx": hx, "hy": hy,
            "monsters": monsters, "items": items}


def new_run(run_id):
    lvl = generate(run_id, 1)
    return {
        "run": run_id, "floor": 1, "turn": 0,
        "hp": 22, "maxhp": 22, "gold": 0, "kills": 0,
        "x": lvl["hx"], "y": lvl["hy"],
        "grid": lvl["grid"], "monsters": lvl["monsters"], "items": lvl["items"],
        "alive": True, "log": ["The gate closes behind you."], "party": [],
    }


# ------------------------------------------------------------------ movement
def _blocked(st, x, y):
    if x < 0 or y < 0 or x >= W or y >= H:
        return True
    return st["grid"][y][x] == WALL


def _monster_at(st, x, y):
    for m in st["monsters"]:
        if m["x"] == x and m["y"] == y:
            return m
    return None


def step(st, direction, who):
    """Advance the world by one turn. Returns a list of log lines."""
    if not st.get("alive"):
        return ["The hero is dead. The next run awaits."]

    dx, dy = DIRS[direction]
    nx, ny = st["x"] + dx, st["y"] + dy
    rnd = random.Random(st["run"] * 7919 + st["turn"] * 131 + st["floor"])
    out = []
    st["turn"] += 1
    if who and who not in st.get("party", []):
        st.setdefault("party", []).append(who)

    target = _monster_at(st, nx, ny)
    if target:
        k = KINDS[target["k"]]
        dmg = rnd.randint(2, 5) + st["floor"] // 4
        target["hp"] -= dmg
        if target["hp"] <= 0:
            st["monsters"].remove(target)
            st["gold"] += k["gold"]
            st["kills"] += 1
            out.append("%s cut down the %s (+%dg)" % (who, k["name"], k["gold"]))
        else:
            out.append("%s struck the %s for %d" % (who, k["name"], dmg))
    elif _blocked(st, nx, ny):
        # bumping stone is a misread, not a move: no turn passes, nothing bites
        st["turn"] -= 1
        return ["%s walked into stone — the dungeon does not charge for that" % who]
    else:
        st["x"], st["y"] = nx, ny
        for it in list(st["items"]):
            if it["x"] == nx and it["y"] == ny:
                st["items"].remove(it)
                if it["t"] == "gold":
                    st["gold"] += it["v"]
                    out.append("%s found %d gold" % (who, it["v"]))
                else:
                    st["hp"] = min(st["maxhp"], st["hp"] + it["v"])
                    out.append("%s drank a potion (+%d hp)" % (who, it["v"]))

        if not out:
            out.append("%s moved %s" % (who, direction))

        if st["grid"][ny][nx] == STAIR:
            st["floor"] += 1
            lvl = generate(st["run"], st["floor"])
            st.update({"grid": lvl["grid"], "monsters": lvl["monsters"],
                       "items": lvl["items"], "x": lvl["hx"], "y": lvl["hy"]})
            st["maxhp"] += 2
            st["hp"] = min(st["maxhp"], st["hp"] + 4)
            out.append("%s descended to floor %d" % (who, st["floor"]))
            st["log"] = (out + st.get("log", []))[:6]
            return out

    # the dungeon answers
    for m in st["monsters"]:
        k = KINDS[m["k"]]
        d = abs(m["x"] - st["x"]) + abs(m["y"] - st["y"])
        if d == 1:
            st["hp"] -= k["dmg"]
            out.append("the %s bit back for %d" % (k["name"], k["dmg"]))
        elif d <= 6:
            sx = 1 if st["x"] > m["x"] else (-1 if st["x"] < m["x"] else 0)
            sy = 1 if st["y"] > m["y"] else (-1 if st["y"] < m["y"] else 0)
            if sx and not _blocked(st, m["x"] + sx, m["y"]) \
                    and not _monster_at(st, m["x"] + sx, m["y"]):
                m["x"] += sx
            elif sy and not _blocked(st, m["x"], m["y"] + sy) \
                    and not _monster_at(st, m["x"], m["y"] + sy):
                m["y"] += sy

    if st["hp"] <= 0:
        st["hp"] = 0
        st["alive"] = False
        out.append("THE HERO FELL ON FLOOR %d" % st["floor"])

    st["log"] = (out + st.get("log", []))[:6]
    return out


# ------------------------------------------------------------------ rendering
BG, WALLC, WALLTOP = "#08080A", "#252530", "#363646"
FLOORC, DOT = "#0B0B0E", "#26262F"
BRASS, RULE, PRIMARY, MUTED = "#E8C07D", "#23222A", "#EDEAE4", "#6B6660"
TINT = {"rat": "#8A857B", "goblin": "#7FA650", "orc": "#C4703A", "wraith": "#A05BC4"}
GOLDC, POTC, BLOOD = "#D4A24C", "#4FA88B", "#C4453A"

SANS = "'Helvetica Neue',Helvetica,Arial,sans-serif"
SERIF = "Georgia,'Times New Roman',Times,serif"
MONO = "ui-monospace,'SF Mono',Menlo,Consolas,monospace"

TILE = 32
OX, OY = 50, 108


def _t(x, y):
    return OX + x * TILE, OY + y * TILE


def render_svg(st):
    W_ = 900
    H_ = OY + H * TILE + 96
    alive = st.get("alive", True)
    hpr = max(0.0, st["hp"] / float(st["maxhp"]))
    hpc = BRASS if hpr > 0.5 else ("#D8A03A" if hpr > 0.25 else BLOOD)

    p = []
    # ---- terrain
    for y in range(H):
        for x in range(W):
            px, py = _t(x, y)
            c = st["grid"][y][x]
            if c == WALL:
                p.append('<rect x="%d" y="%d" width="%d" height="%d" fill="%s"/>'
                         % (px, py, TILE, TILE, WALLC))
                p.append('<rect x="%d" y="%d" width="%d" height="3" fill="%s" opacity="0.85"/>'
                         % (px, py, TILE, WALLTOP))
            else:
                p.append('<rect x="%d" y="%d" width="%d" height="%d" fill="%s"/>'
                         % (px, py, TILE, TILE, FLOORC))
                p.append('<circle cx="%d" cy="%d" r="1.4" fill="%s"/>'
                         % (px + TILE // 2, py + TILE // 2, DOT))
            if c == STAIR:
                p.append('<rect x="%d" y="%d" width="%d" height="%d" fill="%s" opacity="0.14"/>'
                         % (px, py, TILE, TILE, BRASS))
                p.append('<text x="%d" y="%d" class="stair" fill="%s" '
                         'text-anchor="middle">&#8615;</text>'
                         % (px + TILE // 2, py + TILE - 8, BRASS))

    # ---- loot
    for it in st["items"]:
        px, py = _t(it["x"], it["y"])
        cx, cy = px + TILE // 2, py + TILE // 2
        if it["t"] == "gold":
            p.append('<circle cx="%d" cy="%d" r="4.5" fill="%s" opacity="0.9"/>'
                     % (cx, cy, GOLDC))
        else:
            p.append('<rect x="%d" y="%d" width="8" height="11" rx="2" fill="%s"/>'
                     % (cx - 4, cy - 5, POTC))

    # ---- inhabitants
    for m in st["monsters"]:
        px, py = _t(m["x"], m["y"])
        col = TINT[m["k"]]
        p.append('<rect x="%d" y="%d" width="22" height="22" rx="5" fill="%s" opacity="0.16"/>'
                 % (px + 5, py + 5, col))
        p.append('<text x="%d" y="%d" class="mob" fill="%s" text-anchor="middle">%s</text>'
                 % (px + TILE // 2, py + TILE - 10, col, KINDS[m["k"]]["g"]))

    # ---- the hero
    hx, hy = _t(st["x"], st["y"])
    if alive:
        p.append('<circle cx="%d" cy="%d" r="15" fill="%s" opacity="0.13">'
                 '<animate attributeName="r" values="13;18;13" dur="2.6s" '
                 'repeatCount="indefinite"/></circle>'
                 % (hx + TILE // 2, hy + TILE // 2, BRASS))
    p.append('<circle cx="%d" cy="%d" r="10" fill="%s"/>'
             % (hx + TILE // 2, hy + TILE // 2, BRASS if alive else BLOOD))
    p.append('<text x="%d" y="%d" class="hero" text-anchor="middle">%s</text>'
             % (hx + TILE // 2, hy + TILE - 10, "@" if alive else "&#215;"))

    # ---- head-up display
    hud = []
    hud.append('<text x="%d" y="46" class="ttl">THE DESCENT</text>' % OX)
    hud.append('<text x="%d" y="46" class="run" text-anchor="end">RUN %02d '
               '&#183; FLOOR %d &#183; TURN %d</text>'
               % (W_ - OX, st["run"], st["floor"], st["turn"]))
    hud.append('<text x="%d" y="76" class="key">HP</text>' % OX)
    hud.append('<rect x="%d" y="66" width="180" height="6" rx="3" fill="#1A1A20"/>' % (OX + 30))
    hud.append('<rect x="%d" y="66" width="%.0f" height="6" rx="3" fill="%s"/>'
               % (OX + 30, 180 * hpr, hpc))
    hud.append('<text x="%d" y="76" class="val">%d/%d</text>' % (OX + 222, st["hp"], st["maxhp"]))
    hud.append('<text x="%d" y="76" class="key">GOLD</text>' % (OX + 300))
    hud.append('<text x="%d" y="76" class="val">%d</text>' % (OX + 348, st["gold"]))
    hud.append('<text x="%d" y="76" class="key">SLAIN</text>' % (OX + 420))
    hud.append('<text x="%d" y="76" class="val">%d</text>' % (OX + 474, st["kills"]))
    party = st.get("party", [])
    hud.append('<text x="%d" y="76" class="key" text-anchor="end">%d ADVENTURER%s</text>'
               % (W_ - OX, len(party), "" if len(party) == 1 else "S"))

    # ---- chronicle
    logy = OY + H * TILE + 30
    lines = []
    for i, ln in enumerate(st.get("log", [])[:3]):
        lines.append('<text x="%d" y="%d" class="log" opacity="%.2f">%s</text>'
                     % (OX, logy + i * 19, 1.0 - i * 0.30, _esc(ln)))

    dead = ""
    if not alive:
        dead = ('<rect x="0" y="0" width="%d" height="%d" fill="#0A0A0B" opacity="0.72"/>'
                '<text x="%d" y="%d" class="dead" text-anchor="middle">THE HERO FELL</text>'
                '<text x="%d" y="%d" class="deadsub" text-anchor="middle">'
                'floor %d &#183; %d gold &#183; %d slain &#183; %d hands on the blade</text>'
                % (W_, H_, W_ // 2, H_ // 2 - 6, W_ // 2, H_ // 2 + 26,
                   st["floor"], st["gold"], st["kills"], len(party)))

    css = (".ttl{font-family:%s;font-size:21px;letter-spacing:6px;fill:%s}"
           ".run{font-family:%s;font-size:10px;letter-spacing:2.6px;fill:%s}"
           ".key{font-family:%s;font-size:9px;letter-spacing:2.6px;fill:%s}"
           ".val{font-family:%s;font-size:14px;fill:%s}"
           ".stair{font-family:%s;font-size:23px;font-weight:700}"
           ".mob{font-family:%s;font-size:16px;font-weight:700}"
           ".hero{font-family:%s;font-size:17px;font-weight:700;fill:#0A0A0B}"
           ".log{font-family:%s;font-size:12px;letter-spacing:0.4px;fill:%s}"
           ".dead{font-family:%s;font-size:34px;letter-spacing:8px;fill:%s}"
           ".deadsub{font-family:%s;font-size:11px;letter-spacing:3px;fill:%s}"
           % (SERIF, PRIMARY, SANS, MUTED, SANS, MUTED, SERIF, PRIMARY,
              MONO, MONO, MONO, MONO, MUTED, SERIF, BLOOD, SANS, MUTED))

    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" '
            'height="%d" role="img" aria-label="The Descent — run %d, floor %d">'
            '<style>%s</style><rect width="%d" height="%d" fill="%s"/>%s'
            '<line x1="%d" y1="92" x2="%d" y2="92" stroke="%s" stroke-width="1"/>'
            '%s%s%s</svg>'
            % (W_, H_, W_, H_, st["run"], st["floor"], css, W_, H_, BG,
               "".join(hud), OX, W_ - OX, RULE, "".join(p), "".join(lines), dead))


def _esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
