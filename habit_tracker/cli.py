"""Command-line interface for habit management."""

from __future__ import annotations

import argparse
import sqlite3
import sys
from datetime import date

from habit_tracker.charts import save_completion_chart
from habit_tracker.database import (
    add_habit,
    get_habit_by_id,
    get_habit_by_name,
    init_db,
    is_completed_on,
    list_habits,
    log_completion,
    remove_habit,
)
from habit_tracker.stats import get_all_habit_stats, get_habit_stats


def _resolve_habit(target: str):
    if target.isdigit():
        return get_habit_by_id(int(target))
    return get_habit_by_name(target)


def cmd_add(args: argparse.Namespace) -> int:
    name = args.name.strip()
    if not name:
        print("Error: habit name cannot be empty.", file=sys.stderr)
        return 1
    try:
        habit = add_habit(name)
    except sqlite3.IntegrityError:
        print(f"Error: habit '{name}' already exists.", file=sys.stderr)
        return 1
    print(f"Added habit #{habit['id']}: {habit['name']}")
    return 0


def cmd_list(_: argparse.Namespace) -> int:
    habits = list_habits()
    if not habits:
        print('No habits yet. Add one with: python -m habit_tracker add "Your habit"')
        return 0

    today = date.today()
    print(f"{'ID':<6}{'Name':<22}{'Today'}")
    print("-" * 40)
    for habit in habits:
        done = "yes" if is_completed_on(habit["id"], today) else "no"
        print(f"{habit['id']:<6}{habit['name']:<22}{done}")
    return 0


def cmd_remove(args: argparse.Namespace) -> int:
    habit = _resolve_habit(args.target)
    if habit is None:
        print(f"Error: no habit found for '{args.target}'.", file=sys.stderr)
        return 1

    if remove_habit(habit["id"]):
        print(f"Removed habit #{habit['id']}: {habit['name']}")
        return 0

    print(f"Error: could not remove habit '{args.target}'.", file=sys.stderr)
    return 1


def cmd_check(args: argparse.Namespace) -> int:
    habit = _resolve_habit(args.target)
    if habit is None:
        print(f"Error: no habit found for '{args.target}'.", file=sys.stderr)
        return 1

    completed_on: date | None = None
    if args.date:
        try:
            completed_on = date.fromisoformat(args.date)
        except ValueError:
            print("Error: date must be YYYY-MM-DD.", file=sys.stderr)
            return 1

    try:
        completion = log_completion(habit["id"], completed_on=completed_on)
    except sqlite3.IntegrityError:
        day = (completed_on or date.today()).isoformat()
        print(
            f"Error: '{habit['name']}' was already checked off on {day}.",
            file=sys.stderr,
        )
        return 1

    print(f"Checked off '{habit['name']}' for {completion['completed_on']}.")
    return 0


def _print_habit_stats(stats) -> None:
    today_label = "yes" if stats.completed_today else "no"
    last_label = stats.last_completed.isoformat() if stats.last_completed else "never"

    print(f"Habit: {stats.name} (#{stats.habit_id})")
    print(f"Created: {stats.created_on.isoformat()}")
    print(f"Completed today: {today_label}")
    print(f"Last completed: {last_label}")
    print(f"Total completions: {stats.total_completions}")
    print(f"Current streak: {stats.current_streak} day(s)")
    print(f"Longest streak: {stats.longest_streak} day(s)")
    print(
        f"Completion rate: {stats.completion_rate}% "
        f"({stats.total_completions} of {stats.days_tracked} days)"
    )


def cmd_stats(args: argparse.Namespace) -> int:
    if args.target:
        habit = _resolve_habit(args.target)
        if habit is None:
            print(f"Error: no habit found for '{args.target}'.", file=sys.stderr)
            return 1
        stats = get_habit_stats(habit["id"])
        if stats is None:
            print(f"Error: no habit found for '{args.target}'.", file=sys.stderr)
            return 1
        _print_habit_stats(stats)
        return 0

    all_stats = get_all_habit_stats()
    if not all_stats:
        print('No habits yet. Add one with: python -m habit_tracker add "Your habit"')
        return 0

    print(
        f"{'ID':<6}{'Name':<18}{'Today':<7}{'Streak':<8}{'Best':<6}"
        f"{'Total':<7}{'Rate'}"
    )
    print("-" * 60)
    for stats in all_stats:
        today_label = "yes" if stats.completed_today else "no"
        print(
            f"{stats.habit_id:<6}{stats.name:<18}{today_label:<7}"
            f"{stats.current_streak:<8}{stats.longest_streak:<6}"
            f"{stats.total_completions:<7}{stats.completion_rate}%"
        )
    return 0


def cmd_chart(args: argparse.Namespace) -> int:
    habit = _resolve_habit(args.target)
    if habit is None:
        print(f"Error: no habit found for '{args.target}'.", file=sys.stderr)
        return 1

    if args.days < 1:
        print("Error: --days must be at least 1.", file=sys.stderr)
        return 1

    try:
        chart_path = save_completion_chart(
            habit["id"],
            habit["name"],
            days=args.days,
        )
    except ValueError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    print(f"Chart saved to {chart_path}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="habit_tracker",
        description="Track habits from the command line.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="Add a new habit")
    add_parser.add_argument("name", help="Habit name")
    add_parser.set_defaults(func=cmd_add)

    list_parser = subparsers.add_parser("list", help="List all habits")
    list_parser.set_defaults(func=cmd_list)

    remove_parser = subparsers.add_parser("remove", help="Remove a habit by id or name")
    remove_parser.add_argument("target", help="Habit id or name")
    remove_parser.set_defaults(func=cmd_remove)

    check_parser = subparsers.add_parser("check", help="Log a daily completion")
    check_parser.add_argument("target", help="Habit id or name")
    check_parser.add_argument(
        "--date",
        help="Completion date in YYYY-MM-DD format (defaults to today)",
    )
    check_parser.set_defaults(func=cmd_check)

    stats_parser = subparsers.add_parser("stats", help="Show streak and completion stats")
    stats_parser.add_argument(
        "target",
        nargs="?",
        help="Habit id or name (omit for summary of all habits)",
    )
    stats_parser.set_defaults(func=cmd_stats)

    chart_parser = subparsers.add_parser("chart", help="Save a completion chart as PNG")
    chart_parser.add_argument("target", help="Habit id or name")
    chart_parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Number of days to include (default: 7)",
    )
    chart_parser.set_defaults(func=cmd_chart)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    init_db()
    return args.func(args)
