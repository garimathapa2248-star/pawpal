from dataclasses import dataclass
from typing import List, Dict
from datetime import datetime, timedelta


@dataclass
class CareTask:
    title: str
    description: str
    duration_minutes: int
    frequency: str
    effort_level: int
    location: str
    category: str
    priority: str
    status: str = "pending"
    available: bool = True
    weather: str = "clear"
    dependencies: List[str] = None
    time: str = "00:00"  # HH:MM format

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []

    def isViable(self) -> bool:
        if not self.available or self.status == "completed":
            return False
        if self.location == "Outdoor" and self.weather in ["rainy", "stormy"]:
            return False
        return True

    def markUnavailable(self, reason: str) -> None:
        self.available = False

    def markCompleted(self) -> None:
        self.status = "completed"

    def summary(self) -> str:
        return f"{self.title}: {self.description}, {self.duration_minutes} min, {self.frequency}, status {self.status}"


@dataclass
class PetProfile:
    pet_name: str
    species: str
    baseline_tasks: List[CareTask] = None
    optional_tasks: List[CareTask] = None
    wellness_debt: Dict[str, int] = None
    non_negotiables: List[str] = None
    preferences: List[str] = None

    def __post_init__(self):
        if self.baseline_tasks is None:
            self.baseline_tasks = []
        if self.optional_tasks is None:
            self.optional_tasks = []
        if self.wellness_debt is None:
            self.wellness_debt = {}
        if self.non_negotiables is None:
            self.non_negotiables = []
        if self.preferences is None:
            self.preferences = []

    def addBaselineTask(self, task: CareTask) -> None:
        self.baseline_tasks.append(task)

    def recordWellnessDebt(self, reason: str, amount: int) -> None:
        self.wellness_debt[reason] = amount

    def isTaskMandatory(self, task: CareTask) -> bool:
        return task in self.baseline_tasks or task.title in self.non_negotiables

    def needsCriticalCare(self) -> bool:
        return any(debt > 2 for debt in self.wellness_debt.values())

    def violatesPreferences(self, task: CareTask) -> bool:
        for pref in self.preferences:
            if pref == "no outdoor" and task.location == "Outdoor":
                return True
            if pref == "no high effort" and task.effort_level > 3:
                return True
        return False


class OwnerBandwidth:
    def __init__(self, total_minutes: int, remaining_minutes: int, energy_level: int, is_workday: bool):
        self.total_minutes = total_minutes
        self.remaining_minutes = remaining_minutes
        self.energy_level = energy_level
        self.is_workday = is_workday

    def adjustMinutes(self, delta: int) -> None:
        self.remaining_minutes += delta

    def updateEnergy(self, level: int) -> None:
        self.energy_level = level

    def canFitTask(self, task: CareTask) -> bool:
        return self.remaining_minutes >= task.duration_minutes and self.energy_level >= task.effort_level

    def reset(self) -> None:
        self.remaining_minutes = self.total_minutes


class Owner:
    def __init__(self, name: str, bandwidth: OwnerBandwidth):
        self.name = name
        self.bandwidth = bandwidth
        self.pets: List[PetProfile] = []

    def addPet(self, pet: PetProfile) -> None:
        self.pets.append(pet)

    def aggregateTasks(self) -> List[CareTask]:
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.baseline_tasks)
            all_tasks.extend(pet.optional_tasks)
        return all_tasks


class ReSyncCoordinator:
    def __init__(self, owner: Owner):
        self.owner = owner
        self.candidate_tasks: List[CareTask] = owner.aggregateTasks()
        self.scheduled_tasks: List[CareTask] = []

    def generateDailyPlan(self) -> List[CareTask]:
        """Generate an optimized daily care plan respecting owner bandwidth and pet preferences."""
        self.owner.bandwidth.reset()  # Reset time
        self.scheduled_tasks = []
        all_tasks = self.candidate_tasks.copy()
        # Collect all baseline tasks from all pets
        baseline_tasks = []
        for pet in self.owner.pets:
            baseline_tasks.extend(pet.baseline_tasks)
        # First, try to include all baseline tasks
        for task in baseline_tasks:
            if task.isViable() and not any(pet.violatesPreferences(task) for pet in self.owner.pets) and self.owner.bandwidth.canFitTask(task):
                self.scheduled_tasks.append(task)
                self.owner.bandwidth.adjustMinutes(-task.duration_minutes)
        # Then, add optional in priority order, considering debt and duration
        optional = [t for t in all_tasks if t not in baseline_tasks]
        # To consider debt, aggregate max debt across pets
        debt_scores = {}
        for pet in self.owner.pets:
            for cat, debt in pet.wellness_debt.items():
                debt_scores[cat] = max(debt_scores.get(cat, 0), debt)
        prioritized_optional = sorted(optional, key=lambda t: (
            {'high': 0, 'medium': 1, 'low': 2}.get(t.priority, 3),
            -debt_scores.get(t.category, 0),  # Higher debt first
            t.duration_minutes  # Shorter first to fit more
        ))
        for task in prioritized_optional:
            if (task.isViable() and not any(pet.violatesPreferences(task) for pet in self.owner.pets) and 
                self.owner.bandwidth.canFitTask(task) and 
                all(dep in [t.title for t in self.scheduled_tasks] for dep in task.dependencies)):
                self.scheduled_tasks.append(task)
                self.owner.bandwidth.adjustMinutes(-task.duration_minutes)
        self.updateDebt()
        return self.scheduled_tasks

    def resolveConflicts(self) -> None:
        """Remove tasks that violate bandwidth or preference constraints from the schedule."""
        # Remove tasks that don't fit or violate prefs
        self.scheduled_tasks = [
            task for task in self.scheduled_tasks 
            if self.owner.bandwidth.canFitTask(task) and not any(pet.violatesPreferences(task) for pet in self.owner.pets)
        ]

    def explainDecision(self, task: CareTask) -> str:
        """Provide a human-readable explanation for why a task was included or excluded."""
        if task in self.scheduled_tasks:
            reasons = []
            for pet in self.owner.pets:
                if task in pet.baseline_tasks:
                    reasons.append("it's a baseline task")
                if pet.wellness_debt.get(task.category, 0) > 0:
                    reasons.append(f"it reduces {task.category} wellness debt")
            if reasons:
                return f"{task.title} was included because {', and '.join(set(reasons))}."
            else:
                return f"{task.title} was included as it fits the schedule."
        else:
            if not task.isViable():
                return f"{task.title} was excluded because it's not viable (e.g., weather or availability)."
            elif any(pet.violatesPreferences(task) for pet in self.owner.pets):
                return f"{task.title} was excluded due to owner preferences."
            elif not all(dep in [t.title for t in self.scheduled_tasks] for dep in task.dependencies):
                return f"{task.title} was excluded due to unmet dependencies."
            else:
                return f"{task.title} was excluded due to time or energy constraints."

    def prioritizeTasks(self) -> List[CareTask]:
        """Sort candidate tasks by priority, wellness debt, and duration for optimal scheduling."""
        debt_scores = {}
        for pet in self.owner.pets:
            for cat, debt in pet.wellness_debt.items():
                debt_scores[cat] = max(debt_scores.get(cat, 0), debt)
        return sorted(self.candidate_tasks, key=lambda t: (
            {'high': 0, 'medium': 1, 'low': 2}.get(t.priority, 3),
            -debt_scores.get(t.category, 0),
            t.duration_minutes
        ))

    def updateDebt(self) -> None:
        """Decrement wellness debt for each pet based on completed tasks in the schedule."""
        for task in self.scheduled_tasks:
            for pet in self.owner.pets:
                if task.category in pet.wellness_debt:
                    pet.wellness_debt[task.category] = max(0, pet.wellness_debt[task.category] - 1)

    def sort_by_time(self, tasks: List[CareTask]) -> List[CareTask]:
        """Sort tasks by their time attribute in 'HH:MM' format."""
        def time_to_minutes(time_str: str) -> int:
            """Convert 'HH:MM' string to minutes since midnight."""
            hours, minutes = map(int, time_str.split(':'))
            return hours * 60 + minutes
        
        return sorted(tasks, key=lambda task: time_to_minutes(task.time))

    def filter_tasks(self, tasks: List[CareTask] = None, status: str = None, pet_name: str = None) -> List[CareTask]:
        """Filter tasks by completion status and/or pet name."""
        if tasks is None:
            tasks = self.candidate_tasks
        
        filtered_tasks = tasks.copy()
        
        # Filter by status if provided
        if status is not None:
            filtered_tasks = [task for task in filtered_tasks if task.status == status]
        
        # Filter by pet name if provided
        if pet_name is not None:
            pet_tasks = []
            for pet in self.owner.pets:
                if pet.pet_name == pet_name:
                    pet_tasks.extend(pet.baseline_tasks)
                    pet_tasks.extend(pet.optional_tasks)
            # Only keep tasks that belong to the specified pet
            filtered_tasks = [task for task in filtered_tasks if task in pet_tasks]
        
        return filtered_tasks

    def complete_task(self, task: CareTask) -> None:
        """Mark a task as completed and handle recurrence if applicable."""
        # Mark the original task as completed
        task.markCompleted()
        
        # Check if task is recurring
        if task.frequency.lower() in ['daily', 'weekly']:
            # Find which pet this task belongs to
            for pet in self.owner.pets:
                if task in pet.baseline_tasks or task in pet.optional_tasks:
                    # Calculate next occurrence
                    today = datetime.now().date()
                    if task.frequency.lower() == 'daily':
                        next_date = today + timedelta(days=1)
                    elif task.frequency.lower() == 'weekly':
                        next_date = today + timedelta(weeks=1)
                    
                    # Create a new task instance for the next occurrence
                    new_task = CareTask(
                        title=task.title,
                        description=task.description,
                        duration_minutes=task.duration_minutes,
                        frequency=task.frequency,
                        effort_level=task.effort_level,
                        location=task.location,
                        category=task.category,
                        priority=task.priority,
                        status="pending",  # Fresh incomplete copy
                        available=task.available,
                        weather=task.weather,
                        dependencies=task.dependencies.copy() if task.dependencies else None,
                        time=task.time
                    )
                    
                    # Add the new task to the same pet's appropriate list
                    if task in pet.baseline_tasks:
                        pet.baseline_tasks.append(new_task)
                    else:
                        pet.optional_tasks.append(new_task)
                    
                    # Update candidate tasks to include the new recurring task
                    self.candidate_tasks.append(new_task)
                    break  # Found the pet, no need to continue

    def detect_conflicts(self, tasks: List[CareTask] = None) -> List[str]:
        """Detect time conflicts between tasks across all pets using a lightweight warning approach."""
        warnings = []
        time_slots = {}
        
        # If tasks are provided, use them; otherwise scan all pet tasks
        if tasks is not None:
            task_list = tasks
        else:
            task_list = []
            for pet in self.owner.pets:
                task_list.extend(pet.baseline_tasks + pet.optional_tasks)
        
        # Collect all tasks with their times using setdefault for efficiency
        for task in task_list:
            if task.time != "00:00" and task.status == "pending":  # Only check pending tasks that have been assigned times
                time_slots.setdefault(task.time, []).append(task)
        
        # Check for conflicts at each time slot
        for time_slot, tasks_at_time in time_slots.items():
            if len(tasks_at_time) > 1:
                # Multiple tasks at the same time - create warning
                task_names = [task.title for task in tasks_at_time]
                if len(task_names) == 2:
                    warning = f"Warning: {task_names[0]} and {task_names[1]} both scheduled for {time_slot}"
                else:
                    warning = f"Warning: {', '.join(task_names[:-1])}, and {task_names[-1]} all scheduled for {time_slot}"
                warnings.append(warning)
        
        return warnings
