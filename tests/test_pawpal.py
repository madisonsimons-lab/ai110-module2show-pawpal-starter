from datetime import date, time, timedelta
from pathlib import Path
import tempfile

from pawpal_system import Pet, Task, Owner, Scheduler


def test_mark_complete_updates_task_status() -> None:
	task = Task(
		taskId="task-1",
		petId="pet-1",
		description="Morning walk",
		dueDate=date.today(),
		dueTime=time(8, 0),
		frequency="daily",
	)

	assert task.isCompleted is False

	task.mark_complete()

	assert task.isCompleted is True


def test_mark_task_complete_creates_next_daily_occurrence() -> None:
	owner = Owner(ownerId="owner-1", name="Test", email="test@example.com")
	scheduler = Scheduler(schedulerId="sched-1", owner=owner, currentDate=date.today())
	pet = Pet(
		petId="pet-1",
		name="Milo",
		type="Dog",
		breed="Labrador",
		age=4,
		notes="",
		ownerId="owner-1",
	)
	owner.addPet(pet)

	task = Task(
		taskId="task-daily",
		petId="pet-1",
		description="Daily walk",
		dueDate=date.today(),
		dueTime=time(8, 0),
		frequency="daily",
		recurrence_end_date=date.today() + timedelta(days=5),
	)
	scheduler.addTask(task)

	scheduler.mark_task_complete("task-daily")

	all_tasks = scheduler.retrieveAllTasks()
	completed = next(t for t in all_tasks if t.taskId == "task-daily")
	next_task = next(t for t in all_tasks if t.taskId == f"task-daily--{(date.today() + timedelta(days=1)).isoformat()}")

	assert completed.isCompleted is True
	assert next_task.dueDate == date.today() + timedelta(days=1)
	assert next_task.isCompleted is False
	assert next_task.frequency == "daily"


def test_mark_task_complete_creates_next_weekly_occurrence() -> None:
	owner = Owner(ownerId="owner-1", name="Test", email="test@example.com")
	scheduler = Scheduler(schedulerId="sched-1", owner=owner, currentDate=date.today())
	pet = Pet(
		petId="pet-1",
		name="Milo",
		type="Dog",
		breed="Labrador",
		age=4,
		notes="",
		ownerId="owner-1",
	)
	owner.addPet(pet)

	task = Task(
		taskId="task-weekly",
		petId="pet-1",
		description="Weekly grooming",
		dueDate=date.today(),
		dueTime=time(10, 0),
		frequency="weekly",
		recurrence_end_date=date.today() + timedelta(weeks=3),
	)
	scheduler.addTask(task)

	scheduler.mark_task_complete("task-weekly")

	all_tasks = scheduler.retrieveAllTasks()
	next_task = next(t for t in all_tasks if t.taskId == f"task-weekly--{(date.today() + timedelta(weeks=1)).isoformat()}")

	assert next_task.dueDate == date.today() + timedelta(weeks=1)
	assert next_task.isCompleted is False
	assert next_task.frequency == "weekly"


def test_adding_task_to_pet_increases_task_count() -> None:
	pet = Pet(
		petId="pet-1",
		name="Milo",
		type="Dog",
		breed="Labrador",
		age=4,
		notes="Friendly",
		ownerId="owner-1",
	)
	task = Task(
		taskId="task-1",
		petId="pet-1",
		description="Feed breakfast",
		dueDate=date.today(),
		dueTime=time(9, 0),
		frequency="daily",
	)

	initial_count = len(pet.tasks)
	pet.addTask(task)

	assert len(pet.tasks) == initial_count + 1


def test_tasks_sorted_by_priority() -> None:
	"""Verify getTodaysTasks sorts by priority, then time."""
	owner = Owner(ownerId="owner-1", name="Test", email="test@example.com")
	scheduler = Scheduler(schedulerId="sched-1", owner=owner, currentDate=date.today())
	
	pet = Pet(
		petId="pet-1",
		name="Milo",
		type="Dog",
		breed="Labrador",
		age=4,
		notes="",
		ownerId="owner-1",
	)
	owner.addPet(pet)
	
	# Create two tasks at same time, different priorities
	low_priority = Task(
		taskId="task-1",
		petId="pet-1",
		description="Low priority",
		dueDate=date.today(),
		dueTime=time(8, 0),
		frequency="once",
		priority=1,
	)
	high_priority = Task(
		taskId="task-2",
		petId="pet-1",
		description="High priority",
		dueDate=date.today(),
		dueTime=time(8, 0),
		frequency="once",
		priority=3,
	)
	
	scheduler.addTask(high_priority)
	scheduler.addTask(low_priority)
	
	todays = scheduler.getTodaysTasks()
	assert todays[0].priority == 3  # High priority first
	assert todays[1].priority == 1  # Low priority second


def test_priority_first_beats_earlier_time() -> None:
	"""Verify higher priority task is shown before lower-priority earlier task."""
	owner = Owner(ownerId="owner-1", name="Test", email="test@example.com")
	scheduler = Scheduler(schedulerId="sched-1", owner=owner, currentDate=date.today())
	pet = Pet(petId="pet-1", name="Milo", type="Dog", breed="Lab", age=4, notes="", ownerId="owner-1")
	owner.addPet(pet)

	early_low = Task(
		taskId="t-low",
		petId="pet-1",
		description="Low priority early",
		dueDate=date.today(),
		dueTime=time(8, 0),
		priority=1,
	)
	later_high = Task(
		taskId="t-high",
		petId="pet-1",
		description="High priority later",
		dueDate=date.today(),
		dueTime=time(9, 0),
		priority=3,
	)

	scheduler.addTask(early_low)
	scheduler.addTask(later_high)

	todays = scheduler.getTodaysTasks()
	assert todays[0].taskId == "t-high"
	assert todays[1].taskId == "t-low"


def test_recurring_task_expansion() -> None:
	"""Verify recurring tasks expand across a date range."""
	owner = Owner(ownerId="owner-1", name="Test", email="test@example.com")
	scheduler = Scheduler(schedulerId="sched-1", owner=owner, currentDate=date.today())
	
	pet = Pet(
		petId="pet-1",
		name="Milo",
		type="Dog",
		breed="Labrador",
		age=4,
		notes="",
		ownerId="owner-1",
	)
	owner.addPet(pet)
	
	# Create a daily recurring task
	daily_task = Task(
		taskId="task-daily",
		petId="pet-1",
		description="Daily walk",
		dueDate=date.today(),
		dueTime=time(8, 0),
		frequency="daily",
		recurrence_end_date=date.today() + timedelta(days=6),
	)
	
	scheduler.addTask(daily_task)
	
	# Expand for 7 days
	expanded = scheduler.expandRecurringTasks(date.today(), date.today() + timedelta(days=6))
	
	# Should have 7 occurrences (daily for 7 days)
	daily_occurrences = [t for t in expanded if "task-daily" in t.taskId]
	assert len(daily_occurrences) == 7


def test_filter_tasks_for_pet() -> None:
	"""Verify filtering tasks by pet."""
	owner = Owner(ownerId="owner-1", name="Test", email="test@example.com")
	scheduler = Scheduler(schedulerId="sched-1", owner=owner, currentDate=date.today())
	
	pet1 = Pet(petId="pet-1", name="Milo", type="Dog", breed="Lab", age=4, notes="", ownerId="owner-1")
	pet2 = Pet(petId="pet-2", name="Luna", type="Cat", breed="Siamese", age=2, notes="", ownerId="owner-1")
	owner.addPet(pet1)
	owner.addPet(pet2)
	
	task1 = Task(taskId="t1", petId="pet-1", description="Walk", dueDate=date.today(), dueTime=time(8, 0))
	task2 = Task(taskId="t2", petId="pet-2", description="Feed", dueDate=date.today(), dueTime=time(9, 0))
	
	scheduler.addTask(task1)
	scheduler.addTask(task2)
	
	milo_tasks = scheduler.getTasksForPet("pet-1")
	assert len(milo_tasks) == 1
	assert milo_tasks[0].petId == "pet-1"


def test_filter_tasks_by_time_window() -> None:
	"""Verify filtering tasks by time window."""
	owner = Owner(ownerId="owner-1", name="Test", email="test@example.com")
	scheduler = Scheduler(schedulerId="sched-1", owner=owner, currentDate=date.today())
	
	pet = Pet(petId="pet-1", name="Milo", type="Dog", breed="Lab", age=4, notes="", ownerId="owner-1")
	owner.addPet(pet)
	
	task1 = Task(taskId="t1", petId="pet-1", description="Morning", dueDate=date.today(), dueTime=time(8, 0))
	task2 = Task(taskId="t2", petId="pet-1", description="Afternoon", dueDate=date.today(), dueTime=time(14, 0))
	task3 = Task(taskId="t3", petId="pet-1", description="Evening", dueDate=date.today(), dueTime=time(18, 0))
	
	scheduler.addTask(task1)
	scheduler.addTask(task2)
	scheduler.addTask(task3)
	
	# Get morning tasks (7 AM to 12 PM)
	morning = scheduler.getTasksByTimeWindow(time(7, 0), time(12, 0), date_filter=date.today())
	assert len(morning) == 1
	assert morning[0].description == "Morning"


def test_conflict_detection() -> None:
	"""Verify conflict detection identifies overlapping tasks."""
	owner = Owner(ownerId="owner-1", name="Test", email="test@example.com")
	scheduler = Scheduler(schedulerId="sched-1", owner=owner, currentDate=date.today())
	
	pet = Pet(petId="pet-1", name="Milo", type="Dog", breed="Lab", age=4, notes="", ownerId="owner-1")
	owner.addPet(pet)
	
	# Create two tasks at same time (conflict)
	task1 = Task(
		taskId="t1",
		petId="pet-1",
		description="Walk",
		dueDate=date.today(),
		dueTime=time(8, 0),
		duration_minutes=30,
	)
	task2 = Task(
		taskId="t2",
		petId="pet-1",
		description="Grooming",
		dueDate=date.today(),
		dueTime=time(8, 15),
		duration_minutes=20,
	)
	
	scheduler.addTask(task1)
	scheduler.addTask(task2)
	
	conflicts = scheduler.detectConflicts(date.today())
	
	# Should detect conflict for pet-1
	assert "pet-1" in conflicts
	assert len(conflicts["pet-1"]) > 0


def test_same_time_warning_detection_across_pets() -> None:
	"""Verify lightweight warnings detect same-time tasks for different pets."""
	owner = Owner(ownerId="owner-1", name="Test", email="test@example.com")
	scheduler = Scheduler(schedulerId="sched-1", owner=owner, currentDate=date.today())

	pet1 = Pet(petId="pet-1", name="Milo", type="Dog", breed="Lab", age=4, notes="", ownerId="owner-1")
	pet2 = Pet(petId="pet-2", name="Luna", type="Cat", breed="Siamese", age=2, notes="", ownerId="owner-1")
	owner.addPet(pet1)
	owner.addPet(pet2)

	task1 = Task(taskId="t1", petId="pet-1", description="Walk", dueDate=date.today(), dueTime=time(9, 0))
	task2 = Task(taskId="t2", petId="pet-2", description="Feed", dueDate=date.today(), dueTime=time(9, 0))

	scheduler.addTask(task1)
	scheduler.addTask(task2)

	warnings = scheduler.detectSameTimeConflicts(date.today())
	assert time(9, 0) in warnings
	assert len(warnings[time(9, 0)]) == 2


def test_warning_report_returns_message_instead_of_crashing() -> None:
	"""Verify same-time conflicts return a warning string rather than raising an error."""
	owner = Owner(ownerId="owner-1", name="Test", email="test@example.com")
	scheduler = Scheduler(schedulerId="sched-1", owner=owner, currentDate=date.today())

	pet1 = Pet(petId="pet-1", name="Milo", type="Dog", breed="Lab", age=4, notes="", ownerId="owner-1")
	pet2 = Pet(petId="pet-2", name="Luna", type="Cat", breed="Siamese", age=2, notes="", ownerId="owner-1")
	owner.addPet(pet1)
	owner.addPet(pet2)

	scheduler.addTask(Task(taskId="t1", petId="pet-1", description="Walk", dueDate=date.today(), dueTime=time(9, 0)))
	scheduler.addTask(Task(taskId="t2", petId="pet-2", description="Feed", dueDate=date.today(), dueTime=time(9, 0)))

	report = scheduler.getWarningReport(date.today())
	assert "Warning: multiple tasks are scheduled at 09:00" in report
	assert "Milo: Walk" in report
	assert "Luna: Feed" in report


def test_filter_by_status_and_pet() -> None:
	"""Verify combined filtering by completion status and pet ID."""
	owner = Owner(ownerId="owner-1", name="Test", email="test@example.com")
	scheduler = Scheduler(schedulerId="sched-1", owner=owner, currentDate=date.today())
	
	pet1 = Pet(petId="pet-1", name="Milo", type="Dog", breed="Lab", age=4, notes="", ownerId="owner-1")
	pet2 = Pet(petId="pet-2", name="Luna", type="Cat", breed="Siamese", age=2, notes="", ownerId="owner-1")
	owner.addPet(pet1)
	owner.addPet(pet2)
	
	# Create tasks for both pets
	task1 = Task(taskId="t1", petId="pet-1", description="Walk", dueDate=date.today(), dueTime=time(8, 0))
	task2 = Task(taskId="t2", petId="pet-1", description="Feed", dueDate=date.today(), dueTime=time(9, 0))
	task3 = Task(taskId="t3", petId="pet-2", description="Groom", dueDate=date.today(), dueTime=time(10, 0))
	
	scheduler.addTask(task1)
	scheduler.addTask(task2)
	scheduler.addTask(task3)
	
	# Mark task1 as complete
	task1.mark_complete()
	
	# Test: Filter only Milo's incomplete tasks (should be only task2)
	milo_incomplete = scheduler.filter_by_status_and_pet(petId="pet-1", isCompleted=False)
	assert len(milo_incomplete) == 1
	assert milo_incomplete[0].taskId == "t2"
	
	# Test: Filter only completed tasks (should be task1)
	completed = scheduler.filter_by_status_and_pet(isCompleted=True)
	assert len(completed) == 1
	assert completed[0].taskId == "t1"
	
	# Test: Filter all of Milo's tasks regardless of status (should be task1 and task2)
	all_milo = scheduler.filter_by_status_and_pet(petId="pet-1")
	assert len(all_milo) == 2


def test_sorting_correctness_returns_tasks_in_chronological_order() -> None:
	"""Sorting Correctness: tasks should be returned by date, then time."""
	owner = Owner(ownerId="owner-1", name="Test", email="test@example.com")
	scheduler = Scheduler(schedulerId="sched-1", owner=owner, currentDate=date(2026, 3, 1))
	pet = Pet(
		petId="pet-1",
		name="Milo",
		type="Dog",
		breed="Lab",
		age=4,
		notes="",
		ownerId="owner-1",
	)
	owner.addPet(pet)

	# Intentionally add in non-chronological order.
	scheduler.addTask(Task(taskId="t3", petId="pet-1", description="Late", dueDate=date(2026, 3, 2), dueTime=time(9, 0)))
	scheduler.addTask(Task(taskId="t1", petId="pet-1", description="Earliest", dueDate=date(2026, 3, 1), dueTime=time(8, 0)))
	scheduler.addTask(Task(taskId="t2", petId="pet-1", description="Middle", dueDate=date(2026, 3, 1), dueTime=time(12, 0)))

	ordered_ids = [task.taskId for task in scheduler.retrieveAllTasks()]
	assert ordered_ids == ["t1", "t2", "t3"]


def test_recurrence_logic_daily_completion_creates_following_day_task() -> None:
	"""Recurrence Logic: completing a daily task creates the next day's task."""
	base_date = date(2026, 3, 10)
	owner = Owner(ownerId="owner-1", name="Test", email="test@example.com")
	scheduler = Scheduler(schedulerId="sched-1", owner=owner, currentDate=base_date)
	pet = Pet(
		petId="pet-1",
		name="Milo",
		type="Dog",
		breed="Lab",
		age=4,
		notes="",
		ownerId="owner-1",
	)
	owner.addPet(pet)

	daily = Task(
		taskId="daily-walk",
		petId="pet-1",
		description="Daily walk",
		dueDate=base_date,
		dueTime=time(8, 30),
		frequency="daily",
		recurrence_end_date=base_date + timedelta(days=3),
	)
	scheduler.addTask(daily)

	scheduler.mark_task_complete("daily-walk")

	next_id = f"daily-walk--{(base_date + timedelta(days=1)).isoformat()}"
	all_ids = [task.taskId for task in scheduler.retrieveAllTasks()]

	assert "daily-walk" in all_ids
	assert next_id in all_ids

	next_task = next(task for task in scheduler.retrieveAllTasks() if task.taskId == next_id)
	assert next_task.dueDate == base_date + timedelta(days=1)
	assert next_task.frequency == "daily"
	assert next_task.isCompleted is False


def test_find_next_available_slot_returns_open_time() -> None:
	"""Verify advanced slot search returns the earliest free slot for a pet."""
	base_day = date(2026, 3, 10)
	owner = Owner(ownerId="owner-1", name="Test", email="test@example.com")
	scheduler = Scheduler(schedulerId="sched-1", owner=owner, currentDate=base_day)
	pet = Pet(petId="pet-1", name="Milo", type="Dog", breed="Lab", age=4, notes="", ownerId="owner-1")
	owner.addPet(pet)

	scheduler.addTask(Task(taskId="t1", petId="pet-1", description="Walk", dueDate=base_day, dueTime=time(8, 0), duration_minutes=30))
	scheduler.addTask(Task(taskId="t2", petId="pet-1", description="Feed", dueDate=base_day, dueTime=time(9, 0), duration_minutes=30))

	slot = scheduler.find_next_available_slot(
		petId="pet-1",
		duration_minutes=30,
		start_date=base_day,
		day_start=time(8, 0),
		day_end=time(10, 0),
		step_minutes=15,
		search_days=1,
	)

	assert slot is not None
	slot_date, slot_time = slot
	assert slot_date == base_day
	assert slot_time == time(8, 30)


def test_owner_json_round_trip_preserves_pets_and_tasks() -> None:
	"""Verify owner.save_to_json and load_from_json preserve nested task data."""
	owner = Owner(ownerId="owner-1", name="Jordan", email="jordan@example.com")
	pet = Pet(petId="pet-1", name="Milo", type="Dog", breed="Lab", age=4, notes="Friendly", ownerId="owner-1")
	owner.addPet(pet)
	pet.addTask(
		Task(
			taskId="task-1",
			petId="pet-1",
			description="Morning walk",
			dueDate=date(2026, 3, 10),
			dueTime=time(8, 0),
			frequency="daily",
			priority=3,
			duration_minutes=25,
		)
	)

	with tempfile.TemporaryDirectory() as tmp_dir:
		json_path = Path(tmp_dir) / "data.json"
		owner.save_to_json(str(json_path))
		loaded = Owner.load_from_json(str(json_path))

	assert loaded.ownerId == "owner-1"
	assert loaded.name == "Jordan"
	assert len(loaded.viewPets()) == 1
	loaded_pet = loaded.getPet("pet-1")
	assert loaded_pet.name == "Milo"
	assert len(loaded_pet.tasks) == 1
	assert loaded_pet.tasks[0].description == "Morning walk"
	assert loaded_pet.tasks[0].priority == 3


def test_conflict_detection_flags_duplicate_times_for_same_pet() -> None:
	"""Conflict Detection: duplicate start times should be flagged as conflicts."""
	target_date = date(2026, 3, 15)
	owner = Owner(ownerId="owner-1", name="Test", email="test@example.com")
	scheduler = Scheduler(schedulerId="sched-1", owner=owner, currentDate=target_date)
	pet = Pet(
		petId="pet-1",
		name="Milo",
		type="Dog",
		breed="Lab",
		age=4,
		notes="",
		ownerId="owner-1",
	)
	owner.addPet(pet)

	scheduler.addTask(Task(taskId="a", petId="pet-1", description="Walk", dueDate=target_date, dueTime=time(9, 0), duration_minutes=20))
	scheduler.addTask(Task(taskId="b", petId="pet-1", description="Feed", dueDate=target_date, dueTime=time(9, 0), duration_minutes=15))

	conflicts = scheduler.detectConflicts(target_date)

	assert "pet-1" in conflicts
	slot_time, slot_tasks = conflicts["pet-1"][0]
	assert slot_time == time(9, 0)
	assert {task.taskId for task in slot_tasks} == {"a", "b"}
