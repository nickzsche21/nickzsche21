#!/usr/bin/env python3
"""Tiny persistence layer. The whole world lives in one JSON file."""
import json
import os

PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..",
                    "state.json")


def load():
    try:
        with open(PATH) as f:
            return json.load(f)
    except Exception:
        return {"game": None, "hall": [], "deepest": 0}


def save(st):
    with open(PATH, "w") as f:
        json.dump(st, f, indent=2)
