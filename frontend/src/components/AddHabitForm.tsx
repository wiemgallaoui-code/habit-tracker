import type { FormEvent } from "react";

interface AddHabitFormProps {
  onAdd: (name: string, startDate: string) => Promise<void>;
  disabled?: boolean;
}

function todayIsoDate(): string {
  return new Date().toISOString().slice(0, 10);
}

export function AddHabitForm({ onAdd, disabled }: AddHabitFormProps) {
  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const data = new FormData(form);
    const name = String(data.get("name") ?? "").trim();
    const startDate = String(data.get("start_date") ?? todayIsoDate());
    if (!name) return;

    await onAdd(name, startDate);
    form.reset();
    const startInput = form.elements.namedItem("start_date") as HTMLInputElement | null;
    if (startInput) startInput.value = todayIsoDate();
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="rounded-2xl border border-white/10 bg-white/5 p-5 backdrop-blur-sm"
    >
      <div className="flex flex-col gap-3 lg:flex-row">
        <input
          name="name"
          type="text"
          placeholder="New habit, e.g. Morning run"
          disabled={disabled}
          className="flex-1 rounded-xl border border-white/10 bg-slate-950/60 px-4 py-3 text-sm text-white outline-none transition focus:border-emerald-400/60 focus:ring-2 focus:ring-emerald-400/20 disabled:opacity-50"
        />
        <label className="flex flex-col gap-1 text-sm text-slate-400 lg:w-48">
          <span>Tracking starts</span>
          <input
            name="start_date"
            type="date"
            defaultValue={todayIsoDate()}
            disabled={disabled}
            className="rounded-xl border border-white/10 bg-slate-950/60 px-4 py-3 text-sm text-white outline-none transition focus:border-emerald-400/60 focus:ring-2 focus:ring-emerald-400/20 disabled:opacity-50"
          />
        </label>
        <button
          type="submit"
          disabled={disabled}
          className="rounded-xl bg-emerald-500 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-emerald-400 disabled:cursor-not-allowed disabled:opacity-50 lg:self-end"
        >
          Add habit
        </button>
      </div>
    </form>
  );
}
