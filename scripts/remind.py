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
