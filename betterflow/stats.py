"""
Stats tracker — tracks dictation history, word counts, and streaks.
Stores data in ~/.betterflow/stats.json
"""

import json
from datetime import date, timedelta
from pathlib import Path
from betterflow.config import CONFIG_DIR

STATS_FILE = CONFIG_DIR / "stats.json"


def _load_stats() -> dict:
    """Load stats from disk."""
    if STATS_FILE.exists():
        try:
            with open(STATS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"days": {}, "total_words": 0, "total_dictations": 0}


def _save_stats(stats: dict):
    """Write stats to disk."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)


def record_dictation(text: str):
    """Record a completed dictation (call after each successful transcription)."""
    stats = _load_stats()
    today = date.today().isoformat()
    word_count = len(text.split())

    if today not in stats["days"]:
        stats["days"][today] = {"words": 0, "dictations": 0}

    stats["days"][today]["words"] += word_count
    stats["days"][today]["dictations"] += 1
    stats["total_words"] += word_count
    stats["total_dictations"] += 1
    _save_stats(stats)


def get_today_stats() -> dict:
    """Get today's word count and dictation count."""
    stats = _load_stats()
    today = date.today().isoformat()
    day = stats["days"].get(today, {"words": 0, "dictations": 0})
    return day


def get_streak() -> int:
    """Calculate current consecutive-day streak."""
    stats = _load_stats()
    if not stats["days"]:
        return 0
    today = date.today()
    streak = 0
    check_date = today
    while check_date.isoformat() in stats["days"]:
        streak += 1
        check_date -= timedelta(days=1)
    return streak


def get_week_words() -> int:
    """Get total words in the last 7 days."""
    stats = _load_stats()
    total = 0
    today = date.today()
    for i in range(7):
        day_key = (today - timedelta(days=i)).isoformat()
        if day_key in stats["days"]:
            total += stats["days"][day_key]["words"]
    return total


def get_month_words() -> int:
    """Get total words in the current month."""
    stats = _load_stats()
    today = date.today()
    total = 0
    for day_key, day_data in stats["days"].items():
        if day_key.startswith(today.strftime("%Y-%m")):
            total += day_data["words"]
    return total


def get_total_stats() -> dict:
    """Get all-time totals."""
    stats = _load_stats()
    return {
        "total_words": stats.get("total_words", 0),
        "total_dictations": stats.get("total_dictations", 0),
        "days_active": len(stats.get("days", {})),
    }
