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
    repo = "%s/%s" % (USER, USER)
    login = v["user"].get("login", USER)
    stamp = str(int(time.time()))

    organs = v["organs"]
    living = [o for o in organs if o["age"] <= 400][:6]

    # --- organ table -------------------------------------------------------
    rows = []
    for o in living:
        if o["age"] <= 14:
            state = "`ACTIVE`"
        elif o["age"] <= 90:
            state = "`WARM`"
        elif o["age"] <= 180:
            state = "`COOLING`"
        else:
            state = "`NECROTIC`"
        desc = o["desc"] or "*no recorded function*"
        if len(desc) > 84:
            desc = desc[:81] + "..."
        rows.append(
            "| [`%s`](%s) | %s | %s | %d★ | %dd |"
            % (o["name"], o["url"], desc, state, o["stars"], o["age"])
        )
    organ_table = "\n".join(rows)

    cmds = [
        ("OBSERVE", "observe", "Record a sighting. Costs you nothing.",
         "Filed by an observer. The specimen registers that it was seen."),
        ("FEED", "feed", "Raise the pulse. Delays decay by one cycle.",
         "Nutrient introduced to the chamber."),
        ("PROVOKE", "provoke", "Poke it. It remembers who poked it.",
         "Stimulus applied. Response logged permanently."),
        ("AUTOPSY", "autopsy", "Demand the full readout. It will comply.",
         "Full biometric dump requested."),
    ]
    cmd_rows = []
    for name, slug, why, body in cmds:
        link = issue_link(repo, slug, "specimen: %s" % slug,
                          "%s\n\n<!-- do not edit below -->\ncommand=%s" % (body, slug))
        cmd_rows.append("| **[%s](%s)** | %s |" % (name, link, why))
    cmd_table = "\n".join(cmd_rows)

    prognosis = {
        5: "Specimen is in uncontrolled growth. Containment is theoretical.",
        4: "Specimen is metabolising. Output sustained. No intervention required.",
        3: "Specimen is stable but not growing. Monitor.",
        2: "Specimen has gone quiet. Tissue is cooling. Intervention advised.",
        1: "Specimen is failing. Structural corruption spreading through the record.",
        0: "No signal. The chamber is running on memory.",
    }[v["stage"]]

    return f"""<div align="center">

<img src="assets/specimen.svg?v={stamp}" alt="Specimen {v['uid']} — containment chamber" width="100%" />

</div>

```
OBSERVATION LOG — SUBJECT {login.upper()} — DESIGNATION {v['uid']}
────────────────────────────────────────────────────────────────────────────
This page is not written. It is measured.
A machine reads the subject's activity every six hours and re-renders
everything below from what it finds. Nothing here is a claim. It is a reading.
```

<div align="center">

```{organism(v)}```

**STAGE {v['stage']} — {v['stage_label']}**

</div>

```
VITALS ─────────────────────────────────────────────────────────────────────

  DECAY INDEX     {bar(v['decay'])}  {v['decay']:>3}%
  INTEGRITY       {bar(v['integrity'])}  {v['integrity']:>3}%
  PULSE           {v['bpm']} BPM        (beats at the true shipping rate)
  SILENCE         {v['silence']} day(s) since the last recorded signal
  STREAK          {v['streak']} day(s) of continuous output
  VELOCITY        {v['velocity']} commits/day over 30 days

METABOLISM (30d) ───────────────────────────────────────────────────────────

  {sparkline(v['days'])}
  {v['c7']} events / 7d      {v['c30']} events / 30d      {v['total_year']} events / 52w

PROGNOSIS ──────────────────────────────────────────────────────────────────

  {prognosis}
```

## ORGAN SYSTEMS

Every repository is tissue. It is either being fed or it is rotting, and the
table says which. `{v['living']}` living, `{v['necrotic']}` necrotic, `{v['stars']}`★ accumulated.

| ORGAN | FUNCTION | STATE | MASS | LAST PERFUSION |
|:--|:--|:--|--:|--:|
{organ_table}

## INTERACT WITH THE SPECIMEN

The chamber accepts input from anyone. Open an issue and a machine answers —
it updates the readout, replies in your voice, and writes you into the log
below permanently. No account required beyond the one you already have.

| COMMAND | EFFECT |
|:--|:--|
{cmd_table}

{observer_block(st)}

```
────────────────────────────────────────────────────────────────────────────
The subject is a builder in India. He is evolving. That is the whole bio;
the rest of this page is evidence. Last observation {v['stamp']}.
Re-rendered automatically. If this page ever stops changing, he stopped.
────────────────────────────────────────────────────────────────────────────
```
"""


def main():
    st = load_state()
    v = derive(fetch(), st)
    # nutrients evaporate one unit per observation cycle
    if int(st.get("nutrients", 0)) > 0:
        st["nutrients"] = int(st["nutrients"]) - 1
        save_state(st)
    os.makedirs(os.path.join(ROOT, "assets"), exist_ok=True)
    with open(os.path.join(ROOT, "assets", "specimen.svg"), "w") as f:
        f.write(chamber.render(v))

    readme_path = os.path.join(ROOT, "README.md")
    with open(readme_path, "w") as f:
        f.write(render_readme(v, st))
    print("rendered :: stage=%d decay=%d bpm=%d silence=%dd"
          % (v["stage"], v["decay"], v["bpm"], v["silence"]))


if __name__ == "__main__":
    main()
