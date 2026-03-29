from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, time, datetime, timedelta
from typing import Optional

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
    priority: int = 1  # 1=low, 2=medium, 3=high
    duration_minutes: int = 30  # for conflict detection
    recurrence_end_date: Optional[date] = None  # end of recurrence range

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

    def is_recurring(self) -> bool:
        """Return True if this task recurs beyond a single occurrence."""
        return self.frequency != "once"


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
        """Return incomplete tasks due on the scheduler's current date, sorted by time then priority."""
        today_tasks = [
            task
            for task in self.retrieveAllTasks()
            if task.dueDate == self.currentDate and not task.isCompleted
        ]
        # Sort by: time, then priority (descending)
        return sorted(today_tasks, key=lambda t: (t.dueTime, -t.priority))

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

    def getTasksForPet(self, petId: str) -> list[Task]:
        """Return all incomplete tasks for a specific pet."""
        return [task for task in self.retrieveAllTasks() if task.petId == petId and not task.isCompleted]

    def getTasksByStatus(self, isCompleted: bool) -> list[Task]:
        """Filter tasks by completion status."""
        return [task for task in self.retrieveAllTasks() if task.isCompleted == isCompleted]

    def getTasksByTimeWindow(self, start_time: time, end_time: time, date_filter: Optional[date] = None) -> list[Task]:
        """Get incomplete tasks within a time window, optionally for a specific date."""
        tasks = self.retrieveAllTasks()
        if date_filter:
            tasks = [t for t in tasks if t.dueDate == date_filter]
        return [t for t in tasks if start_time <= t.dueTime <= end_time and not t.isCompleted]

    def getTasksForPetAndStatus(self, petId: str, isCompleted: bool) -> list[Task]:
        """Combine filters: pet + status."""
        return [
            t for t in self.retrieveAllTasks()
            if t.petId == petId and t.isCompleted == isCompleted
        ]

    def expandRecurringTasks(self, startDate: date, endDate: date) -> list[Task]:
        """Expand all recurring tasks across a date range, generating new task instances."""
        expanded: list[Task] = []

        for pet in self.owner.viewPets():
            for task in pet.tasks:
                if not task.is_recurring():
                    # Non-recurring: add if in range
                    if startDate <= task.dueDate <= endDate:
                        expanded.append(task)
                else:
                    # Recurring: generate instances
                    current_date = max(task.dueDate, startDate)
                    recurrence_limit = task.recurrence_end_date or endDate

                    while current_date <= min(endDate, recurrence_limit):
                        # Create a new task instance for this occurrence
                        occurrence = Task(
                            taskId=f"{task.taskId}--{current_date.isoformat()}",
                            petId=task.petId,
                            description=task.description,
                            dueDate=current_date,
                            dueTime=task.dueTime,
                            frequency="once",  # mark as non-recurring
                            priority=task.priority,
                            duration_minutes=task.duration_minutes,
                            isCompleted=False,
                        )
                        expanded.append(occurrence)

                        # Advance by frequency
                        if task.frequency == "daily":
                            current_date += timedelta(days=1)
                        elif task.frequency == "weekly":
                            current_date += timedelta(weeks=1)
                        elif task.frequency == "monthly":
                            # Edge case: handle month-end dates gracefully
                            try:
                                if current_date.month == 12:
                                    current_date = current_date.replace(year=current_date.year + 1, month=1)
                                else:
                                    current_date = current_date.replace(month=current_date.month + 1)
                            except ValueError:
                                # Day doesn't exist in next month (e.g., Jan 31 → Feb 31)
                                break

        return sorted(expanded, key=lambda t: (t.dueDate, t.dueTime))

    def detectConflicts(self, date_filter: Optional[date] = None) -> dict:
        """Detect overlapping tasks for each pet on a given date."""
        target_date = date_filter or self.currentDate
        conflicts: dict = {}

        for pet in self.owner.viewPets():
            # Get tasks for this pet on the target date
            pet_tasks = [
                t for t in pet.viewTasks()
                if t.dueDate == target_date and not t.isCompleted
            ]

            # Group tasks by start time + duration overlap
            time_slots: dict = {}
            for task in pet_tasks:
                task_start = datetime.combine(task.dueDate, task.dueTime)
                task_end = task_start + timedelta(minutes=task.duration_minutes)

                # Check if this task overlaps with any existing slot
                found_overlap = False
                for slot_time, slot_tasks in time_slots.items():
                    slot_start = datetime.combine(target_date, slot_time)
                    slot_end = slot_start + timedelta(
                        minutes=max(t.duration_minutes for t in slot_tasks)
                    )

                    # Overlap detection: task_start < slot_end AND task_end > slot_start
                    if task_start < slot_end and task_end > slot_start:
                        slot_tasks.append(task)
                        found_overlap = True
                        break

                if not found_overlap:
                    # No overlap found, create new slot
                    time_slots[task.dueTime] = [task]

            # Collect conflict slots (len > 1)
            pet_conflicts = [
                (slot_time, slot_tasks)
                for slot_time, slot_tasks in time_slots.items()
                if len(slot_tasks) > 1
            ]

            if pet_conflicts:
                conflicts[pet.petId] = pet_conflicts

        return conflicts

    def getConflictReport(self, date_filter: Optional[date] = None) -> str:
        """Return a human-readable conflict report."""
        conflicts = self.detectConflicts(date_filter)

        if not conflicts:
            return "No scheduling conflicts detected."

        report = []
        for petId, conflict_slots in conflicts.items():
            pet = self.owner.getPet(petId)
            report.append(f"\n⚠ Conflicts for {pet.name}:")
            for slot_time, tasks in conflict_slots:
                times_str = ", ".join([
                    f"{t.dueTime.strftime('%H:%M')}–{(datetime.combine(date.today(), t.dueTime) + timedelta(minutes=t.duration_minutes)).time().strftime('%H:%M')}"
                    for t in tasks
                ])
                descriptions = ", ".join([t.description for t in tasks])
                report.append(f"  {times_str}: {descriptions}")

        return "\n".join(report)
