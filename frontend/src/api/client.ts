import type { Habit, Stats } from "../types";

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(error.detail ?? "Request failed");
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

export function fetchHabits(): Promise<Habit[]> {
  return request<Habit[]>("/api/habits");
}

export function createHabit(name: string): Promise<Habit> {
  return request<Habit>("/api/habits", {
    method: "POST",
    body: JSON.stringify({ name }),
  });
}

export function deleteHabit(id: number): Promise<void> {
  return request<void>(`/api/habits/${id}`, { method: "DELETE" });
}

export function checkHabit(id: number): Promise<void> {
  return request<void>(`/api/habits/${id}/check`, {
    method: "POST",
    body: JSON.stringify({}),
  });
}

export function fetchStats(): Promise<Stats[]> {
  return request<Stats[]>("/api/stats");
}

export function chartUrl(id: number, days = 7): string {
  return `/api/habits/${id}/chart?days=${days}`;
}
