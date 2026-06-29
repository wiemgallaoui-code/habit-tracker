"""Command-line interface for habit management."""

from __future__ import annotations

import argparse
import sqlite3
import sys
from datetime import date

from habit_tracker.database import (
    add_habit,
    get_habit_by_id,
    get_habit_by_name,
    init_db,
    list_habits,
    log_completion,
    remove_habit,
)


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

    print(f"{'ID':<6}{'Name'}")
    print("-" * 30)
    for habit in habits:
        print(f"{habit['id']:<6}{habit['name']}")
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

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    init_db()
    return args.func(args)
