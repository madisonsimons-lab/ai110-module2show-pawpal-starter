from datetime import date, time

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

	tasks = [
		Task(
			taskId="task-001",
			petId="pet-001",
			description="Morning walk",
			dueDate=date.today(),
			dueTime=time(8, 0),
			frequency="daily",
		),
		Task(
			taskId="task-002",
			petId="pet-002",
			description="Feed breakfast",
			dueDate=date.today(),
			dueTime=time(9, 0),
			frequency="daily",
		),
		Task(
			taskId="task-003",
			petId="pet-001",
			description="Evening play session",
			dueDate=date.today(),
			dueTime=time(18, 30),
			frequency="daily",
		),
	]

	for task in tasks:
		scheduler.addTask(task)

	return scheduler


def print_todays_schedule(scheduler: Scheduler) -> None:
	todays_tasks = scheduler.getTodaysTasks()
	print("Today's Schedule")
	print("=" * 40)
	print(f"Owner: {scheduler.owner.name} ({scheduler.owner.email})")
	print(f"Date: {scheduler.currentDate.isoformat()}")
	print("-" * 40)

	if not todays_tasks:
		print("No tasks scheduled for today.")
		return

	for task in todays_tasks:
		pet = scheduler.owner.getPet(task.petId)
		print(f"{task.dueTime.strftime('%I:%M %p')} - {pet.name}: {task.description}")


if __name__ == "__main__":
	demo_scheduler = seed_demo_data()
	print_todays_schedule(demo_scheduler)
