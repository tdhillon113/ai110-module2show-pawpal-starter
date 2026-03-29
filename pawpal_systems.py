from dataclasses import dataclass, field
from typing import List, Optional
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
    preferred_start_hour: int = 8  # Preferred hour to start (0-23)
    last_completed_date: Optional[date] = None
    due_date: Optional[date] = None

    def mark_complete(self):
        """Marks the task as completed."""
        self.is_completed = True
        self.last_completed_date = date.today()

    def is_due(self, current_time: datetime) -> bool:
        """Checks if the task is due based on current time and frequency/due_date."""
        if self.is_completed:
            return False
        today = current_time.date()
        if self.due_date and today >= self.due_date:
            return True
        # Fallback to frequency-based check
        if self.frequency == Frequency.DAILY:
            return self.last_completed_date != today if self.last_completed_date else True
        elif self.frequency == Frequency.WEEKLY:
            if self.last_completed_date is None:
                return True
            days_since = (today - self.last_completed_date).days
            return days_since >= 7
        elif self.frequency == Frequency.AS_NEEDED:
            return True  # Always due if not completed
        return False


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

    def filter_tasks(self, pet: Optional[Pet] = None, completed: Optional[bool] = None, priority: Optional[Priority] = None) -> List[Task]:
        """Filters tasks by pet, completion status, and priority."""
        return [t for t in self.tasks if
                (pet is None or t.pet == pet) and
                (completed is None or t.is_completed == completed) and
                (priority is None or t.priority == priority)]


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
    conflicts: List[str] = field(default_factory=list)

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
        summary += f"Feasible: {self.is_feasible()}\n"
        if self.conflicts:
            summary += "Conflicts:\n" + "\n".join(f"- {c}" for c in self.conflicts) + "\n"
        return summary


class Scheduler:
    def __init__(self, owner: Owner):
        self.owner = owner
        self.available_hours = owner.available_hours
        self.wake_time = owner.wake_time
        self.sleep_time = owner.sleep_time

    def generate_plan(self) -> DailyPlan:
        """Generates a daily plan by scheduling tasks sequentially with conflict detection."""
        plan = DailyPlan(date.today())
        current_time = self.wake_time
        total_duration = 0
        scheduled_intervals = []  # List of (start_time, end_time) for conflict detection

        # Detect potential conflicts before scheduling
        potential_conflicts = self.detect_potential_conflicts()
        plan.conflicts.extend(potential_conflicts)

        # Sort tasks by priority (HIGH first), then by preferred start hour, then duration
        sorted_tasks = sorted(
            [t for t in self.owner.tasks if t.is_due(datetime.combine(date.today(), time(0, 0)))],
            key=lambda t: (t.priority.value, t.preferred_start_hour, t.duration_min)
        )

        for task in sorted_tasks:
            start_time = current_time
            end_datetime = datetime.combine(date.today(), current_time) + timedelta(minutes=task.duration_min)
            end_time = end_datetime.time()

            # Check for time conflicts (overlaps with existing scheduled tasks)
            conflict = any(
                start_time < existing_end and end_time > existing_start
                for existing_start, existing_end in scheduled_intervals
            )

            if not conflict and end_time <= self.sleep_time:
                scheduled = ScheduledTask(task, start_time, f"Scheduled for {task.pet.name}")
                plan.items.append(scheduled)
                scheduled_intervals.append((start_time, end_time))
                total_duration += task.duration_min
                current_time = end_time
            else:
                reason = "Skipped due to time conflict" if conflict else "Skipped due to time constraints"
                scheduled = ScheduledTask(task, start_time, reason, skipped=True)
                plan.items.append(scheduled)

        plan.total_duration = total_duration

        # Additional conflict detection after scheduling
        self.detect_scheduled_conflicts(plan)

        return plan

    def detect_potential_conflicts(self) -> List[str]:
        """Lightweight pre-scheduling conflict detection: Warns about multiple tasks at the same preferred hour."""
        from collections import defaultdict
        hour_tasks = defaultdict(list)
        for task in self.owner.tasks:
            if not task.is_completed and task.is_due(datetime.combine(date.today(), time(0, 0))):
                hour_tasks[task.preferred_start_hour].append(task)
        conflicts = []
        for hour, tasks in hour_tasks.items():
            if len(tasks) > 1:
                task_names = [t.name for t in tasks]
                pet_names = [t.pet.name for t in tasks]
                conflicts.append(f"Potential overload at {hour}:00: {', '.join(task_names)} for {', '.join(set(pet_names))}")
        return conflicts

    def detect_scheduled_conflicts(self, plan: DailyPlan):
        """Detects conflicts in the scheduled plan: same pet at same time or overlaps."""
        for i, item1 in enumerate(plan.items):
            if item1.skipped:
                continue
            for j, item2 in enumerate(plan.items):
                if i >= j or item2.skipped:
                    continue
                # Check if same pet and same start time
                if item1.task.pet == item2.task.pet and item1.start_time == item2.start_time:
                    plan.conflicts.append(f"Same pet ({item1.task.pet.name}) has two tasks at {item1.start_time.strftime('%H:%M')}: '{item1.task.name}' and '{item2.task.name}'")
                # Check for time overlaps
                end1 = (datetime.combine(date.today(), item1.start_time) + timedelta(minutes=item1.task.duration_min)).time()
                if item1.start_time < item2.start_time < end1:
                    plan.conflicts.append(f"Time overlap: '{item1.task.name}' ends at {end1.strftime('%H:%M')} but '{item2.task.name}' starts at {item2.start_time.strftime('%H:%M')}")

    def sort_tasks_by_time(self, tasks: List[Task]) -> List[Task]:
        """Sorts a list of Task objects by their preferred start hour (earliest first)."""
        return sorted(tasks, key=lambda t: t.preferred_start_hour)

    def filter_tasks(self, tasks: List[Task], completed: Optional[bool] = None, pet: Optional[Pet] = None) -> List[Task]:
        """Filters tasks by completion status and/or pet reference.

        Returns a new list of tasks that match all provided criteria.
        """
        return [t for t in tasks if
                (completed is None or t.is_completed == completed) and
                (pet is None or t.pet == pet)]

    def detect_potential_conflicts(self) -> List[str]:
        """Scans owner tasks and reports potential scheduling conflicts before planning.

        Returns list of warning strings for tasks that share the same preferred start hour.
        """
        from collections import defaultdict
        hour_tasks = defaultdict(list)
        for task in self.owner.tasks:
            if not task.is_completed and task.is_due(datetime.combine(date.today(), time(0, 0))):
                hour_tasks[task.preferred_start_hour].append(task)
        conflicts = []
        for hour, tasks in hour_tasks.items():
            if len(tasks) > 1:
                task_names = [t.name for t in tasks]
                pet_names = [t.pet.name for t in tasks]
                conflicts.append(f"Potential overload at {hour}:00: {', '.join(task_names)} for {', '.join(set(pet_names))}")
        return conflicts

    def detect_scheduled_conflicts(self, plan: DailyPlan):
        """Checks a generated DailyPlan and appends conflict messages for schedule overlaps.

        This method is non-fatal; it reports warning messages and keeps schedule results available.
        """
        for i, item1 in enumerate(plan.items):
            if item1.skipped:
                continue
            for j, item2 in enumerate(plan.items):
                if i >= j or item2.skipped:
                    continue
                if item1.task.pet == item2.task.pet and item1.start_time == item2.start_time:
                    plan.conflicts.append(f"Same pet ({item1.task.pet.name}) has two tasks at {item1.start_time.strftime('%H:%M')}: '{item1.task.name}' and '{item2.task.name}'")
                end1 = (datetime.combine(date.today(), item1.start_time) + timedelta(minutes=item1.task.duration_min)).time()
                if item1.start_time < item2.start_time < end1:
                    plan.conflicts.append(f"Time overlap: '{item1.task.name}' ends at {end1.strftime('%H:%M')} but '{item2.task.name}' starts at {item2.start_time.strftime('%H:%M')}")

    def mark_task_complete(self, task: Task):
        """Marks a task complete and creates a new instance for recurring tasks."""
        task.mark_complete()
        if task.frequency in (Frequency.DAILY, Frequency.WEEKLY):
            days = 1 if task.frequency == Frequency.DAILY else 7
            new_due_date = task.last_completed_date + timedelta(days=days)
            new_task = Task(
                task_id=f"{task.task_id}_recurring_{new_due_date.isoformat()}",
                name=task.name,
                pet=task.pet,
                category=task.category,
                duration_min=task.duration_min,
                priority=task.priority,
                frequency=task.frequency,
                preferred_start_hour=task.preferred_start_hour,
                due_date=new_due_date
            )
            self.owner.add_task(new_task)

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