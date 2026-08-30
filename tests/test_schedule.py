"""Deterministic tests that do not require an LLM or AWS credentials."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "02-schedule-data" / "schedule.py"


def load_module():
    spec = importlib.util.spec_from_file_location("schedule_data", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load schedule module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


schedule = load_module()


class ScheduleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = schedule.load_schedule()
        cls.sessions = cls.payload["sessions"]

    def test_snapshot_contains_expected_edition(self) -> None:
        self.assertEqual(self.payload["edition"]["year"], 2026)
        self.assertEqual(len(self.sessions), 135)

    def test_filters_security_sessions_in_person(self) -> None:
        results = schedule.search_sessions(
            self.sessions,
            track="security",
            session_type="in-person",
        )
        self.assertGreater(len(results), 0)
        self.assertTrue(all(item["track"] == "SECURITY" for item in results))
        self.assertTrue(all(item["type"] == "In-person" for item in results))

    def test_search_is_case_insensitive_and_chronological(self) -> None:
        results = schedule.search_sessions(self.sessions, query="KuBeRnEtEs")
        self.assertGreater(len(results), 0)
        starts = [item["start"] for item in results]
        self.assertEqual(starts, sorted(starts))


if __name__ == "__main__":
    unittest.main()
