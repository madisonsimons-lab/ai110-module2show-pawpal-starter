import streamlit as st

from datetime import date, time

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
owner_name = st.text_input("Owner name", value="Jordan")
owner_email = st.text_input("Owner email", value="jordan@example.com")

# Persist one Owner object for the current browser session.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(
        ownerId="owner-session-1",
        name=owner_name,
        email=owner_email,
    )
else:
    # Keep the stored object, but sync editable display fields.
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
            )
            st.session_state.scheduler.addTask(new_task)
            st.success("Task scheduled successfully.")
        except ValueError as error:
            st.error(str(error))

st.divider()

st.subheader("Build Schedule")
schedule_day = st.date_input("Schedule date", value=date.today(), key="schedule_day")
st.session_state.scheduler.currentDate = schedule_day

if st.button("Generate schedule"):
    todays_tasks = st.session_state.scheduler.getTodaysTasks()
    if not todays_tasks:
        st.info("No tasks scheduled for this day.")
    else:
        task_rows = []
        for task in todays_tasks:
            pet = st.session_state.owner.getPet(task.petId)
            task_rows.append(
                {
                    "time": task.dueTime.strftime("%I:%M %p"),
                    "pet": pet.name,
                    "description": task.description,
                    "frequency": task.frequency,
                    "completed": task.isCompleted,
                }
            )
        st.success(f"Generated schedule for {schedule_day.isoformat()}")
        st.table(task_rows)
