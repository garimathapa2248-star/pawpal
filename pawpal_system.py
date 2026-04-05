from dataclasses import dataclass
from typing import List, Dict


@dataclass
class CareTask:
    title: str
    duration_minutes: int
    effort_level: int
    location: str
    category: str
    priority: str
    available: bool = True

    def isViable(self) -> bool:
        pass

    def markUnavailable(self, reason: str) -> None:
        pass

    def summary(self) -> str:
        pass


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
        pass

    def recordWellnessDebt(self, reason: str, amount: int) -> None:
        pass

    def isTaskMandatory(self, task: CareTask) -> bool:
        pass

    def needsCriticalCare(self) -> bool:
        pass


class OwnerBandwidth:
    def __init__(self, total_minutes: int, remaining_minutes: int, energy_level: int, is_workday: bool):
        self.total_minutes = total_minutes
        self.remaining_minutes = remaining_minutes
        self.energy_level = energy_level
        self.is_workday = is_workday

    def adjustMinutes(self, delta: int) -> None:
        pass

    def updateEnergy(self, level: int) -> None:
        pass

    def canFitTask(self, task: CareTask) -> bool:
        pass


class ReSyncCoordinator:
    def __init__(self, pet_profile: PetProfile, owner_bandwidth: OwnerBandwidth):
        self.pet_profile = pet_profile
        self.owner_bandwidth = owner_bandwidth
        self.candidate_tasks: List[CareTask] = []
        self.scheduled_tasks: List[CareTask] = []

    def generateDailyPlan(self) -> List[CareTask]:
        pass

    def resolveConflicts(self) -> None:
        pass

    def explainDecision(self, task: CareTask) -> str:
        pass

    def prioritizeTasks(self) -> List[CareTask]:
        pass
