from datetime import date, time, datetime, timezone, timedelta
import pytest
from pawpal_system import (
    Task, TaskType, TaskStatus, Priority,
    Pet, Owner, Scheduler, OwnershipError, ValidationError,
)


def _build_owner_with_pet() -> tuple[Owner, Pet, Scheduler]:
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
    return owner, pet, scheduler


@pytest.fixture
def scheduler_with_one_pet() -> Scheduler:
    _, _, scheduler = _build_owner_with_pet()
    return scheduler


@pytest.fixture
def scheduler_with_two_pets() -> tuple[Scheduler, Pet, Pet]:
    owner = Owner(owner_id="o1", name="Alice", email="alice@example.com", phone="555-0100")
    pet1 = Pet(
        pet_id="p1",
        name="Buddy",
        species="Dog",
        breed="Labrador",
        weight=60.0,
        birth_date=date(2020, 1, 1),
        owner_id="o1",
    )
    pet2 = Pet(
        pet_id="p2",
        name="Milo",
        species="Cat",
        breed="Tabby",
        weight=12.0,
        birth_date=date(2021, 6, 10),
        owner_id="o1",
    )
    owner.add_pet(pet1)
    owner.add_pet(pet2)
    return Scheduler(owner), pet1, pet2


def test_mark_complete_sets_status_to_completed():
    """Verifies that marking a task complete updates its status to COMPLETED."""
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


def test_fixture_scheduler_with_one_pet_starts_empty(scheduler_with_one_pet):
    """Verifies the single-pet scheduler fixture starts with no tasks."""
    assert scheduler_with_one_pet.get_tasks_for_pet("p1") == []


def test_create_task_increases_pet_task_count():
    """Verifies creating a task increases the task count for that pet by one."""
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


def test_sorting_correctness_get_tasks_for_pet_returns_chronological_order(scheduler_with_one_pet):
    """Verifies pet tasks are returned in chronological date/time order."""
    scheduler = scheduler_with_one_pet

    scheduler.create_task(
        pet_id="p1",
        task_type=TaskType.FEEDING,
        description="Late task",
        scheduled_date=date(2026, 3, 31),
        scheduled_time=time(18, 0),
        task_id="t3",
    )
    scheduler.create_task(
        pet_id="p1",
        task_type=TaskType.EXERCISE,
        description="Early next",
        scheduled_date=date(2026, 3, 31),
        scheduled_time=time(7, 30),
        task_id="t2",
    )
    scheduler.create_task(
        pet_id="p1",
        task_type=TaskType.GROOMING,
        description="Previous day",
        scheduled_date=date(2026, 3, 30),
        scheduled_time=time(21, 0),
        task_id="t1",
    )

    ordered = scheduler.get_tasks_for_pet("p1")
    assert [task.task_id for task in ordered] == ["t1", "t2", "t3"]


def test_get_tasks_for_date_returns_time_sorted_tasks(scheduler_with_one_pet):
    """Verifies tasks returned for a date are sorted by scheduled time."""
    scheduler = scheduler_with_one_pet
    target_day = date(2026, 4, 1)

    scheduler.create_task(
        pet_id="p1",
        task_type=TaskType.EXERCISE,
        description="Noon walk",
        scheduled_date=target_day,
        scheduled_time=time(12, 0),
        task_id="a",
    )
    scheduler.create_task(
        pet_id="p1",
        task_type=TaskType.FEEDING,
        description="Breakfast",
        scheduled_date=target_day,
        scheduled_time=time(8, 0),
        task_id="b",
    )

    tasks = scheduler.get_tasks_for_date(target_day)
    assert [task.task_id for task in tasks] == ["b", "a"]


def test_sort_by_time_handles_empty_and_unsorted_inputs(scheduler_with_one_pet):
    """Verifies sort_by_time handles empty lists and sorts unsorted tasks correctly."""
    scheduler = scheduler_with_one_pet
    assert scheduler.sort_by_time([]) == []

    t1 = Task(
        task_id="x1",
        task_type=TaskType.FEEDING,
        pet_id="p1",
        description="later",
        scheduled_date=date(2026, 4, 2),
        scheduled_time=time(19, 0),
        priority=Priority.MEDIUM,
    )
    t2 = Task(
        task_id="x2",
        task_type=TaskType.FEEDING,
        pet_id="p1",
        description="earlier",
        scheduled_date=date(2026, 4, 2),
        scheduled_time=time(7, 0),
        priority=Priority.MEDIUM,
    )

    sorted_tasks = scheduler.sort_by_time([t1, t2])
    assert [task.task_id for task in sorted_tasks] == ["x2", "x1"]


def test_same_time_tasks_are_all_returned_without_loss(scheduler_with_one_pet):
    """Verifies tasks sharing the same scheduled time are all preserved in results."""
    scheduler = scheduler_with_one_pet
    same_day = date(2026, 4, 3)

    scheduler.create_task(
        pet_id="p1",
        task_type=TaskType.FEEDING,
        description="Task A",
        scheduled_date=same_day,
        scheduled_time=time(9, 0),
        task_id="same-a",
    )
    scheduler.create_task(
        pet_id="p1",
        task_type=TaskType.MEDICATION,
        description="Task B",
        scheduled_date=same_day,
        scheduled_time=time(9, 0),
        task_id="same-b",
    )

    tasks = scheduler.get_tasks_for_date(same_day)
    assert len(tasks) == 2
    assert all(task.scheduled_time == time(9, 0) for task in tasks)
    assert {task.task_id for task in tasks} == {"same-a", "same-b"}


def test_mark_task_complete_daily_creates_next_day_task():
    """Verifies completing a daily task generates a new task for the next day."""
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


def test_mark_task_complete_daily_is_case_insensitive_for_frequency(scheduler_with_one_pet):
    """Verifies daily recurrence generation is case-insensitive for frequency values."""
    scheduler = scheduler_with_one_pet
    today = date(2026, 4, 4)

    task = scheduler.create_task(
        pet_id="p1",
        task_type=TaskType.FEEDING,
        description="Daily meal",
        scheduled_date=today,
        scheduled_time=time(8, 30),
        frequency="DAILY",
        task_id="daily-uppercase",
    )

    scheduler.mark_task_complete(task.task_id)
    tasks = scheduler.get_tasks_for_pet("p1")
    assert len(tasks) == 2
    generated = next(t for t in tasks if t.task_id != task.task_id)
    assert generated.scheduled_date == today + timedelta(days=1)


def test_mark_task_complete_unsupported_frequency_does_not_generate_new_task(scheduler_with_one_pet):
    """Verifies unsupported recurrence frequencies do not generate follow-up tasks."""
    scheduler = scheduler_with_one_pet

    task = scheduler.create_task(
        pet_id="p1",
        task_type=TaskType.GROOMING,
        description="Monthly brush",
        scheduled_date=date(2026, 4, 5),
        scheduled_time=time(10, 0),
        frequency="monthly",
        task_id="monthly-1",
    )

    scheduler.mark_task_complete(task.task_id)
    tasks = scheduler.get_tasks_for_pet("p1")
    assert len(tasks) == 1
    assert tasks[0].status == TaskStatus.COMPLETED


def test_mark_task_complete_weekly_creates_next_week_task():
    """Verifies completing a weekly task generates a new task seven days later."""
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


def test_create_recurring_task_generates_only_matching_weekdays_in_range(scheduler_with_one_pet):
    """Verifies recurring task creation only schedules tasks on selected weekdays."""
    scheduler = scheduler_with_one_pet
    start = date(2026, 3, 30)  # Monday
    end = date(2026, 4, 5)     # Sunday

    scheduler.create_recurring_task(
        pet_id="p1",
        task_type=TaskType.EXERCISE,
        days_of_week=[0, 2, 4],  # Mon, Wed, Fri
        scheduled_time=time(17, 0),
        description="MWF walk",
        start_date=start,
        end_date=end,
    )

    tasks = scheduler.get_tasks_for_pet("p1")
    produced_dates = [task.scheduled_date for task in tasks]
    assert produced_dates == [date(2026, 3, 30), date(2026, 4, 1), date(2026, 4, 3)]


def test_create_recurring_task_with_no_matching_weekday_generates_no_tasks(scheduler_with_one_pet):
    """Verifies no recurring tasks are created when no weekdays match the range."""
    scheduler = scheduler_with_one_pet
    start = date(2026, 3, 30)  # Monday
    end = date(2026, 3, 30)

    scheduler.create_recurring_task(
        pet_id="p1",
        task_type=TaskType.FEEDING,
        days_of_week=[1],  # Tuesday only
        scheduled_time=time(8, 0),
        description="Tuesday breakfast",
        start_date=start,
        end_date=end,
    )

    assert scheduler.get_tasks_for_pet("p1") == []


def test_conflict_detection_flags_two_tasks_at_exact_same_time(scheduler_with_one_pet):
    """Verifies conflict detection reports same-pet tasks scheduled at the same time."""
    scheduler = scheduler_with_one_pet
    when = date(2026, 4, 6)

    scheduler.create_task(
        pet_id="p1",
        task_type=TaskType.FEEDING,
        description="Meal",
        scheduled_date=when,
        scheduled_time=time(9, 0),
        task_id="c1",
    )
    scheduler.create_task(
        pet_id="p1",
        task_type=TaskType.MEDICATION,
        description="Pill",
        scheduled_date=when,
        scheduled_time=time(9, 0),
        task_id="c2",
    )

    conflict_report = scheduler.detect_conflicts()
    assert "Scheduling conflicts detected:" in conflict_report
    assert "Buddy has 2 tasks at 2026-04-06 09:00" in conflict_report
    assert "Meal" in conflict_report
    assert "Pill" in conflict_report


def test_conflict_detection_no_conflicts_returns_clear_message(scheduler_with_one_pet):
    """Verifies conflict detection returns a clear message when no conflicts exist."""
    scheduler = scheduler_with_one_pet
    scheduler.create_task(
        pet_id="p1",
        task_type=TaskType.FEEDING,
        description="Meal",
        scheduled_date=date(2026, 4, 7),
        scheduled_time=time(8, 0),
        task_id="clean-1",
    )

    assert scheduler.detect_conflicts() == "No scheduling conflicts detected."


def test_conflict_detection_same_time_different_pets_is_not_conflict(scheduler_with_two_pets):
    """Verifies same-time tasks for different pets are not treated as conflicts."""
    scheduler, pet1, pet2 = scheduler_with_two_pets
    when = date(2026, 4, 8)

    scheduler.create_task(
        pet_id=pet1.pet_id,
        task_type=TaskType.FEEDING,
        description="Buddy meal",
        scheduled_date=when,
        scheduled_time=time(9, 0),
    )
    scheduler.create_task(
        pet_id=pet2.pet_id,
        task_type=TaskType.FEEDING,
        description="Milo meal",
        scheduled_date=when,
        scheduled_time=time(9, 0),
    )

    assert scheduler.detect_conflicts() == "No scheduling conflicts detected."


def test_filter_tasks_by_completion_and_pet_name(scheduler_with_two_pets):
    """Verifies filtering by completion state and pet name returns expected tasks."""
    scheduler, pet1, pet2 = scheduler_with_two_pets
    first = scheduler.create_task(
        pet_id=pet1.pet_id,
        task_type=TaskType.FEEDING,
        description="Buddy meal",
        scheduled_date=date(2026, 4, 9),
        scheduled_time=time(8, 0),
        task_id="f1",
    )
    scheduler.create_task(
        pet_id=pet2.pet_id,
        task_type=TaskType.EXERCISE,
        description="Milo play",
        scheduled_date=date(2026, 4, 9),
        scheduled_time=time(10, 0),
        task_id="f2",
    )

    scheduler.mark_task_complete(first.task_id)

    completed = scheduler.filter_tasks(is_complete=True)
    assert [task.task_id for task in completed] == ["f1"]

    buddy_tasks = scheduler.filter_tasks(pet_name="buddy")
    assert [task.task_id for task in buddy_tasks] == ["f1"]


def test_reschedule_task_moves_task_between_date_indexes(scheduler_with_one_pet):
    """Verifies rescheduling moves a task from the old date index to the new one."""
    scheduler = scheduler_with_one_pet
    task = scheduler.create_task(
        pet_id="p1",
        task_type=TaskType.VET_VISIT,
        description="Checkup",
        scheduled_date=date(2026, 4, 10),
        scheduled_time=time(11, 0),
        task_id="r1",
    )

    scheduler.reschedule_task(task.task_id, new_date=date(2026, 4, 11), new_time=time(13, 0))

    old_day_tasks = scheduler.get_tasks_for_date(date(2026, 4, 10))
    new_day_tasks = scheduler.get_tasks_for_date(date(2026, 4, 11))
    assert old_day_tasks == []
    assert [t.task_id for t in new_day_tasks] == ["r1"]


def test_get_overdue_tasks_returns_only_pending_past_tasks(scheduler_with_one_pet):
    """Verifies overdue task retrieval includes only pending tasks in the past."""
    scheduler = scheduler_with_one_pet
    past = date.today() - timedelta(days=2)
    future = date.today() + timedelta(days=2)

    overdue_task = scheduler.create_task(
        pet_id="p1",
        task_type=TaskType.MEDICATION,
        description="Past pill",
        scheduled_date=past,
        scheduled_time=time(8, 0),
        task_id="o1",
    )
    non_overdue_task = scheduler.create_task(
        pet_id="p1",
        task_type=TaskType.EXERCISE,
        description="Future walk",
        scheduled_date=future,
        scheduled_time=time(8, 0),
        task_id="o2",
    )
    non_overdue_task.mark_complete(datetime.now(timezone.utc))

    overdue = scheduler.get_overdue_tasks()
    assert [task.task_id for task in overdue] == [overdue_task.task_id]


def test_build_daily_plan_respects_available_minutes_and_priority(scheduler_with_one_pet):
    """Verifies daily planning respects time limits while prioritizing higher-priority tasks."""
    scheduler = scheduler_with_one_pet
    day = date(2026, 4, 12)

    scheduler.create_task(
        pet_id="p1",
        task_type=TaskType.FEEDING,
        description="High priority meal",
        scheduled_date=day,
        scheduled_time=time(8, 0),
        priority=Priority.HIGH,
        duration_minutes=15,
        task_id="p-high",
    )
    scheduler.create_task(
        pet_id="p1",
        task_type=TaskType.GROOMING,
        description="Low priority brush",
        scheduled_date=day,
        scheduled_time=time(9, 0),
        priority=Priority.LOW,
        duration_minutes=20,
        task_id="p-low",
    )

    plan = scheduler.build_daily_plan(day, available_minutes=20, include_overdue=False)
    assert [task.task_id for task in plan.selected_tasks] == ["p-high"]
    assert [task.task_id for task in plan.skipped_tasks] == ["p-low"]
    assert plan.total_minutes == 15


def test_mark_task_complete_with_unknown_id_raises_validation_error(scheduler_with_one_pet):
    """Verifies marking an unknown task ID complete raises ValidationError."""
    with pytest.raises(ValidationError):
        scheduler_with_one_pet.mark_task_complete("missing-id")


def test_create_task_for_unowned_pet_raises_ownership_error():
    """Verifies creating a task for a non-owned pet raises OwnershipError."""
    owner = Owner(owner_id="o1", name="Alice", email="alice@example.com", phone="555-0100")
    scheduler = Scheduler(owner)

    with pytest.raises(OwnershipError):
        scheduler.create_task(
            pet_id="not-owned",
            task_type=TaskType.FEEDING,
            description="Invalid",
            scheduled_date=date(2026, 4, 13),
            scheduled_time=time(8, 0),
        )


def test_mark_task_complete_twice_raises_error(scheduler_with_one_pet):
    """Verifies completing the same task twice raises an exception."""
    task = scheduler_with_one_pet.create_task(
        pet_id="p1",
        task_type=TaskType.FEEDING,
        description="One-time meal",
        scheduled_date=date(2026, 4, 14),
        scheduled_time=time(8, 0),
        task_id="twice-1",
    )

    scheduler_with_one_pet.mark_task_complete(task.task_id)
    with pytest.raises(Exception):
        scheduler_with_one_pet.mark_task_complete(task.task_id)
