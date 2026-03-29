from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, time


@dataclass
class Task:
	taskId: str
	petId: str
	title: str
	description: str
	date: date
	time: time
	status: str

	def createTask(self) -> None:
		pass

	def editTask(
		self,
		title: str,
		description: str,
		task_date: date,
		task_time: time,
		status: str,
	) -> None:
		pass

	def markComplete(self) -> None:
		pass

	def deleteTask(self) -> None:
		pass

	def displayTask(self) -> str:
		pass


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
		pass

	def displayPetDetails(self) -> str:
		pass

	def addTask(self, task: Task) -> None:
		pass

	def viewTasks(self) -> list[Task]:
		pass


class Owner:
	def __init__(self, ownerId: str, name: str, email: str) -> None:
		self.ownerId = ownerId
		self.name = name
		self.email = email
		self.listOfPets: list[Pet] = []

	def addPet(self, pet: Pet) -> None:
		pass

	def removePet(self, petId: str) -> None:
		pass

	def viewPets(self) -> list[Pet]:
		pass

	def assignTaskToPet(self, petId: str, task: Task) -> None:
		pass


class Scheduler:
	def __init__(self, schedulerId: str, currentDate: date) -> None:
		self.schedulerId = schedulerId
		self.listOfTasks: list[Task] = []
		self.currentDate = currentDate

	def addTask(self, task: Task) -> None:
		pass

	def removeTask(self, taskId: str) -> None:
		pass

	def getTodaysTasks(self) -> list[Task]:
		pass

	def getUpcomingTasks(self) -> list[Task]:
		pass

	def organizeTasksByDate(self) -> dict[date, list[Task]]:
		pass
