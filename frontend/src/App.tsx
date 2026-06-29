import { useCallback, useEffect, useState } from "react";
import {
  checkHabit,
  createHabit,
  deleteHabit,
  fetchHabits,
} from "./api/client";
import { AddHabitForm } from "./components/AddHabitForm";
import { ChartModal } from "./components/ChartModal";
import { HabitCard } from "./components/HabitCard";
import { SummaryBar } from "./components/SummaryBar";
import type { Habit } from "./types";

export default function App() {
  const [habits, setHabits] = useState<Habit[]>([]);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [chartHabit, setChartHabit] = useState<Habit | null>(null);
  const [chartDays, setChartDays] = useState(7);

  const loadHabits = useCallback(async () => {
    setError(null);
    try {
      const data = await fetchHabits();
      setHabits(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load habits");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadHabits();
  }, [loadHabits]);

  async function withBusy<T>(action: () => Promise<T>): Promise<T | undefined> {
    setBusy(true);
    setError(null);
    try {
      return await action();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
      return undefined;
    } finally {
      setBusy(false);
    }
  }

  async function handleAdd(name: string) {
    await withBusy(async () => {
      await createHabit(name);
      await loadHabits();
    });
  }

  async function handleCheck(id: number) {
    await withBusy(async () => {
      await checkHabit(id);
      await loadHabits();
    });
  }

  async function handleDelete(id: number) {
    const habit = habits.find((item) => item.id === id);
    if (!habit) return;
    const confirmed = window.confirm(`Delete "${habit.name}"?`);
    if (!confirmed) return;

    await withBusy(async () => {
      await deleteHabit(id);
      await loadHabits();
    });
  }

  return (
    <div className="mx-auto min-h-screen max-w-6xl px-4 py-8 sm:px-6 lg:px-8">
      <header className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-sm font-medium uppercase tracking-[0.2em] text-emerald-300">
            Full-stack demo
          </p>
          <h1 className="mt-2 text-4xl font-bold tracking-tight text-white">
            Habit Tracker
          </h1>
          <p className="mt-2 max-w-2xl text-slate-400">
            Python, SQLite, FastAPI, and a React dashboard for daily habits,
            streaks, and charts.
          </p>
        </div>
        <div className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-slate-300">
          API + SQLite backend
        </div>
      </header>

      {error && (
        <div className="mb-6 rounded-2xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-200">
          {error}
        </div>
      )}

      <div className="space-y-8">
        <SummaryBar habits={habits} />
        <AddHabitForm onAdd={handleAdd} disabled={busy} />

        {loading ? (
          <div className="rounded-2xl border border-white/10 bg-white/5 p-8 text-center text-slate-400">
            Loading habits...
          </div>
        ) : habits.length === 0 ? (
          <div className="rounded-2xl border border-dashed border-white/10 bg-white/5 p-10 text-center">
            <h2 className="text-lg font-semibold text-white">No habits yet</h2>
            <p className="mt-2 text-sm text-slate-400">
              Add your first habit above to start tracking.
            </p>
          </div>
        ) : (
          <section className="grid gap-5 lg:grid-cols-2">
            {habits.map((habit) => (
              <HabitCard
                key={habit.id}
                habit={habit}
                busy={busy}
                onCheck={handleCheck}
                onDelete={handleDelete}
                onShowChart={setChartHabit}
              />
            ))}
          </section>
        )}
      </div>

      <ChartModal
        habit={chartHabit}
        days={chartDays}
        onClose={() => setChartHabit(null)}
        onDaysChange={setChartDays}
      />
    </div>
  );
}
