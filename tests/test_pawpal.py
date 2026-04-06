import pytest
from pawpal_system import CareTask, PetProfile

def test_task_completion():
    """Verify that calling markCompleted() changes the task's status to 'completed'."""
    task = CareTask("Test Task", "A test task", 10, "daily", 1, "Indoor", "Health", "high")
    assert task.status == "pending"
    task.markCompleted()
    assert task.status == "completed"

def test_task_addition():
    """Verify that adding a task to a Pet increases that pet's baseline task count."""
    pet = PetProfile("Test Pet", "dog")
    initial_count = len(pet.baseline_tasks)
    task = CareTask("New Task", "Another task", 15, "daily", 2, "Indoor", "Enrichment", "medium")
    pet.addBaselineTask(task)
    assert len(pet.baseline_tasks) == initial_count + 1
    assert pet.baseline_tasks[-1] == task
