import streamlit as st
from pawpal_system import Owner, PetProfile, CareTask, ReSyncCoordinator, OwnerBandwidth

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

# Initialize Owner in session_state as a 'vault' for persistent data across app interactions
if 'owner' not in st.session_state:
    bandwidth = OwnerBandwidth(480, 480, 5, True)  # Default: 8 hours, energy 5
    st.session_state.owner = Owner("Jordan", bandwidth)

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

# Add Pet button
if st.button("Add Pet"):
    pet = PetProfile(pet_name, species)
    st.session_state.owner.addPet(pet)
    st.success(f"Pet '{pet_name}' added successfully!")
    st.rerun()  # Trigger rerun to update UI

st.markdown("### Tasks")
st.caption("Add a few tasks. In your final version, these should feed into your scheduler.")

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

if st.button("Add task"):
    if st.session_state.owner.pets:
        pet = st.session_state.owner.pets[-1]  # Add to the last added pet
        task = CareTask(task_title, f"Task: {task_title}", duration, "daily", 2, "Indoor", "General", priority)
        pet.optional_tasks.append(task)
        st.success(f"Task '{task_title}' added to {pet.pet_name}!")
        st.rerun()
    else:
        st.error("Please add a pet first.")

# Display current pets and tasks
if st.session_state.owner.pets:
    st.write("Current Pets and Tasks:")
    for pet in st.session_state.owner.pets:
        st.write(f"**{pet.pet_name} ({pet.species})**")
        all_tasks = pet.baseline_tasks + pet.optional_tasks
        if all_tasks:
            for task in all_tasks:
                st.write(f"- {task.title} ({task.duration_minutes} min, {task.priority})")
        else:
            st.write("- No tasks yet.")
else:
    st.info("No pets added yet.")

st.divider()

st.subheader("Build Schedule")
st.caption("This button calls your scheduling logic.")

if st.button("Generate schedule"):
    if st.session_state.owner.pets:
        scheduler = ReSyncCoordinator(st.session_state.owner)
        schedule = scheduler.generateDailyPlan()
        st.success("Schedule generated!")
        if schedule:
            st.write("**Today's Schedule:**")
            for i, task in enumerate(schedule, 1):
                st.write(f"{i}. {task.summary()}")
            st.write(f"Remaining time: {st.session_state.owner.bandwidth.remaining_minutes} minutes")
        else:
            st.info("No tasks scheduled.")
    else:
        st.error("Please add a pet and tasks first.")
