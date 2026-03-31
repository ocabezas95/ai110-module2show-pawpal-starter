# PawPal+

PawPal+ is a Streamlit-based pet care planner that helps owners manage daily routines for one or more pets. It combines task management, conflict detection, recurring schedules, and constraint-aware daily planning in a clean, interactive UI.

## Project Overview

PawPal+ models pet care around four core concepts:

- `Owner`: Stores owner contact information and registered pets.
- `Pet`: Stores pet profile and health-related details.
- `Task`: Represents a care activity (feeding, medication, grooming, exercise, etc.) with scheduling metadata.
- `Scheduler`: Central service that indexes tasks, validates ownership, manages recurring rules, detects conflicts, and builds daily plans.

The app supports both a rich Streamlit interface (`app.py`) and a scriptable backend (`pawpal_system.py`) suitable for testing and extension.

## Features

### Core capabilities

- Add and manage pets under an owner profile.
- Create, edit, complete, reschedule, and delete care tasks.
- Track task status (`pending`, `completed`, `missed`).
- Generate a daily schedule with rationale for selected vs skipped tasks.

### Scheduling algorithms and logic

- **Indexed task retrieval**
	- Uses hash-based indexes for efficient lookups:
	- `task_id -> task` (constant-time direct lookup)
	- `pet_id -> set(task_ids)` (per-pet retrieval)
	- `scheduled_date -> set(task_ids)` (per-date retrieval)

- **Chronological ordering**
	- Tasks are sorted by `(scheduled_date, scheduled_time)` for pet/date views.
	- `sort_by_time()` provides stable time-only ordering for same-day displays.

- **Conflict detection**
	- Tasks are grouped by `(pet_id, scheduled_date, scheduled_time)`.
	- Any group with size > 1 is flagged as a conflict.
	- Returns either a readable report (`detect_conflicts`) or conflict task IDs (`detect_conflict_task_ids`) for UI highlighting.

- **Recurring task automation**
	- Completing a task with `frequency="daily"` or `frequency="weekly"` auto-creates the next occurrence at +1 or +7 days.
	- Recurring rules can also generate tasks over a date window for selected weekdays (`create_recurring_task`).

- **Constraint-aware daily planning (greedy selection)**
	- Candidate tasks include pending tasks on the target date and optional overdue tasks.
	- Scoring function:
		- Priority weights: `HIGH=3`, `MEDIUM=2`, `LOW=1`
		- Optional preferred-task-type bonus: `+2`
	- Tasks are sorted by descending score, then by scheduled time.
	- A greedy pass selects tasks while total duration remains within `available_minutes`.
	- Non-fitting tasks are skipped with explicit rationale.

## How to Run

### 1. Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Windows (PowerShell):

```powershell
.venv\Scripts\Activate.ps1
```

### 2. Launch the Streamlit app

```bash
streamlit run app.py
```

When the app opens, you can add pets, assign tasks, edit schedules, mark tasks complete, and generate a daily plan.

## Smarter Scheduling

- **Time-based sorting** so tasks appear in execution order.
- **Task filtering** by completion status and pet name.
- **Recurring completion behavior** for daily/weekly routines.
- **Recurring rule generation** across selected weekdays and date ranges.
- **Conflict detection** for exact same-pet, same-date, same-time collisions.
- **Rescheduling support** that updates internal indexes safely.
- **Overdue task surfacing** for pending tasks in the past.

## Testing PawPal+

Run the test suite with:

```bash
python -m pytest
```

Or run the primary test module:

```bash
python -m pytest tests/test_pawpal.py
```

What is covered:

- **Task lifecycle**: completion behavior and error paths.
- **Sorting and retrieval**: chronological ordering for pet/date queries and same-time preservation.
- **Recurrence**: daily/weekly follow-up generation and weekday-based recurring creation.
- **Conflict handling**: true conflict detection and no false positives across different pets.
- **Filtering and overdue logic**: completion/pet filters and past-due pending tasks.
- **Rescheduling correctness**: date-index updates after task moves.
- **Planning behavior**: available-time constraints and priority-aware task selection.

## 📸 Demo


![PawPal+ demo screenshot placeholder](images/Screenshot%202026-03-31%20at%2012.15.05 AM.png)
![PawPal+ demo screenshot placeholder](images/Screenshot%202026-03-30%20at%2011.45.57 PM.png)
![PawPal+ demo screenshot placeholder](images/Screenshot%202026-03-31%20at%2012.14.07 AM.png)
![PawPal+ demo screenshot placeholder](images/Screenshot%202026-03-31%20at%2012.16.18 AM.png)





