from pawpal_system import CareTask, PetProfile, OwnerBandwidth, Owner, ReSyncCoordinator
from datetime import datetime, date

def assign_time_slots(tasks: list, start_hour: int = 8) -> list:
    """Assign tasks to specific time slots starting from start_hour."""
    scheduled = []
    current_time = start_hour * 60  # Convert to minutes
    
    for task in tasks:
        # If task already has a time set (not default), use it instead of assigning new time
        if task.time != "00:00":
            scheduled.append(task)
            continue
            
        if task.category == "Health" and task.priority == "high":
            # Force morning feeding tasks
            if "Feed" in task.title and current_time < 10 * 60:
                task.time = format_time(current_time)  # Set time on task
                scheduled.append(task)
                current_time += task.duration_minutes
                continue
        
        # Check if task fits in remaining day (assume 8 PM cutoff)
        if current_time + task.duration_minutes <= 20 * 60:
            task.time = format_time(current_time)  # Set time on task
            scheduled.append(task)
            current_time += task.duration_minutes + 15  # Add 15 min buffer
        else:
            # Skip task if it doesn't fit
            continue
    
    return scheduled

def detect_conflicts(scheduler: ReSyncCoordinator, schedule: list) -> list:
    """Detect various types of scheduling conflicts."""
    conflicts = []
    
    # Pet availability conflicts
    pet_tasks = {}
    for task in schedule:
        for pet in scheduler.owner.pets:
            if task in pet.baseline_tasks + pet.optional_tasks:
                if pet.pet_name not in pet_tasks:
                    pet_tasks[pet.pet_name] = []
                pet_tasks[pet.pet_name].append(task)
    
    for pet_name, tasks in pet_tasks.items():
        # Check if pet has multiple high-effort tasks
        high_effort = [t for t in tasks if t.effort_level > 3]
        if len(high_effort) > 1:
            conflicts.append(f"{pet_name} has multiple high-effort tasks")
    
    # Dependency conflicts
    for task in schedule:
        for dep in task.dependencies:
            if not any(dep in t.title for t in schedule):
                conflicts.append(f"{task.title} missing dependency: {dep}")
    
    return conflicts

def format_time(minutes: int) -> str:
    """Convert minutes since midnight to HH:MM format."""
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours:02d}:{mins:02d}"

def main():
    # Create owner with bandwidth (60 minutes, energy level 4)
    bandwidth = OwnerBandwidth(60, 60, 4, True)
    owner = Owner("Jordan", bandwidth)

    # Create first pet: Mochi (dog)
    mochi = PetProfile("Mochi", "dog", preferences=["no high effort"])
    mochi.addBaselineTask(CareTask("Feed", "Morning feeding", 10, "daily", 1, "Indoor", "Health", "high"))
    mochi.optional_tasks = [
        CareTask("Walk", "Evening walk", 30, "daily", 3, "Outdoor", "Exercise", "medium"),
        CareTask("Play", "Indoor play", 15, "daily", 2, "Indoor", "Enrichment", "low")
    ]
    mochi.recordWellnessDebt("Exercise", 2)
    owner.addPet(mochi)

    # Create second pet: Whiskers (cat)
    whiskers = PetProfile("Whiskers", "cat", preferences=["no outdoor"])
    whiskers.addBaselineTask(CareTask("Feed Cat", "Cat food", 5, "daily", 1, "Indoor", "Health", "high"))
    # Intentionally create a task that conflicts with Mochi's feeding time
    whiskers.optional_tasks = [
        CareTask("Brush", "Grooming session", 20, "daily", 2, "Indoor", "Enrichment", "medium", time="08:00"),  # Same time as Feed
        CareTask("Laser Play", "Interactive play", 10, "daily", 1, "Indoor", "Enrichment", "low")
    ]
    whiskers.recordWellnessDebt("Enrichment", 1)
    owner.addPet(whiskers)

    # Create scheduler and generate plan
    scheduler = ReSyncCoordinator(owner)
    schedule = scheduler.generateDailyPlan()

    # Print Today's Schedule
    print("🐾 PawPal+ Today's Schedule for", owner.name)
    print("=" * 40)
    if schedule:
        for i, task in enumerate(schedule, 1):
            print(f"{i}. {task.summary()}")
    else:
        print("No tasks scheduled.")
    print(f"\nRemaining time: {owner.bandwidth.remaining_minutes} minutes")
    print(f"Remaining energy: {owner.bandwidth.energy_level}")

    # Demonstrate time-slot assignment
    print("\n📅 Time-Slot Assignment:")
    print("-" * 30)
    time_assigned_tasks = assign_time_slots(schedule)
    
    # Demonstrate sorting by time
    sorted_tasks = scheduler.sort_by_time(time_assigned_tasks)
    for task in sorted_tasks:
        print(f"{task.time}: {task.title} ({task.duration_minutes} min)")

    # Demonstrate conflict detection BEFORE task completion
    print("\n⚠️  Time Conflict Detection:")
    print("-" * 28)
    # Use the time-assigned tasks for conflict detection since they have proper times set
    conflicts = scheduler.detect_conflicts(time_assigned_tasks)
    if conflicts:
        print("Conflicts found:")
        for conflict in conflicts:
            print(f"- {conflict}")
    else:
        print("No time conflicts detected!")
    
    print("\nProgram continues running despite conflicts...")

    # Demonstrate filtering by pet
    print("\n🐕 Tasks for Mochi:")
    print("-" * 20)
    mochi_tasks = scheduler.filter_tasks(pet_name="Mochi")
    for task in mochi_tasks:
        print(f"- {task.title} ({task.status})")

    # Demonstrate filtering by status
    print("\n✅ Pending Tasks:")
    print("-" * 18)
    pending_tasks = scheduler.filter_tasks(status="pending")
    for task in pending_tasks:
        print(f"- {task.title}")

    # Demonstrate combined filtering
    print("\n🐱 Completed Tasks for Whiskers:")
    print("-" * 32)
    whiskers_completed = scheduler.filter_tasks(status="completed", pet_name="Whiskers")
    if whiskers_completed:
        for task in whiskers_completed:
            print(f"- {task.title}")
    else:
        print("No completed tasks found for Whiskers.")

    # NEW: Demonstrate sorting and filtering with out-of-order tasks
    print("\n🔄 Out-of-Order Tasks Demonstration:")
    print("-" * 40)
    
    # Create tasks with explicit times that are out of chronological order
    out_of_order_tasks = [
        CareTask("Evening Task", "Late evening activity", 15, "daily", 2, "Indoor", "Enrichment", "medium", time="19:30"),
        CareTask("Morning Task", "Early morning activity", 10, "daily", 1, "Indoor", "Health", "high", time="08:00"),
        CareTask("Afternoon Task", "Midday activity", 20, "daily", 3, "Outdoor", "Exercise", "low", time="14:15"),
        CareTask("Lunch Task", "Noon activity", 5, "daily", 1, "Indoor", "Health", "high", time="12:00"),
    ]
    
    print("Original order (unsorted):")
    for task in out_of_order_tasks:
        print(f"  {task.time}: {task.title}")
    
    # Sort them chronologically
    sorted_out_of_order = scheduler.sort_by_time(out_of_order_tasks)
    print("\nAfter sorting by time:")
    for task in sorted_out_of_order:
        print(f"  {task.time}: {task.title}")
    
    # Filter the sorted tasks
    print("\nFiltered results from sorted tasks:")
    morning_tasks = scheduler.filter_tasks(tasks=sorted_out_of_order, status="pending")
    print(f"  Pending tasks: {len(morning_tasks)} found")
    
    # Show filtering by time range (morning tasks before 12:00)
    morning_only = [task for task in sorted_out_of_order if task.time < "12:00"]
    print(f"  Morning tasks (before 12:00): {len(morning_only)} found")
    for task in morning_only:
        print(f"    {task.time}: {task.title}")

    # Demonstrate task completion with recurrence
    print("\n✅ Task Completion with Recurrence:")
    print("-" * 35)
    
    # Find a daily task to complete
    daily_task = None
    for task in scheduler.candidate_tasks:
        if task.frequency.lower() == "daily" and task.status == "pending":
            daily_task = task
            break
    
    if daily_task:
        print(f"Completing task: {daily_task.title} (frequency: {daily_task.frequency})")
        print(f"Before completion - Task status: {daily_task.status}")
        
        # Count tasks before completion
        initial_task_count = len(scheduler.candidate_tasks)
        
        # Complete the task using the new method
        scheduler.complete_task(daily_task)
        
        print(f"After completion - Task status: {daily_task.status}")
        print(f"Total tasks after completion: {len(scheduler.candidate_tasks)} (was {initial_task_count})")
        
        # Show that a new task was created
        new_tasks = [t for t in scheduler.candidate_tasks if t.status == "pending" and t.title == daily_task.title]
        print(f"New pending tasks with same title: {len(new_tasks)}")
        
        if new_tasks:
            print(f"New task details: {new_tasks[-1].title} - Status: {new_tasks[-1].status}")
    else:
        print("No daily tasks found to complete.")

if __name__ == "__main__":
    main()
