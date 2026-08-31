"""Multi-conference data loader and search utilities."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"

CONFERENCES: dict[str, dict[str, str]] = {
    "nerdearla": {
        "snapshot": "nerdearla-argentina-2026.json",
        "name": "Nerdearla Argentina 2026",
    },
    "kubecon-na-2026": {
        "snapshot": "kubecon-na-2026.json",
        "name": "KubeCon + CloudNativeCon North America 2026",
    },
}


def list_conferences() -> list[str]:
    """Return the list of supported conference IDs."""
    return list(CONFERENCES.keys())


def _conference_id_from_session_id(session_id: str) -> str | None:
    """Detect the conference from a session ID prefix."""
    for cid in CONFERENCES:
        if session_id.startswith(f"{cid}-"):
            return cid
    return None


def load_conference(conference_id: str) -> dict[str, Any]:
    """Load the normalized snapshot for a conference."""
    if conference_id not in CONFERENCES:
        raise ValueError(
            f"Unknown conference: {conference_id}. "
            f"Supported: {list_conferences()}"
        )
    path = DATA_DIR / CONFERENCES[conference_id]["snapshot"]
    return json.loads(path.read_text(encoding="utf-8"))


def load_all_conferences() -> dict[str, dict[str, Any]]:
    """Load all supported conference snapshots."""
    return {cid: load_conference(cid) for cid in CONFERENCES}


def search_sessions(
    conference_id: str | None = None,
    query: str | None = None,
    day: str | None = None,
    track: str | None = None,
    session_type: str | None = None,
) -> list[dict[str, Any]]:
    """Search sessions across one or all conferences."""
    conferences = (
        [conference_id] if conference_id else list_conferences()
    )
    query_text = (query or "").casefold()
    track_text = (track or "").casefold()
    type_text = (session_type or "").casefold()
    results: list[dict[str, Any]] = []
    for cid in conferences:
        snapshot = load_conference(cid)
        for session in snapshot.get("sessions", []):
            if query_text:
                searchable = " ".join(
                    str(session.get(k, ""))
                    for k in ("title", "description", "track", "tags")
                ).casefold()
                if query_text not in searchable:
                    continue
            if day:
                start = session.get("start", "")
                if not start.startswith(day):
                    continue
            if track_text:
                track_name = str(session.get("track", "")).casefold()
                if track_name != track_text and track_text not in track_name:
                    continue
            if type_text:
                stype = str(session.get("type", "")).casefold()
                if stype != type_text:
                    continue
            results.append(session)
    results.sort(key=lambda s: (s.get("start", ""), s.get("title", "")))
    return results


def get_session(conference_id: str, session_id: str) -> dict[str, Any] | None:
    """Get a single session by its full ID (e.g. 'kubecon-na-2026-1244695')."""
    snapshot = load_conference(conference_id)
    for session in snapshot.get("sessions", []):
        if session.get("id") == session_id:
            return session
    return None


def get_session_by_id(session_id: str) -> dict[str, Any] | None:
    """Resolve a session ID across all conferences."""
    cid = _conference_id_from_session_id(session_id)
    if cid is None:
        return None
    return get_session(cid, session_id)


def compact_session(session: dict[str, Any]) -> dict[str, Any]:
    """Project a session to a compact representation."""
    speakers = session.get("speakers", []) or []
    speaker_names = []
    for sp in speakers:
        if isinstance(sp, dict):
            full = sp.get("full_name") or f"{sp.get('first_name', '')} {sp.get('last_name', '')}".strip()
            if full:
                speaker_names.append(full)
    return {
        "id": session.get("id"),
        "conference_id": session.get("conference_id"),
        "title": session.get("title"),
        "start": session.get("start"),
        "end": session.get("end"),
        "track": session.get("track"),
        "location": session.get("location_name"),
        "type": session.get("type"),
        "language": session.get("language"),
        "speakers": speaker_names,
    }


def load_nerdearla_fallback() -> dict[str, Any]:
    """Load Nerdearla using the original schedule module (for compat)."""
    schedule_path = ROOT / "02-schedule-data" / "schedule.py"
    spec = importlib.util.spec_from_file_location("schedule_data", schedule_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load Nerdearla schedule module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return {"sessions": module.load_schedule()["sessions"]}
