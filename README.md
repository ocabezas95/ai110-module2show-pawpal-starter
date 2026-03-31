# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## Smarter Scheduling

PawPal+ includes smarter scheduling tools that make daily pet-care planning more reliable:

- **Time-based sorting:** Orders tasks by scheduled date/time so routines are easy to follow in sequence.
- **Task filtering:** Narrows task views by completion status and pet name for faster tracking.
- **Recurring task automation:** Automatically generates the next daily/weekly task when a recurring item is completed.
- **Conflict detection:** Flags overlapping tasks assigned to the same pet at the same date/time slot.

## Testing PawPal+

Run the test suite with:

```bash
python -m pytest
```

Main test categories:

- **Sorting:** Verifies tasks are returned in correct chronological order for pet and date views, including same-time and unsorted input cases.
- **Recurrence:** Confirms recurring behavior works for daily/weekly completion and recurring generation across weekday ranges.
- **Conflict detection:** Ensures the scheduler reports true same-pet time collisions and avoids false conflicts for different pets.

Confidence level (1-5 stars): ☆☆☆☆☆
