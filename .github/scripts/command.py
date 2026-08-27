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

REPO = os.environ.get("GITHUB_REPOSITORY", "%s/%s" % (USER, USER))
EVENT = os.environ.get("GITHUB_EVENT_PATH", "")

VALID = ("observe", "feed", "provoke", "autopsy")

REPLY = {
    "observe": (
        "**OBSERVATION RECORDED.**\n\n"
        "You have been added to the chamber log. The specimen does not know "
        "what you look like, only that you were here at `{ts}`. "
        "That is now permanent."
    ),
    "feed": (
        "**NUTRIENT ACCEPTED.**\n\n"
        "Decay index reduced. Reserve now `{n}` unit(s) — it evaporates by one "
        "every observation cycle, so this is a loan against entropy, not a cure. "
        "The only real cure is the subject shipping something."
    ),
    "provoke": (
        "**STIMULUS LOGGED.**\n\n"
        "The specimen registered the contact and did not enjoy it. "
        "You are now recorded as a hostile observer. There is no way to undo this. "
        "Provocation count: `{p}`."
    ),
    "autopsy": (
        "**FULL READOUT — SUBJECT {user}**\n\n"
        "```\nDECAY {decay}%   INTEGRITY {integrity}%   PULSE {bpm} BPM\n"
        "SILENCE {silence}d   STREAK {streak}d   VELOCITY {velocity}/day\n"
        "TISSUE {living} living / {necrotic} necrotic   MASS {stars}★\n```\n\n"
        "The subject is not dead. The subject is measured. "
        "There is a difference, and this page exists to keep it."
    ),
}


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
        comment(num, "**UNRECOGNISED STIMULUS.**\n\nThe chamber accepts `observe`, "
                     "`feed`, `provoke`, `autopsy`. Nothing else registers.")
        close(num)
        return

    st = load_state()
    st.setdefault("observers", {})
    st.setdefault("log", [])
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    rec = st["observers"].setdefault(login, {"avatar": avatar, "n": 0, "provokes": 0})
    rec["avatar"] = avatar or rec.get("avatar", "")
    rec["n"] = rec.get("n", 0) + 1
    if cmd == "provoke":
        rec["provokes"] = rec.get("provokes", 0) + 1
    if cmd == "feed":
        st["nutrients"] = min(12, int(st.get("nutrients", 0)) + 1)

    st["log"].insert(0, {"who": login, "avatar": avatar, "cmd": cmd, "ts": ts})
    st["log"] = st["log"][:40]
    save_state(st)

    # respond in character
    if cmd == "autopsy":
        from vitals import fetch, derive
        v = derive(fetch(), st)
        body = REPLY["autopsy"].format(
            user=login, decay=v["decay"], integrity=v["integrity"], bpm=v["bpm"],
            silence=v["silence"], streak=v["streak"], velocity=v["velocity"],
            living=v["living"], necrotic=v["necrotic"], stars=v["stars"])
    else:
        body = REPLY[cmd].format(ts=ts, n=st.get("nutrients", 0),
                                 p=rec.get("provokes", 0))

    comment(num, body + "\n\n<sub>The chamber re-renders within the minute. "
                        "You will appear in the observation log on the profile.</sub>")
    close(num)
    print("handled %s from %s" % (cmd, login))


if __name__ == "__main__":
    main()
