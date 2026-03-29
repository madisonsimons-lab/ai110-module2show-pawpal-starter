import streamlit as st

import json
from datetime import date, time
from pathlib import Path

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Owner")
DATA_FILE = "data.json"


def persist_data() -> None:
    """Save current owner state to local JSON storage."""
    st.session_state.owner.save_to_json(DATA_FILE)


if "owner" not in st.session_state:
    data_path = Path(DATA_FILE)
    if data_path.exists():
        try:
            st.session_state.owner = Owner.load_from_json(DATA_FILE)
            st.success("Loaded pets and tasks from data.json")
        except (json.JSONDecodeError, ValueError, KeyError, OSError):
            st.warning("Could not load existing data.json. Starting fresh session data.")
            st.session_state.owner = Owner(
                ownerId="owner-session-1",
                name="Jordan",
                email="jordan@example.com",
            )
    else:
        st.session_state.owner = Owner(
            ownerId="owner-session-1",
            name="Jordan",
            email="jordan@example.com",
        )

owner_name = st.text_input("Owner name", value=st.session_state.owner.name)
owner_email = st.text_input("Owner email", value=st.session_state.owner.email)

st.session_state.owner.name = owner_name
st.session_state.owner.email = owner_email

if "scheduler" not in st.session_state:
    st.session_state.scheduler = Scheduler(
        schedulerId="scheduler-session-1",
        owner=st.session_state.owner,
        currentDate=date.today(),
    )

st.caption(
    f"Session owner loaded: {st.session_state.owner.name} "
    f"(id={st.session_state.owner.ownerId}, email={st.session_state.owner.email})"
)

st.divider()

st.subheader("Add a Pet")
with st.form("add_pet_form"):
    col1, col2 = st.columns(2)
    with col1:
        pet_id = st.text_input("Pet ID", value="pet-001")
        pet_name = st.text_input("Pet name", value="Mochi")
        pet_type = st.selectbox("Species", ["dog", "cat", "other"])
    with col2:
        pet_breed = st.text_input("Breed", value="Mixed")
        pet_age = st.number_input("Age", min_value=0, max_value=50, value=2)
        pet_notes = st.text_input("Notes", value="Loves treats")

    add_pet_submitted = st.form_submit_button("Add pet")

if add_pet_submitted:
    try:
        new_pet = Pet(
            petId=pet_id.strip(),
            name=pet_name.strip(),
            type=pet_type,
            breed=pet_breed.strip(),
            age=int(pet_age),
            notes=pet_notes.strip(),
            ownerId=st.session_state.owner.ownerId,
        )
        st.session_state.owner.addPet(new_pet)
        persist_data()
        st.success(f"Added pet: {new_pet.name}")
    except ValueError as error:
        st.error(str(error))

pets = st.session_state.owner.viewPets()
if pets:
    st.markdown("### Current Pets")
    pet_rows = [
        {
            "petId": pet.petId,
            "name": pet.name,
            "type": pet.type,
            "breed": pet.breed,
            "age": pet.age,
            "task_count": len(pet.tasks),
        }
        for pet in pets
    ]
    st.table(pet_rows)
else:
    st.info("No pets yet. Add one above.")

st.divider()

st.subheader("Schedule a Task")
if not pets:
    st.info("Add at least one pet before scheduling a task.")
else:
    pet_options = {f"{pet.name} ({pet.petId})": pet.petId for pet in pets}
    with st.form("add_task_form"):
        col1, col2 = st.columns(2)
        with col1:
            task_id = st.text_input("Task ID", value="task-001")
            selected_pet_label = st.selectbox("Choose pet", list(pet_options.keys()))
            task_description = st.text_input("Task description", value="Morning walk")
        with col2:
            task_date = st.date_input("Task date", value=date.today())
            task_time = st.time_input("Task time", value=time(8, 0))
            task_frequency = st.selectbox(
                "Frequency", ["once", "daily", "weekly", "monthly"]
            )
            task_priority_label = st.selectbox("Priority", ["Low", "Medium", "High"], index=1)
            duration_minutes = st.number_input(
                "Duration (minutes)",
                min_value=5,
                max_value=240,
                value=30,
                step=5,
            )

        add_task_submitted = st.form_submit_button("Schedule task")

    if add_task_submitted:
        try:
            selected_pet_id = pet_options[selected_pet_label]
            new_task = Task(
                taskId=task_id.strip(),
                petId=selected_pet_id,
                description=task_description.strip(),
                dueDate=task_date,
                dueTime=task_time,
                frequency=task_frequency,
                priority={"Low": 1, "Medium": 2, "High": 3}[task_priority_label],
                duration_minutes=int(duration_minutes),
            )
            st.session_state.scheduler.addTask(new_task)
            persist_data()
            st.success("Task scheduled successfully.")
        except ValueError as error:
            st.error(str(error))

st.divider()

st.subheader("Build Schedule")
schedule_day = st.date_input("Schedule date", value=date.today(), key="schedule_day")
st.session_state.scheduler.currentDate = schedule_day

pet_filter_options = {"All pets": None}
for pet in st.session_state.owner.viewPets():
    pet_filter_options[f"{pet.name} ({pet.petId})"] = pet.petId

filter_col1, filter_col2 = st.columns(2)
with filter_col1:
    selected_pet_filter = st.selectbox("Pet filter", list(pet_filter_options.keys()))
with filter_col2:
    status_filter_label = st.selectbox(
        "Status filter",
        ["Incomplete only", "Completed only", "All"],
    )

use_time_window = st.checkbox("Filter by time window")
if use_time_window:
    time_col1, time_col2 = st.columns(2)
    with time_col1:
        start_time = st.time_input("Start time", value=time(7, 0), key="start_time")
    with time_col2:
        end_time = st.time_input("End time", value=time(20, 0), key="end_time")

if st.button("Generate schedule"):
    status_filter_map = {
        "Incomplete only": False,
        "Completed only": True,
        "All": None,
    }
    requested_pet_id = pet_filter_options[selected_pet_filter]
    requested_status = status_filter_map[status_filter_label]

    filtered_tasks = st.session_state.scheduler.filter_by_status_and_pet(
        petId=requested_pet_id,
        isCompleted=requested_status,
    )
    filtered_tasks = [task for task in filtered_tasks if task.dueDate == schedule_day]

    if use_time_window:
        if start_time > end_time:
            st.error("Start time must be before or equal to end time.")
            st.stop()

        window_tasks = st.session_state.scheduler.getTasksByTimeWindow(
            start_time,
            end_time,
            date_filter=schedule_day,
        )
        allowed_ids = {task.taskId for task in window_tasks}
        filtered_tasks = [task for task in filtered_tasks if task.taskId in allowed_ids]

    sorted_tasks = st.session_state.scheduler.sort_by_time_and_priority(filtered_tasks)

    if not sorted_tasks:
        st.info("No tasks scheduled for this day.")
    else:
        priority_labels = {1: "Low", 2: "Medium", 3: "High"}
        priority_badges = {1: "🔵 Low", 2: "🟡 Medium", 3: "🔴 High"}

        def task_emoji(description: str) -> str:
            lower = description.lower()
            if "walk" in lower:
                return "🚶"
            if "feed" in lower or "food" in lower:
                return "🍽️"
            if "med" in lower:
                return "💊"
            if "vet" in lower:
                return "🩺"
            return "🐾"

        task_rows = []
        for task in sorted_tasks:
            pet = st.session_state.owner.getPet(task.petId)
            task_rows.append(
                {
                    "task": f"{task_emoji(task.description)} {task.description}",
                    "time": task.dueTime.strftime("%I:%M %p"),
                    "pet": pet.name,
                    "priority": priority_badges.get(task.priority, "⚪ Unknown"),
                    "frequency": task.frequency,
                    "duration(min)": task.duration_minutes,
                    "status": "✅ Done" if task.isCompleted else "⏳ Pending",
                }
            )
        st.success(
            f"Generated schedule for {schedule_day.isoformat()} ({len(sorted_tasks)} task(s))."
        )
        st.table(task_rows)

    same_time_warning_report = st.session_state.scheduler.getWarningReport(schedule_day)
    if same_time_warning_report == "No same-time scheduling warnings.":
        st.success("No same-time scheduling warnings for this date.")
    else:
        st.warning("Potential same-time task conflicts found.")
        st.warning(same_time_warning_report)

    overlap_conflicts = st.session_state.scheduler.detectConflicts(schedule_day)
    if overlap_conflicts:
        conflict_rows = []
        for pet_id, slots in overlap_conflicts.items():
            pet_name = st.session_state.owner.getPet(pet_id).name
            for slot_time, slot_tasks in slots:
                conflict_rows.append(
                    {
                        "pet": pet_name,
                        "conflict_start": slot_time.strftime("%I:%M %p"),
                        "tasks": ", ".join(task.description for task in slot_tasks),
                    }
                )

        st.warning("Overlapping task durations detected. Consider moving one task.")
        st.table(conflict_rows)
    else:
        st.success("No overlapping task-duration conflicts for this date.")

st.divider()
st.subheader("Find Next Available Slot")

if pets:
    slot_pet_options = {f"{pet.name} ({pet.petId})": pet.petId for pet in pets}
    slot_col1, slot_col2, slot_col3 = st.columns(3)
    with slot_col1:
        slot_pet_label = st.selectbox("Pet", list(slot_pet_options.keys()), key="slot_pet")
    with slot_col2:
        slot_duration = st.number_input("Needed minutes", min_value=5, max_value=180, value=30, step=5)
    with slot_col3:
        slot_search_days = st.number_input("Search days", min_value=1, max_value=30, value=7)

    if st.button("Suggest next free slot"):
        pet_id = slot_pet_options[slot_pet_label]
        suggestion = st.session_state.scheduler.find_next_available_slot(
            petId=pet_id,
            duration_minutes=int(slot_duration),
            start_date=schedule_day,
            search_days=int(slot_search_days),
        )
        if suggestion is None:
            st.warning("No free slot found in the selected search window.")
        else:
            slot_date, slot_time = suggestion
            st.success(
                "Suggested slot: "
                f"{slot_date.isoformat()} at {slot_time.strftime('%I:%M %p')}"
            )

save_col1, save_col2 = st.columns([1, 2])
with save_col1:
    if st.button("Save now"):
        persist_data()
        st.success("Saved to data.json")
with save_col2:
    st.caption("PawPal+ also auto-saves when you add pets or tasks.")
