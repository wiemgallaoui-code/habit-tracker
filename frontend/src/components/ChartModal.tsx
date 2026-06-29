import { chartUrl } from "../api/client";
import type { Habit } from "../types";

interface ChartModalProps {
  habit: Habit | null;
  days: number;
  onClose: () => void;
  onDaysChange: (days: number) => void;
}

export function ChartModal({ habit, days, onClose, onDaysChange }: ChartModalProps) {
  if (!habit) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 p-4 backdrop-blur-sm">
      <div className="w-full max-w-3xl rounded-3xl border border-white/10 bg-slate-900 p-6 shadow-2xl">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h2 className="text-xl font-semibold text-white">{habit.name}</h2>
            <p className="mt-1 text-sm text-slate-400">Completion chart</p>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg border border-white/10 px-3 py-1.5 text-sm text-slate-300 hover:text-white"
          >
            Close
          </button>
        </div>

        <div className="mt-4 flex gap-2">
          {[7, 14, 30].map((option) => (
            <button
              key={option}
              type="button"
              onClick={() => onDaysChange(option)}
              className={`rounded-lg px-3 py-1.5 text-sm transition ${
                days === option
                  ? "bg-emerald-500 text-slate-950"
                  : "border border-white/10 text-slate-300 hover:text-white"
              }`}
            >
              {option} days
            </button>
          ))}
        </div>

        <div className="mt-5 overflow-hidden rounded-2xl border border-white/10 bg-white">
          <img
            src={`${chartUrl(habit.id, days)}&t=${Date.now()}`}
            alt={`${habit.name} completion chart`}
            className="w-full"
          />
        </div>
      </div>
    </div>
  );
}
