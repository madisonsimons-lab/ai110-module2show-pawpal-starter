from datetime import date, time

from pawpal_system import Pet, Task


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
