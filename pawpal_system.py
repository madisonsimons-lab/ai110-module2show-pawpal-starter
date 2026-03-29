from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, time

VALID_FREQUENCIES = {"once", "daily", "weekly", "monthly"}


@dataclass
class Task:
    taskId: str
    petId: str
    description: str
    dueDate: date
    dueTime: time
    frequency: str = "once"
    isCompleted: bool = False

    def __post_init__(self) -> None:
        """Validate task frequency after dataclass initialization."""
        if self.frequency not in VALID_FREQUENCIES:
            raise ValueError(
                f"Invalid frequency '{self.frequency}'. "
                f"Expected one of {sorted(VALID_FREQUENCIES)}."
            )

    def createTask(self) -> None:
        """Reset a task to an incomplete state."""
        self.isCompleted = False

    def editTask(
        self,
        description: str,
        due_date: date,
        due_time: time,
        frequency: str,
    ) -> None:
        """Update core task details and recurrence frequency."""
        if frequency not in VALID_FREQUENCIES:
            raise ValueError(
                f"Invalid frequency '{frequency}'. "
                f"Expected one of {sorted(VALID_FREQUENCIES)}."
            )

        self.description = description
        self.dueDate = due_date
        self.dueTime = due_time
        self.frequency = frequency

    def markComplete(self) -> None:
        """Mark a task as completed."""
        self.isCompleted = True

    def mark_complete(self) -> None:
        """Mark a task complete using snake_case naming."""
        self.markComplete()

    def deleteTask(self) -> None:
        """Soft-delete a task by marking it completed."""
        # Scheduler or Pet handles collection removal; this flag supports soft delete behavior.
        self.isCompleted = True

    def displayTask(self) -> str:
        """Return a human-readable summary of a task."""
        completion = "done" if self.isCompleted else "pending"
        return (
            f"Task[{self.taskId}] for pet {self.petId}: {self.description} "
            f"on {self.dueDate.isoformat()} at {self.dueTime.isoformat()} "
            f"({self.frequency}, {completion})"
        )


@dataclass
class Pet:
    petId: str
    name: str
    type: str
    breed: str
    age: int
    notes: str
    ownerId: str
    tasks: list[Task] = field(default_factory=list)

    def updatePetInfo(
        self,
        name: str,
        pet_type: str,
        breed: str,
        age: int,
        notes: str,
    ) -> None:
        """Update editable profile fields for a pet."""
        self.name = name
        self.type = pet_type
        self.breed = breed
        self.age = age
        self.notes = notes

    def displayPetDetails(self) -> str:
        """Return a human-readable summary of a pet profile."""
        return (
            f"Pet[{self.petId}] {self.name} ({self.type}, {self.breed}), "
            f"age {self.age}, owner={self.ownerId}, tasks={len(self.tasks)}"
        )

    def addTask(self, task: Task) -> None:
        """Add a task to this pet after validating identifiers."""
        if task.petId != self.petId:
            raise ValueError(
                f"Task petId '{task.petId}' does not match petId '{self.petId}'."
            )

        if any(existing.taskId == task.taskId for existing in self.tasks):
            raise ValueError(f"Task ID '{task.taskId}' already exists for pet '{self.petId}'.")

        self.tasks.append(task)

    def add_task(self, task: Task) -> None:
        """Add a task using snake_case naming."""
        self.addTask(task)

    def removeTask(self, taskId: str) -> None:
        """Remove a task by id from this pet."""
        for index, task in enumerate(self.tasks):
            if task.taskId == taskId:
                self.tasks.pop(index)
                return
        raise ValueError(f"Task ID '{taskId}' not found for pet '{self.petId}'.")

    def viewTasks(self) -> list[Task]:
        """Return this pet's tasks sorted by date and time."""
        return sorted(self.tasks, key=lambda t: (t.dueDate, t.dueTime))


class Owner:
    def __init__(self, ownerId: str, name: str, email: str) -> None:
        """Initialize an owner with empty pet collections."""
        self.ownerId = ownerId
        self.name = name
        self.email = email
        self.listOfPets: list[Pet] = []
        self._petsById: dict[str, Pet] = {}

    def addPet(self, pet: Pet) -> None:
        """Register a new pet for this owner."""
        if pet.ownerId != self.ownerId:
            raise ValueError(
                f"Pet ownerId '{pet.ownerId}' does not match owner '{self.ownerId}'."
            )

        if pet.petId in self._petsById:
            raise ValueError(f"Pet ID '{pet.petId}' already exists for this owner.")

        self.listOfPets.append(pet)
        self._petsById[pet.petId] = pet

    def removePet(self, petId: str) -> None:
        """Remove one of the owner's pets by id."""
        pet = self._petsById.pop(petId, None)
        if pet is None:
            raise ValueError(f"Pet ID '{petId}' not found for owner '{self.ownerId}'.")

        self.listOfPets.remove(pet)

    def viewPets(self) -> list[Pet]:
        """Return a shallow copy of the owner's pet list."""
        return list(self.listOfPets)

    def getPet(self, petId: str) -> Pet:
        """Retrieve a pet by id for this owner."""
        pet = self._petsById.get(petId)
        if pet is None:
            raise ValueError(f"Pet ID '{petId}' not found for owner '{self.ownerId}'.")
        return pet

    def assignTaskToPet(self, petId: str, task: Task) -> None:
        """Assign a task to one of the owner's pets."""
        pet = self.getPet(petId)
        pet.addTask(task)

    def getAllTasks(self) -> list[Task]:
        """Aggregate all tasks across every pet owned by this owner."""
        tasks: list[Task] = []
        for pet in self.listOfPets:
            tasks.extend(pet.viewTasks())
        return sorted(tasks, key=lambda t: (t.dueDate, t.dueTime))


class Scheduler:
    def __init__(self, schedulerId: str, owner: Owner, currentDate: date) -> None:
        """Initialize the scheduler with an owner context and current date."""
        self.schedulerId = schedulerId
        self.owner = owner
        self.currentDate = currentDate

    def retrieveAllTasks(self) -> list[Task]:
        """Retrieve every task from all pets associated with the owner."""
        # Core retrieval strategy: aggregate every task from every pet owned by this owner.
        return self.owner.getAllTasks()

    def addTask(self, task: Task) -> None:
        """Add a task by delegating assignment to the owner."""
        self.owner.assignTaskToPet(task.petId, task)

    def removeTask(self, taskId: str) -> None:
        """Remove a task id from whichever pet currently owns it."""
        for pet in self.owner.viewPets():
            for task in pet.tasks:
                if task.taskId == taskId:
                    pet.removeTask(taskId)
                    return
        raise ValueError(f"Task ID '{taskId}' not found across owner's pets.")

    def getTodaysTasks(self) -> list[Task]:
        """Return incomplete tasks due on the scheduler's current date."""
        return [
            task
            for task in self.retrieveAllTasks()
            if task.dueDate == self.currentDate and not task.isCompleted
        ]

    def getUpcomingTasks(self) -> list[Task]:
        """Return incomplete tasks due after the scheduler's current date."""
        return [
            task
            for task in self.retrieveAllTasks()
            if task.dueDate > self.currentDate and not task.isCompleted
        ]

    def organizeTasksByDate(self) -> dict[date, list[Task]]:
        """Group all tasks by due date with each day sorted by time."""
        organized: dict[date, list[Task]] = {}
        for task in self.retrieveAllTasks():
            organized.setdefault(task.dueDate, []).append(task)

        for task_date in organized:
            organized[task_date].sort(key=lambda t: t.dueTime)

        return dict(sorted(organized.items(), key=lambda item: item[0]))
