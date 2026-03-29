import streamlit as st
from pawpal_systems import Owner, Pet, Task, Scheduler, Priority, Frequency
from datetime import time

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

st.subheader("Quick Demo Inputs (UI only)")
owner_name = st.text_input("Owner name", value="Jordan")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

# Check and initialize owner in session_state
if "owner" not in st.session_state:
    st.session_state.owner = None

if st.button("Create Owner and Pet"):
    if st.session_state.owner is None:
        pet = Pet(pet_name, species.capitalize(), "Unknown", 1)  # Default breed and age
        owner = Owner(owner_name, f"{owner_name.lower()}@example.com", 8.0, time(8, 0), time(22, 0))
        owner.pets.append(pet)
        st.session_state.owner = owner
        st.success("Owner and pet created!")
    else:
        st.info("Owner already exists in session.")

st.markdown("### Tasks")
st.caption("Add a few tasks. In your final version, these should feed into your scheduler.")

if "tasks" not in st.session_state:
    st.session_state.tasks = []

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

if st.button("Add task"):
    if st.session_state.owner is not None:
        # Create Task object and add to owner
        pet = st.session_state.owner.pets[0] if st.session_state.owner.pets else None
        if pet:
            priority_enum = Priority.HIGH if priority == "high" else Priority.MEDIUM if priority == "medium" else Priority.LOW
            task = Task(str(len(st.session_state.owner.tasks) + 1), task_title, pet, "General", int(duration), priority_enum, Frequency.DAILY)
            st.session_state.owner.add_task(task)
            st.success(f"Task '{task_title}' added to owner!")
        else:
            st.error("No pet found for owner.")
    else:
        st.warning("Create an owner first before adding tasks.")
    # Still add to session_state.tasks for display
    st.session_state.tasks.append(
        {"title": task_title, "duration_minutes": int(duration), "priority": priority}
    )

if st.session_state.tasks:
    st.write("Current tasks (UI view):")
    st.table(st.session_state.tasks)
else:
    st.info("No tasks yet. Add one above.")

# Display owner data if exists
if st.session_state.owner:
    st.subheader("Current Owner Data")
    st.write(f"**Owner:** {st.session_state.owner.name} ({st.session_state.owner.email})")
    st.write("**Pets:**")
    for pet in st.session_state.owner.pets:
        st.write(f"- {pet.summary()}")
    st.write("**Tasks:**")
    for task in st.session_state.owner.tasks:
        st.write(f"- {task.name} ({task.duration_min} min, Priority: {task.priority.name}, Frequency: {task.frequency.value})")

st.markdown("### Add Another Pet")
new_pet_name = st.text_input("New Pet Name", key="new_pet_name")
new_species = st.selectbox("New Species", ["Dog", "Cat", "Other"], key="new_species")
new_breed = st.text_input("Breed", key="new_breed")
new_age = st.number_input("Age", min_value=0, max_value=30, value=1, key="new_age")

if st.button("Add Pet"):
    if st.session_state.owner:
        new_pet = Pet(new_pet_name, new_species, new_breed, new_age)
        st.session_state.owner.pets.append(new_pet)
        st.success(f"Pet '{new_pet_name}' added!")
        st.rerun()  # Refresh to update display
    else:
        st.warning("Create an owner first before adding pets.")

st.divider()

st.subheader("Build Schedule")
st.caption("This button should call your scheduling logic once you implement it.")

if st.button("Generate schedule"):
    if st.session_state.owner is not None and st.session_state.owner.tasks:
        scheduler = Scheduler(st.session_state.owner)
        plan = scheduler.generate_plan()
        st.subheader("Generated Schedule")
        st.code(plan.to_summary())
        st.success("Schedule generated!")
    else:
        st.warning("Create an owner and add tasks first.")
