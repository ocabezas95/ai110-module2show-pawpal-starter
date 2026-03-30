from datetime import date, time, datetime, timezone
from pawpal_system import (
    Task, TaskType, TaskStatus, Priority,
    Pet, Owner, Scheduler,
)


def test_mark_complete_sets_status_to_completed():
    # Verifies that calling mark_complete() transitions a PENDING task to COMPLETED
    task = Task(
        task_id="t1",
        task_type=TaskType.FEEDING,
        pet_id="p1",
        description="Morning feeding",
        scheduled_date=date(2026, 3, 30),
        scheduled_time=time(8, 0),
        priority=Priority.MEDIUM,
    )
    task.mark_complete(datetime.now(timezone.utc))
    assert task.status == TaskStatus.COMPLETED


def test_create_task_increases_pet_task_count():
    # Verifies that adding a task via the Scheduler increments the pet's task list by 1
    owner = Owner(owner_id="o1", name="Alice", email="alice@example.com", phone="555-0100")
    pet = Pet(
        pet_id="p1",
        name="Buddy",
        species="Dog",
        breed="Labrador",
        weight=60.0,
        birth_date=date(2020, 1, 1),
        owner_id="o1",
    )
    owner.add_pet(pet)
    scheduler = Scheduler(owner)

    before = len(scheduler.get_tasks_for_pet("p1"))
    scheduler.create_task(
        pet_id="p1",
        task_type=TaskType.EXERCISE,
        description="Afternoon walk",
        scheduled_date=date(2026, 3, 30),
        scheduled_time=time(15, 0),
    )
    after = len(scheduler.get_tasks_for_pet("p1"))

    assert after == before + 1
