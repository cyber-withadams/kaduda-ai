"""
Tiny in-memory session store keyed by phone number.

This is intentionally the simplest possible thing that works for an MVP.
Two things to know before you rely on this in production:
  1. It resets every time the server restarts (fine for testing, not for launch).
  2. It will leak memory forever if you never trim old sessions.

Swap this module for Redis (or a Postgres table) once you have real users —
the function signatures below are the only contract the rest of the app
depends on, so the swap doesn't touch main.py or ai.py.
"""

from collections import defaultdict
from datetime import datetime, timedelta

_SESSIONS = defaultdict(list)  # phone_number -> [{"role": ..., "content": ...}, ...]
_LAST_SEEN = {}

MAX_TURNS_KEPT = 6          # how many past messages we keep for context
SESSION_TIMEOUT = timedelta(hours=6)  # start a fresh conversation after this


def get_history(phone_number: str) -> list:
    _expire_if_stale(phone_number)
    return _SESSIONS[phone_number]


def add_turn(phone_number: str, role: str, content: str):
    _SESSIONS[phone_number].append({"role": role, "content": content})
    _SESSIONS[phone_number] = _SESSIONS[phone_number][-MAX_TURNS_KEPT:]
    _LAST_SEEN[phone_number] = datetime.utcnow()


def _expire_if_stale(phone_number: str):
    last = _LAST_SEEN.get(phone_number)
    if last and datetime.utcnow() - last > SESSION_TIMEOUT:
        _SESSIONS[phone_number] = []
