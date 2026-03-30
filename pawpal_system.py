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
        # Return a formatted summary string of this pet's details
        pass

    def update_weight(self, new_weight: float) -> None:
        # Validate new_weight > 0, then update self.weight
        pass

    def add_medical_record(self, record: str) -> None:
        # Strip whitespace, reject empty strings, then append to self.medications
        pass

    def get_age(self) -> int:
        # Calculate and return the pet's current age in years from birth_date
        pass

    def is_on_medication(self) -> bool:
        # Return True if the medications list is non-empty
        pass


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
        # Raise TaskStateError if not PENDING; set status and completion_timestamp
        pass

    def mark_missed(self) -> None:
        # Raise TaskStateError if not PENDING; set status to MISSED
        pass

    def reschedule(self, new_date: date, new_time: time) -> None:
        # Raise TaskStateError if not PENDING; update scheduled_date and scheduled_time
        pass

    def is_overdue(self, current_time: datetime) -> bool:
        # Return True only when PENDING and scheduled datetime is before current_time
        pass

    def get_details(self) -> str:
        # Return a formatted string with all task fields
        pass

    def set_reminder(self, time_before: int) -> None:
        # Validate time_before > 0, then set reminder_minutes_before
        pass


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
        # Return a human-readable summary of selected/skipped tasks and total time
        pass


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
        # Verify pet.owner_id matches, reject duplicate pet_id, then store in both structures
        pass

    def remove_pet(self, pet_id: str) -> None:
        # Pop from _pets_by_id, raise ValidationError if missing, filter _pets list
        pass

    def get_all_pets(self) -> list[Pet]:
        # Return a shallow copy of _pets
        pass

    def update_contact_info(self, email: str, phone: str) -> None:
        # Strip and update _email and _phone
        pass

    def get_pet_by_id(self, pet_id: str) -> Optional[Pet]:
        # O(1) lookup via _pets_by_id; return None if not found
        pass


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
    # Internal helpers (implement these first — used by everything else)
    # ------------------------------------------------------------------

    def _assert_pet_belongs_to_owner(self, pet_id: str) -> None:
        # Raise OwnershipError if owner.get_pet_by_id(pet_id) returns None
        pass

    def _find_task_or_raise(self, task_id: str) -> Task:
        # Return task from _tasks_by_id, raise ValidationError if missing
        pass

    def _index_task(self, task: Task) -> None:
        # Add task to _tasks, _tasks_by_id, _task_ids_by_pet, _task_ids_by_date
        pass

    def _delete_task(self, task_id: str) -> None:
        # Remove task from all four index structures
        pass

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
        # Verify ownership, build Task (uuid4 id if none given), index it, return it
        pass

    def remove_pet(self, pet_id: str, task_policy: str = "block_if_pending") -> None:
        """
        Remove a pet and resolve related tasks according to task_policy.

        task_policy options:
        - "block_if_pending"  → raise ValidationError if any pending tasks exist.
        - "delete_all_tasks"  → silently delete every task for this pet first.
        """
        # 1. Assert ownership. 2. Apply policy. 3. Call self._owner.remove_pet(pet_id).
        pass

    def get_tasks_for_pet(self, pet_id: str) -> list[Task]:
        # Look up task ids in _task_ids_by_pet; return sorted by scheduled date+time
        pass

    def get_tasks_for_date(self, target_date: date) -> list[Task]:
        # Look up task ids in _task_ids_by_date; return sorted by scheduled_time
        pass

    def get_today_tasks(self) -> list[Task]:
        # Delegate to get_tasks_for_date(date.today())
        pass

    def get_overdue_tasks(self) -> list[Task]:
        # Return PENDING tasks whose scheduled datetime is before now (UTC), oldest first
        pass

    def get_completed_tasks(
        self, pet_id: str, date_range: tuple[date, date]
    ) -> list[Task]:
        # Assert ownership; filter pet tasks by COMPLETED status within date range
        pass

    def complete_task(self, task_id: str) -> None:
        # Find task, call mark_complete with datetime.now(timezone.utc)
        pass

    def reschedule_task(
        self, task_id: str, new_date: date, new_time: time
    ) -> None:
        # Remove old date index, call task.reschedule(), add new date index
        pass

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
        # Build a RecurringRule, store it, then generate Task instances up to end_date
        pass

    def get_upcoming_week(self) -> list[Task]:
        # Return tasks for today through today+6 days, sorted by scheduled datetime
        pass

    def generate_report(self, pet_id: str) -> str:
        # Assert ownership; count total/completed/pending/missed tasks; return summary string
        pass

    def build_daily_plan(
        self,
        target_date: date,
        available_minutes: int,
        preferred_task_types: Optional[list[TaskType]] = None,
        include_overdue: bool = True,
    ) -> DailyPlan:
        # Score and greedily select PENDING tasks that fit within available_minutes
        pass
