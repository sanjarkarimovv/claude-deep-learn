#!/usr/bin/env python3
"""Claude Deep Learn: oʻquv progress ini boshqaruvchi CLI.

/dars skill holatni faqat shu CLI orqali oʻzgartiradi. JSON ni qoʻlda
tahrirlash xatoga olib keladi, CLI esa testlar bilan himoyalangan.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import List, Optional

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_STATE_DIR = Path.home() / ".claude-deep-learn"
TAG_ICONS = {"ai": "🧠", "claude": "🟠", "mix": "🟠🧠", "project": "📱"}
DOC_PREFIXES = {
    "code": "https://code.claude.com/docs/en/",
    "api": "https://platform.claude.com/docs/en/",
}
WEEKDAYS = ["Dushanba", "Seshanba", "Chorshanba", "Payshanba", "Juma", "Shanba", "Yakshanba"]
SATURDAY, SUNDAY = 5, 6


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
