import streamlit as st
from uuid import uuid4
from datetime import date, time
from pawpal_system import (
    Owner, Pet, TaskType, Priority,
    Scheduler, ValidationError, OwnershipError,
)

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

# ---------------------------------------------------------------------------
# Session state initialization — runs only once per browser session
# ---------------------------------------------------------------------------
if "owner" not in st.session_state:
    st.session_state.owner = Owner(
        owner_id=str(uuid4()),
        name="Jordan",
        email="jordan@example.com",
        phone="555-0100",
    )

if "scheduler" not in st.session_state:
    st.session_state.scheduler = Scheduler(st.session_state.owner)

if "pets" not in st.session_state:
    st.session_state.pets = []

# Convenient aliases
owner = st.session_state.owner
scheduler = st.session_state.scheduler

st.title("🐾 PawPal+")

with st.expander("Scenario", expanded=False):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.
"""
    )

st.divider()

# ---------------------------------------------------------------------------
# Add a pet
# ---------------------------------------------------------------------------
st.subheader("Add a Pet")

with st.form("add_pet_form", clear_on_submit=True):
    col_a, col_b = st.columns(2)
    with col_a:
        pet_name   = st.text_input("Pet name", value="Mochi")
        species    = st.selectbox("Species", ["dog", "cat", "other"])
        breed      = st.text_input("Breed", value="Mixed")
    with col_b:
        weight     = st.number_input("Weight (lbs)", min_value=0.1, max_value=500.0, value=10.0, step=0.1)
        birth_date = st.date_input("Date of birth", value=date(2020, 1, 1), max_value=date.today())

    pet_submitted = st.form_submit_button("Add Pet")

if pet_submitted:
    new_pet = Pet(
        pet_id=str(uuid4()),
        name=pet_name,
        species=species,
        breed=breed,
        weight=weight,
        birth_date=birth_date,
        owner_id=owner.owner_id,
    )
    try:
        owner.add_pet(new_pet)
        st.session_state.pets = owner.get_all_pets()
        st.success(f"Added {new_pet.name}!")
    except (ValidationError, OwnershipError) as e:
        st.error(str(e))

if st.session_state.pets:
    st.markdown("**Your pets:**")
    for pet in st.session_state.pets:
        st.info(pet.get_info())
else:
    st.info("No pets added yet.")

st.divider()

# ---------------------------------------------------------------------------
# Add a task — calls scheduler.create_task()
# ---------------------------------------------------------------------------
st.subheader("Add a Task")

_TASK_TYPE_LABELS = {t.value.replace("_", " ").title(): t for t in TaskType}
_PRIORITY_LABELS  = {p.value.capitalize(): p for p in Priority}

if not st.session_state.pets:
    st.info("Add a pet above before creating tasks.")
else:
    with st.form("add_task_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            pet_options        = {p.name: p.pet_id for p in st.session_state.pets}
            selected_pet_name  = st.selectbox("Pet", list(pet_options.keys()))
            task_type_label    = st.selectbox("Task type", list(_TASK_TYPE_LABELS.keys()))
            description        = st.text_input("Description", value="Morning walk")
        with col2:
            priority_label  = st.selectbox("Priority", list(_PRIORITY_LABELS.keys()), index=1)
            duration        = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
            sched_date      = st.date_input("Scheduled date", value=date.today())
            sched_time      = st.time_input("Scheduled time", value=time(8, 0))

        task_submitted = st.form_submit_button("Add Task")

    if task_submitted:
        try:
            scheduler.create_task(
                pet_id=pet_options[selected_pet_name],
                task_type=_TASK_TYPE_LABELS[task_type_label],
                description=description,
                scheduled_date=sched_date,
                scheduled_time=sched_time,
                priority=_PRIORITY_LABELS[priority_label],
                duration_minutes=int(duration),
            )
            st.success(f"Task '{description}' added!")
        except (ValidationError, OwnershipError) as e:
            st.error(str(e))

# Display today's tasks from the scheduler
today_tasks = scheduler.get_today_tasks()
if today_tasks:
    st.markdown("**Today's tasks:**")
    for task in today_tasks:
        status_color = {"pending": "🟡", "completed": "🟢", "missed": "🔴"}.get(task.status.value, "⚪")
        with st.expander(f"{status_color} [{task.priority.value.upper()}] {task.description} — {task.scheduled_time.strftime('%H:%M')} ({task.duration_minutes} min)"):
            st.code(task.get_details())
else:
    st.info("No tasks scheduled for today.")

st.divider()

# ---------------------------------------------------------------------------
# All pets & their tasks overview
# ---------------------------------------------------------------------------
st.subheader("All Pets & Tasks")

if not st.session_state.pets:
    st.info("No pets added yet.")
else:
    STATUS_ICON = {"pending": "🟡", "completed": "🟢", "missed": "🔴"}
    PRIORITY_BADGE = {"high": "🔴 HIGH", "medium": "🟠 MED", "low": "🔵 LOW"}

    for pet in st.session_state.pets:
        st.markdown(f"### {pet.name}")

        col_left, col_right = st.columns([1, 3])
        with col_left:
            st.markdown(f"**Species:** {pet.species.capitalize()}")
            st.markdown(f"**Breed:** {pet.breed}")
            st.markdown(f"**Weight:** {pet.weight} lbs")

        pet_tasks = scheduler.get_tasks_for_pet(pet.pet_id)

        with col_right:
            if not pet_tasks:
                st.info("No tasks assigned to this pet yet.")
            else:
                for task in sorted(pet_tasks, key=lambda t: (t.scheduled_date, t.scheduled_time)):
                    icon   = STATUS_ICON.get(task.status.value, "⚪")
                    badge  = PRIORITY_BADGE.get(task.priority.value, task.priority.value)
                    label  = (
                        f"{icon} {task.scheduled_date} {task.scheduled_time.strftime('%H:%M')}  "
                        f"— {task.description} ({task.duration_minutes} min)  |  {badge}"
                    )
                    with st.expander(label):
                        st.markdown(f"**Status:** {task.status.value.capitalize()}")
                        st.markdown(f"**Type:** {task.task_type.value.replace('_', ' ').title()}")
                        st.code(task.get_details())

        st.divider()

# ---------------------------------------------------------------------------
# Build schedule — calls scheduler.build_daily_plan()
# ---------------------------------------------------------------------------
st.subheader("Build Schedule")

available_minutes = st.slider(
    "How many minutes do you have today?",
    min_value=15, max_value=480, value=120, step=15,
)

if st.button("Generate schedule"):
    if not st.session_state.pets:
        st.warning("Add a pet and some tasks first.")
    elif not today_tasks:
        st.warning("No tasks scheduled for today. Add tasks above first.")
    else:
        plan = scheduler.build_daily_plan(
            target_date=date.today(),
            available_minutes=available_minutes,
        )
        st.text(plan.explain())
