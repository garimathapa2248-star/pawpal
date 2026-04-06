import pytest
from datetime import datetime, timedelta
from pawpal_system import CareTask, PetProfile, Owner, OwnerBandwidth, ReSyncCoordinator

def test_task_completion():
    """Verify that calling markCompleted() changes the task's status to 'completed'."""
    task = CareTask("Test Task", "A test task", 10, "daily", 1, "Indoor", "Health", "high")
    assert task.status == "pending"
    task.markCompleted()
    assert task.status == "completed"

def test_complete_task_with_recurrence():
    """Verify that completing a recurring task creates a new task instance."""
    from pawpal_system import ReSyncCoordinator, Owner, OwnerBandwidth
    
    # Create owner with pet
    bandwidth = OwnerBandwidth(60, 60, 4, True)
    owner = Owner("Test", bandwidth)
    
    pet = PetProfile("Test Pet", "dog")
    recurring_task = CareTask("Daily Walk", "Morning walk", 30, "daily", 2, "Outdoor", "Exercise", "medium")
    pet.baseline_tasks.append(recurring_task)
    owner.addPet(pet)
    
    scheduler = ReSyncCoordinator(owner)
    
    # Initial state
    assert len(pet.baseline_tasks) == 1
    assert recurring_task.status == "pending"
    initial_candidate_count = len(scheduler.candidate_tasks)
    
    # Complete the task
    scheduler.complete_task(recurring_task)
    
    # Verify original task is completed
    assert recurring_task.status == "completed"
    
    # Verify a new task was created
    assert len(pet.baseline_tasks) == 2
    assert len(scheduler.candidate_tasks) == initial_candidate_count + 1
    
    # Verify the new task is pending and has the same properties
    new_task = pet.baseline_tasks[-1]
    assert new_task.status == "pending"
    assert new_task.title == recurring_task.title
    assert new_task.frequency == recurring_task.frequency
    assert new_task != recurring_task  # Different object

def test_task_addition():
    """Verify that adding a task to a Pet increases that pet's baseline task count."""
    pet = PetProfile("Test Pet", "dog")
    initial_count = len(pet.baseline_tasks)
    task = CareTask("New Task", "Another task", 15, "daily", 2, "Indoor", "Enrichment", "medium")
    pet.addBaselineTask(task)
    assert len(pet.baseline_tasks) == initial_count + 1
    assert pet.baseline_tasks[-1] == task

def test_sort_by_time():
    """Verify that sort_by_time() sorts tasks chronologically by their time attribute."""
    from pawpal_system import ReSyncCoordinator, Owner, OwnerBandwidth
    
    # Create a simple owner and scheduler
    bandwidth = OwnerBandwidth(60, 60, 4, True)
    owner = Owner("Test", bandwidth)
    scheduler = ReSyncCoordinator(owner)
    
    # Create tasks with different times
    task1 = CareTask("Morning Task", "Early task", 10, "daily", 1, "Indoor", "Health", "high", time="10:00")
    task2 = CareTask("Afternoon Task", "Later task", 15, "daily", 2, "Indoor", "Enrichment", "medium", time="14:30")
    task3 = CareTask("Evening Task", "Late task", 20, "daily", 3, "Indoor", "Exercise", "low", time="08:00")
    
    tasks = [task1, task2, task3]
    sorted_tasks = scheduler.sort_by_time(tasks)
    
    # Should be sorted: 08:00, 10:00, 14:30
    assert sorted_tasks[0].time == "08:00"
    assert sorted_tasks[1].time == "10:00"
    assert sorted_tasks[2].time == "14:30"

def test_detect_conflicts():
    """Verify that detect_conflicts() identifies time conflicts between tasks."""
    from pawpal_system import ReSyncCoordinator, Owner, OwnerBandwidth, PetProfile
    
    # Create owner with pets
    bandwidth = OwnerBandwidth(60, 60, 4, True)
    owner = Owner("Test", bandwidth)
    
    # Create pets with conflicting tasks
    pet1 = PetProfile("Rex", "dog")
    pet1.baseline_tasks.append(CareTask("Feed", "Morning feeding", 10, "daily", 1, "Indoor", "Health", "high", time="08:00"))
    
    pet2 = PetProfile("Luna", "cat") 
    pet2.optional_tasks.append(CareTask("Brush", "Grooming session", 20, "daily", 2, "Indoor", "Enrichment", "medium", time="08:00"))
    
    owner.addPet(pet1)
    owner.addPet(pet2)
    
    scheduler = ReSyncCoordinator(owner)
    
    # Test conflict detection
    conflicts = scheduler.detect_conflicts()
    
    assert len(conflicts) == 1
    assert "Warning: Feed and Brush both scheduled for 08:00" in conflicts[0]
    
    # Test with no conflicts
    pet2.optional_tasks[0].time = "09:00"  # Change time to avoid conflict
    conflicts = scheduler.detect_conflicts()
    assert len(conflicts) == 0


def test_task_sorting():
    """Verify that sort_by_time() correctly orders tasks chronologically."""
    # Create a simple owner and scheduler
    bandwidth = OwnerBandwidth(120, 120, 5, True)
    owner = Owner("Test Owner", bandwidth)
    scheduler = ReSyncCoordinator(owner)
    
    # Create tasks with different times in non-sequential order
    task1 = CareTask("Afternoon Walk", "Walk at 2 PM", 30, "daily", 2, "Outdoor", "Exercise", "medium", time="14:00")
    task2 = CareTask("Morning Breakfast", "Feed in morning", 20, "daily", 1, "Indoor", "Health", "high", time="08:00")
    task3 = CareTask("Midday Playtime", "Play session", 25, "daily", 2, "Indoor", "Enrichment", "low", time="11:00")
    
    tasks = [task1, task2, task3]
    sorted_tasks = scheduler.sort_by_time(tasks)
    
    # Assert tasks are sorted in chronological order: 08:00, 11:00, 14:00
    assert sorted_tasks[0].time == "08:00"
    assert sorted_tasks[0].title == "Morning Breakfast"
    assert sorted_tasks[1].time == "11:00"
    assert sorted_tasks[1].title == "Midday Playtime"
    assert sorted_tasks[2].time == "14:00"
    assert sorted_tasks[2].title == "Afternoon Walk"


def test_daily_recurrence():
    """Verify that completing a daily task creates a new task for the next day."""
    # Create owner with pet and daily task
    bandwidth = OwnerBandwidth(120, 120, 5, True)
    owner = Owner("Test Owner", bandwidth)
    
    pet = PetProfile("Buddy", "dog")
    daily_task = CareTask("Daily Walk", "Morning walk with Buddy", 30, "daily", 2, "Outdoor", "Exercise", "medium", time="08:00")
    pet.baseline_tasks.append(daily_task)
    owner.addPet(pet)
    
    scheduler = ReSyncCoordinator(owner)
    initial_task_count = len(pet.baseline_tasks)
    
    # Complete the task
    scheduler.complete_task(daily_task)
    
    # Verify original task is marked completed
    assert daily_task.status == "completed"
    
    # Verify a new task was created
    assert len(pet.baseline_tasks) == initial_task_count + 1
    new_task = pet.baseline_tasks[-1]
    
    # Verify the new task has pending status and same properties
    assert new_task.status == "pending"
    assert new_task.title == "Daily Walk"
    assert new_task.frequency == "daily"
    assert new_task.duration_minutes == 30
    assert new_task.category == "Exercise"


def test_conflict_detection():
    """Verify that detect_conflicts() identifies tasks scheduled at the same time for different pets."""
    # Create owner with two pets having conflicting tasks
    bandwidth = OwnerBandwidth(120, 120, 5, True)
    owner = Owner("Test Owner", bandwidth)
    
    # Create first pet with a task at 09:00
    pet1 = PetProfile("Max", "dog")
    task1 = CareTask("Dog Feeding", "Morning feeding", 10, "daily", 1, "Indoor", "Health", "high", time="09:00")
    pet1.baseline_tasks.append(task1)
    owner.addPet(pet1)
    
    # Create second pet with a task at the same time
    pet2 = PetProfile("Whiskers", "cat")
    task2 = CareTask("Cat Feeding", "Morning feeding", 10, "daily", 1, "Indoor", "Health", "high", time="09:00")
    pet2.baseline_tasks.append(task2)
    owner.addPet(pet2)
    
    scheduler = ReSyncCoordinator(owner)
    
    # Detect conflicts
    conflicts = scheduler.detect_conflicts()
    
    # Verify a conflict is detected
    assert len(conflicts) > 0
    assert "09:00" in conflicts[0]
    assert "Dog Feeding" in conflicts[0] or "Cat Feeding" in conflicts[0]


def test_empty_scheduler():
    """Verify that empty pet profiles and task lists don't cause errors during sorting or conflict detection."""
    # Create owner with no pets
    bandwidth = OwnerBandwidth(120, 120, 5, True)
    owner = Owner("Test Owner", bandwidth)
    scheduler = ReSyncCoordinator(owner)
    
    # Test sorting empty task list
    empty_tasks = []
    sorted_tasks = scheduler.sort_by_time(empty_tasks)
    assert sorted_tasks == []
    
    # Test conflict detection with no pets
    conflicts = scheduler.detect_conflicts()
    assert conflicts == []
    
    # Add a pet with no tasks and test again
    pet = PetProfile("EmptyPet", "dog")
    owner.addPet(pet)
    
    conflicts = scheduler.detect_conflicts()
    assert conflicts == []
    
    # Test sorting empty scheduled tasks
    empty_schedule = scheduler.generateDailyPlan()
    assert isinstance(empty_schedule, list)
