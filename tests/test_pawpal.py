from datetime import date, time, datetime, timezone, timedelta
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


def test_mark_task_complete_daily_creates_next_day_task():
    # Verifies daily tasks auto-generate the next day's task when completed.
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

    today = date(2026, 3, 30)
    daily_task = scheduler.create_task(
        pet_id="p1",
        task_type=TaskType.FEEDING,
        description="Daily breakfast",
        scheduled_date=today,
        scheduled_time=time(8, 0),
        priority=Priority.MEDIUM,
        frequency="daily",
    )

    scheduler.mark_task_complete(daily_task.task_id)

    all_tasks = scheduler.get_tasks_for_pet("p1")
    assert len(all_tasks) == 2

    completed_original = next(t for t in all_tasks if t.task_id == daily_task.task_id)
    next_day_task = next(t for t in all_tasks if t.task_id != daily_task.task_id)

    assert completed_original.status == TaskStatus.COMPLETED
    assert next_day_task.status == TaskStatus.PENDING
    assert next_day_task.scheduled_date == today + timedelta(days=1)
    assert next_day_task.scheduled_time == time(8, 0)
    assert next_day_task.frequency == "daily"


def test_mark_task_complete_weekly_creates_next_week_task():
    # Verifies weekly tasks auto-generate the next week's task when completed.
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

    today = date(2026, 3, 30)
    weekly_task = scheduler.create_task(
        pet_id="p1",
        task_type=TaskType.GROOMING,
        description="Weekly brush",
        scheduled_date=today,
        scheduled_time=time(9, 0),
        priority=Priority.LOW,
        frequency="weekly",
    )

    scheduler.mark_task_complete(weekly_task.task_id)

    all_tasks = scheduler.get_tasks_for_pet("p1")
    assert len(all_tasks) == 2

    completed_original = next(t for t in all_tasks if t.task_id == weekly_task.task_id)
    next_week_task = next(t for t in all_tasks if t.task_id != weekly_task.task_id)

    assert completed_original.status == TaskStatus.COMPLETED
    assert next_week_task.status == TaskStatus.PENDING
    assert next_week_task.scheduled_date == today + timedelta(days=7)
    assert next_week_task.scheduled_time == time(9, 0)
    assert next_week_task.frequency == "weekly"
