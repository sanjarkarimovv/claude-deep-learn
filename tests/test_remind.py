import sys
import unittest
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import remind  # noqa: E402

PROGRESS = {
    "lastCompletedDate": "2026-11-14",  # Shanba, shuning uchun Dushanbada streak tirik
    "streak": 5,
    "current": {"id": "02-03", "title": "CLAUDE.md va memory", "status": "idle"},
}


def at(day, hour, minute=0):
    return datetime(2026, 11, day, hour, minute)


class BuildMessageTest(unittest.TestCase):
    def test_silent_on_sunday(self):
        self.assertIsNone(remind.build_message(PROGRESS, at(22, 10)))

    def test_silent_before_nine(self):
        self.assertIsNone(remind.build_message(PROGRESS, at(16, 8, 59)))

    def test_silent_when_done_today(self):
        done = dict(PROGRESS, lastCompletedDate="2026-11-16")
        self.assertIsNone(remind.build_message(done, at(16, 10)))

    def test_silent_when_course_finished(self):
        self.assertIsNone(remind.build_message(dict(PROGRESS, current=None), at(16, 10)))

    def test_morning_message_names_lesson(self):
        message = remind.build_message(PROGRESS, at(16, 9))
        self.assertIn("02-03 · CLAUDE.md va memory", message)
        self.assertIn("/dars", message)

    def test_afternoon_message_is_firmer(self):
        self.assertIn("hali qilinmadi", remind.build_message(PROGRESS, at(16, 13)))

    def test_evening_message_warns_about_streak(self):
        message = remind.build_message(PROGRESS, at(16, 21))
        self.assertIn("5 kunlik streak", message)
        self.assertIn("3 soat", message)

    def test_evening_without_live_streak(self):
        broken = dict(PROGRESS, lastCompletedDate="2026-11-10")
        message = remind.build_message(broken, at(16, 22))
        self.assertNotIn("streak", message)
        self.assertIn("2 soat", message)

    def test_last_reminder_counts_minutes(self):
        self.assertIn("bir necha daqiqa", remind.build_message(PROGRESS, at(16, 23, 59)))

    def test_saturday_is_review(self):
        self.assertIn("Haftalik review", remind.build_message(PROGRESS, at(21, 10)))


if __name__ == "__main__":
    unittest.main()
