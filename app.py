import streamlit as st
from pawpal_system import Owner, PetProfile, CareTask, ReSyncCoordinator, OwnerBandwidth

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")

# Initialize Owner in session_state as a 'vault' for persistent data across app interactions
if 'owner' not in st.session_state:
    bandwidth = OwnerBandwidth(480, 480, 5, True)  # Default: 8 hours, energy 5
    st.session_state.owner = Owner("Jordan", bandwidth)

if 'scheduler' not in st.session_state:
    st.session_state.scheduler = ReSyncCoordinator(st.session_state.owner)

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to **PawPal+**, your intelligent pet care planning assistant.

This app helps you organize and schedule care tasks for your pet(s) based on time availability, priorities, and preferences.
"""
)

st.divider()

# ===== SETUP SECTION =====
st.subheader("📋 Setup: Owner & Pets")
col1, col2 = st.columns(2)

with col1:
    owner_name = st.text_input("Owner name", value=st.session_state.owner.name, key="owner_name_input")
    st.session_state.owner.name = owner_name

with col2:
    st.metric("Available Time (minutes)", st.session_state.owner.bandwidth.remaining_minutes)
    st.metric("Energy Level", st.session_state.owner.bandwidth.energy_level)

st.markdown("**Add a Pet**")
col1, col2, col3 = st.columns(3)
with col1:
    pet_name = st.text_input("Pet name", value="Mochi")
with col2:
    species = st.selectbox("Species", ["dog", "cat", "bird", "rabbit", "other"])
with col3:
    if st.button("➕ Add Pet"):
        pet = PetProfile(pet_name, species)
        st.session_state.owner.addPet(pet)
        st.session_state.scheduler = ReSyncCoordinator(st.session_state.owner)
        st.success(f"Pet '{pet_name}' added successfully!")
        st.rerun()

# Display current pets
if st.session_state.owner.pets:
    st.markdown(f"**Current Pets:** {', '.join([f'{p.pet_name} ({p.species})' for p in st.session_state.owner.pets])}")
else:
    st.info("No pets added yet. Add a pet to get started!")

st.divider()

# ===== TASK MANAGEMENT SECTION =====
st.subheader("✅ Add Tasks")
st.caption("Add care tasks for your pets with specific times and priorities.")

if st.session_state.owner.pets:
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        task_time = st.text_input("Time (HH:MM)", value="08:00", max_chars=5)
    with col3:
        duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=30)
    with col4:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        frequency = st.selectbox("Frequency", ["daily", "weekly", "one-time"])
    with col2:
        location = st.selectbox("Location", ["Indoor", "Outdoor"])
    with col3:
        category = st.selectbox("Category", ["Exercise", "Health", "Enrichment", "Grooming", "General"])
    
    selected_pet = st.selectbox("Add task to pet:", [p.pet_name for p in st.session_state.owner.pets])
    
    if st.button("➕ Add Task"):
        try:
            # Validate time format
            if len(task_time) == 5 and task_time[2] == ':':
                pet = next(p for p in st.session_state.owner.pets if p.pet_name == selected_pet)
                task = CareTask(
                    title=task_title,
                    description=f"{task_title} at {task_time}",
                    duration_minutes=duration,
                    frequency=frequency,
                    effort_level=2,
                    location=location,
                    category=category,
                    priority=priority,
                    time=task_time
                )
                pet.optional_tasks.append(task)
                st.session_state.scheduler = ReSyncCoordinator(st.session_state.owner)
                st.success(f"Task '{task_title}' added to {pet.pet_name}!")
                st.rerun()
            else:
                st.error("Please enter time in HH:MM format (e.g., 14:30)")
        except Exception as e:
            st.error(f"Error adding task: {e}")
else:
    st.warning("Please add a pet first to create tasks.")

st.divider()

# ===== PET DASHBOARD & TASK MANAGEMENT =====
st.subheader("📅 Pet Dashboard & Schedule")

if st.session_state.owner.pets:
    # Get scheduler instance
    scheduler = st.session_state.scheduler
    
    # Display conflict warnings at the top
    conflicts = scheduler.detect_conflicts()
    if conflicts:
        st.warning(f"⚠️ **Schedule Conflicts Detected:**\n\n" + "\n".join(conflicts))
    else:
        st.success("✅ No schedule conflicts detected!")
    
    # Display each pet's task dashboard
    for pet in st.session_state.owner.pets:
        with st.expander(f"🐾 {pet.pet_name} ({pet.species})", expanded=True):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**Tasks for {pet.pet_name}**")
                
                # Collect and sort all tasks
                all_tasks = pet.baseline_tasks + pet.optional_tasks
                
                if all_tasks:
                    sorted_tasks = scheduler.sort_by_time(all_tasks)
                    
                    # Create a table-like display with task management
                    for idx, task in enumerate(sorted_tasks):
                        task_col1, task_col2, task_col3, task_col4 = st.columns([2, 1, 1, 1])
                        
                        with task_col1:
                            status_icon = "✓" if task.status == "completed" else "○"
                            st.write(f"{status_icon} **{task.title}** @ {task.time}")
                        
                        with task_col2:
                            st.caption(f"{task.duration_minutes}m")
                        
                        with task_col3:
                            priority_color = {"high": "🔴", "medium": "🟡", "low": "🟢"}
                            st.caption(priority_color.get(task.priority, "⚪"))
                        
                        with task_col4:
                            if task.status != "completed":
                                if st.button("✅ Done", key=f"complete_{id(task)}_{idx}"):
                                    scheduler.complete_task(task)
                                    if task.frequency.lower() in ['daily', 'weekly']:
                                        st.success(f"✅ Task completed! Next {task.frequency} task scheduled.")
                                    else:
                                        st.success("✅ Task marked complete!")
                                    st.rerun()
                else:
                    st.info(f"No tasks assigned to {pet.pet_name} yet.")
            
            with col2:
                st.markdown("**Stats**")
                pending = sum(1 for t in all_tasks if t.status == "pending")
                completed = sum(1 for t in all_tasks if t.status == "completed")
                st.metric("Pending", pending)
                st.metric("Completed", completed)
                
                # Wellness debt display
                if pet.wellness_debt:
                    st.markdown("**Wellness Debt**")
                    for category, debt in pet.wellness_debt.items():
                        st.write(f"- {category}: {debt}")

else:
    st.info("No pets added yet. Add a pet in the Setup section to manage tasks.")

st.divider()

# ===== SCHEDULE GENERATION =====
st.subheader("🎯 Generate Daily Plan")
st.caption("Create an optimized schedule based on available time, priorities, and constraints.")

if st.button("📅 Generate Schedule"):
    if st.session_state.owner.pets:
        scheduler = ReSyncCoordinator(st.session_state.owner)
        st.session_state.scheduler = scheduler
        
        schedule = scheduler.generateDailyPlan()
        
        if schedule:
            st.success("✅ Schedule generated successfully!")
            
            st.markdown("**📋 Today's Optimized Schedule:**")
            sorted_schedule = scheduler.sort_by_time(schedule)
            
            for i, task in enumerate(sorted_schedule, 1):
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.write(f"**{i}. {task.title}** ({task.duration_minutes} min)")
                    st.caption(task.description)
                with col2:
                    st.caption(f"⏰ {task.time}")
                with col3:
                    priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}
                    st.caption(priority_icon.get(task.priority, "⚪"))
            
            total_time = sum(t.duration_minutes for t in schedule)
            st.info(f"Total scheduled time: {total_time} minutes | Remaining: {st.session_state.owner.bandwidth.remaining_minutes} minutes")
            
            # Display explanations for each task
            with st.expander("📝 Why were these tasks selected?"):
                for task in sorted_schedule:
                    explanation = scheduler.explainDecision(task)
                    st.write(f"- **{task.title}**: {explanation}")
        else:
            st.warning("No tasks could be scheduled. Check conflicts or adjust constraints.")
    else:
        st.error("Please add a pet and tasks first.")
