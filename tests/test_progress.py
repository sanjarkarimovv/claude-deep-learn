import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))
import progress as p  # noqa: E402

FRI, SAT, MON = date(2026, 11, 13), date(2026, 11, 14), date(2026, 11, 16)

MINI = {
    "modules": [
        {"number": "00", "slug": "asoslar", "title": "Asoslar", "lessons": [
            {"id": "00-01", "tag": "ai", "title": "Birinchi", "goal": "G1",
             "practice": "P1", "docs": ["code:overview"]},
            {"id": "00-02", "tag": "claude", "title": "Ikkinchi", "goal": "G2",
             "practice": "P2", "docs": ["api:intro"]},
        ]},
    ]
}


class StreakTest(unittest.TestCase):
    def test_first_completion_starts_streak(self):
        self.assertEqual(p.next_streak(None, FRI, 0), 1)

    def test_consecutive_day_extends_streak(self):
        self.assertEqual(p.next_streak("2026-11-13", SAT, 3), 4)

    def test_sunday_rest_does_not_break_streak(self):
        self.assertEqual(p.next_streak("2026-11-14", MON, 4), 5)

    def test_missed_day_resets_streak(self):
        self.assertEqual(p.next_streak("2026-11-12", SAT, 7), 1)

    def test_same_day_keeps_streak(self):
        self.assertEqual(p.next_streak("2026-11-16", MON, 5), 5)

    def test_effective_streak_is_zero_when_broken(self):
        progress = {"streak": 7, "lastCompletedDate": "2026-11-12"}
        self.assertEqual(p.effective_streak(progress, MON), 0)

    def test_effective_streak_survives_sunday(self):
        progress = {"streak": 7, "lastCompletedDate": "2026-11-14"}
        self.assertEqual(p.effective_streak(progress, MON), 7)


if __name__ == "__main__":
    unittest.main()
