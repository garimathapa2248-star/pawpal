import pytest
from pawpal_system import CareTask, PetProfile

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
