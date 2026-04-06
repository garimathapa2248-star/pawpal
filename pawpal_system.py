from dataclasses import dataclass
from typing import List, Dict


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
        # Remove tasks that don't fit or violate prefs
        self.scheduled_tasks = [
            task for task in self.scheduled_tasks 
            if self.owner.bandwidth.canFitTask(task) and not any(pet.violatesPreferences(task) for pet in self.owner.pets)
        ]

    def explainDecision(self, task: CareTask) -> str:
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
        for task in self.scheduled_tasks:
            for pet in self.owner.pets:
                if task.category in pet.wellness_debt:
                    pet.wellness_debt[task.category] = max(0, pet.wellness_debt[task.category] - 1)
