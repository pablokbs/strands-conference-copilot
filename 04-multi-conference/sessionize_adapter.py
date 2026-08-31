"""Sessionize API adapter: normalize external data into our internal model."""

from __future__ import annotations

from typing import Any

CONFERENCE_ID = "kubecon-na-2026"
CONFERENCE_NAME = "KubeCon + CloudNativeCon North America 2026"
CONFERENCE_TIMEZONE = "America/Denver"
CONFERENCE_EDITION = "2026"
SESSIONIZE_URL = "https://kubecon-cloudnativecon-north-america-2026.sessionize.com"


def _normalize_speaker(speaker_id: str, speakers_map: dict[str, dict]) -> dict[str, Any]:
    raw = speakers_map.get(speaker_id, {})
    first = raw.get("firstName", "") or ""
    last = raw.get("lastName", "") or ""
    full = raw.get("fullName") or f"{first} {last}".strip() or f"Speaker {speaker_id[:8]}"
    return {
        "id": speaker_id,
        "conference_id": CONFERENCE_ID,
        "first_name": first,
        "last_name": last,
        "full_name": full,
        "bio": raw.get("bio"),
        "tag": raw.get("tagLine"),
    }


def normalize_sessionize_session(
    session: dict[str, Any],
    speakers_map: dict[str, dict],
    rooms_map: dict[int, dict],
    categories_map: dict[int, dict],
) -> dict[str, Any]:
    """Normalize a Sessionize session dict into our internal model."""
    session_id = session.get("id", "")
    starts = session.get("startsAt", "")
    ends = session.get("endsAt", "")
    day = starts[:10] if starts else None
    room_id = session.get("roomId")
    room_info = rooms_map.get(room_id, {}) if room_id is not None else {}
    category_ids = session.get("categoryItems", []) or []
    category_names = [
        categories_map[cid]["name"] for cid in category_ids if cid in categories_map
    ]
    track = category_names[0] if category_names else "General"

    return {
        "id": f"{CONFERENCE_ID}-{session_id}",
        "raw_id": session_id,
        "conference_id": CONFERENCE_ID,
        "title": session.get("title", ""),
        "description": session.get("description"),
        "start": starts,
        "end": ends,
        "day": day,
        "track": track,
        "tags": category_names,
        "location_name": room_info.get("name", f"Room {room_id}"),
        "room_id": room_id,
        "language": "EN",
        "type": "In-person",
        "format": "session" if not session.get("isServiceSession") else "service",
        "speakers": [
            _normalize_speaker(sid, speakers_map) for sid in session.get("speakers", []) or []
        ],
        "speaker_ids": session.get("speakers", []) or [],
        "category_ids": category_ids,
        "is_service_session": bool(session.get("isServiceSession")),
        "is_plenum_session": bool(session.get("isPlenumSession")),
        "status": session.get("status", "Accepted"),
        "url": f"{SESSIONIZE_URL}/session/{session_id}",
    }


def build_snapshot(
    raw_schedule: dict[str, Any],
    raw_speakers: list[dict[str, Any]] | None = None,
    raw_rooms: list[dict[str, Any]] | None = None,
    raw_categories: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build the normalized snapshot from raw Sessionize payloads."""
    speakers_list = raw_speakers or []
    speakers_map = {s.get("id"): s for s in speakers_list}
    rooms_map: dict[int, dict] = {}
    for r in raw_rooms or []:
        rid = r.get("id")
        if rid is not None:
            rooms_map[rid] = r
    categories_map: dict[int, dict] = {}
    for c in raw_categories or []:
        cid = c.get("id")
        if cid is not None:
            categories_map[cid] = c

    sessions = [
        normalize_sessionize_session(s, speakers_map, rooms_map, categories_map)
        for s in raw_schedule.get("sessions", [])
    ]

    return {
        "conference": {
            "id": CONFERENCE_ID,
            "name": CONFERENCE_NAME,
            "edition": CONFERENCE_EDITION,
            "timezone": CONFERENCE_TIMEZONE,
            "url": SESSIONIZE_URL,
        },
        "speakers": [_normalize_speaker(s.get("id", ""), speakers_map) for s in speakers_list],
        "rooms": [
            {
                "id": r.get("id"),
                "conference_id": CONFERENCE_ID,
                "name": r.get("name", f"Room {r.get('id')}"),
                "description": r.get("description"),
            }
            for r in (raw_rooms or [])
        ],
        "categories": [
            {
                "id": c.get("id"),
                "conference_id": CONFERENCE_ID,
                "name": c.get("name", f"Category {c.get('id')}"),
                "description": c.get("description"),
            }
            for c in (raw_categories or [])
        ],
        "sessions": sessions,
    }
