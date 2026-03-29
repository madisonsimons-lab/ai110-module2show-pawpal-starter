from datetime import date, time, timedelta

from pawpal_system import Owner, Pet, Scheduler, Task


def seed_demo_data() -> Scheduler:
	owner = Owner(ownerId="owner-001", name="Madison", email="madison@example.com")

	pet1 = Pet(
		petId="pet-001",
		name="Milo",
		type="Dog",
		breed="Labrador",
		age=4,
		notes="Needs a long walk in the evening.",
		ownerId=owner.ownerId,
	)
	pet2 = Pet(
		petId="pet-002",
		name="Luna",
		type="Cat",
		breed="Siamese",
		age=2,
		notes="Prefers wet food in the morning.",
		ownerId=owner.ownerId,
	)

	owner.addPet(pet1)
	owner.addPet(pet2)

	scheduler = Scheduler(schedulerId="sched-001", owner=owner, currentDate=date.today())

	# Create recurring and one-time tasks with priorities
	tasks = [
		Task(
			taskId="task-001",
			petId="pet-001",
			description="Morning walk",
			dueDate=date.today(),
			dueTime=time(8, 0),
			frequency="daily",
			priority=3,
			duration_minutes=30,
			recurrence_end_date=date.today() + timedelta(days=7),
		),
		Task(
			taskId="task-002",
			petId="pet-002",
			description="Feed breakfast",
			dueDate=date.today(),
			dueTime=time(9, 0),
			frequency="daily",
			priority=2,
			duration_minutes=15,
			recurrence_end_date=date.today() + timedelta(days=7),
		),
		Task(
			taskId="task-003",
			petId="pet-001",
			description="Evening play session",
			dueDate=date.today(),
			dueTime=time(18, 30),
			frequency="daily",
			priority=2,
			duration_minutes=45,
			recurrence_end_date=date.today() + timedelta(days=7),
		),
		Task(
			taskId="task-004",
			petId="pet-002",
			description="Vet appointment",
			dueDate=date.today() + timedelta(days=3),
			dueTime=time(10, 0),
			frequency="once",
			priority=3,
			duration_minutes=60,
		),
	]

	for task in tasks:
		scheduler.addTask(task)

	return scheduler


def print_todays_schedule(scheduler: Scheduler) -> None:
	todays_tasks = scheduler.getTodaysTasks()
	print("Today's Schedule (sorted by time, then priority)")
	print("=" * 60)
	print(f"Owner: {scheduler.owner.name} ({scheduler.owner.email})")
	print(f"Date: {scheduler.currentDate.isoformat()}")
	print("-" * 60)

	if not todays_tasks:
		print("No tasks scheduled for today.")
		return

	for task in todays_tasks:
		pet = scheduler.owner.getPet(task.petId)
		priority_label = {1: "Low", 2: "Medium", 3: "High"}[task.priority]
		duration = f"({task.duration_minutes} min)" if task.duration_minutes else ""
		print(f"{task.dueTime.strftime('%I:%M %p')} - {pet.name}: {task.description} [{priority_label}] {duration}")


def print_recurring_week_schedule(scheduler: Scheduler) -> None:
	"""Display expanded recurring tasks for the next 7 days."""
	print("\n\n7-Day Recurring Schedule Expansion")
	print("=" * 60)
	
	start = scheduler.currentDate
	end = start + timedelta(days=6)
	
	expanded = scheduler.expandRecurringTasks(start, end)
	
	if not expanded:
		print("No tasks found for this period.")
		return
	
	# Organize by date
	by_date = {}
	for task in expanded:
		by_date.setdefault(task.dueDate, []).append(task)
	
	for day in sorted(by_date.keys()):
		print(f"\n{day.strftime('%A, %B %d')}:")
		day_tasks = sorted(by_date[day], key=lambda t: t.dueTime)
		for task in day_tasks:
			pet = scheduler.owner.getPet(task.petId)
			print(f"  {task.dueTime.strftime('%H:%M')} - {pet.name}: {task.description}")


def print_conflict_detection(scheduler: Scheduler) -> None:
	"""Display any scheduling conflicts for today."""
	print("\n\nConflict Detection Report")
	print("=" * 60)
	report = scheduler.getConflictReport(scheduler.currentDate)
	print(report)


def demo_filtering(scheduler: Scheduler) -> None:
	"""Demonstrate filtering capabilities."""
	print("\n\nFiltering Capabilities Demo")
	print("=" * 60)
	
	# Filter by pet
	print(f"\nAll tasks for Milo (pet-001):")
	milo_tasks = scheduler.getTasksForPet("pet-001")
	for task in milo_tasks:
		print(f"  {task.dueTime.strftime('%H:%M')} - {task.description}")
	
	# Filter by status
	completed = scheduler.getTasksByStatus(isCompleted=True)
	incomplete = scheduler.getTasksByStatus(isCompleted=False)
	print(f"\nTotal incomplete tasks: {len(incomplete)}")
	print(f"Total completed tasks: {len(completed)}")
	
	# Filter by time window
	morning_tasks = scheduler.getTasksByTimeWindow(time(7, 0), time(12, 0))
	print(f"\nMorning tasks (7 AM - 12 PM): {len(morning_tasks)} tasks")
	for task in morning_tasks:
		pet = scheduler.owner.getPet(task.petId)
		print(f"  {task.dueTime.strftime('%H:%M')} - {pet.name}: {task.description}")


if __name__ == "__main__":
	demo_scheduler = seed_demo_data()
	print_todays_schedule(demo_scheduler)
	print_recurring_week_schedule(demo_scheduler)
	print_conflict_detection(demo_scheduler)
	demo_filtering(demo_scheduler)
