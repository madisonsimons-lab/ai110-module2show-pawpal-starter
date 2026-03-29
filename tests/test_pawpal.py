from datetime import date, time, timedelta

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
	"""Verify getTodaysTasks sorts by time, then priority."""
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
