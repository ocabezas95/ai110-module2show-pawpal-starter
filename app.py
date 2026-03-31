import streamlit as st
from collections import defaultdict
from uuid import uuid4
from datetime import date, time, datetime, timezone
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

if "editing_task_id" not in st.session_state:
    st.session_state.editing_task_id = None
if "editing_section" not in st.session_state:
    st.session_state.editing_section = None

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
        pet_name   = st.text_input("Pet name")
        species    = st.selectbox("Species", ["dog", "cat", "other"])
        breed      = st.text_input("Breed")
    with col_b:
        weight     = st.number_input("Weight (lbs)", min_value=0.1, max_value=500.0, value=10.0, step=0.1)
        birth_date = st.date_input("Date of birth", value=date(2020, 1, 1), max_value=date.today())
        on_medication = st.checkbox("On medication")
    pet_notes = st.text_area("Notes", placeholder="Any additional notes about your pet...")

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
        medications=["On medication"] if on_medication else [],
        notes=pet_notes,
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
            selected_pet_name  = st.selectbox("Pet", list(pet_options.keys()), key="task_pet")
            task_type_label    = st.selectbox("Task type", list(_TASK_TYPE_LABELS.keys()), key="task_type")
            description        = st.text_input("Description", value="Morning walk", key="task_desc")
        with col2:
            priority_label  = st.selectbox("Priority", list(_PRIORITY_LABELS.keys()), index=1, key="task_priority")
            duration        = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20, key="task_duration")
            sched_date      = st.date_input("Scheduled date", value=date.today(), key="task_date")
            sched_time      = st.time_input("Scheduled time", value=time(8, 0), key="task_time")
            _FREQ_OPTIONS   = ["Once", "Daily", "Weekly", "Biweekly", "Monthly"]
            frequency_label = st.selectbox("Frequency", _FREQ_OPTIONS, key="task_frequency")

        task_submitted = st.form_submit_button("Add Task")

    if task_submitted:
        try:
            _freq_value = None if frequency_label == "Once" else frequency_label.lower()
            scheduler.create_task(
                pet_id=pet_options[selected_pet_name],
                task_type=_TASK_TYPE_LABELS[task_type_label],
                description=description,
                scheduled_date=sched_date,
                scheduled_time=sched_time,
                priority=_PRIORITY_LABELS[priority_label],
                duration_minutes=int(duration),
                frequency=_freq_value,
            )
            st.success(f"Task '{description}' added!")
            if scheduler.detect_conflict_task_ids():
                st.warning(
                    "This task may conflict with another at the same time. "
                    "Check the ⚠️ markers in the schedule below."
                )
        except (ValidationError, OwnershipError) as e:
            st.error(str(e))

# Display today's tasks from the scheduler
today_tasks = scheduler.sort_by_time(scheduler.get_today_tasks())
if today_tasks:
    st.markdown("**Today's tasks:**")

    # Completed banner
    completed_today = [t for t in today_tasks if t.status.value == "completed"]
    if completed_today:
        st.success(f"{len(completed_today)} task(s) completed today!")

    # Detailed, actionable conflict warnings
    _today_pet_map = {p.pet_id: p.name for p in st.session_state.pets}
    _today_groups: dict = defaultdict(list)
    for _t in today_tasks:
        _today_groups[(_t.pet_id, _t.scheduled_date, _t.scheduled_time)].append(_t)
    for (_pid, ___, _tt), _grp in _today_groups.items():
        if len(_grp) > 1:
            _names = " and ".join(f"'{t.description}'" for t in _grp)
            st.warning(
                f"⚠️ Conflict: {_names} are both scheduled at "
                f"{_tt.strftime('%H:%M')} for {_today_pet_map.get(_pid, _pid)}. "
                f"Use ✏️ Edit to fix the time."
            )

    conflict_ids = scheduler.detect_conflict_task_ids()
    _PRI_ICON = {"HIGH": "🔴", "MEDIUM": "🟠", "LOW": "🔵"}
    _TYPE_ICON = {"FEEDING": "🍽️", "MEDICATION": "💊", "GROOMING": "✂️", "VET_VISIT": "🏥", "EXERCISE": "🏃", "OTHER": "📋"}
    _COL_W = [0.55, 1.9, 1.0, 0.5, 0.9, 0.7, 0.85, 0.85]

    # Header
    _hcols = st.columns(_COL_W)
    for _h, _c in zip(["Time", "Description", "Priority", "Dur.", "Type", "Freq.", "", ""], _hcols):
        _c.caption(_h)

    for task in today_tasks:
        with st.container():
            tcols = st.columns(_COL_W)
            _time_label = task.scheduled_time.strftime("%H:%M")
            tcols[0].markdown(f"**{_time_label}**{'  ⚠️' if task.task_id in conflict_ids else ''}")
            tcols[1].write(task.description)
            _pri = task.priority.value.upper()
            tcols[2].write(f"{_PRI_ICON.get(_pri, '')} {_pri}")
            tcols[3].write(f"{task.duration_minutes}m")
            tcols[4].write(task.task_type.value.replace("_", " ").title())
            tcols[5].write((task.frequency or "once").capitalize())
            if task.status.value == "pending":
                if tcols[6].button("✅ Done", key=f"complete_{task.task_id}"):
                    task.mark_complete(datetime.now(timezone.utc))
                    st.rerun()
                if tcols[7].button("✏️ Edit", key=f"edit_today_{task.task_id}"):
                    st.session_state.editing_task_id = task.task_id
                    st.session_state.editing_section = "today"
            else:
                tcols[6].write({"completed": "✅ Done", "missed": "🔴 Missed"}.get(task.status.value, ""))

        # Inline edit form — opens below this row when ✏️ is clicked
        if (st.session_state.editing_task_id == task.task_id
                and st.session_state.editing_section == "today"):
            with st.form(key=f"edit_form_today_{task.task_id}"):
                st.caption("Edit task")
                _fc1, _fc2 = st.columns(2)
                _new_desc = _fc1.text_input("Description", value=task.description)
                _new_time = _fc2.time_input("Scheduled time", value=task.scheduled_time)
                _fc3, _fc4 = st.columns(2)
                _pri_keys = list(_PRIORITY_LABELS.keys())
                _pri_idx = next((i for i, v in enumerate(_PRIORITY_LABELS.values()) if v == task.priority), 0)
                _new_pri = _fc3.selectbox("Priority", _pri_keys, index=_pri_idx)
                _type_keys = list(_TASK_TYPE_LABELS.keys())
                _type_idx = next((i for i, v in enumerate(_TASK_TYPE_LABELS.values()) if v == task.task_type), 0)
                _new_type = _fc4.selectbox("Task type", _type_keys, index=_type_idx)
                _fc5, _fc6 = st.columns(2)
                _new_dur = _fc5.number_input("Duration (min)", value=task.duration_minutes, min_value=1, max_value=240)
                _freq_opts = ["Once", "Daily", "Weekly", "Biweekly", "Monthly"]
                _freq_idx = next((i for i, f in enumerate(_freq_opts) if f.lower() == (task.frequency or "once").lower()), 0)
                _new_freq = _fc6.selectbox("Frequency", _freq_opts, index=_freq_idx)
                _fs, _fc = st.columns(2)
                _save = _fs.form_submit_button("💾 Save")
                _cancel = _fc.form_submit_button("Cancel")
            if _save:
                task.description = _new_desc
                task.priority = _PRIORITY_LABELS[_new_pri]
                task.duration_minutes = int(_new_dur)
                task.task_type = _TASK_TYPE_LABELS[_new_type]
                task.frequency = None if _new_freq == "Once" else _new_freq.lower()
                if _new_time != task.scheduled_time:
                    scheduler.reschedule_task(task.task_id, task.scheduled_date, _new_time)
                st.session_state.editing_task_id = None
                st.session_state.editing_section = None
                st.rerun()
            if _cancel:
                st.session_state.editing_task_id = None
                st.session_state.editing_section = None
                st.rerun()
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
    all_conflict_ids = scheduler.detect_conflict_task_ids()
    _AP_PRI_ICON = {"HIGH": "🔴", "MEDIUM": "🟠", "LOW": "🔵"}
    _AP_STATUS = {"pending": "🟡", "completed": "🟢", "missed": "🔴"}
    _AP_COL_W = [0.55, 0.4, 1.8, 0.9, 0.5, 0.85, 0.7, 0.85, 0.95]

    for pet in st.session_state.pets:
        st.markdown(f"### {pet.name}")
        st.caption(f"{pet.species.capitalize()} · {pet.breed} · {pet.weight} lbs")

        pet_tasks = scheduler.sort_by_time(scheduler.get_tasks_for_pet(pet.pet_id))

        if not pet_tasks:
            st.info("No tasks assigned to this pet yet.")
        else:
            completed = [t for t in pet_tasks if t.status.value == "completed"]
            if completed:
                st.success(f"{len(completed)} task(s) completed for {pet.name}!")

            # Actionable conflict warnings for this pet
            _ap_groups: dict = defaultdict(list)
            for _t in pet_tasks:
                _ap_groups[(_t.pet_id, _t.scheduled_date, _t.scheduled_time)].append(_t)
            for (___, ___, _att), _agrp in _ap_groups.items():
                if len(_agrp) > 1:
                    _anames = " and ".join(f"'{t.description}'" for t in _agrp)
                    st.warning(
                        f"⚠️ Conflict: {_anames} are both scheduled at "
                        f"{_att.strftime('%H:%M')} for {pet.name}. "
                        f"Use ✏️ Edit to fix the time."
                    )

            # Header
            _ahcols = st.columns(_AP_COL_W)
            for _h, _c in zip(["Time", "", "Description", "Priority", "Dur.", "Type", "Freq.", "", ""], _ahcols):
                _c.caption(_h)

            for task in pet_tasks:
                with st.container():
                    tcols = st.columns(_AP_COL_W)
                    _atime = task.scheduled_time.strftime("%H:%M")
                    tcols[0].markdown(f"**{_atime}**{'  ⚠️' if task.task_id in all_conflict_ids else ''}")
                    tcols[1].write(_AP_STATUS.get(task.status.value, "⚪"))
                    tcols[2].write(task.description)
                    _apri = task.priority.value.upper()
                    tcols[3].write(f"{_AP_PRI_ICON.get(_apri, '')} {_apri}")
                    tcols[4].write(f"{task.duration_minutes}m")
                    tcols[5].write(task.task_type.value.replace("_", " ").title())
                    tcols[6].write((task.frequency or "once").capitalize())
                    if task.status.value == "pending":
                        if tcols[7].button("✏️ Edit", key=f"edit_all_{task.task_id}"):
                            st.session_state.editing_task_id = task.task_id
                            st.session_state.editing_section = "all_pets"
                    if tcols[8].button("🗑️ Delete", key=f"delete_{task.task_id}"):
                        scheduler._delete_task(task.task_id)
                        st.rerun()

                # Inline edit form — opens below this row when ✏️ is clicked
                if (st.session_state.editing_task_id == task.task_id
                        and st.session_state.editing_section == "all_pets"):
                    with st.form(key=f"edit_form_all_{task.task_id}"):
                        st.caption("Edit task")
                        _afc1, _afc2 = st.columns(2)
                        _anew_desc = _afc1.text_input("Description", value=task.description)
                        _anew_time = _afc2.time_input("Scheduled time", value=task.scheduled_time)
                        _afc3, _afc4 = st.columns(2)
                        _apri_keys = list(_PRIORITY_LABELS.keys())
                        _apri_idx = next((i for i, v in enumerate(_PRIORITY_LABELS.values()) if v == task.priority), 0)
                        _anew_pri = _afc3.selectbox("Priority", _apri_keys, index=_apri_idx)
                        _atype_keys = list(_TASK_TYPE_LABELS.keys())
                        _atype_idx = next((i for i, v in enumerate(_TASK_TYPE_LABELS.values()) if v == task.task_type), 0)
                        _anew_type = _afc4.selectbox("Task type", _atype_keys, index=_atype_idx)
                        _afc5, _afc6 = st.columns(2)
                        _anew_dur = _afc5.number_input("Duration (min)", value=task.duration_minutes, min_value=1, max_value=240)
                        _afreq_opts = ["Once", "Daily", "Weekly", "Biweekly", "Monthly"]
                        _afreq_idx = next((i for i, f in enumerate(_afreq_opts) if f.lower() == (task.frequency or "once").lower()), 0)
                        _anew_freq = _afc6.selectbox("Frequency", _afreq_opts, index=_afreq_idx)
                        _afs, _afc = st.columns(2)
                        _asave = _afs.form_submit_button("💾 Save")
                        _acancel = _afc.form_submit_button("Cancel")
                    if _asave:
                        task.description = _anew_desc
                        task.priority = _PRIORITY_LABELS[_anew_pri]
                        task.duration_minutes = int(_anew_dur)
                        task.task_type = _TASK_TYPE_LABELS[_anew_type]
                        task.frequency = None if _anew_freq == "Once" else _anew_freq.lower()
                        if _anew_time != task.scheduled_time:
                            scheduler.reschedule_task(task.task_id, task.scheduled_date, _anew_time)
                        st.session_state.editing_task_id = None
                        st.session_state.editing_section = None
                        st.rerun()
                    if _acancel:
                        st.session_state.editing_task_id = None
                        st.session_state.editing_section = None
                        st.rerun()

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

        # Summary metrics
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Time", f"{plan.total_minutes} min")
        m2.metric("Tasks Selected", len(plan.selected_tasks))
        m3.metric("Tasks Skipped", len(plan.skipped_tasks))

        # Time utilization progress bar
        utilization = min(plan.total_minutes / available_minutes, 1.0)
        st.progress(utilization, text=f"Time utilization: {plan.total_minutes}/{available_minutes} min ({utilization:.0%})")

        # Selected tasks as cards
        _SCHED_PRI_ICON = {"HIGH": "🔴", "MEDIUM": "🟠", "LOW": "🔵"}
        _SCHED_TYPE_ICON = {"FEEDING": "🍽️", "MEDICATION": "💊", "GROOMING": "✂️", "VET_VISIT": "🏥", "EXERCISE": "🏃", "OTHER": "📋"}
        pet_map = {p.pet_id: p.name for p in st.session_state.pets}

        if plan.selected_tasks:
            st.markdown("#### Selected Tasks")
            for task in plan.selected_tasks:
                pri_key = task.priority.value.upper()
                type_key = task.task_type.value.upper()
                pri_icon = _SCHED_PRI_ICON.get(pri_key, "")
                type_icon = _SCHED_TYPE_ICON.get(type_key, "📋")
                type_label = task.task_type.value.replace("_", " ").title()
                pet_name = pet_map.get(task.pet_id, "Unknown")

                freq_label = (task.frequency or "once").capitalize()
                with st.container(border=True):
                    c1, c2, c3, c4, c5 = st.columns([1, 2.5, 1.2, 0.8, 1])
                    c1.markdown(f"**{task.scheduled_time.strftime('%H:%M')}**")
                    c2.markdown(f"{pri_icon} **{task.description}**  \n{type_icon} {type_label} · {pet_name}")
                    c3.markdown(f"Priority: **{pri_key}**")
                    c4.markdown(f"**{task.duration_minutes}** min")
                    c5.markdown(f"🔄 {freq_label}")
        else:
            st.info("No tasks were selected for this plan.")

        # Skipped tasks expander
        if plan.skipped_tasks:
            with st.expander(f"Skipped Tasks ({len(plan.skipped_tasks)})", expanded=False):
                for task in plan.skipped_tasks:
                    pri_key = task.priority.value.upper()
                    type_key = task.task_type.value.upper()
                    st.markdown(
                        f"- {_SCHED_PRI_ICON.get(pri_key, '')} **{task.description}** "
                        f"({_SCHED_TYPE_ICON.get(type_key, '')} {task.task_type.value.replace('_', ' ').title()}, "
                        f"{task.duration_minutes} min)"
                    )

        # Rationale expander
        if plan.rationale:
            with st.expander("Rationale", expanded=False):
                for note in plan.rationale:
                    st.markdown(f"- {note}")
