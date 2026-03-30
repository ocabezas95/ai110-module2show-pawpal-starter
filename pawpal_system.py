from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, time, datetime
from enum import Enum
from typing import Optional


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
# Pet (dataclass)
# ---------------------------------------------------------------------------

@dataclass
class Pet:
    pet_id: str
    name: str
    species: str
    breed: str
    age: int
    weight: float
    birth_date: date
    owner_id: str
    medications: list[str] = field(default_factory=list)

    def get_info(self) -> str:
        # Return a formatted summary string of this pet's details
        pass

    def update_weight(self, new_weight: float) -> None:
        # Update the pet's weight to new_weight
        pass

    def add_medical_record(self, record: str) -> None:
        # Append a new medical record or medication entry to the pet
        pass

    def get_age(self) -> int:
        # Calculate and return the pet's current age from birth_date
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
    status: TaskStatus = TaskStatus.PENDING
    completion_timestamp: Optional[datetime] = None

    def mark_complete(self, timestamp: datetime) -> None:
        # Set status to COMPLETED and record the completion timestamp
        pass

    def mark_missed(self) -> None:
        # Set status to MISSED
        pass

    def reschedule(self, new_date: date, new_time: time) -> None:
        # Update scheduled_date and scheduled_time to the new values
        pass

    def is_overdue(self, current_time: datetime) -> bool:
        # Return True if the task is still PENDING and its scheduled datetime is in the past
        pass

    def get_details(self) -> str:
        # Return a formatted string with all task details
        pass

    def set_reminder(self, time_before: int) -> None:
        # Schedule a reminder to fire time_before minutes before the task
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

    def add_pet(self, pet: Pet) -> None:
        # Add a Pet instance to this owner's pet list
        pass

    def remove_pet(self, pet_id: str) -> None:
        # Remove the pet with the given pet_id from the pet list
        pass

    def get_all_pets(self) -> list[Pet]:
        # Return the full list of pets belonging to this owner
        pass

    def update_contact_info(self, email: str, phone: str) -> None:
        # Update the owner's email and phone number
        pass

    def get_pet_by_id(self, pet_id: str) -> Optional[Pet]:
        # Find and return the pet matching pet_id, or None if not found
        pass


# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------

class Scheduler:
    def __init__(self, owner_id: str) -> None:
        self._owner_id: str = owner_id
        self._tasks: list[Task] = []
        self._recurring_tasks: list[Task] = []

    def create_task(
        self,
        pet_id: str,
        task_type: TaskType,
        description: str,
        scheduled_date: date,
        scheduled_time: time,
    ) -> Task:
        # Build and store a new Task, then return it
        pass

    def get_tasks_for_pet(self, pet_id: str) -> list[Task]:
        # Return all tasks whose pet_id matches the given id
        pass

    def get_tasks_for_date(self, target_date: date) -> list[Task]:
        # Return all tasks scheduled on target_date
        pass

    def get_today_tasks(self) -> list[Task]:
        # Return all tasks scheduled for today's date
        pass

    def get_overdue_tasks(self) -> list[Task]:
        # Return all tasks that are PENDING and past their scheduled datetime
        pass

    def get_completed_tasks(
        self, pet_id: str, date_range: tuple[date, date]
    ) -> list[Task]:
        # Return completed tasks for a pet within the given date range
        pass

    def complete_task(self, task_id: str) -> None:
        # Mark the task with task_id as complete using the current timestamp
        pass

    def reschedule_task(
        self, task_id: str, new_date: date, new_time: time
    ) -> None:
        # Find the task by task_id and update its scheduled date and time
        pass

    def create_recurring_task(
        self,
        pet_id: str,
        task_type: TaskType,
        days_of_week: list[int],
        scheduled_time: time,
    ) -> None:
        # Generate recurring task instances for the specified days of the week
        pass

    def get_upcoming_week(self) -> list[Task]:
        # Return all tasks scheduled within the next 7 days
        pass

    def generate_report(self, pet_id: str) -> str:
        # Build and return a summary report of all tasks for the given pet
        pass
