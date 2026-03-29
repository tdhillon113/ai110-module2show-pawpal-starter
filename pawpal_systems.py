from dataclasses import dataclass, field
from typing import List
from datetime import datetime


@dataclass
class Task:
    description: str
    due_by: datetime
    frequency: str
    is_completed: bool

    def mark_complete(self):
        pass

    def mark_incomplete(self):
        pass

    def is_due(self, current_time: datetime) -> bool:
        pass


@dataclass
class Pet:
    name: str
    type: str
    breed: str
    age: int
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task):
        pass

    def remove_task(self, task: Task):
        pass

    def get_tasks(self) -> List[Task]:
        pass


@dataclass
class Owner:
    name: str
    pets: List[Pet] = field(default_factory=list)


class Scheduler:
    def retrieve_tasks(self, owner: Owner) -> List[Task]:
        pass

    def organize_tasks(self, tasks: List[Task]) -> List[Task]:
        pass

    def generate_daily_plan(self, owner: Owner) -> List[Task]:
        pass

    def update_task_status(self, task: Task, status: bool):
        pass