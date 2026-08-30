"""Small deterministic CLI for exploring the Nerdearla schedule."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "data" / "nerdearla-argentina-2026.json"


def load_schedule() -> dict:
    return json.loads(SNAPSHOT.read_text(encoding="utf-8"))


def search_sessions(
    sessions: list[dict],
    query: str | None = None,
    day: str | None = None,
    track: str | None = None,
    session_type: str | None = None,
) -> list[dict]:
    query_text = (query or "").casefold()
    track_text = (track or "").casefold()
    type_text = (session_type or "").casefold()
    results = []
    for session in sessions:
        searchable = " ".join(
            str(session.get(key, ""))
            for key in ("title", "description", "tags", "track")
        ).casefold()
        if query_text and query_text not in searchable:
            continue
        if day and not session["start"].startswith(day):
            continue
        if track_text and session.get("track", "").casefold() != track_text:
            continue
        if type_text and session.get("type", "").casefold() != type_text:
            continue
        results.append(session)
    return sorted(results, key=lambda item: (item["start"], item["title"]))


def compact(session: dict) -> dict:
    return {
        "id": session["id"],
        "title": session["title"],
        "start": session["start"],
        "end": session["end"],
        "track": session["track"],
        "location": session["location_name"],
        "type": session["type"],
        "language": session["language"],
        "speakers": [
            f"{speaker['first_name']} {speaker['last_name']}".strip()
            for speaker in session["speakers"]
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("stats")
    search = subparsers.add_parser("search")
    search.add_argument("--query")
    search.add_argument("--day", help="YYYY-MM-DD")
    search.add_argument("--track")
    search.add_argument("--type", dest="session_type")
    args = parser.parse_args()

    payload = load_schedule()
    sessions = payload["sessions"]
    if args.command == "stats":
        summary = {
            "edition": payload["edition"],
            "sessions": len(sessions),
            "days": Counter(s["start"][:10] for s in sessions),
            "tracks": Counter(s["track"] for s in sessions),
        }
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return

    results = search_sessions(
        sessions,
        query=args.query,
        day=args.day,
        track=args.track,
        session_type=args.session_type,
    )
    print(json.dumps([compact(item) for item in results], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
