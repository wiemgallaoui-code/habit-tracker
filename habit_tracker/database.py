"""SQLite database layer for habit tracking."""

from __future__ import annotations

import sqlite3
from datetime import date, datetime
from pathlib import Path

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "data" / "habits.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS habits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE COLLATE NOCASE,
    created_at TEXT NOT NULL,
    start_date TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS completions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    habit_id INTEGER NOT NULL,
    completed_on TEXT NOT NULL,
    FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE,
    UNIQUE (habit_id, completed_on)
);
"""

HABIT_COLUMNS = "id, name, created_at, start_date"


def _migrate_schema(conn: sqlite3.Connection) -> None:
    columns = {row[1] for row in conn.execute("PRAGMA table_info(habits)")}
    if "start_date" not in columns:
        conn.execute("ALTER TABLE habits ADD COLUMN start_date TEXT")
        conn.execute(
            """
            UPDATE habits
            SET start_date = substr(created_at, 1, 10)
            WHERE start_date IS NULL OR start_date = ''
            """
        )
        conn.commit()


def get_connection(db_path: Path | str | None = None) -> sqlite3.Connection:
    """Open a SQLite connection with foreign keys enabled."""
    path = Path(db_path) if db_path else DEFAULT_DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(db_path: Path | str | None = None) -> None:
    """Create tables if they do not exist."""
    with get_connection(db_path) as conn:
        conn.executescript(SCHEMA)
        _migrate_schema(conn)


def add_habit(
    name: str,
    start_date: date | None = None,
    db_path: Path | str | None = None,
) -> sqlite3.Row:
    """Insert a habit and return the new row."""
    created_at = datetime.now().isoformat(timespec="seconds")
    tracking_start = (start_date or date.today()).isoformat()
    with get_connection(db_path) as conn:
        cursor = conn.execute(
            "INSERT INTO habits (name, created_at, start_date) VALUES (?, ?, ?)",
            (name.strip(), created_at, tracking_start),
        )
        conn.commit()
        row = conn.execute(
            f"SELECT {HABIT_COLUMNS} FROM habits WHERE id = ?",
            (cursor.lastrowid,),
        ).fetchone()
    if row is None:
        raise RuntimeError("Failed to create habit.")
    return row


def list_habits(db_path: Path | str | None = None) -> list[sqlite3.Row]:
    """Return all habits ordered by name."""
    with get_connection(db_path) as conn:
        rows = conn.execute(
            f"SELECT {HABIT_COLUMNS} FROM habits ORDER BY name COLLATE NOCASE"
        ).fetchall()
    return list(rows)


def get_habit_by_id(habit_id: int, db_path: Path | str | None = None) -> sqlite3.Row | None:
    """Return a habit by id, or None if not found."""
    with get_connection(db_path) as conn:
        return conn.execute(
            f"SELECT {HABIT_COLUMNS} FROM habits WHERE id = ?",
            (habit_id,),
        ).fetchone()


def get_habit_by_name(name: str, db_path: Path | str | None = None) -> sqlite3.Row | None:
    """Return a habit by name (case-insensitive), or None if not found."""
    with get_connection(db_path) as conn:
        return conn.execute(
            f"SELECT {HABIT_COLUMNS} FROM habits WHERE name = ? COLLATE NOCASE",
            (name.strip(),),
        ).fetchone()


def update_start_date(
    habit_id: int,
    start_date: date,
    db_path: Path | str | None = None,
) -> sqlite3.Row | None:
    """Update the tracking start date for a habit."""
    with get_connection(db_path) as conn:
        conn.execute(
            "UPDATE habits SET start_date = ? WHERE id = ?",
            (start_date.isoformat(), habit_id),
        )
        conn.commit()
        return conn.execute(
            f"SELECT {HABIT_COLUMNS} FROM habits WHERE id = ?",
            (habit_id,),
        ).fetchone()


def remove_habit(habit_id: int, db_path: Path | str | None = None) -> bool:
    """Delete a habit and its completions. Returns True if a row was deleted."""
    with get_connection(db_path) as conn:
        cursor = conn.execute("DELETE FROM habits WHERE id = ?", (habit_id,))
        conn.commit()
        return cursor.rowcount > 0


def log_completion(
    habit_id: int,
    completed_on: date | None = None,
    db_path: Path | str | None = None,
) -> sqlite3.Row:
    """Record a completion for a habit on a given date (defaults to today)."""
    day = (completed_on or date.today()).isoformat()
    with get_connection(db_path) as conn:
        conn.execute(
            "INSERT INTO completions (habit_id, completed_on) VALUES (?, ?)",
            (habit_id, day),
        )
        conn.commit()
        row = conn.execute(
            """
            SELECT id, habit_id, completed_on
            FROM completions
            WHERE habit_id = ? AND completed_on = ?
            """,
            (habit_id, day),
        ).fetchone()
    if row is None:
        raise RuntimeError("Failed to log completion.")
    return row


def get_completions(
    habit_id: int,
    db_path: Path | str | None = None,
) -> list[sqlite3.Row]:
    """Return all completion dates for a habit, newest first."""
    with get_connection(db_path) as conn:
        rows = conn.execute(
            """
            SELECT id, habit_id, completed_on
            FROM completions
            WHERE habit_id = ?
            ORDER BY completed_on DESC
            """,
            (habit_id,),
        ).fetchall()
    return list(rows)


def is_completed_on(
    habit_id: int,
    completed_on: date,
    db_path: Path | str | None = None,
) -> bool:
    """Return True if the habit was completed on the given date."""
    with get_connection(db_path) as conn:
        row = conn.execute(
            """
            SELECT 1 FROM completions
            WHERE habit_id = ? AND completed_on = ?
            """,
            (habit_id, completed_on.isoformat()),
        ).fetchone()
    return row is not None
