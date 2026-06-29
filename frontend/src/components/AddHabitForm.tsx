import type { FormEvent } from "react";

interface AddHabitFormProps {
  onAdd: (name: string) => Promise<void>;
  disabled?: boolean;
}

export function AddHabitForm({ onAdd, disabled }: AddHabitFormProps) {
  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const data = new FormData(form);
    const name = String(data.get("name") ?? "").trim();
    if (!name) return;

    await onAdd(name);
    form.reset();
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="flex flex-col gap-3 rounded-2xl border border-white/10 bg-white/5 p-5 backdrop-blur-sm sm:flex-row"
    >
      <input
        name="name"
        type="text"
        placeholder="New habit, e.g. Morning run"
        disabled={disabled}
        className="flex-1 rounded-xl border border-white/10 bg-slate-950/60 px-4 py-3 text-sm text-white outline-none transition focus:border-emerald-400/60 focus:ring-2 focus:ring-emerald-400/20 disabled:opacity-50"
      />
      <button
        type="submit"
        disabled={disabled}
        className="rounded-xl bg-emerald-500 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-emerald-400 disabled:cursor-not-allowed disabled:opacity-50"
      >
        Add habit
      </button>
    </form>
  );
}
