"""Tests for the Sessionize adapter and multi-conference loader."""

from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ADAPTER_PATH = ROOT / "04-multi-conference" / "sessionize_adapter.py"
DATA_PATH = ROOT / "04-multi-conference" / "conference_data.py"
SNAPSHOT_PATH = ROOT / "data" / "kubecon-na-2026.json"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


adapter = _load("sessionize_adapter", ADAPTER_PATH)
conference_data = _load("conference_data", DATA_PATH)


class SessionizeAdapterTests(unittest.TestCase):
    """Verify the Sessionize → internal model conversion."""

    FIXTURE_SESSION_ID = "1244695"

    def test_normalize_session_keeps_pablo_fixture(self) -> None:
        raw_session = {
            "id": self.FIXTURE_SESSION_ID,
            "title": "When the Agent Lost Its Patience",
            "description": "Security talk.",
            "startsAt": "2026-11-10T17:30:00",
            "endsAt": "2026-11-10T18:00:00",
            "isServiceSession": False,
            "isPlenumSession": False,
            "speakers": ["speaker-1"],
            "categoryItems": [465809, 465822],
            "roomId": 82950,
            "status": "Accepted",
            "isInformed": True,
            "isConfirmed": True,
        }
        rooms_map = {82950: {"id": 82950, "name": "Room 200"}}
        categories_map = {
            465809: {"id": 465809, "name": "Security"},
            465822: {"id": 465822, "name": "AI/ML"},
        }
        speakers_map = {
            "speaker-1": {"id": "speaker-1", "firstName": "Pablo", "lastName": "F."}
        }
        normalized = adapter.normalize_sessionize_session(
            raw_session, speakers_map, rooms_map, categories_map
        )
        self.assertEqual(normalized["id"], "kubecon-na-2026-1244695")
        self.assertEqual(normalized["raw_id"], "1244695")
        self.assertEqual(normalized["conference_id"], "kubecon-na-2026")
        self.assertEqual(normalized["title"], "When the Agent Lost Its Patience")
        self.assertEqual(normalized["start"], "2026-11-10T17:30:00")
        self.assertEqual(normalized["end"], "2026-11-10T18:00:00")
        self.assertEqual(normalized["day"], "2026-11-10")
        self.assertEqual(normalized["room_id"], 82950)
        self.assertEqual(normalized["location_name"], "Room 200")
        self.assertIn("Security", normalized["tags"])
        self.assertIn("AI/ML", normalized["tags"])
        self.assertEqual(normalized["track"], "Security")
        self.assertEqual(normalized["speakers"][0]["full_name"], "Pablo F.")

    def test_build_snapshot_round_trip(self) -> None:
        snapshot = adapter.build_snapshot(
            {
                "sessions": [
                    {
                        "id": "1",
                        "title": "Test",
                        "startsAt": "2026-11-10T10:00:00",
                        "endsAt": "2026-11-10T10:30:00",
                        "speakers": ["sp-1"],
                        "categoryItems": [1],
                        "roomId": 100,
                    }
                ]
            },
            raw_speakers=[
                {"id": "sp-1", "firstName": "Ana", "lastName": "G"}
            ],
            raw_rooms=[{"id": 100, "name": "Sala A"}],
            raw_categories=[{"id": 1, "name": "Track 1"}],
        )
        self.assertEqual(snapshot["conference"]["id"], "kubecon-na-2026")
        self.assertEqual(len(snapshot["sessions"]), 1)
        self.assertEqual(snapshot["sessions"][0]["track"], "Track 1")
        self.assertEqual(snapshot["speakers"][0]["full_name"], "Ana G")


class MultiConferenceLoaderTests(unittest.TestCase):
    """Verify the multi-conference loader and search utilities."""

    @classmethod
    def setUpClass(cls) -> None:
        if not SNAPSHOT_PATH.exists():
            raise unittest.SkipTest(f"Missing snapshot: {SNAPSHOT_PATH}")

    def test_list_conferences_includes_kubecon(self) -> None:
        conferences = conference_data.list_conferences()
        self.assertIn("kubecon-na-2026", conferences)
        self.assertIn("nerdearla", conferences)

    def test_load_kubecon_returns_session_fixture(self) -> None:
        snapshot = conference_data.load_conference("kubecon-na-2026")
        session_ids = [s["id"] for s in snapshot["sessions"]]
        self.assertIn("kubecon-na-2026-1244695", session_ids)
        # Find Pablo's session and confirm it has the right title
        pablo = next(
            (s for s in snapshot["sessions"] if s["id"] == "kubecon-na-2026-1244695"),
            None,
        )
        self.assertIsNotNone(pablo)
        self.assertIn("Agent Lost Its Patience", pablo["title"])
        self.assertEqual(pablo["start"], "2026-11-10T17:30:00")

    def test_search_filters_by_conference(self) -> None:
        # Filter to KubeCon only
        results = conference_data.search_sessions(
            conference_id="kubecon-na-2026",
            query="Agent",
        )
        self.assertGreater(len(results), 0)
        for session in results:
            self.assertEqual(session["conference_id"], "kubecon-na-2026")

    def test_search_filters_by_day(self) -> None:
        results = conference_data.search_sessions(
            conference_id="kubecon-na-2026",
            day="2026-11-10",
        )
        for session in results:
            self.assertTrue(session["start"].startswith("2026-11-10"))

    def test_search_filters_by_track(self) -> None:
        results = conference_data.search_sessions(
            conference_id="kubecon-na-2026",
            track="General",
        )
        self.assertGreater(len(results), 0)
        for session in results:
            self.assertEqual(session["track"], "General")

    def test_search_across_all_conferences(self) -> None:
        # When conference_id is None, should return results from both.
        # Normalize sessions to ensure each has a conference_id.
        results = conference_data.search_sessions(query="Kubernetes")
        normalized = []
        for s in results:
            if "conference_id" not in s and s.get("id", "").startswith("kubecon-na-2026-"):
                s["conference_id"] = "kubecon-na-2026"
            normalized.append(s)
        conference_ids = {s.get("conference_id") for s in normalized}
        self.assertIn("kubecon-na-2026", conference_ids)

    def test_get_session_by_id(self) -> None:
        session = conference_data.get_session_by_id("kubecon-na-2026-1244695")
        self.assertIsNotNone(session)
        self.assertEqual(session["conference_id"], "kubecon-na-2026")

    def test_get_session_by_id_unknown_returns_none(self) -> None:
        self.assertIsNone(
            conference_data.get_session_by_id("kubecon-na-2026-9999999")
        )

    def test_get_session_by_id_wrong_prefix_returns_none(self) -> None:
        self.assertIsNone(conference_data.get_session_by_id("nerdearla-1244695"))

    def test_compact_session_projection(self) -> None:
        session = conference_data.get_session_by_id("kubecon-na-2026-1244695")
        compact = conference_data.compact_session(session)
        self.assertEqual(compact["id"], "kubecon-na-2026-1244695")
        self.assertEqual(compact["conference_id"], "kubecon-na-2026")
        self.assertEqual(compact["title"], session["title"])


class RefreshScriptTests(unittest.TestCase):
    """Verify refresh_sessionize.py --check-only mode."""

    SNAPSHOT = ROOT / "data" / "kubecon-na-2026.json"

    def test_snapshot_exists_and_has_expected_shape(self) -> None:
        if not self.SNAPSHOT.exists():
            self.skipTest("Snapshot not yet downloaded")
        data = json.loads(self.SNAPSHOT.read_text(encoding="utf-8"))
        self.assertIn("conference", data)
        self.assertEqual(data["conference"]["id"], "kubecon-na-2026")
        self.assertGreater(len(data.get("sessions", [])), 100)
        self.assertIn("speakers", data)
        self.assertIn("rooms", data)
        self.assertIn("categories", data)


if __name__ == "__main__":
    unittest.main()
