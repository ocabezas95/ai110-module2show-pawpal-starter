from pawpal_system import Owner, Pet, Scheduler, TaskType, Priority
from datetime import date, time

# ---------------------------------------------------------------------------
# 1. Create owner
# ---------------------------------------------------------------------------
owner = Owner(
    owner_id="owner-001",
    name="Alice Johnson",
    email="alice@email.com",
    phone="555-0100",
)
owner_name = "Alice Johnson"

# ---------------------------------------------------------------------------
# 2. Create two pets and register them with the owner
# ---------------------------------------------------------------------------
dog = Pet(
    pet_id="pet-001",
    name="Max",
    species="Dog",
    breed="Golden Retriever",
    weight=65.0,
    birth_date=date(2019, 4, 10),
    owner_id="owner-001",
)

cat = Pet(
    pet_id="pet-002",
    name="Whiskers",
    species="Cat",
    breed="Tabby",
    weight=10.5,
    birth_date=date(2021, 8, 22),
    owner_id="owner-001",
)

owner.add_pet(dog)
owner.add_pet(cat)

# ---------------------------------------------------------------------------
# 3. Create scheduler and add tasks (intentionally out of chronological order)
# ---------------------------------------------------------------------------
scheduler = Scheduler(owner)

evening_feeding_dog = scheduler.create_task(
    pet_id="pet-001",
    task_type=TaskType.FEEDING,
    description="Evening Feeding",
    scheduled_date=date.today(),
    scheduled_time=time(18, 0),
    priority=Priority.HIGH,
    duration_minutes=10,
)

afternoon_play = scheduler.create_task(
    pet_id="pet-002",
    task_type=TaskType.OTHER,
    description="Afternoon Playtime",
    scheduled_date=date.today(),
    scheduled_time=time(14, 30),
    priority=Priority.MEDIUM,
    duration_minutes=20,
)

morning_walk = scheduler.create_task(
    pet_id="pet-001",
    task_type=TaskType.EXERCISE,
    description="Morning Walk",
    scheduled_date=date.today(),
    scheduled_time=time(7, 0),
    priority=Priority.HIGH,
    duration_minutes=30,
)

dinner_cat = scheduler.create_task(
    pet_id="pet-002",
    task_type=TaskType.FEEDING,
    description="Dinner Time",
    scheduled_date=date.today(),
    scheduled_time=time(18, 30),
    priority=Priority.HIGH,
    duration_minutes=10,
)

early_medication_cat = scheduler.create_task(
    pet_id="pet-002",
    task_type=TaskType.MEDICATION,
    description="Morning Medication",
    scheduled_date=date.today(),
    scheduled_time=time(6, 45),
    priority=Priority.MEDIUM,
    duration_minutes=10,
)

# Intentional conflict: same pet, same date, same exact time
conflict_walk_max = scheduler.create_task(
    pet_id="pet-001",
    task_type=TaskType.EXERCISE,
    description="Conflict Walk",
    scheduled_date=date.today(),
    scheduled_time=time(9, 0),
    priority=Priority.MEDIUM,
    duration_minutes=20,
)

conflict_grooming_max = scheduler.create_task(
    pet_id="pet-001",
    task_type=TaskType.GROOMING,
    description="Conflict Grooming",
    scheduled_date=date.today(),
    scheduled_time=time(9, 0),
    priority=Priority.LOW,
    duration_minutes=15,
)

# Mark one task complete to validate completion-status filters
scheduler.complete_task(evening_feeding_dog.task_id)

# ---------------------------------------------------------------------------
# 4. Retrieve and print today's schedule + sorting/filtering checks
# ---------------------------------------------------------------------------
schedule = scheduler.get_today_tasks()
sorted_by_time = scheduler.sort_by_time(schedule)

completed_tasks = scheduler.filter_tasks(is_complete=True)
incomplete_tasks = scheduler.filter_tasks(is_complete=False)
max_tasks = scheduler.filter_tasks(pet_name="Max")
max_completed_tasks = scheduler.filter_tasks(is_complete=True, pet_name="Max")

pet_lookup = {p.pet_id: p for p in owner.get_all_pets()}

print()
print("=" * 60)
print("           PAW PAL  --  TODAY'S SCHEDULE")
print("=" * 60)
print(f"  Owner : {owner_name}")
print(f"  Pets  : {', '.join(p.name for p in owner.get_all_pets())}")
print(f"  Date  : {date.today().strftime('%A, %B %d %Y')}")
print("-" * 60)

if not schedule:
    print("  No tasks scheduled for today.")
else:
    print("\n  Tasks returned by get_today_tasks():")
    for task in schedule:
        pet = pet_lookup.get(task.pet_id)
        pet_label = f"{pet.name} ({pet.breed})" if pet else task.pet_id
        time_str = task.scheduled_time.strftime("%I:%M %p")
        print(f"\n  {time_str}  |  {task.task_type.value.upper():<12}  [{task.priority.value.upper()}]")
        print(f"    Task   : {task.description}")
        print(f"    Pet    : {pet_label}")
        print(f"    Length : {task.duration_minutes} min  |  Status: {task.status.value}")

print("\n" + "-" * 60)
print("  Sorted with scheduler.sort_by_time()")
print("-" * 60)
for task in sorted_by_time:
    print(f"  {task.scheduled_time.strftime('%H:%M')} - {task.description} ({task.status.value})")

print("\n" + "-" * 60)
print("  Filter checks")
print("-" * 60)
print(f"  Completed tasks count                : {len(completed_tasks)}")
print(f"  Incomplete tasks count               : {len(incomplete_tasks)}")
print(f"  Tasks for pet name 'Max'             : {len(max_tasks)}")
print(f"  Completed tasks for pet name 'Max'   : {len(max_completed_tasks)}")

print("\n" + "-" * 60)
print("  Conflict detection")
print("-" * 60)
print(scheduler.detect_conflicts())

print("\n  Completed task descriptions:")
for task in completed_tasks:
    print(f"    - {task.description}")

print("\n  Incomplete task descriptions:")
for task in incomplete_tasks:
    print(f"    - {task.description}")

print("\n  Max's task descriptions:")
for task in max_tasks:
    print(f"    - {task.description} ({task.status.value})")

print()
print("=" * 60)
print()
