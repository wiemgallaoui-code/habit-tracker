import type { Habit } from "../types";

interface SummaryBarProps {
  habits: Habit[];
}

export function SummaryBar({ habits }: SummaryBarProps) {
  const doneToday = habits.filter((habit) => habit.completed_today).length;
  const totalStreak = habits.reduce((sum, habit) => sum + habit.current_streak, 0);
  const avgRate =
    habits.length === 0
      ? 0
      : Math.round(
          habits.reduce((sum, habit) => sum + habit.completion_rate, 0) / habits.length,
        );

  const items = [
    { label: "Habits", value: habits.length },
    { label: "Done today", value: doneToday },
    { label: "Active streaks", value: totalStreak },
    { label: "Avg. rate", value: `${avgRate}%` },
  ];

  return (
    <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      {items.map((item) => (
        <div
          key={item.label}
          className="rounded-2xl border border-white/10 bg-gradient-to-br from-white/10 to-white/5 p-5 backdrop-blur-sm"
        >
          <div className="text-sm text-slate-400">{item.label}</div>
          <div className="mt-2 text-3xl font-bold text-white">{item.value}</div>
        </div>
      ))}
    </section>
  );
}
