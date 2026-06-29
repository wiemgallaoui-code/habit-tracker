# CLI Habit Tracker

A command-line habit tracker built with **Python**, **SQLite**, and **matplotlib**. Track daily habits, view streaks, and visualize progress over time.

## Features

- Add, list, and remove habits
- Log daily completions
- Streak and completion stats
- Matplotlib charts saved to `charts/`

## Setup

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

## Usage

```bash
python -m habit_tracker add "Exercise"
python -m habit_tracker add "Read 20 minutes"
python -m habit_tracker list
python -m habit_tracker remove 1
python -m habit_tracker remove "Exercise"
python -m habit_tracker check "Exercise"
python -m habit_tracker check 1
python -m habit_tracker check "Exercise" --date 2026-06-01
python -m habit_tracker stats
python -m habit_tracker stats "Exercise"
python -m habit_tracker chart "Exercise"
python -m habit_tracker chart "Exercise" --days 30
```

## Project structure

```
CLI Habit Tracker/
├── habit_tracker/     # application package
├── data/              # SQLite database (gitignored)
├── charts/            # saved matplotlib figures (gitignored)
├── requirements.txt
└── README.md
```

## License

MIT
