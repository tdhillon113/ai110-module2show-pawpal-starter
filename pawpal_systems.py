from dataclasses import dataclass, field
from typing import List
from datetime import datetime, date, time, timedelta
from enum import Enum


class Priority(Enum):
    HIGH = 1
    MEDIUM = 2
    LOW = 3


class Frequency(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    AS_NEEDED = "as_needed"


@dataclass
class Pet:
    name: str
    species: str
    breed: str
    age: int

    def summary(self) -> str:
        """Returns a summary of the pet."""
        return f"{self.name} is a {self.age}-year-old {self.breed} {self.species}."


@dataclass
class Task:
    task_id: str
    name: str
    pet: Pet
    category: str
    duration_min: int
    priority: Priority
    frequency: Frequency
    is_completed: bool = False

    def mark_complete(self):
        """Marks the task as completed."""
        self.is_completed = True

    def is_due(self, current_time: datetime) -> bool:
        """Checks if the task is due based on current time."""
        # Simple implementation: assume due if not completed
        # For recurring tasks, could check based on frequency and last completion
        return not self.is_completed


@dataclass
class Owner:
    name: str
    email: str
    available_hours: float
    wake_time: time
    sleep_time: time
    pets: List[Pet] = field(default_factory=list)
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task):
        """Adds a task to the owner's task list."""
        self.tasks.append(task)

    def remove_task(self, task: Task):
        """Removes a task from the owner's task list."""
        self.tasks.remove(task)


@dataclass
class ScheduledTask:
    task: Task
    start_time: time
    reason: str
    skipped: bool = False


@dataclass
class DailyPlan:
    date: date
    items: List[ScheduledTask] = field(default_factory=list)
    total_duration: int = 0

    def is_feasible(self) -> bool:
        """Checks if the daily plan is feasible (no tasks skipped)."""
        # Check if total duration fits within available hours (assuming 24h day, but could be more precise)
        # For simplicity, assume feasible if no items are skipped (logic in Scheduler)
        return not any(item.skipped for item in self.items)

    def to_summary(self) -> str:
        """Returns a formatted summary of the daily plan."""
        summary = f"Daily Plan for {self.date.strftime('%Y-%m-%d')}:\n"
        for item in self.items:
            status = " (Skipped)" if item.skipped else ""
            summary += f"- {item.start_time.strftime('%H:%M')}: {item.task.name} for {item.task.pet.name} ({item.reason}){status}\n"
        summary += f"Total duration: {self.total_duration} minutes\n"
        summary += f"Feasible: {self.is_feasible()}"
        return summary


class Scheduler:
    def __init__(self, owner: Owner):
        self.owner = owner
        self.available_hours = owner.available_hours
        self.wake_time = owner.wake_time
        self.sleep_time = owner.sleep_time

    def generate_plan(self) -> DailyPlan:
        """Generates a daily plan by scheduling tasks sequentially."""
        plan = DailyPlan(date.today())
        current_time = self.wake_time
        total_duration = 0

        # Sort tasks by priority (HIGH first) and then by duration
        sorted_tasks = sorted(
            [t for t in self.owner.tasks if not t.is_completed],
            key=lambda t: (t.priority.value, t.duration_min)
        )

        for task in sorted_tasks:
            start_time = current_time
            end_datetime = datetime.combine(date.today(), current_time) + timedelta(minutes=task.duration_min)
            end_time = end_datetime.time()

            if end_time <= self.sleep_time:
                scheduled = ScheduledTask(task, start_time, f"Scheduled for {task.pet.name}")
                plan.items.append(scheduled)
                total_duration += task.duration_min
                current_time = end_time
            else:
                scheduled = ScheduledTask(task, start_time, "Skipped due to time constraints", skipped=True)
                plan.items.append(scheduled)

        plan.total_duration = total_duration
        return plan

    def check_budget(self) -> bool:
        """Checks if the total task duration fits within available hours."""
        total_duration = sum(task.duration_min for task in self.owner.tasks if not task.is_completed)
        return total_duration <= self.available_hours * 60

    def explain_plan(self) -> str:
        """Returns a summary explanation of the generated plan."""
        plan = self.generate_plan()
        return plan.to_summary()

    def organize_tasks(self, tasks: List[Task]) -> List[Task]:
        """Organizes tasks by priority and duration."""
        pass

    def generate_daily_plan(self, owner: Owner) -> List[Task]:
        """Generates a daily plan for the owner."""
        pass

    def update_task_status(self, task: Task, status: bool):
        """Updates the completion status of a task."""
        pass