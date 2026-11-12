# Claude Deep Learn Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** `/dars` skill orqali boshqariladigan 54 darslik lokal Claude oʻquv kursini qurish: progress tracking, avtomatik `roadmap.md` va macOS eslatmalari bilan.

**Architecture:**
- **Yagona manba:** `curriculum.json` (54 dars).
- **Holat:** `progress.json`. U faqat test bilan himoyalangan `scripts/progress.py` CLI orqali oʻzgaradi. Har saqlashda CLI `roadmap.md` ni qayta yaratadi va `~/.claude-deep-learn/state.json` ga nusxa yozadi.
- **Nega nusxa kerak:** macOS TCC `~/Desktop` ni himoyalaydi, `launchd` esa faqat shu nusxani oʻqiydi.
- **`/dars` skill:** `` !`progress.py status` `` bilan joriy holatni oladi va state machine boʻyicha ishlaydi.
- **`remind.py`:** `launchd` uni har soatda ishga tushiradi. Script `state.json` ni oʻqib, `osascript` orqali notification koʻrsatadi.

**Tech Stack:** Python 3.9 stdlib (`/usr/bin/python3`, `unittest`), Bash, macOS `launchd` + `osascript`, Claude Code skills.

**Design:** `docs/plans/2026-11-12-claude-learning-roadmap-design.md`

**Kunlar (testlar uchun):** 2026-11-12 Payshanba, 13 Juma, 14 Shanba, 15 Yakshanba, 16 Dushanba, 21 Shanba, 22 Yakshanba.

---

### Task 1: progress.py — streak mantiqi

**Files:**
- Create: `scripts/progress.py`
- Test: `tests/test_progress.py`

**Step 1: Failing test yozish**

`tests/test_progress.py`:
```python
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
```

**Step 2: Fail boʻlishini tekshirish**

Run: `python3 -m unittest tests.test_progress -v`
Expected: `ModuleNotFoundError: No module named 'progress'`

**Step 3: Minimal implementation**

`scripts/progress.py`:
```python
#!/usr/bin/env python3
"""Claude Deep Learn: oʻquv progress ini boshqaruvchi CLI.

/dars skill holatni faqat shu CLI orqali oʻzgartiradi. JSON ni qoʻlda
tahrirlash xatoga olib keladi, CLI esa testlar bilan himoyalangan.
"""
from __future__ import annotations

from datetime import date, timedelta
from typing import Optional


def previous_lesson_day(today: date) -> date:
    """Yakshanba dam kuni: Dushanbadan oldingi dars kuni Shanba."""
    return today - timedelta(days=2 if today.weekday() == 0 else 1)


def streak_alive(last: Optional[str], today: date) -> bool:
    return last is not None and date.fromisoformat(last) >= previous_lesson_day(today)


def next_streak(last: Optional[str], today: date, streak: int) -> int:
    if last == today.isoformat():
        return streak
    return streak + 1 if streak_alive(last, today) else 1


def effective_streak(progress: dict, today: date) -> int:
    """Koʻrsatish uchun: streak uzilgan boʻlsa 0."""
    return progress["streak"] if streak_alive(progress["lastCompletedDate"], today) else 0
```

**Step 4: Pass boʻlishini tekshirish**

Run: `python3 -m unittest tests.test_progress -v`
Expected: 7 tests OK

**Step 5: Commit**
```bash
git add scripts/progress.py tests/test_progress.py
git commit -m "feat(progress): add streak logic with Sunday rest day"
```

---

### Task 2: progress.py — holat oʻtishlari va koʻrinishlar

**Files:**
- Modify: `scripts/progress.py`
- Test: `tests/test_progress.py`

**Step 1: Failing test qoʻshish** (`StreakTest` klassidan keyin, `if __name__` dan oldin)

```python
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
```

**Step 2: Fail boʻlishini tekshirish**

Run: `python3 -m unittest tests.test_progress -v`
Expected: `AttributeError: module 'progress' has no attribute 'new_progress'`

**Step 3: Implementation** (`scripts/progress.py` ga qoʻshish)

Importlarni yangilash:
```python
import json
from datetime import date, timedelta
from pathlib import Path
from typing import List, Optional
```

Konstantalar (importlardan keyin):
```python
TAG_ICONS = {"ai": "🧠", "claude": "🟠", "mix": "🟠🧠", "project": "📱"}
DOC_PREFIXES = {
    "code": "https://code.claude.com/docs/en/",
    "api": "https://platform.claude.com/docs/en/",
}
WEEKDAYS = ["Dushanba", "Seshanba", "Chorshanba", "Payshanba", "Juma", "Shanba", "Yakshanba"]
SATURDAY, SUNDAY = 5, 6
```

Funksiyalar (`effective_streak` dan keyin):
```python
# ---------- Curriculum ----------

def load_curriculum(root: Path) -> dict:
    return json.loads((root / "curriculum.json").read_text(encoding="utf-8"))


def all_lessons(curriculum: dict) -> List[dict]:
    return [lesson for module in curriculum["modules"] for lesson in module["lessons"]]


def doc_url(ref: str) -> str:
    prefix, _, path = ref.partition(":")
    return DOC_PREFIXES[prefix] + path + ".md"


def lesson_ref(lesson: dict) -> dict:
    return {"id": lesson["id"], "title": lesson["title"], "status": "idle", "startedAt": None}


# ---------- Holat oʻtishlari ----------

def new_progress(curriculum: dict, start: date) -> dict:
    return {
        "startDate": start.isoformat(),
        "lastCompletedDate": None,
        "streak": 0,
        "current": lesson_ref(all_lessons(curriculum)[0]),
        "completed": [],
        "reviews": [],
    }


def start_lesson(progress: dict, today: date) -> dict:
    current = progress["current"]
    if current is None:
        raise ValueError("Kurs allaqachon tugagan")
    if current["status"] != "task_given":
        current["status"] = "task_given"
        current["startedAt"] = today.isoformat()
    return progress


def _mark_day_done(progress: dict, today: date) -> None:
    progress["streak"] = next_streak(progress["lastCompletedDate"], today, progress["streak"])
    progress["lastCompletedDate"] = today.isoformat()


def complete_lesson(progress: dict, curriculum: dict, today: date, score: str) -> dict:
    current = progress["current"]
    if current is None:
        raise ValueError("Kurs allaqachon tugagan")
    if current["status"] != "task_given":
        raise ValueError("Avval darsni boshlang (start)")
    lessons = all_lessons(curriculum)
    index = [lesson["id"] for lesson in lessons].index(current["id"])
    progress["completed"].append({"id": current["id"], "date": today.isoformat(), "quizScore": score})
    _mark_day_done(progress, today)
    progress["current"] = lesson_ref(lessons[index + 1]) if index + 1 < len(lessons) else None
    return progress


def complete_review(progress: dict, today: date, score: str) -> dict:
    progress["reviews"].append({"date": today.isoformat(), "quizScore": score})
    _mark_day_done(progress, today)
    return progress


# ---------- Koʻrinishlar ----------

def summary(progress: dict, curriculum: dict, today: date) -> dict:
    lessons = all_lessons(curriculum)
    done_ids = {item["id"] for item in progress["completed"]}
    weekday = today.weekday()
    monday = today - timedelta(days=weekday)
    info = {
        "today": today.isoformat(),
        "weekday": WEEKDAYS[weekday],
        "mode": "review" if weekday == SATURDAY else "rest" if weekday == SUNDAY else "lesson",
        "doneToday": progress["lastCompletedDate"] == today.isoformat(),
        "streak": effective_streak(progress, today),
        "completed": f"{len(done_ids)}/{len(lessons)}",
        "thisWeek": [item["id"] for item in progress["completed"]
                     if date.fromisoformat(item["date"]) >= monday],
        "upcoming": [f"{l['id']} {TAG_ICONS[l['tag']]} {l['title']}"
                     for l in lessons if l["id"] not in done_ids][:5],
        "current": None,
    }
    current = progress["current"]
    if current:
        lesson = next(l for l in lessons if l["id"] == current["id"])
        module = next(m for m in curriculum["modules"] if m["number"] == current["id"][:2])
        info["current"] = dict(
            current,
            tag=TAG_ICONS[lesson["tag"]],
            module=f"{module['number']}. {module['title']}",
            goal=lesson["goal"],
            practice=lesson["practice"],
            docs=[doc_url(ref) for ref in lesson["docs"]],
            lessonFile=f"lessons/{module['number']}-{module['slug']}/{lesson['id']}.md",
            practiceDir=f"practice/{lesson['id']}",
        )
    return info


def render_roadmap(progress: dict, curriculum: dict) -> str:
    done = {item["id"] for item in progress["completed"]}
    current_id = progress["current"]["id"] if progress["current"] else None
    total = len(all_lessons(curriculum))
    filled = round(20 * len(done) / total)
    lines = [
        "# 🗺️ Claude Deep Learn Roadmap",
        "",
        "> Bu fayl avtomatik yaratiladi (`scripts/progress.py`). Qoʻlda tahrirlamang.",
        "",
        f"**Progress:** `{'█' * filled}{'░' * (20 - filled)}` {len(done)}/{total}",
        "",
        "🧠 AI umumiy · 🟠 Claude maxsus · 📱 Amaliy loyiha · ✅ bajarildi · 👉 joriy · ⬜ navbatda",
    ]
    for module in curriculum["modules"]:
        lines += ["", f"## {module['number']}. {module['title']}", "",
                  "| | ID | Teg | Mavzu | Maqsad |", "|---|---|---|---|---|"]
        for lesson in module["lessons"]:
            mark = "✅" if lesson["id"] in done else "👉" if lesson["id"] == current_id else "⬜"
            lines.append(f"| {mark} | {lesson['id']} | {TAG_ICONS[lesson['tag']]} "
                         f"| {lesson['title']} | {lesson['goal']} |")
    return "\n".join(lines) + "\n"
```

**Step 4: Pass boʻlishini tekshirish**

Run: `python3 -m unittest tests.test_progress -v`
Expected: 15 tests OK

**Step 5: Commit**
```bash
git add scripts/progress.py tests/test_progress.py
git commit -m "feat(progress): add lesson transitions, summary and roadmap rendering"
```

---

### Task 3: progress.py — CLI

**Files:**
- Modify: `scripts/progress.py`
- Test: `tests/test_progress.py`

**Step 1: Failing test qoʻshish** (`ViewTest` dan keyin)

```python
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
```

**Step 2: Fail boʻlishini tekshirish**

Run: `python3 -m unittest tests.test_progress -v`
Expected: 3 ta `CliTest` FAIL (CLI hali yoʻq, returncode 0 va stdout boʻsh)

**Step 3: Implementation**

Importlarga qoʻshish: `import argparse`, `import os`, `import sys`.

Konstantalarga qoʻshish:
```python
ROOT = Path(__file__).resolve().parent.parent
DEFAULT_STATE_DIR = Path.home() / ".claude-deep-learn"
```

Fayl oxiriga:
```python
# ---------- Saqlash va CLI ----------

def save(progress: dict, curriculum: dict, root: Path, state_dir: Path) -> None:
    text = json.dumps(progress, ensure_ascii=False, indent=2) + "\n"
    (root / "progress.json").write_text(text, encoding="utf-8")
    (root / "roadmap.md").write_text(render_roadmap(progress, curriculum), encoding="utf-8")
    # launchd ~/Desktop ni oʻqiy olmaydi (macOS TCC), shuning uchun nusxa yozamiz
    state_dir.mkdir(parents=True, exist_ok=True)
    (state_dir / "state.json").write_text(text, encoding="utf-8")


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="progress.py", description="Claude Deep Learn progress")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--today", type=date.fromisoformat)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("init").add_argument("--start", type=date.fromisoformat)
    commands.add_parser("status")
    commands.add_parser("start")
    commands.add_parser("complete").add_argument("--score", required=True)
    commands.add_parser("review-done").add_argument("--score", required=True)
    commands.add_parser("render")
    args = parser.parse_args(argv)

    today = args.today or date.today()
    state_dir = Path(os.environ.get("DL_STATE_DIR", DEFAULT_STATE_DIR))
    curriculum = load_curriculum(args.root)
    progress_path = args.root / "progress.json"
    try:
        if args.command == "init":
            if progress_path.exists():
                raise ValueError("progress.json allaqachon mavjud")
            progress = new_progress(curriculum, args.start or today)
        else:
            if not progress_path.exists():
                raise ValueError("progress.json topilmadi: avval `init` qiling")
            progress = json.loads(progress_path.read_text(encoding="utf-8"))
            if args.command == "start":
                start_lesson(progress, today)
            elif args.command == "complete":
                complete_lesson(progress, curriculum, today, args.score)
            elif args.command == "review-done":
                complete_review(progress, today, args.score)
    except ValueError as error:
        print(f"Xato: {error}", file=sys.stderr)
        return 1

    save(progress, curriculum, args.root, state_dir)
    print(json.dumps(summary(progress, curriculum, today), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

**Step 4: Pass boʻlishini tekshirish**

Run: `python3 -m unittest tests.test_progress -v`
Expected: 18 tests OK

**Step 5: Commit**
```bash
git add scripts/progress.py tests/test_progress.py
git commit -m "feat(progress): add CLI with state mirror for launchd"
```

---

### Task 4: curriculum.json (54 dars)

**Files:**
- Create: `curriculum.json` (kontent: **Appendix A**)
- Test: `tests/test_curriculum.py`

**Step 1: Failing test yozish**

`tests/test_curriculum.py`:
```python
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
```

**Step 2: Fail boʻlishini tekshirish**

Run: `python3 -m unittest tests.test_curriculum -v`
Expected: `FileNotFoundError: ... curriculum.json`

**Step 3: Appendix A dan faylni chiqarish**
```bash
python3 - docs/plans/2026-11-12-claude-learning-roadmap-plan.md curriculum.json <<'EOF'
import json, sys
text = open(sys.argv[1], encoding="utf-8").read()
block = text.split("<!-- curriculum.json -->", 1)[1]
body = block.split("```json\n", 1)[1].split("\n```", 1)[0]
data = json.loads(body)
open(sys.argv[2], "w", encoding="utf-8").write(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
EOF
```

**Step 4: Pass boʻlishini tekshirish**

Run: `python3 -m unittest tests.test_curriculum -v`
Expected: 4 tests OK

**Step 5: Docs linklarini tekshirish** (barchasi 200 qaytarishi kerak)
```bash
python3 -c 'import sys; sys.path.insert(0,"scripts"); import progress as p; from pathlib import Path
c=p.load_curriculum(Path(".")); print("\n".join(sorted({p.doc_url(d) for l in p.all_lessons(c) for d in l["docs"]})))' \
| while read -r url; do code=$(curl -s -o /dev/null -w '%{http_code}' -L "$url"); [ "$code" = 200 ] || echo "$code $url"; done
```
Expected: hech narsa chiqmaydi. Chiqsa, `llms.txt` dan toʻgʻri yoʻlni topib, `curriculum.json` ni tuzatish.

**Step 6: Commit**
```bash
git add curriculum.json tests/test_curriculum.py
git commit -m "feat: add 54-lesson curriculum with validation tests"
```

---

### Task 5: remind.py — eslatma matni

**Files:**
- Create: `scripts/remind.py`
- Test: `tests/test_remind.py`

**Step 1: Failing test yozish**

`tests/test_remind.py`:
```python
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
```

**Step 2: Fail boʻlishini tekshirish**

Run: `python3 -m unittest tests.test_remind -v`
Expected: `ModuleNotFoundError: No module named 'remind'`

**Step 3: Implementation**

`scripts/remind.py`:
```python
#!/usr/bin/env python3
"""Kunlik dars eslatmasi. launchd har soatda ishga tushiradi.

~/.claude-deep-learn/state.json ni oʻqiydi (progress.py yozadi) va
bugungi dars bajarilmagan boʻlsa macOS notification koʻrsatadi.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from progress import SATURDAY, SUNDAY, effective_streak

TITLE = "Claude Deep Learn"
DEFAULT_STATE_FILE = Path.home() / ".claude-deep-learn" / "state.json"
START_HOUR = 9


def build_message(progress: dict, now: datetime) -> Optional[str]:
    """Eslatma matni yoki eslatma kerak boʻlmasa None."""
    if now.weekday() == SUNDAY or now.hour < START_HOUR:
        return None
    if progress.get("lastCompletedDate") == now.date().isoformat():
        return None
    current = progress.get("current")
    if not current:
        return None

    if now.weekday() == SATURDAY:
        topic = "Haftalik review"
    else:
        topic = f"{current['id']} · {current['title']}"

    if now.hour < 13:
        return f"📚 Bugungi dars: {topic} (~40 daq). Terminalda /dars yozing."
    if now.hour < 21:
        return f"⏰ Bugungi dars hali qilinmadi: {topic}. 30 daqiqa ajrating!"

    left = "bir necha daqiqa" if now.hour == 23 and now.minute >= 30 else f"{24 - now.hour} soat"
    streak = effective_streak(progress, now.date())
    if streak > 0:
        return f"🔥 {streak} kunlik streak xavf ostida! Kun tugashiga {left} qoldi: {topic}"
    return f"🔥 Kun tugashiga {left} qoldi. Bugungi darsni boshlang: {topic}"


def notify(message: str) -> None:
    # Matn argv orqali uzatiladi, shuning uchun AppleScript injection boʻlmaydi
    subprocess.run(
        ["/usr/bin/osascript",
         "-e", "on run argv",
         "-e", 'display notification (item 1 of argv) with title (item 2 of argv) sound name "Glass"',
         "-e", "end run",
         message, TITLE],
        check=False,
    )


def main(argv: List[str]) -> int:
    if "--test" in argv:
        notify("✅ Eslatmalar ishlayapti! Bu test xabari.")
        return 0
    state_file = Path(os.environ.get("DL_STATE_FILE", DEFAULT_STATE_FILE))
    if not state_file.exists():
        return 0
    progress = json.loads(state_file.read_text(encoding="utf-8"))
    message = build_message(progress, datetime.now())
    if message is None:
        return 0
    if os.environ.get("REMIND_DRY_RUN"):
        print(message)
    else:
        notify(message)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
```

**Step 4: Pass boʻlishini tekshirish**

Run: `python3 -m unittest discover -s tests -v`
Expected: barcha 32 test OK

**Step 5: Commit**
```bash
git add scripts/remind.py tests/test_remind.py
git commit -m "feat(remind): add escalating daily reminder messages"
```

---

### Task 6: Kursni ishga tushirish va CLAUDE.md

**Files:**
- Create: `progress.json`, `roadmap.md` (CLI yaratadi), `CLAUDE.md`

**Step 1: Progress ni yaratish**

Run: `python3 scripts/progress.py init`
Expected: JSON chiqadi, unda `"current": {"id": "00-01", ...}` va `"completed": "0/54"`. `roadmap.md` 9 ta modul bilan yaratiladi.

**Step 2: `CLAUDE.md` yozish**
```markdown
# Claude Deep Learn

Bu repo Claude ni (Claude Code, Claude API, Agent SDK) chuqur oʻrganish uchun shaxsiy kurs va laboratoriya.
Foydalanuvchi Middle+ mobile developer (Flutter, Kotlin). Maqsadi: AI Mobile Developer boʻlish.

## Til
- Doim oʻzbek tilida (lotin, toʻgʻri oʻ/gʻ belgilari bilan) tushuntir. Technical terms, kod va identifikatorlar inglizcha qoladi.
- Foydalanuvchining inglizchasi boshlangʻich darajada: inglizcha docs dan iqtibos keltirsang, oʻzbekcha izohla.

## Oʻqituvchi qoidalari
- Har bir tushunchani teg bilan belgila: 🧠 [AI umumiy] yoki 🟠 [Claude maxsus]. Farqini aniq koʻrsat.
- Amaliyot nazariyadan muhimroq: har dars amaliy topshiriq bilan tugaydi.
- Topshiriqni foydalanuvchi oʻzi bajaradi. Hint ber, lekin u soʻramaguncha tayyor yechim yozma.
- Maʼlumotni xotiradan emas, rasmiy docs dan tekshir, chunki Claude Code tez oʻzgaradi:
  - Claude Code va Agent SDK: https://code.claude.com/docs/llms.txt
  - Claude API: https://platform.claude.com/llms.txt

## Tuzilma
- `curriculum.json`: 54 dars, yagona manba. `roadmap.md` undan avtomatik yaratiladi, qoʻlda tahrirlama.
- `progress.json`: holat. Faqat `python3 scripts/progress.py <init|status|start|complete|review-done|render>` orqali oʻzgartir.
- `lessons/`: dars matnlari (dars kuni yaratiladi). `practice/<id>/`: foydalanuvchi ishi va `XULOSA.md`.
- `scripts/remind.py` + launchd: kunlik eslatmalar. Script lar oʻzgarsa, `scripts/reminder-install.sh` ni qayta ishga tushir.
- `docs/plans/`: design va implementation plan.

## Buyruqlar
- Testlar: `python3 -m unittest discover -s tests -v`
- Holat: `python3 scripts/progress.py status`
- Kunlik dars: `/dars` (umumiy holat uchun `/dars holat`)
```

**Step 3: Commit**
```bash
git add progress.json roadmap.md CLAUDE.md
git commit -m "feat: initialize course progress, roadmap and CLAUDE.md"
```

---

### Task 7: `/dars` skill

**Files:**
- Create: `.claude/skills/dars/SKILL.md`
- Create: `.claude/skills/dars/lesson-template.md`

**Step 1: `SKILL.md` yozish**
````markdown
---
name: dars
description: Claude Deep Learn kursining kunlik darsi. Keyingi darsni boshlaydi, topshiriqni tekshiradi va progress ni yangilaydi.
argument-hint: "[holat]"
disable-model-invocation: true
allowed-tools: Bash(python3 ${CLAUDE_PROJECT_DIR}/scripts/progress.py *) Read Write Edit Glob Grep WebFetch
---

# /dars: kunlik oʻqituvchi

## Joriy holat (avtomatik)

!`python3 ${CLAUDE_PROJECT_DIR}/scripts/progress.py status`

Argument: `$ARGUMENTS`

## Rejimni tanlash

Yuqoridagi JSON va argument boʻyicha **faqat bitta** rejimni tanla, tartib bilan:

1. Argument `holat` boʻlsa → **Holat**
2. `current` null boʻlsa → **Kurs tugadi**
3. `mode` = `rest` boʻlsa → bugun dam olish kuni ekanini ayt. Foydalanuvchi baribir xohlasa, 5–6-qoidalar boʻyicha davom et
4. `mode` = `review`, `doneToday` = false boʻlsa → **Review**
5. `current.status` = `idle` boʻlsa → **Yangi dars**
6. `current.status` = `task_given` boʻlsa → **Tekshiruv**

## Yangi dars

1. `current.lessonFile` mavjud boʻlsa, uni oʻqi. Mavjud boʻlmasa:
   - `current.docs` dagi sahifalarni WebFetch bilan oʻqi (eng yangi maʼlumot shu yerda).
   - `${CLAUDE_SKILL_DIR}/lesson-template.md` shabloni boʻyicha dars faylini yoz. Hajmi ~10 daqiqalik oʻqish boʻlsin.
2. `current.practiceDir` ichida `TOPSHIRIQ.md` yarat: vazifa (`current.practice` asosida, ~30 daqiqa) va 3–5 ta aniq tekshiruv mezoni.
3. Run: `python3 ${CLAUDE_PROJECT_DIR}/scripts/progress.py start`
4. Foydalanuvchiga quyidagilarni koʻrsat:
   - sarlavha (`id`, `tag`, `title`);
   - nazariyaning qisqa mazmuni va dars fayliga link;
   - topshiriq va mezonlar.
   Oxirida yoz: "Bajarib boʻlgach, yana `/dars` deb yozing."

## Tekshiruv

1. `TOPSHIRIQ.md` mezonlarini oʻqi va `current.practiceDir` dagi ishni tekshir. Ish boshqa joyda boʻlsa, foydalanuvchidan soʻra.
2. Har bir mezon uchun ✅ yoki ❌ belgisi va qisqa feedback ber. ❌ boʻlsa, nimani tuzatish kerakligini ayt va **toʻxta**: progress oʻzgarmaydi.
3. 3 ta active recall savol ber, **bittadan**, har birida javobni kut. Javobni baholab, toʻgʻri javobni qisqa tushuntir.
4. `XULOSA.md` ni tekshir. Fayl yoʻq boʻlsa, foydalanuvchidan oʻz soʻzlari bilan 3–5 qator yozishni soʻra. Uni sen yozib berma.
5. Hammasi tayyor boʻlsa:
   - Run: `python3 ${CLAUDE_PROJECT_DIR}/scripts/progress.py complete --score "<toʻgʻri javoblar>/3"`
   - Natijani streak bilan nishonla va keyingi dars nomini ayt.

## Review (Shanba)

1. `practice/review-<today>/TOPSHIRIQ.md` mavjud boʻlsa, mini-loyihani tekshir (Tekshiruv dagi 1–2-qadamlar), keyin 3-qadamga oʻt.
   Mavjud boʻlmasa:
   - `thisWeek` dagi darslarning fayllarini oʻqi. Roʻyxat boʻsh boʻlsa, barcha oʻtilgan darslarni ol.
   - 5 ta quiz savoli ber (🧠 va 🟠 aralash), bittadan.
   - Hafta mavzularini birlashtiradigan 20–30 daqiqalik mini-loyihani `practice/review-<today>/TOPSHIRIQ.md` ga yoz.
2. Foydalanuvchi mini-loyihani bajargach, uni tekshir.
3. Run: `python3 ${CLAUDE_PROJECT_DIR}/scripts/progress.py review-done --score "<toʻgʻri>/5"`

## Holat

Progress bar, streak, joriy dars va `upcoming` roʻyxatini chiroyli koʻrsat, `roadmap.md` ga havola ber. Holatni oʻzgartirma.

## Kurs tugadi

Foydalanuvchini tabrikla, 54 darsning qisqa xulosasini va keyingi oʻsish yoʻnalishlarini taklif qil.

## Qoidalar

- Oʻzbek tilida yoz, technical terms inglizcha qoladi. Har bir tushunchani 🧠 yoki 🟠 bilan belgila.
- Bir dars 30–60 daqiqaga sigʻsin.
- Topshiriqni foydalanuvchi oʻzi bajaradi. Sen hint berasan, foydalanuvchi soʻrasa hint darajasini oshirasan.
- `progress.json` va `roadmap.md` ni qoʻlda tahrirlama, faqat `progress.py` orqali oʻzgartir.
````

**Step 2: `lesson-template.md` yozish**
```markdown
# {id} · {tag} {title}

> **Modul:** {module} · **Vaqt:** ~10 daq nazariya + ~30 daq amaliyot
> **Maqsad:** {goal}

## 1. Nima uchun bu muhim?
2–3 jumla: real ishda qanday foyda beradi, AI mobile developer uchun misol.

## 2. Asosiy tushunchalar
3–6 ta tushuncha: har biri qisqa taʼrif va misol bilan.
Har birida ayt: bu 🧠 umumiy AI tushunchasimi yoki 🟠 Claude ga xosmi?

## 3. Amalda qanday koʻrinadi
Kod, buyruq yoki konfiguratsiya misollari.

## 4. Koʻp uchraydigan xatolar
2–3 ta tuzoq va ulardan qochish yoʻli.

## 5. Topshiriq
`TOPSHIRIQ.md` bilan bir xil: vazifa va tekshiruv mezonlari.

## 6. Manbalar
Rasmiy docs linklari.
```

**Step 3: Tekshirish**

Run: `python3 scripts/progress.py status`
Expected: exit 0. Bu buyruq skill ichidagi injection buyrugʻi bilan bir xil.

Keyin foydalanuvchi Claude Code da `/dars holat` ni ishga tushiradi.
Expected: progress `0/54` va joriy dars `00-01 🧠 LLM qanday ishlaydi`.

**Step 4: Commit**
```bash
git add .claude/skills/dars
git commit -m "feat: add /dars teaching skill and lesson template"
```

---

### Task 8: Eslatmalarni oʻrnatish

**Files:**
- Create: `scripts/reminder-install.sh`, `scripts/reminder-uninstall.sh`

**Step 1: `scripts/reminder-install.sh`**
```bash
#!/bin/bash
# Kunlik eslatmalarni yoqadi.
# macOS TCC ~/Desktop ni himoyalaydi va launchd dan ishga tushgan python3 uni
# oʻqiy olmasligi mumkin. Shuning uchun script lar ~/.claude-deep-learn ga
# nusxalanadi, holat esa state.json nusxasidan oʻqiladi.
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
STATE_DIR="$HOME/.claude-deep-learn"
LABEL="com.claude-deep-learn.reminder"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"

mkdir -p "$STATE_DIR" "$HOME/Library/LaunchAgents"
cp "$REPO/scripts/remind.py" "$REPO/scripts/progress.py" "$STATE_DIR/"
/usr/bin/python3 "$REPO/scripts/progress.py" status > /dev/null  # state.json ni yangilaydi

{
  cat <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>$LABEL</string>
  <key>ProgramArguments</key>
  <array>
    <string>/usr/bin/python3</string>
    <string>$STATE_DIR/remind.py</string>
  </array>
  <key>StandardOutPath</key><string>$STATE_DIR/remind.log</string>
  <key>StandardErrorPath</key><string>$STATE_DIR/remind.log</string>
  <key>StartCalendarInterval</key>
  <array>
EOF
  for hour in $(seq 9 23); do
    printf '    <dict><key>Hour</key><integer>%d</integer><key>Minute</key><integer>0</integer></dict>\n' "$hour"
  done
  printf '    <dict><key>Hour</key><integer>23</integer><key>Minute</key><integer>59</integer></dict>\n'
  cat <<EOF
  </array>
</dict>
</plist>
EOF
} > "$PLIST"

plutil -lint "$PLIST"
launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST"
echo "✅ Eslatmalar yoqildi: har kuni 09:00–23:59 (yakshanbadan tashqari)."
echo "   Test: /usr/bin/python3 $STATE_DIR/remind.py --test"
```

**Step 2: `scripts/reminder-uninstall.sh`**
```bash
#!/bin/bash
# Kunlik eslatmalarni oʻchiradi. Holat fayllari ~/.claude-deep-learn da qoladi.
set -euo pipefail
LABEL="com.claude-deep-learn.reminder"
launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
rm -f "$HOME/Library/LaunchAgents/$LABEL.plist"
echo "🔕 Eslatmalar oʻchirildi."
```

**Step 3: Oʻrnatish va tekshirish**
```bash
chmod +x scripts/reminder-*.sh
scripts/reminder-install.sh
launchctl print "gui/$(id -u)/com.claude-deep-learn.reminder" | grep -E "state|path"
REMIND_DRY_RUN=1 /usr/bin/python3 ~/.claude-deep-learn/remind.py
/usr/bin/python3 ~/.claude-deep-learn/remind.py --test
```

Expected:
- `plutil` "OK" deydi va `launchctl print` job ni koʻrsatadi.
- Dry run: 9:00 dan keyin va dars bajarilmagan boʻlsa xabar matni chiqadi, aks holda hech narsa chiqmaydi.
- `--test` ekranda notification chiqaradi. Chiqmasa, foydalanuvchi System Settings → Notifications → "Script Editor" ga ruxsat beradi.

**Step 4: Commit**
```bash
git add scripts/reminder-install.sh scripts/reminder-uninstall.sh
git commit -m "feat: add launchd reminder install/uninstall scripts"
```

---

### Task 9: README, design tuzatish va yakuniy tekshiruv

**Files:**
- Create: `README.md`
- Modify: `docs/plans/2026-11-12-claude-learning-roadmap-design.md`. U yerda `remind.sh` ni `remind.py` ga almashtirish va state nusxasi haqida jumla qoʻshish kerak.

**Step 1: `README.md`**
```markdown
# Claude Deep Learn

Claude Code va Claude API ni professional darajada oʻrganish uchun 54 darslik amaliy roadmap.
Darslarni `/dars` skill boshqaradi. Har kuni amaliy topshiriq bor, eslatmalar esa dars unutilmasligini taʼminlaydi.

**Maqsad:** AI Mobile Developer.

## Qanday ishlaydi
- `/dars`: keyingi darsni boshlaydi yoki topshiriqni tekshiradi
- `/dars holat`: progress, streak va keyingi mavzular
- [`roadmap.md`](roadmap.md): toʻliq xarita (avtomatik yangilanadi)
- Eslatmalar (macOS): `scripts/reminder-install.sh`, oʻchirish uchun `scripts/reminder-uninstall.sh`

🧠 AI umumiy · 🟠 Claude maxsus · 📱 Amaliy loyiha

## Tuzilma
| Yoʻl | Vazifasi |
|---|---|
| `curriculum.json` | 54 dars (yagona manba) |
| `progress.json` | Joriy holat (`scripts/progress.py` boshqaradi) |
| `lessons/` | Dars matnlari |
| `practice/` | Topshiriqlar va xulosalar |
| `.claude/skills/dars/` | `/dars` skill |

## Testlar
python3 -m unittest discover -s tests -v
```

**Step 2: Design hujjatini tuzatish** (`remind.sh` → `remind.py` va state nusxasi haqida izoh)

**Step 3: Yakuniy tekshiruv**

Run: `python3 -m unittest discover -s tests -v && python3 scripts/progress.py status`
Expected: 32 tests OK va status JSON

**Step 4: Commit**
```bash
git add README.md docs/plans/2026-11-12-claude-learning-roadmap-design.md
git commit -m "docs: add README and sync design with implementation"
```

---

## Appendix A: curriculum.json

Tag lar: `ai` = 🧠, `claude` = 🟠, `mix` = 🟠🧠, `project` = 📱.
Docs prefikslari: `code:` → `https://code.claude.com/docs/en/<path>.md`, `api:` → `https://platform.claude.com/docs/en/<path>.md`.

<!-- curriculum.json -->
```json
{"modules": [
{"number": "00", "slug": "ai-asoslari", "title": "AI asoslari", "lessons": [
{"id": "00-01", "tag": "ai", "title": "LLM qanday ishlaydi", "goal": "Next-token prediction, transformer va training bosqichlarini tushunish", "practice": "Bir xil promptni Claude ga 3 marta yuborib, javoblardagi farqni va uning sababini yozish", "docs": ["api:intro", "api:about-claude/glossary"]},
{"id": "00-02", "tag": "ai", "title": "Tokens va context window", "goal": "Token nima, context window chegarasi va narx qanday hisoblanishini bilish", "practice": "/context bilan session dagi token taqsimotini tahlil qilish va oʻzbekcha matn nega koʻproq token olishini tushuntirish", "docs": ["api:build-with-claude/token-counting", "api:build-with-claude/context-windows"]},
{"id": "00-03", "tag": "ai", "title": "Sampling, hallucination va cheklovlar", "goal": "Temperature, knowledge cutoff va hallucination sabablarini tushunish", "practice": "Claude hallucination qiladigan 3 ta savol topish va har birini yaxshiroq prompt bilan tuzatish", "docs": ["api:test-and-evaluate/strengthen-guardrails/reduce-hallucinations", "api:test-and-evaluate/strengthen-guardrails/increase-consistency"]},
{"id": "00-04", "tag": "ai", "title": "Prompt engineering asoslari", "goal": "Aniq koʻrsatma, misollar (few-shot), rol va bosqichma-bosqich fikrlash texnikalari", "practice": "Flutter widget yaratish uchun yomon promptni 4 ta texnika bilan yaxshilab, natijalarni solishtirish", "docs": ["api:build-with-claude/prompt-engineering/overview", "api:build-with-claude/prompt-engineering/claude-prompting-best-practices"]},
{"id": "00-05", "tag": "ai", "title": "Agents va tool use konsepsiyasi", "goal": "Agentic loop (think → act → observe) va tool calling qanday ishlashini tushunish", "practice": "Claude Code dagi bitta vazifaning tool chaqiruvlarini kuzatib, agentic loop diagrammasini chizish", "docs": ["api:agents-and-tools/tool-use/how-tool-use-works", "code:how-claude-code-works"]},
{"id": "00-06", "tag": "ai", "title": "Embeddings, RAG va evals", "goal": "Vector search, retrieval va AI sifatini oʻlchash (evals) asoslarini bilish", "practice": "Mobile AI ilova uchun RAG arxitekturasi va 5 ta eval mezonini loyihalash", "docs": ["api:build-with-claude/embeddings", "api:test-and-evaluate/develop-tests"]}
]},
{"number": "01", "slug": "claude-ekotizimi", "title": "Claude ekotizimi", "lessons": [
{"id": "01-01", "tag": "claude", "title": "Claude model family va model tanlash", "goal": "Opus, Sonnet, Haiku va Fable farqlari, narxlari va qaysi vazifaga qaysi model", "practice": "5 ta real vazifa uchun model tanlash jadvalini sabab va taxminiy narx bilan tuzish", "docs": ["api:models/overview", "api:about-claude/models/choosing-a-model", "api:about-claude/pricing"]},
{"id": "01-02", "tag": "claude", "title": "Thinking va effort", "goal": "Thinking va effort darajalari sifat, tezlik va narxga qanday taʼsir qilishini bilish", "practice": "Bitta murakkab vazifani turli effort darajalarida bajartirib, natijalarni solishtirish", "docs": ["api:build-with-claude/thinking", "api:build-with-claude/effort", "code:model-config"]},
{"id": "01-03", "tag": "claude", "title": "Claude surfaces va Claude uchun prompting", "goal": "claude.ai, Claude Code, Desktop, Web, mobile va API qachon kerakligi; XML tags bilan prompting", "practice": "Bitta promptni XML tags bilan qayta yozish va qaysi ish uchun qaysi surface qulayligini xaritalash", "docs": ["code:platforms", "api:build-with-claude/prompt-engineering/claude-prompting-best-practices"]}
]},
{"number": "02", "slug": "claude-code-asoslari", "title": "Claude Code asoslari", "lessons": [
{"id": "02-01", "tag": "claude", "title": "Claude Code qanday ishlaydi", "goal": "Agentic loop, built-in tools va Claude Code arxitekturasini tushunish", "practice": "Flutter loyihada Claude ga savol berib, qaysi tool lar va nima uchun ishlatilganini tahlil qilish", "docs": ["code:how-claude-code-works", "code:tools-reference", "code:features-overview"]},
{"id": "02-02", "tag": "claude", "title": "Interactive mode va buyruqlar", "goal": "Slash commands, @ mentions, ! bash mode va shortcut larni erkin ishlatish", "practice": "Eng foydali 10 ta buyruq va shortcut dan shaxsiy cheat sheet tuzish", "docs": ["code:interactive-mode", "code:commands"]},
{"id": "02-03", "tag": "claude", "title": ".claude papka va CLAUDE.md", "goal": "Memory ierarxiyasi (user, project, local), /init va CLAUDE.md best practices", "practice": "Flutter loyihangiz uchun arxitektura, buyruqlar va qoidalarni oʻz ichiga olgan CLAUDE.md yozish", "docs": ["code:claude-directory", "code:memory"]},
{"id": "02-04", "tag": "claude", "title": "Context window boshqaruvi", "goal": "/context, /compact, /clear va prompt caching bilan context ni samarali boshqarish", "practice": "Uzun session da /context ni kuzatib, qachon /compact yoki /clear kerakligini aniqlash", "docs": ["code:context-window", "code:prompt-caching"]},
{"id": "02-05", "tag": "claude", "title": "Sessions", "goal": "Session larni resume, continue, fork qilish va nomlash", "practice": "Bitta vazifani 2 ta session ga boʻlib, --resume va --continue bilan davom ettirish", "docs": ["code:sessions"]},
{"id": "02-06", "tag": "claude", "title": "Permission modes va permissions", "goal": "default, acceptEdits, plan va auto rejimlari hamda allow/deny qoidalarini tushunish", "practice": "Loyiha uchun xavfsiz permission qoidalarini yozish (flutter test ruxsat, xavfli buyruqlar taqiq)", "docs": ["code:permission-modes", "code:permissions"]},
{"id": "02-07", "tag": "claude", "title": "Checkpointing va model sozlamalari", "goal": "/rewind bilan oʻzgarishlarni qaytarish, /model, fast mode va advisor ni ishlatish", "practice": "Ataylab notoʻgʻri oʻzgarish qildirib, /rewind bilan qaytarish; model va effort ni almashtirib koʻrish", "docs": ["code:checkpointing", "code:model-config", "code:fast-mode", "code:advisor"]}
]},
{"number": "03", "slug": "professional-workflow", "title": "Professional workflow", "lessons": [
{"id": "03-01", "tag": "claude", "title": "Claude Code best practices", "goal": "Explore → plan → code → commit oqimi va aniq prompt yozish qoidalari", "practice": "Flutter loyihada kichik feature ni toʻliq explore → plan → code → commit oqimi bilan qilish", "docs": ["code:best-practices", "code:common-workflows"]},
{"id": "03-02", "tag": "claude", "title": "Plan mode chuqur", "goal": "Plan mode qachon kerakligini bilish, plan ni tahrirlash va tasdiqlash", "practice": "Oʻrtacha murakkab refactoring ni plan mode da rejalashtirib, plan ni 2 marta takomillashtirish", "docs": ["code:permission-modes", "code:common-workflows"]},
{"id": "03-03", "tag": "claude", "title": "Git workflow va worktrees", "goal": "Claude bilan commit, branch, PR va parallel worktree session lar", "practice": "Ikki feature ni 2 ta worktree da parallel session larda ishlab, merge qilish", "docs": ["code:worktrees", "code:common-workflows"]},
{"id": "03-04", "tag": "claude", "title": "Claude bilan debugging", "goal": "Xatoni reproduce qilish, log tahlili va root cause ni topish metodikasi", "practice": "Flutter loyihaga ataylab kiritilgan bug ni Claude bilan tizimli debugging orqali topish", "docs": ["code:common-workflows", "code:troubleshooting"]},
{"id": "03-05", "tag": "claude", "title": "Claude bilan TDD", "goal": "Test-first prompting va verification loop orqali ishonchli kod yozish", "practice": "Dart utility funksiyasini TDD bilan yozish: avval test, keyin implementation", "docs": ["code:best-practices"]},
{"id": "03-06", "tag": "claude", "title": "Code review va xavfsizlik", "goal": "/code-review, security guidance va ultrareview imkoniyatlarini ishlatish", "practice": "Oʻz kodingizda /code-review ishlatib, topilgan muammolarni tahlil qilish va tuzatish", "docs": ["code:code-review-local", "code:ultrareview", "code:security-guidance"]}
]},
{"number": "04", "slug": "customization", "title": "Customization", "lessons": [
{"id": "04-01", "tag": "claude", "title": "Settings va precedence", "goal": "User, project, local va managed settings qatlamlari qanday ishlashini tushunish", "practice": "Shu repo uchun .claude/settings.json yaratib, precedence ni tajribada tekshirish", "docs": ["code:settings", "code:settings-reference"]},
{"id": "04-02", "tag": "claude", "title": "Chuqur permissions va sandboxing", "goal": "Murakkab permission qoidalari va sandboxed Bash bilan xavfsiz ishlash", "practice": "Sandboxing ni yoqib, tarmoq va fayl tizimi cheklovlarini sinab koʻrish", "docs": ["code:permissions", "code:sandboxing"]},
{"id": "04-03", "tag": "claude", "title": "Skills I: skill anatomiyasi", "goal": "SKILL.md tuzilishi, frontmatter, arguments va dynamic context injection", "practice": "/dars skill ini tahlil qilib, uning har bir qismi nima qilishini tushuntirish", "docs": ["code:skills"]},
{"id": "04-04", "tag": "claude", "title": "Skills II: oʻz skill ingizni yaratish", "goal": "Real ish uchun qayta ishlatiladigan skill yozish va sinash", "practice": "Flutter feature scaffolding (Clean Architecture qatlamlari) uchun skill yozish", "docs": ["code:skills", "api:agents-and-tools/agent-skills/best-practices"]},
{"id": "04-05", "tag": "claude", "title": "Subagents", "goal": "Built-in va custom subagent lar, ularning context va tool cheklovlari", "practice": "Flutter code reviewer subagent yaratib, loyihada ishlatish", "docs": ["code:sub-agents"]},
{"id": "04-06", "tag": "claude", "title": "Hooks", "goal": "Lifecycle event lar (PreToolUse, PostToolUse, Stop) bilan automation qurish", "practice": "progress.json oʻzgarganda vizual HTML roadmap ni avtomatik yangilaydigan hook yozish", "docs": ["code:hooks-guide", "code:hooks"]},
{"id": "04-07", "tag": "claude", "title": "MCP", "goal": "MCP protokoli, server ulash, scope lar va xavfsizlik", "practice": "Foydali MCP server (masalan GitHub yoki Figma) ulab, real vazifada ishlatish", "docs": ["code:mcp-quickstart", "code:mcp"]},
{"id": "04-08", "tag": "claude", "title": "Output styles, statusline va keybindings", "goal": "Claude Code interfeysi va javob uslubini oʻzingizga moslash", "practice": "Joriy dars va streak ni koʻrsatadigan statusline yozish", "docs": ["code:output-styles", "code:statusline", "code:keybindings"]},
{"id": "04-09", "tag": "claude", "title": "Plugins", "goal": "Plugin larni oʻrnatish, marketplace lar va oʻz plugin ingizni yaratish", "practice": "Oʻz skill, subagent va hook laringizni bitta plugin ga yigʻish", "docs": ["code:plugins/overview", "code:plugins/install", "code:plugins/create"]}
]},
{"number": "05", "slug": "automation", "title": "Automation va multi-agent", "lessons": [
{"id": "05-01", "tag": "claude", "title": "Headless mode", "goal": "claude -p, output formatlari va Claude ni script lardan ishlatish", "practice": "Git diff dan avtomatik CHANGELOG yozadigan headless script yaratish", "docs": ["code:headless", "code:cli-reference"]},
{"id": "05-02", "tag": "claude", "title": "GitHub Actions va CI", "goal": "Claude Code ni CI/CD pipeline ga ulash", "practice": "GitHub repo da PR larni avtomatik review qiladigan Claude workflow sozlash", "docs": ["code:github-actions"]},
{"id": "05-03", "tag": "claude", "title": "Scheduled tasks va routines", "goal": "/loop, cron, cloud routines va desktop scheduled tasks farqini bilish", "practice": "remind.py ga Telegram bot orqali telefon eslatmasini qoʻshish", "docs": ["code:scheduled-tasks", "code:routines", "code:desktop-scheduled-tasks"]},
{"id": "05-04", "tag": "claude", "title": "/goal va uzoq ishlaydigan vazifalar", "goal": "Claude ni aniq yakunlash sharti bilan mustaqil ishlatish", "practice": "/goal bilan kichik loyihada barcha test lar oʻtguncha ishlatish", "docs": ["code:goal"]},
{"id": "05-05", "tag": "claude", "title": "Multi-agent: parallel agents, teams va workflows", "goal": "Parallel agent lar, agent teams va dynamic workflows qachon kerakligini bilish", "practice": "Katta vazifani parallel subagent larga boʻlib bajartirish va natijani solishtirish", "docs": ["code:agents", "code:agent-teams", "code:workflows"]},
{"id": "05-06", "tag": "claude", "title": "Channels, artifacts va remote ishlash", "goal": "Channels, artifacts, Remote Control, web va mobile dan Claude Code bilan ishlash", "practice": "Dars xulosalaringizdan artifact sahifa yaratish va telefondan Remote Control bilan ulanish", "docs": ["code:channels", "code:artifacts", "code:remote-control", "code:claude-code-on-the-web"]}
]},
{"number": "06", "slug": "claude-api", "title": "Claude API", "lessons": [
{"id": "06-01", "tag": "mix", "title": "Messages API asoslari", "goal": "API key, birinchi request, message threads va stop reasons", "practice": "curl va Dart da Messages API ga birinchi soʻrovni yuborish", "docs": ["api:get-started", "api:build-with-claude/working-with-messages", "api:build-with-claude/handling-stop-reasons", "api:about-claude/api-credits-for-subscribers"]},
{"id": "06-02", "tag": "mix", "title": "Streaming", "goal": "SSE event lari va real-time javobni qayta ishlash", "practice": "Dart da javobni token-by-token chiqaradigan streaming client yozish", "docs": ["api:build-with-claude/streaming"]},
{"id": "06-03", "tag": "mix", "title": "Tool use I: tool lar va agent loop", "goal": "Tool larni aniqlash, tool call larni qayta ishlash va agent loop yozish", "practice": "Ob-havo va kalkulyator tool lari bilan oddiy agent loop yozish", "docs": ["api:agents-and-tools/tool-use/overview", "api:agents-and-tools/tool-use/define-tools", "api:agents-and-tools/tool-use/handle-tool-calls"]},
{"id": "06-04", "tag": "mix", "title": "Tool use II: server tools va tool runner", "goal": "Web search, code execution, tool runner, parallel va strict tool use", "practice": "Web search tool bilan manbalar keltirib javob beradigan script yozish", "docs": ["api:agents-and-tools/tool-use/server-tools", "api:agents-and-tools/tool-use/tool-runner", "api:agents-and-tools/tool-use/parallel-tool-use", "api:agents-and-tools/tool-use/strict-tool-use"]},
{"id": "06-05", "tag": "mix", "title": "Structured outputs, vision va PDF", "goal": "JSON schema bilan ishonchli output, rasm va PDF tahlili", "practice": "Ilova skrinshotidan UI elementlar roʻyxatini JSON shaklida chiqarish", "docs": ["api:build-with-claude/structured-outputs", "api:build-with-claude/vision", "api:build-with-claude/pdf-support"]},
{"id": "06-06", "tag": "mix", "title": "Prompt caching, token counting va narx", "goal": "Caching bilan narx va latency ni kamaytirish, xarajatni hisoblash", "practice": "Bir xil soʻrovlarni caching bilan va caching siz yuborib, narxini solishtirish", "docs": ["api:build-with-claude/prompt-caching", "api:build-with-claude/token-counting", "api:about-claude/pricing"]},
{"id": "06-07", "tag": "mix", "title": "Context management: compaction va memory", "goal": "Context editing, compaction va memory tool bilan uzun suhbatlarni boshqarish", "practice": "Uzun chat uchun compaction strategiyasini sinab koʻrish", "docs": ["api:build-with-claude/context-editing", "api:build-with-claude/compaction", "api:agents-and-tools/tool-use/memory-tool"]},
{"id": "06-08", "tag": "mix", "title": "Batch, Files API, evals va guardrails", "goal": "Ommaviy ishlov, fayllar, sifatni oʻlchash va prompt injection dan himoya", "practice": "20 ta test case bilan oddiy eval yozib, promptni yaxshilash", "docs": ["api:build-with-claude/batch-processing", "api:build-with-claude/files", "api:test-and-evaluate/develop-tests", "api:test-and-evaluate/strengthen-guardrails/mitigate-jailbreaks"]}
]},
{"number": "07", "slug": "agent-sdk", "title": "Agent SDK", "lessons": [
{"id": "07-01", "tag": "claude", "title": "Agent SDK va agent loop", "goal": "Agent SDK nima, Claude Code bilan aloqasi va agent loop qanday ishlaydi", "practice": "Quickstart asosida birinchi agent ni ishga tushirish", "docs": ["code:agent-sdk/overview", "code:agent-sdk/quickstart", "code:agent-sdk/agent-loop"]},
{"id": "07-02", "tag": "claude", "title": "Custom tools va MCP", "goal": "SDK da oʻz tool laringiz va MCP server larni ulash", "practice": "Loyiha fayllarini tahlil qiladigan custom tool li agent yozish", "docs": ["code:agent-sdk/custom-tools", "code:agent-sdk/mcp"]},
{"id": "07-03", "tag": "claude", "title": "Permissions, hooks va sessions", "goal": "Agent xatti-harakatini nazorat qilish va session larni boshqarish", "practice": "Xavfli buyruqlarni bloklaydigan hook li agent yozish", "docs": ["code:agent-sdk/permissions", "code:agent-sdk/hooks", "code:agent-sdk/sessions"]},
{"id": "07-04", "tag": "claude", "title": "Hosting va xavfsiz deploy", "goal": "Agent ni production ga xavfsiz chiqarish va xarajatni kuzatish", "practice": "Agent uchun deploy rejasi va xavfsizlik checklist ini tuzish", "docs": ["code:agent-sdk/hosting", "code:agent-sdk/secure-deployment", "code:agent-sdk/cost-tracking"]}
]},
{"number": "08", "slug": "capstone", "title": "Capstone: AI mobile ilova", "lessons": [
{"id": "08-01", "tag": "project", "title": "Arxitektura va backend proxy", "goal": "Flutter ilova ↔ proxy ↔ Claude API arxitekturasi va API key xavfsizligi", "practice": "Dart (shelf) da Claude API uchun proxy server yozish", "docs": ["api:get-api-key", "api:manage-claude/authentication"]},
{"id": "08-02", "tag": "project", "title": "Streaming chat UI", "goal": "SSE stream ni Flutter UI ga (BLoC) ulash", "practice": "Javob token-by-token chiqadigan chat ekranini qurish", "docs": ["api:build-with-claude/streaming"]},
{"id": "08-03", "tag": "project", "title": "Mobile da tool use", "goal": "Ilova funksiyalarini Claude ga tool sifatida berish", "practice": "Chat ga 2 ta app tool qoʻshish (masalan eslatma yaratish va qidiruv)", "docs": ["api:agents-and-tools/tool-use/overview", "api:agents-and-tools/tool-use/handle-tool-calls"]},
{"id": "08-04", "tag": "project", "title": "Narx, xatolar va production", "goal": "Prompt caching, rate limits, error handling va foydalanuvchi limitlari", "practice": "Proxy ga caching, retry va foydalanuvchi limitini qoʻshish", "docs": ["api:build-with-claude/prompt-caching", "api:build-with-claude/handling-stop-reasons"]},
{"id": "08-05", "tag": "project", "title": "CI, review va yakuniy retrospektiva", "goal": "Claude GitHub Actions bilan CI va butun kurs boʻyicha xulosa", "practice": "Capstone repo ga Claude review workflow qoʻshish va kurs retrospektivasini yozish", "docs": ["code:github-actions"]}
]}
]}
```
