from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, time, datetime, timedelta, timezone
from enum import Enum
from typing import Optional
from uuid import uuid4


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class TaskType(Enum):
    FEEDING = "feeding"
    MEDICATION = "medication"
    GROOMING = "grooming"
    VET_VISIT = "vet_visit"
    EXERCISE = "exercise"
    OTHER = "other"


class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TaskStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    MISSED = "missed"


# ---------------------------------------------------------------------------
# Domain-specific errors
# ---------------------------------------------------------------------------

class OwnershipError(ValueError):
    pass


class TaskStateError(ValueError):
    pass


class ValidationError(ValueError):
    pass


# ---------------------------------------------------------------------------
# Pet (dataclass)
# ---------------------------------------------------------------------------

@dataclass
class Pet:
    pet_id: str
    name: str
    species: str
    breed: str
    weight: float
    birth_date: date          # source of truth — do NOT store age as a field
    owner_id: str
    medications: list[str] = field(default_factory=list)

    def get_info(self) -> str:
        """Return a formatted summary string of this pet's details."""
        age = self.get_age()
        med_status = "Yes" if self.is_on_medication() else "No"
        return (
            f"Pet: {self.name} ({self.species}, {self.breed})\n"
            f"  Age: {age} year(s)  |  Weight: {self.weight} lbs\n"
            f"  On medication: {med_status}"
        )

    def update_weight(self, new_weight: float) -> None:
        """Validate new_weight > 0, then update self.weight."""
        if new_weight <= 0:
            raise ValidationError(f"Weight must be positive, got {new_weight}.")
        self.weight = new_weight

    def add_medical_record(self, record: str) -> None:
        """Strip whitespace, reject empty strings, then append to self.medications."""
        record = record.strip()
        if not record:
            raise ValidationError("Medical record cannot be empty.")
        self.medications.append(record)

    def get_age(self) -> int:
        """Calculate and return the pet's current age in years from birth_date."""
        today = date.today()
        age = today.year - self.birth_date.year
        # Subtract 1 if the birthday hasn't occurred yet this calendar year
        if (today.month, today.day) < (self.birth_date.month, self.birth_date.day):
            age -= 1
        return age

    def is_on_medication(self) -> bool:
        """Return True if the medications list is non-empty."""
        return len(self.medications) > 0


# ---------------------------------------------------------------------------
# Task (dataclass)
# ---------------------------------------------------------------------------

@dataclass
class Task:
    task_id: str
    task_type: TaskType
    pet_id: str
    description: str
    scheduled_date: date
    scheduled_time: time
    priority: Priority
    duration_minutes: int = 15
    status: TaskStatus = TaskStatus.PENDING
    completion_timestamp: Optional[datetime] = None
    reminder_minutes_before: Optional[int] = None

    def mark_complete(self, timestamp: datetime) -> None:
        """Raise TaskStateError if not PENDING; set status and completion_timestamp."""
        if self.status != TaskStatus.PENDING:
            raise TaskStateError(
                f"Task '{self.task_id}' cannot be completed — "
                f"current status is '{self.status.value}'."
            )
        self.status = TaskStatus.COMPLETED
        self.completion_timestamp = timestamp

    def mark_missed(self) -> None:
        """Raise TaskStateError if not PENDING; set status to MISSED."""
        if self.status != TaskStatus.PENDING:
            raise TaskStateError(
                f"Task '{self.task_id}' cannot be marked missed — "
                f"current status is '{self.status.value}'."
            )
        self.status = TaskStatus.MISSED

    def reschedule(self, new_date: date, new_time: time) -> None:
        """Raise TaskStateError if not PENDING; update scheduled_date and scheduled_time."""
        if self.status != TaskStatus.PENDING:
            raise TaskStateError(
                f"Task '{self.task_id}' cannot be rescheduled — "
                f"current status is '{self.status.value}'."
            )
        self.scheduled_date = new_date
        self.scheduled_time = new_time

    def is_overdue(self, current_time: datetime) -> bool:
        """Return True only when PENDING and scheduled datetime is before current_time."""
        if self.status != TaskStatus.PENDING:
            return False
        scheduled_dt = datetime.combine(self.scheduled_date, self.scheduled_time)
        # Strip timezone info for a naive comparison
        naive_now = current_time.replace(tzinfo=None) if current_time.tzinfo else current_time
        return scheduled_dt < naive_now

    def get_details(self) -> str:
        """Return a formatted string with all task fields."""
        reminder = (
            f"{self.reminder_minutes_before} min before"
            if self.reminder_minutes_before is not None
            else "None"
        )
        completion = (
            self.completion_timestamp.isoformat()
            if self.completion_timestamp is not None
            else "—"
        )
        return (
            f"Task [{self.task_id}]\n"
            f"  Type      : {self.task_type.value}\n"
            f"  Pet       : {self.pet_id}\n"
            f"  Desc      : {self.description}\n"
            f"  Scheduled : {self.scheduled_date} at {self.scheduled_time.strftime('%H:%M')}\n"
            f"  Priority  : {self.priority.value}\n"
            f"  Duration  : {self.duration_minutes} min\n"
            f"  Status    : {self.status.value}\n"
            f"  Completed : {completion}\n"
            f"  Reminder  : {reminder}"
        )

    def set_reminder(self, time_before: int) -> None:
        """Validate time_before > 0, then set reminder_minutes_before."""
        if time_before <= 0:
            raise ValidationError(f"Reminder time must be positive, got {time_before}.")
        self.reminder_minutes_before = time_before


# ---------------------------------------------------------------------------
# RecurringRule (frozen dataclass — one rule generates many Task instances)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class RecurringRule:
    rule_id: str
    pet_id: str
    task_type: TaskType
    description: str
    priority: Priority
    duration_minutes: int
    days_of_week: tuple[int, ...]   # Monday=0 … Sunday=6
    scheduled_time: time
    start_date: date
    end_date: Optional[date] = None


# ---------------------------------------------------------------------------
# DailyPlan (dataclass — output of Scheduler.build_daily_plan)
# ---------------------------------------------------------------------------

@dataclass
class DailyPlan:
    target_date: date
    selected_tasks: list[Task]
    skipped_tasks: list[Task]
    total_minutes: int
    rationale: list[str]

    def explain(self) -> str:
        """Return a human-readable summary of selected/skipped tasks and total time."""
        lines = [
            f"Daily Plan for {self.target_date}",
            f"  Total time scheduled : {self.total_minutes} min",
            f"  Tasks selected       : {len(self.selected_tasks)}",
            f"  Tasks skipped        : {len(self.skipped_tasks)}",
        ]
        if self.selected_tasks:
            lines.append("\nSelected tasks:")
            for task in self.selected_tasks:
                lines.append(
                    f"  [{task.priority.value.upper()}] {task.description} "
                    f"({task.scheduled_time.strftime('%H:%M')}, {task.duration_minutes} min)"
                )
        if self.skipped_tasks:
            lines.append("\nSkipped tasks:")
            for task in self.skipped_tasks:
                lines.append(f"  - {task.description} ({task.duration_minutes} min)")
        if self.rationale:
            lines.append("\nRationale:")
            for note in self.rationale:
                lines.append(f"  • {note}")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Owner
# ---------------------------------------------------------------------------

class Owner:
    def __init__(
        self,
        owner_id: str,
        name: str,
        email: str,
        phone: str,
    ) -> None:
        self._owner_id: str = owner_id
        self._name: str = name
        self._email: str = email
        self._phone: str = phone
        self._pets: list[Pet] = []
        self._pets_by_id: dict[str, Pet] = {}   # O(1) pet lookup

    @property
    def owner_id(self) -> str:
        return self._owner_id

    def add_pet(self, pet: Pet) -> None:
        """Verify pet.owner_id matches, reject duplicate pet_id, then store in both structures."""
        if pet.owner_id != self._owner_id:
            raise OwnershipError(
                f"Pet '{pet.pet_id}' belongs to owner '{pet.owner_id}', "
                f"not '{self._owner_id}'."
            )
        if pet.pet_id in self._pets_by_id:
            raise ValidationError(
                f"Pet '{pet.pet_id}' is already registered with this owner."
            )
        self._pets.append(pet)
        self._pets_by_id[pet.pet_id] = pet

    def remove_pet(self, pet_id: str) -> None:
        """Pop from _pets_by_id, raise ValidationError if missing, filter _pets list."""
        if pet_id not in self._pets_by_id:
            raise ValidationError(f"Pet '{pet_id}' not found.")
        del self._pets_by_id[pet_id]
        self._pets = [p for p in self._pets if p.pet_id != pet_id]

    def get_all_pets(self) -> list[Pet]:
        """Return a shallow copy of _pets."""
        return list(self._pets)

    def update_contact_info(self, email: str, phone: str) -> None:
        """Strip and update _email and _phone."""
        self._email = email.strip()
        self._phone = phone.strip()

    def get_pet_by_id(self, pet_id: str) -> Optional[Pet]:
        """O(1) lookup via _pets_by_id; return None if not found."""
        return self._pets_by_id.get(pet_id)


# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------

class Scheduler:
    def __init__(self, owner: Owner) -> None:
        self._owner: Owner = owner                              # needed for ownership checks
        self._owner_id: str = owner.owner_id
        self._tasks: list[Task] = []
        self._tasks_by_id: dict[str, Task] = {}                # O(1) task lookup
        self._task_ids_by_pet: dict[str, set[str]] = {}        # O(1) per-pet queries
        self._task_ids_by_date: dict[date, set[str]] = {}      # O(1) per-date queries
        self._recurring_rules: dict[str, RecurringRule] = {}   # rule_id → rule

    # ------------------------------------------------------------------
    # Internal helpers (used by everything else)
    # ------------------------------------------------------------------

    def _assert_pet_belongs_to_owner(self, pet_id: str) -> None:
        """Raise OwnershipError if owner.get_pet_by_id(pet_id) returns None."""
        if self._owner.get_pet_by_id(pet_id) is None:
            raise OwnershipError(
                f"Pet '{pet_id}' does not belong to owner '{self._owner_id}'."
            )

    def _find_task_or_raise(self, task_id: str) -> Task:
        """Return task from _tasks_by_id, raise ValidationError if missing."""
        task = self._tasks_by_id.get(task_id)
        if task is None:
            raise ValidationError(f"Task '{task_id}' not found.")
        return task

    def _index_task(self, task: Task) -> None:
        """Add task to _tasks, _tasks_by_id, _task_ids_by_pet, _task_ids_by_date."""
        self._tasks.append(task)
        self._tasks_by_id[task.task_id] = task

        # Per-pet index
        self._task_ids_by_pet.setdefault(task.pet_id, set()).add(task.task_id)

        # Per-date index
        self._task_ids_by_date.setdefault(task.scheduled_date, set()).add(task.task_id)

    def _delete_task(self, task_id: str) -> None:
        """Remove task from all four index structures."""
        task = self._tasks_by_id.pop(task_id, None)
        if task is None:
            return
        self._tasks = [t for t in self._tasks if t.task_id != task_id]
        self._task_ids_by_pet.get(task.pet_id, set()).discard(task_id)
        self._task_ids_by_date.get(task.scheduled_date, set()).discard(task_id)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def create_task(
        self,
        pet_id: str,
        task_type: TaskType,
        description: str,
        scheduled_date: date,
        scheduled_time: time,
        priority: Priority = Priority.MEDIUM,
        duration_minutes: int = 15,
        task_id: Optional[str] = None,
    ) -> Task:
        """Verify ownership, build Task (uuid4 id if none given), index it, return it."""
        self._assert_pet_belongs_to_owner(pet_id)
        task = Task(
            task_id=task_id or str(uuid4()),
            task_type=task_type,
            pet_id=pet_id,
            description=description,
            scheduled_date=scheduled_date,
            scheduled_time=scheduled_time,
            priority=priority,
            duration_minutes=duration_minutes,
        )
        self._index_task(task)
        return task

    def remove_pet(self, pet_id: str, task_policy: str = "block_if_pending") -> None:
        """
        Remove a pet and resolve related tasks according to task_policy.

        task_policy options:
        - "block_if_pending"  → raise ValidationError if any pending tasks exist.
        - "delete_all_tasks"  → silently delete every task for this pet first.
        """
        self._assert_pet_belongs_to_owner(pet_id)

        pet_task_ids = list(self._task_ids_by_pet.get(pet_id, set()))

        if task_policy == "block_if_pending":
            for tid in pet_task_ids:
                task = self._tasks_by_id.get(tid)
                if task and task.status == TaskStatus.PENDING:
                    raise ValidationError(
                        f"Pet '{pet_id}' has pending tasks. Complete or remove them first, "
                        "or use task_policy='delete_all_tasks'."
                    )
        elif task_policy == "delete_all_tasks":
            for tid in pet_task_ids:
                self._delete_task(tid)
        else:
            raise ValidationError(f"Unknown task_policy: '{task_policy}'.")

        self._owner.remove_pet(pet_id)
        self._task_ids_by_pet.pop(pet_id, None)

    def get_tasks_for_pet(self, pet_id: str) -> list[Task]:
        """Look up task ids in _task_ids_by_pet; return sorted by scheduled date+time."""
        task_ids = self._task_ids_by_pet.get(pet_id, set())
        tasks = [self._tasks_by_id[tid] for tid in task_ids if tid in self._tasks_by_id]
        return sorted(tasks, key=lambda t: (t.scheduled_date, t.scheduled_time))

    def get_tasks_for_date(self, target_date: date) -> list[Task]:
        """Look up task ids in _task_ids_by_date; return sorted by scheduled_time."""
        task_ids = self._task_ids_by_date.get(target_date, set())
        tasks = [self._tasks_by_id[tid] for tid in task_ids if tid in self._tasks_by_id]
        return sorted(tasks, key=lambda t: t.scheduled_time)

    def get_today_tasks(self) -> list[Task]:
        """Delegate to get_tasks_for_date(date.today())."""
        return self.get_tasks_for_date(date.today())

    def get_overdue_tasks(self) -> list[Task]:
        """Return PENDING tasks whose scheduled datetime is before now (UTC), oldest first."""
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        overdue = [task for task in self._tasks if task.is_overdue(now)]
        return sorted(overdue, key=lambda t: (t.scheduled_date, t.scheduled_time))

    def get_completed_tasks(
        self, pet_id: str, date_range: tuple[date, date]
    ) -> list[Task]:
        """Assert ownership; filter pet tasks by COMPLETED status within date range."""
        self._assert_pet_belongs_to_owner(pet_id)
        start, end = date_range
        return [
            task for task in self.get_tasks_for_pet(pet_id)
            if task.status == TaskStatus.COMPLETED
            and start <= task.scheduled_date <= end
        ]

    def complete_task(self, task_id: str) -> None:
        """Find task, call mark_complete with datetime.now(timezone.utc)."""
        task = self._find_task_or_raise(task_id)
        task.mark_complete(datetime.now(timezone.utc))

    def reschedule_task(
        self, task_id: str, new_date: date, new_time: time
    ) -> None:
        """Remove old date index, call task.reschedule(), add new date index."""
        task = self._find_task_or_raise(task_id)
        old_date = task.scheduled_date

        # Remove from old date bucket
        self._task_ids_by_date.get(old_date, set()).discard(task_id)

        task.reschedule(new_date, new_time)

        # Insert into new date bucket
        self._task_ids_by_date.setdefault(new_date, set()).add(task_id)

    def create_recurring_task(
        self,
        pet_id: str,
        task_type: TaskType,
        days_of_week: list[int],
        scheduled_time: time,
        description: Optional[str] = None,
        priority: Priority = Priority.MEDIUM,
        duration_minutes: int = 15,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> None:
        """Build a RecurringRule, store it, then generate Task instances up to end_date."""
        self._assert_pet_belongs_to_owner(pet_id)

        start = start_date or date.today()
        finish = end_date or (start + timedelta(days=90))   # 90-day horizon by default
        desc = description or task_type.value.replace("_", " ").title()
        days_set = tuple(days_of_week)

        rule = RecurringRule(
            rule_id=str(uuid4()),
            pet_id=pet_id,
            task_type=task_type,
            description=desc,
            priority=priority,
            duration_minutes=duration_minutes,
            days_of_week=days_set,
            scheduled_time=scheduled_time,
            start_date=start,
            end_date=end_date,
        )
        self._recurring_rules[rule.rule_id] = rule

        # Walk every day in [start, finish] and create a task on matching weekdays
        current = start
        while current <= finish:
            if current.weekday() in days_set:
                self.create_task(
                    pet_id=pet_id,
                    task_type=task_type,
                    description=desc,
                    scheduled_date=current,
                    scheduled_time=scheduled_time,
                    priority=priority,
                    duration_minutes=duration_minutes,
                )
            current += timedelta(days=1)

    def get_upcoming_week(self) -> list[Task]:
        """Return tasks for today through today+6 days, sorted by scheduled datetime."""
        today = date.today()
        tasks: list[Task] = []
        for offset in range(7):
            tasks.extend(self.get_tasks_for_date(today + timedelta(days=offset)))
        return sorted(tasks, key=lambda t: (t.scheduled_date, t.scheduled_time))

    def generate_report(self, pet_id: str) -> str:
        """Assert ownership; count total/completed/pending/missed tasks; return summary string."""
        self._assert_pet_belongs_to_owner(pet_id)
        pet = self._owner.get_pet_by_id(pet_id)
        all_tasks = self.get_tasks_for_pet(pet_id)

        total = len(all_tasks)
        completed = sum(1 for t in all_tasks if t.status == TaskStatus.COMPLETED)
        pending   = sum(1 for t in all_tasks if t.status == TaskStatus.PENDING)
        missed    = sum(1 for t in all_tasks if t.status == TaskStatus.MISSED)
        rate      = (completed / total * 100) if total > 0 else 0.0

        return (
            f"=== Report for {pet.name} ===\n"
            f"  Total tasks     : {total}\n"
            f"  Completed       : {completed}\n"
            f"  Pending         : {pending}\n"
            f"  Missed          : {missed}\n"
            f"  Completion rate : {rate:.1f}%"
        )

    def build_daily_plan(
        self,
        target_date: date,
        available_minutes: int,
        preferred_task_types: Optional[list[TaskType]] = None,
        include_overdue: bool = True,
    ) -> DailyPlan:
        """Score and greedily select PENDING tasks that fit within available_minutes."""
        # Collect candidates: today's pending tasks + optionally overdue tasks
        candidates: list[Task] = [
            t for t in self.get_tasks_for_date(target_date)
            if t.status == TaskStatus.PENDING
        ]

        if include_overdue:
            now = datetime.now(timezone.utc).replace(tzinfo=None)
            overdue = [
                t for t in self._tasks
                if t.is_overdue(now) and t.scheduled_date != target_date
            ]
            # Prepend overdue tasks so they compete for time alongside today's tasks
            candidates = overdue + candidates

        # Score: HIGH=3, MEDIUM=2, LOW=1; bonus +2 for preferred task types
        priority_score = {Priority.HIGH: 3, Priority.MEDIUM: 2, Priority.LOW: 1}

        def score(task: Task) -> int:
            s = priority_score.get(task.priority, 0)
            if preferred_task_types and task.task_type in preferred_task_types:
                s += 2
            return s

        # Sort by score descending; use scheduled_time as a tiebreaker
        candidates.sort(key=lambda t: (-score(t), t.scheduled_time))

        selected: list[Task] = []
        skipped: list[Task] = []
        minutes_used = 0
        rationale: list[str] = []

        for task in candidates:
            if minutes_used + task.duration_minutes <= available_minutes:
                selected.append(task)
                minutes_used += task.duration_minutes
                rationale.append(
                    f"Selected '{task.description}' "
                    f"(priority={task.priority.value}, {task.duration_minutes} min)"
                )
            else:
                skipped.append(task)
                remaining = available_minutes - minutes_used
                rationale.append(
                    f"Skipped '{task.description}' — needs {task.duration_minutes} min, "
                    f"only {remaining} min remaining"
                )

        return DailyPlan(
            target_date=target_date,
            selected_tasks=selected,
            skipped_tasks=skipped,
            total_minutes=minutes_used,
            rationale=rationale,
        )
