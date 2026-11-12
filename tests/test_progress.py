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


class TransitionTest(unittest.TestCase):
    def setUp(self):
        self.progress = p.new_progress(MINI, FRI)

    def test_new_progress_points_to_first_lesson(self):
        self.assertEqual(self.progress["current"]["id"], "00-01")
        self.assertEqual(self.progress["current"]["status"], "idle")

    def test_complete_requires_started_lesson(self):
        with self.assertRaises(ValueError):
            p.complete_lesson(self.progress, MINI, FRI, "3/3")

    def test_complete_records_and_advances(self):
        p.start_lesson(self.progress, FRI)
        p.complete_lesson(self.progress, MINI, FRI, "2/3")
        self.assertEqual(self.progress["completed"],
                         [{"id": "00-01", "date": "2026-11-13", "quizScore": "2/3"}])
        self.assertEqual(self.progress["current"]["id"], "00-02")
        self.assertEqual(self.progress["lastCompletedDate"], "2026-11-13")
        self.assertEqual(self.progress["streak"], 1)

    def test_completing_last_lesson_finishes_course(self):
        for day in (FRI, SAT):
            p.start_lesson(self.progress, day)
            p.complete_lesson(self.progress, MINI, day, "3/3")
        self.assertIsNone(self.progress["current"])
        self.assertEqual(self.progress["streak"], 2)

    def test_review_counts_for_streak_without_advancing(self):
        p.complete_review(self.progress, SAT, "4/5")
        self.assertEqual(self.progress["current"]["id"], "00-01")
        self.assertEqual(self.progress["lastCompletedDate"], "2026-11-14")
        self.assertEqual(self.progress["reviews"], [{"date": "2026-11-14", "quizScore": "4/5"}])


class ViewTest(unittest.TestCase):
    def test_doc_url_expands_prefix(self):
        self.assertEqual(p.doc_url("code:skills"), "https://code.claude.com/docs/en/skills.md")
        self.assertEqual(p.doc_url("api:build-with-claude/streaming"),
                         "https://platform.claude.com/docs/en/build-with-claude/streaming.md")

    def test_render_marks_lesson_states(self):
        progress = p.new_progress(MINI, FRI)
        p.start_lesson(progress, FRI)
        p.complete_lesson(progress, MINI, FRI, "3/3")
        text = p.render_roadmap(progress, MINI)
        self.assertIn("| ✅ | 00-01 | 🧠 | Birinchi | G1 |", text)
        self.assertIn("| 👉 | 00-02 | 🟠 | Ikkinchi | G2 |", text)
        self.assertIn("1/2", text)

    def test_summary_describes_current_lesson(self):
        info = p.summary(p.new_progress(MINI, FRI), MINI, SAT)
        self.assertEqual(info["mode"], "review")
        self.assertFalse(info["doneToday"])
        self.assertEqual(info["current"]["lessonFile"], "lessons/00-asoslar/00-01.md")
        self.assertEqual(info["current"]["practiceDir"], "practice/00-01")
        self.assertEqual(info["current"]["docs"], ["https://code.claude.com/docs/en/overview.md"])


class CliTest(unittest.TestCase):
    def run_cli(self, root, *args):
        env = dict(os.environ, DL_STATE_DIR=str(root / "state"))
        return subprocess.run(
            [sys.executable, str(SCRIPTS / "progress.py"), "--root", str(root),
             "--today", "2026-11-13", *args],
            capture_output=True, text=True, env=env)

    def make_root(self, tmp):
        root = Path(tmp)
        (root / "curriculum.json").write_text(json.dumps(MINI), encoding="utf-8")
        return root

    def test_full_lesson_cycle(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.make_root(tmp)
            for command in (["init"], ["start"], ["complete", "--score", "3/3"]):
                result = self.run_cli(root, *command)
                self.assertEqual(result.returncode, 0, result.stderr)
            status = json.loads(result.stdout)
            self.assertTrue(status["doneToday"])
            self.assertEqual(status["current"]["id"], "00-02")
            self.assertIn("✅", (root / "roadmap.md").read_text(encoding="utf-8"))
            mirror = json.loads((root / "state" / "state.json").read_text(encoding="utf-8"))
            self.assertEqual(mirror["lastCompletedDate"], "2026-11-13")

    def test_init_refuses_to_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.make_root(tmp)
            self.run_cli(root, "init")
            result = self.run_cli(root, "init")
            self.assertEqual(result.returncode, 1)
            self.assertIn("allaqachon", result.stderr)

    def test_status_without_init_fails_cleanly(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_cli(self.make_root(tmp), "status")
            self.assertEqual(result.returncode, 1)
            self.assertIn("init", result.stderr)


if __name__ == "__main__":
    unittest.main()
