"""Download and validate the Nerdearla schedule snapshot."""

from __future__ import annotations

import json
import os
import sys
import urllib.request
from pathlib import Path

DEFAULT_EVENT_ID = "148d7ff3-134c-48b5-8bc2-52bf025d2ac4"
ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "data" / "nerdearla-argentina-2026.json"


def api_url() -> str:
    event_id = os.getenv("NERDEARLA_EVENT_ID", DEFAULT_EVENT_ID)
    return os.getenv(
        "NERDEARLA_API_URL",
        f"https://backstage.nerdearla.com/api/sessions/?event_id={event_id}",
    )


def validate(payload: object) -> dict:
    if not isinstance(payload, dict):
        raise ValueError("API response must be an object")
    edition = payload.get("edition")
    sessions = payload.get("sessions")
    if not isinstance(edition, dict) or not isinstance(sessions, list):
        raise ValueError("API response must contain edition and sessions")
    required = {"id", "title", "start", "end", "track", "location_name"}
    for index, session in enumerate(sessions):
        if not isinstance(session, dict):
            raise ValueError(f"Session {index} must be an object")
        missing = required.difference(session)
        if missing:
            raise ValueError(f"Session {index} is missing: {sorted(missing)}")
    return payload


def main() -> None:
    request = urllib.request.Request(
        api_url(),
        headers={"User-Agent": "strands-conference-copilot/0.1"},
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.load(response)
        validated = validate(payload)
    except Exception as exc:
        print(f"Could not refresh schedule: {exc}", file=sys.stderr)
        print(f"Existing snapshot remains at {SNAPSHOT}", file=sys.stderr)
        raise SystemExit(1) from exc

    SNAPSHOT.parent.mkdir(parents=True, exist_ok=True)
    temporary = SNAPSHOT.with_suffix(".json.tmp")
    temporary.write_text(
        json.dumps(validated, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary.replace(SNAPSHOT)
    print(f"Saved {len(validated['sessions'])} sessions to {SNAPSHOT}")


if __name__ == "__main__":
    main()
