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
