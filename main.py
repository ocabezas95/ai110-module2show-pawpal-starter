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
# 3. Create scheduler and add at least three tasks at different times
# ---------------------------------------------------------------------------
scheduler = Scheduler(owner)

morning_walk = scheduler.create_task(
    pet_id="pet-001",
    task_type=TaskType.EXERCISE,
    description="Morning Walk",
    scheduled_date=date.today(),
    scheduled_time=time(7, 0),
    priority=Priority.HIGH,
    duration_minutes=30,
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

evening_feeding_dog = scheduler.create_task(
    pet_id="pet-001",
    task_type=TaskType.FEEDING,
    description="Evening Feeding",
    scheduled_date=date.today(),
    scheduled_time=time(18, 0),
    priority=Priority.HIGH,
    duration_minutes=10,
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

# ---------------------------------------------------------------------------
# 4. Retrieve and print today's schedule
# ---------------------------------------------------------------------------
schedule = scheduler.get_today_tasks()

pet_lookup = {p.pet_id: p for p in owner.get_all_pets()}

print()
print("=" * 60)
print("           PAW PAL  --  TODAY'S SCHEDULE")
print("=" * 60)
print(f"  Owner : {owner._name}")
print(f"  Pets  : {', '.join(p.name for p in owner.get_all_pets())}")
print(f"  Date  : {date.today().strftime('%A, %B %d %Y')}")
print("-" * 60)

if not schedule:
    print("  No tasks scheduled for today.")
else:
    for task in schedule:
        pet = pet_lookup.get(task.pet_id)
        pet_label = f"{pet.name} ({pet.breed})" if pet else task.pet_id
        time_str = task.scheduled_time.strftime("%I:%M %p")
        print(f"\n  {time_str}  |  {task.task_type.value.upper():<12}  [{task.priority.value.upper()}]")
        print(f"    Task   : {task.description}")
        print(f"    Pet    : {pet_label}")
        print(f"    Length : {task.duration_minutes} min  |  Status: {task.status.value}")

print()
print("=" * 60)
print()
