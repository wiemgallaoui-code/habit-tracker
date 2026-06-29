import type { Habit } from "../types";

interface HabitCardProps {
  habit: Habit;
  onCheck: (id: number) => Promise<void>;
  onDelete: (id: number) => Promise<void>;
  onShowChart: (habit: Habit) => void;
  busy?: boolean;
}

function StatPill({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-xl border border-white/10 bg-slate-950/40 px-3 py-2">
      <div className="text-[11px] uppercase tracking-wide text-slate-400">{label}</div>
      <div className="mt-1 text-sm font-semibold text-white">{value}</div>
    </div>
  );
}

export function HabitCard({
  habit,
  onCheck,
  onDelete,
  onShowChart,
  busy,
}: HabitCardProps) {
  return (
    <article className="group rounded-3xl border border-white/10 bg-white/5 p-5 shadow-xl shadow-black/20 backdrop-blur-sm transition hover:border-emerald-400/20 hover:bg-white/[0.07]">
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-lg font-semibold text-white">{habit.name}</h3>
            <span
              className={`rounded-full px-2.5 py-1 text-xs font-medium ${
                habit.completed_today
                  ? "bg-emerald-500/15 text-emerald-300"
                  : "bg-slate-700/60 text-slate-300"
              }`}
            >
              {habit.completed_today ? "Done today" : "Pending"}
            </span>
          </div>
          <p className="mt-1 text-sm text-slate-400">Habit #{habit.id}</p>
        </div>

        <button
          type="button"
          disabled={busy || habit.completed_today}
          onClick={() => onCheck(habit.id)}
          className="rounded-xl bg-emerald-500 px-4 py-2 text-sm font-semibold text-slate-950 transition hover:bg-emerald-400 disabled:cursor-not-allowed disabled:bg-slate-700 disabled:text-slate-300"
        >
          {habit.completed_today ? "Checked" : "Check in"}
        </button>
      </div>

      <div className="mt-5 grid grid-cols-2 gap-3 sm:grid-cols-4">
        <StatPill label="Streak" value={habit.current_streak} />
        <StatPill label="Best" value={habit.longest_streak} />
        <StatPill label="Total" value={habit.total_completions} />
        <StatPill label="Rate" value={`${habit.completion_rate}%`} />
      </div>

      <div className="mt-5 flex flex-wrap gap-2">
        <button
          type="button"
          disabled={busy}
          onClick={() => onShowChart(habit)}
          className="rounded-lg border border-white/10 px-3 py-2 text-sm text-slate-200 transition hover:border-blue-400/30 hover:text-white disabled:opacity-50"
        >
          View chart
        </button>
        <button
          type="button"
          disabled={busy}
          onClick={() => onDelete(habit.id)}
          className="rounded-lg border border-red-500/20 px-3 py-2 text-sm text-red-300 transition hover:bg-red-500/10 disabled:opacity-50"
        >
          Delete
        </button>
      </div>
    </article>
  );
}
