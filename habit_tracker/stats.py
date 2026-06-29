"""Streak and completion statistics for habits."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta

from habit_tracker.database import get_completions, get_habit_by_id, list_habits


@dataclass(frozen=True)
class HabitStats:
    habit_id: int
    name: str
    created_on: date
    tracking_start: date
    total_completions: int
    current_streak: int
    longest_streak: int
    completion_rate: float
    days_tracked: int
    completed_today: bool
    last_completed: date | None


def _completion_dates(habit_id: int) -> set[date]:
    return {
        date.fromisoformat(row["completed_on"])
        for row in get_completions(habit_id)
    }


def _current_streak(completion_dates: set[date], today: date) -> int:
    if not completion_dates:
        return 0

    cursor = today if today in completion_dates else today - timedelta(days=1)
    if cursor not in completion_dates:
        return 0

    streak = 0
    while cursor in completion_dates:
        streak += 1
        cursor -= timedelta(days=1)
    return streak


def _longest_streak(completion_dates: set[date]) -> int:
    if not completion_dates:
        return 0

    sorted_dates = sorted(completion_dates)
    longest = 1
    current = 1
    for index in range(1, len(sorted_dates)):
        if sorted_dates[index] - sorted_dates[index - 1] == timedelta(days=1):
            current += 1
            longest = max(longest, current)
        else:
            current = 1
    return longest


def _habit_created_on(created_at: str) -> date:
    return datetime.fromisoformat(created_at).date()


def _habit_tracking_start(habit) -> date:
    return date.fromisoformat(habit["start_date"])


def get_habit_stats(habit_id: int, today: date | None = None) -> HabitStats | None:
    """Return stats for one habit, or None if the habit does not exist."""
    habit = get_habit_by_id(habit_id)
    if habit is None:
        return None

    today = today or date.today()
    created_on = _habit_created_on(habit["created_at"])
    tracking_start = _habit_tracking_start(habit)
    all_completion_dates = _completion_dates(habit_id)
    completion_dates = {
        day
        for day in all_completion_dates
        if tracking_start <= day <= today
    }
    days_tracked = max((today - tracking_start).days + 1, 1)
    total = len(completion_dates)
    rate = round(min((total / days_tracked) * 100, 100.0), 1)
    last_completed = max(all_completion_dates) if all_completion_dates else None

    return HabitStats(
        habit_id=habit["id"],
        name=habit["name"],
        created_on=created_on,
        tracking_start=tracking_start,
        total_completions=total,
        current_streak=_current_streak(all_completion_dates, today),
        longest_streak=_longest_streak(all_completion_dates),
        completion_rate=rate,
        days_tracked=days_tracked,
        completed_today=today in completion_dates,
        last_completed=last_completed,
    )


def get_all_habit_stats(today: date | None = None) -> list[HabitStats]:
    """Return stats for every habit."""
    today = today or date.today()
    stats: list[HabitStats] = []
    for habit in list_habits():
        habit_stats = get_habit_stats(habit["id"], today=today)
        if habit_stats is not None:
            stats.append(habit_stats)
    return stats
