"""FastAPI backend for the Habit Tracker web app."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import sqlite3
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from backend.schemas import (
    CheckRequest,
    HabitCreate,
    HabitResponse,
    MessageResponse,
    StartDateUpdate,
    StatsResponse,
)
from habit_tracker.charts import save_completion_chart
from habit_tracker.database import (
    add_habit,
    get_habit_by_id,
    init_db,
    log_completion,
    remove_habit,
    update_start_date,
)
from habit_tracker.stats import HabitStats, get_all_habit_stats, get_habit_stats

app = FastAPI(title="Habit Tracker API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _stats_to_response(stats: HabitStats) -> StatsResponse:
    return StatsResponse(
        habit_id=stats.habit_id,
        name=stats.name,
        created_on=stats.created_on.isoformat(),
        tracking_start=stats.tracking_start.isoformat(),
        total_completions=stats.total_completions,
        current_streak=stats.current_streak,
        longest_streak=stats.longest_streak,
        completion_rate=stats.completion_rate,
        days_tracked=stats.days_tracked,
        completed_today=stats.completed_today,
        last_completed=stats.last_completed.isoformat() if stats.last_completed else None,
    )


def _habit_to_response(stats: HabitStats) -> HabitResponse:
    habit = get_habit_by_id(stats.habit_id)
    if habit is None:
        raise HTTPException(status_code=404, detail="Habit not found")
    return HabitResponse(
        id=stats.habit_id,
        name=stats.name,
        created_at=habit["created_at"],
        start_date=habit["start_date"],
        completed_today=stats.completed_today,
        current_streak=stats.current_streak,
        longest_streak=stats.longest_streak,
        total_completions=stats.total_completions,
        completion_rate=stats.completion_rate,
    )


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/habits", response_model=list[HabitResponse])
def get_habits() -> list[HabitResponse]:
    return [_habit_to_response(stats) for stats in get_all_habit_stats()]


@app.post("/api/habits", response_model=HabitResponse, status_code=201)
def create_habit(payload: HabitCreate) -> HabitResponse:
    name = payload.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Habit name cannot be empty")

    start_date: date | None = None
    if payload.start_date:
        try:
            start_date = date.fromisoformat(payload.start_date)
        except ValueError as error:
            raise HTTPException(status_code=400, detail="Start date must be YYYY-MM-DD") from error

    try:
        habit = add_habit(name, start_date=start_date)
    except sqlite3.IntegrityError as error:
        raise HTTPException(status_code=409, detail=f"Habit '{name}' already exists") from error

    stats = get_habit_stats(habit["id"])
    if stats is None:
        raise HTTPException(status_code=500, detail="Failed to load habit stats")
    return _habit_to_response(stats)


@app.patch("/api/habits/{habit_id}/start-date", response_model=HabitResponse)
def change_start_date(habit_id: int, payload: StartDateUpdate) -> HabitResponse:
    habit = get_habit_by_id(habit_id)
    if habit is None:
        raise HTTPException(status_code=404, detail="Habit not found")

    try:
        start_date = date.fromisoformat(payload.start_date)
    except ValueError as error:
        raise HTTPException(status_code=400, detail="Start date must be YYYY-MM-DD") from error

    updated = update_start_date(habit_id, start_date)
    if updated is None:
        raise HTTPException(status_code=500, detail="Failed to update start date")

    stats = get_habit_stats(habit_id)
    if stats is None:
        raise HTTPException(status_code=500, detail="Failed to load habit stats")
    return _habit_to_response(stats)


@app.delete("/api/habits/{habit_id}", response_model=MessageResponse)
def delete_habit(habit_id: int) -> MessageResponse:
    habit = get_habit_by_id(habit_id)
    if habit is None:
        raise HTTPException(status_code=404, detail="Habit not found")
    remove_habit(habit_id)
    return MessageResponse(message=f"Removed habit '{habit['name']}'")


@app.post("/api/habits/{habit_id}/check", response_model=MessageResponse)
def check_habit(habit_id: int, payload: CheckRequest | None = None) -> MessageResponse:
    habit = get_habit_by_id(habit_id)
    if habit is None:
        raise HTTPException(status_code=404, detail="Habit not found")

    completed_on: date | None = None
    if payload and payload.date:
        try:
            completed_on = date.fromisoformat(payload.date)
        except ValueError as error:
            raise HTTPException(status_code=400, detail="Date must be YYYY-MM-DD") from error

    try:
        completion = log_completion(habit_id, completed_on=completed_on)
    except sqlite3.IntegrityError as error:
        day = (completed_on or date.today()).isoformat()
        raise HTTPException(
            status_code=409,
            detail=f"Already checked off on {day}",
        ) from error

    return MessageResponse(
        message=f"Checked off '{habit['name']}' for {completion['completed_on']}"
    )


@app.get("/api/habits/{habit_id}/stats", response_model=StatsResponse)
def habit_stats(habit_id: int) -> StatsResponse:
    stats = get_habit_stats(habit_id)
    if stats is None:
        raise HTTPException(status_code=404, detail="Habit not found")
    return _stats_to_response(stats)


@app.get("/api/stats", response_model=list[StatsResponse])
def all_stats() -> list[StatsResponse]:
    return [_stats_to_response(stats) for stats in get_all_habit_stats()]


@app.get("/api/habits/{habit_id}/chart")
def habit_chart(
    habit_id: int,
    days: int = Query(default=7, ge=1, le=90),
) -> FileResponse:
    habit = get_habit_by_id(habit_id)
    if habit is None:
        raise HTTPException(status_code=404, detail="Habit not found")

    try:
        chart_path = save_completion_chart(habit_id, habit["name"], days=days)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    return FileResponse(
        path=Path(chart_path),
        media_type="image/png",
        filename=chart_path.name,
    )
