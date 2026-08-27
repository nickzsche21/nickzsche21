#!/usr/bin/env python3
"""
SPECIMEN — vitals acquisition.
Pulls real GitHub telemetry and derives the organism's biological state.
Stdlib only. No third-party services. No API keys beyond GITHUB_TOKEN.
"""
import json
import os
import ssl
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta

USER = os.environ.get("SPECIMEN_USER", "nickzsche21")
TOKEN = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN") or ""
CTX = ssl.create_default_context()


def _req(url, data=None, headers=None):
    h = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "specimen-observation-rig",
    }
    if TOKEN:
        h["Authorization"] = "bearer " + TOKEN
    if headers:
        h.update(headers)
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(url, data=body, headers=h)
    try:
        with urllib.request.urlopen(req, context=CTX, timeout=30) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        print("HTTP %s on %s :: %s" % (e.code, url, e.read()[:300]))
        return None
    except Exception as e:
        print("ERR on %s :: %s" % (url, e))
        return None


STATE_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", "state.json"
)


def load_state():
    try:
        with open(STATE_PATH) as f:
            return json.load(f)
    except Exception:
        return {"nutrients": 0, "observers": {}, "log": []}


def save_state(st):
    with open(STATE_PATH, "w") as f:
        json.dump(st, f, indent=2)


def graphql(query):
    return _req("https://api.github.com/graphql", {"query": query})


def fetch():
    """Acquire raw telemetry."""
    out = {}
    out["user"] = _req("https://api.github.com/users/%s" % USER) or {}

    repos = []
    for page in (1, 2):
        chunk = _req(
            "https://api.github.com/users/%s/repos?per_page=100&sort=pushed&page=%d"
            % (USER, page)
        )
        if not chunk:
            break
        repos.extend(chunk)
        if len(chunk) < 100:
            break
    out["repos"] = [r for r in repos if not r.get("fork")]

    q = """query{user(login:"%s"){
      contributionsCollection{
        totalCommitContributions
        totalPullRequestContributions
        totalIssueContributions
        totalRepositoriesWithContributedCommits
        contributionCalendar{
          totalContributions
          weeks{contributionDays{date contributionCount}}
        }
      }
    }}""" % USER
    g = graphql(q)
    cc = {}
    if g and g.get("data", {}).get("user"):
        cc = g["data"]["user"]["contributionsCollection"]
    out["contrib"] = cc
    return out


def _days(cal):
    """Flatten the contribution calendar into an ordered list of (date, count)."""
    days = []
    for w in cal.get("weeks", []):
        for d in w.get("contributionDays", []):
            days.append((d["date"], d["contributionCount"]))
    days.sort(key=lambda x: x[0])
    return days


def derive(raw, state=None):
    """Turn telemetry into biology."""
    now = datetime.now(timezone.utc)
    cal = raw.get("contrib", {}).get("contributionCalendar", {}) or {}
    days = _days(cal)
    counts = [c for _, c in days]

    v = {}
    v["user"] = raw.get("user", {})
    v["uid"] = raw.get("user", {}).get("id", 0)
    v["total_year"] = cal.get("totalContributions", 0)
    v["days"] = days

    # --- windows -------------------------------------------------------
    last7 = counts[-7:] if counts else [0]
    last30 = counts[-30:] if counts else [0]
    last90 = counts[-90:] if counts else [0]
    v["c7"] = sum(last7)
    v["c30"] = sum(last30)
    v["c90"] = sum(last90)

    # --- silence: days since the last recorded signal -------------------
    silence = 0
    for _, c in reversed(days):
        if c > 0:
            break
        silence += 1
    v["silence"] = silence

    # --- streak ---------------------------------------------------------
    streak = 0
    for _, c in reversed(days):
        if c == 0:
            break
        streak += 1
    v["streak"] = streak

    peak = max(counts) if counts else 0
    v["peak"] = peak

    # --- velocity: commits/day over 30d, normalised ----------------------
    v["velocity"] = round(v["c30"] / 30.0, 2)

    # --- BPM: the heartbeat literally beats at the shipping rate ---------
    # 30 bpm at total silence -> 132 bpm at a hard sprint.
    bpm = 30 + min(v["c7"], 40) * 2.55
    if silence > 3:
        bpm = max(24, bpm - silence * 2.5)
    v["bpm"] = int(max(20, min(140, bpm)))

    # --- DECAY INDEX: 0 = thriving, 100 = flatline ------------------------
    # Silence dominates; low 30d volume compounds it.
    d_sil = min(silence, 30) / 30.0 * 62.0
    d_vol = (1.0 - min(v["c30"], 45) / 45.0) * 38.0
    # Visitor attention is real input: nutrients offset decay, then evaporate.
    nutrients = int(state.get("nutrients", 0)) if state else 0
    v["nutrients"] = nutrients
    relief = min(9.0, nutrients * 1.5)
    v["relief"] = int(round(relief))
    decay = int(max(0, min(100, round(d_sil + d_vol - relief))))
    v["decay"] = decay
    v["integrity"] = 100 - decay

    # --- STAGE -----------------------------------------------------------
    if decay <= 12:
        stage, label = 5, "ASCENDANT"
    elif decay <= 30:
        stage, label = 4, "ACTIVE"
    elif decay <= 52:
        stage, label = 3, "STABLE"
    elif decay <= 72:
        stage, label = 2, "DORMANT"
    elif decay <= 90:
        stage, label = 1, "DECAYING"
    else:
        stage, label = 0, "FLATLINE"
    v["stage"] = stage
    v["stage_label"] = label

    # --- repo organs -------------------------------------------------------
    organs = []
    for r in raw.get("repos", []):
        pushed = r.get("pushed_at")
        age = 999
        if pushed:
            try:
                dt = datetime.strptime(pushed, "%Y-%m-%dT%H:%M:%SZ").replace(
                    tzinfo=timezone.utc
                )
                age = (now - dt).days
            except Exception:
                pass
        organs.append(
            {
                "name": r.get("name", "?"),
                "desc": (r.get("description") or "").strip(),
                "stars": r.get("stargazers_count", 0),
                "lang": (r.get("language") or "—"),
                "age": age,
                "url": r.get("html_url", ""),
            }
        )
    organs.sort(key=lambda o: (-o["stars"], o["age"]))
    v["organs"] = organs
    v["necrotic"] = len([o for o in organs if o["age"] > 180])
    v["living"] = len([o for o in organs if o["age"] <= 180])
    v["stars"] = sum(o["stars"] for o in organs)

    v["now"] = now
    v["stamp"] = now.strftime("%Y-%m-%d %H:%M UTC")
    return v


if __name__ == "__main__":
    d = derive(fetch(), load_state())
    print(json.dumps({k: val for k, val in d.items()
                      if k not in ("days", "organs", "user", "now")}, indent=2))
