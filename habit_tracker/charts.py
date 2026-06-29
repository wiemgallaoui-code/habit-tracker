"""Matplotlib charts for habit completion data."""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from habit_tracker.database import get_completions

CHARTS_DIR = Path(__file__).resolve().parent.parent / "charts"


def _sanitize_filename(name: str) -> str:
    cleaned = "".join(char if char.isalnum() else "_" for char in name.lower())
    return cleaned.strip("_") or "habit"


def _completion_dates(habit_id: int) -> set[date]:
    return {
        date.fromisoformat(row["completed_on"])
        for row in get_completions(habit_id)
    }


def save_completion_chart(
    habit_id: int,
    habit_name: str,
    days: int = 7,
    end_date: date | None = None,
) -> Path:
    """Save a bar chart of daily completions and return the file path."""
    if days < 1:
        raise ValueError("days must be at least 1")

    end = end_date or date.today()
    start = end - timedelta(days=days - 1)
    completed = _completion_dates(habit_id)

    dates = [start + timedelta(days=offset) for offset in range(days)]
    values = [1 if day in completed else 0 for day in dates]
    labels = [day.strftime("%m/%d") for day in dates]
    colors = ["#27ae60" if value else "#c0392b" for value in values]

    fig, ax = plt.subplots(figsize=(max(8, days * 0.5), 4))
    ax.bar(labels, values, color=colors, width=0.7)
    ax.set_ylim(0, 1.2)
    ax.set_yticks([0, 1])
    ax.set_yticklabels(["Missed", "Done"])
    ax.set_title(f"{habit_name} — last {days} day(s)")
    ax.set_xlabel("Date")

    done_count = sum(values)
    ax.text(
        0.02,
        0.95,
        f"Completed: {done_count}/{days}",
        transform=ax.transAxes,
        fontsize=10,
        verticalalignment="top",
    )

    plt.tight_layout()

    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    output_path = CHARTS_DIR / f"{_sanitize_filename(habit_name)}_{days}days.png"
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path
