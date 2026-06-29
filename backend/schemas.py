"""Pydantic schemas for the REST API."""

from __future__ import annotations

from pydantic import BaseModel, Field


class HabitCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    start_date: str | None = None


class StartDateUpdate(BaseModel):
    start_date: str


class CheckRequest(BaseModel):
    date: str | None = None


class HabitResponse(BaseModel):
    id: int
    name: str
    created_at: str
    start_date: str
    completed_today: bool
    current_streak: int
    longest_streak: int
    total_completions: int
    completion_rate: float


class StatsResponse(BaseModel):
    habit_id: int
    name: str
    created_on: str
    tracking_start: str
    total_completions: int
    current_streak: int
    longest_streak: int
    completion_rate: float
    days_tracked: int
    completed_today: bool
    last_completed: str | None


class MessageResponse(BaseModel):
    message: str
