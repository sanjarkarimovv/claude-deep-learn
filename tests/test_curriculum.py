import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import progress as p  # noqa: E402


class CurriculumTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.curriculum = p.load_curriculum(ROOT)
        cls.lessons = p.all_lessons(cls.curriculum)

    def test_has_nine_sequential_modules(self):
        numbers = [m["number"] for m in self.curriculum["modules"]]
        self.assertEqual(numbers, [f"{i:02d}" for i in range(9)])

    def test_has_54_lessons(self):
        self.assertEqual(len(self.lessons), 54)

    def test_ids_are_unique_and_match_module(self):
        ids = [lesson["id"] for lesson in self.lessons]
        self.assertEqual(len(ids), len(set(ids)))
        for module in self.curriculum["modules"]:
            for lesson in module["lessons"]:
                self.assertRegex(lesson["id"], rf"^{module['number']}-\d{{2}}$")

    def test_lessons_are_complete(self):
        for lesson in self.lessons:
            with self.subTest(lesson=lesson["id"]):
                self.assertIn(lesson["tag"], p.TAG_ICONS)
                for field in ("title", "goal", "practice"):
                    self.assertTrue(lesson[field].strip())
                self.assertTrue(lesson["docs"])
                for ref in lesson["docs"]:
                    self.assertIn(ref.partition(":")[0], p.DOC_PREFIXES)


if __name__ == "__main__":
    unittest.main()
