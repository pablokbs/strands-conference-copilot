"""Download the Sessionize schedule snapshot for KubeCon NA 2026."""

from __future__ import annotations

import json
import os
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "data" / "kubecon-na-2026.json"

SCHEDULE_URL = (
    "https://kubecon-cloudnativecon-north-america-2026.sessionize.com/api/schedule"
)
DATA_URL = (
    "https://kubecon-cloudnativecon-north-america-2026.sessionize.com/api/data"
)
USER_AGENT = "strands-conference-copilot/0.1"


def fetch_json(url: str, timeout: int = 60) -> object:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.load(response)


def main() -> None:
    dry_run = "--check-only" in sys.argv
    if dry_run:
        if not SNAPSHOT.exists():
            print(f"Missing snapshot at {SNAPSHOT}", file=sys.stderr)
            raise SystemExit(1)
        snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
        sessions = snapshot.get("sessions", [])
        if not sessions:
            print(f"Snapshot {SNAPSHOT} has no sessions", file=sys.stderr)
            raise SystemExit(1)
        print(
            f"OK: {SNAPSHOT.name} has {len(sessions)} sessions "
            f"({snapshot['conference']['name']})"
        )
        return

    print(f"Fetching {SCHEDULE_URL}...")
    raw_schedule = fetch_json(SCHEDULE_URL)
    raw_speakers: list = []
    raw_rooms: list = []
    raw_categories: list = []

    # Speakers / rooms / categories are typically in /api/schedule but may also
    # be in separate endpoints. Try to extract them from the schedule payload
    # first, fall back to dedicated endpoints if not present.
    if isinstance(raw_schedule, dict):
        raw_speakers = raw_schedule.get("speakers", []) or []
        raw_rooms = raw_schedule.get("rooms", []) or []
        raw_categories = raw_schedule.get("categories", []) or []

    # Local import to avoid a hard dependency if the script runs without
    # the adapter module present.
    from sessionize_adapter import build_snapshot  # type: ignore

    snapshot = build_snapshot(
        raw_schedule,
        raw_speakers=raw_speakers,
        raw_rooms=raw_rooms,
        raw_categories=raw_categories,
    )

    SNAPSHOT.parent.mkdir(parents=True, exist_ok=True)
    tmp = SNAPSHOT.with_suffix(".json.tmp")
    tmp.write_text(
        json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    tmp.replace(SNAPSHOT)
    print(
        f"Saved {len(snapshot['sessions'])} sessions to {SNAPSHOT} "
        f"({snapshot['conference']['name']})"
    )


if __name__ == "__main__":
    main()
