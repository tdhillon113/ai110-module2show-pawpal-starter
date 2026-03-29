import pytest
from pawpal_systems import Task, Pet, Owner, Scheduler, Priority, Frequency
from datetime import datetime, date, time, timedelta


def test_task_completion():
    """Verify that calling mark_complete() changes the task's status."""
    pet = Pet("Buddy", "Dog", "Golden Retriever", 3)
    task = Task("1", "Walk Buddy", pet, "Exercise", 30, Priority.HIGH, Frequency.DAILY)
    
    # Initially not completed
    assert not task.is_completed
    
    # Mark complete
    task.mark_complete()
    
    # Now completed
    assert task.is_completed


def test_task_addition():
    """Verify that adding a task to an Owner increases the owner's task count."""
    owner = Owner("John Doe", "john@example.com", 8.0, time(8, 0), time(22, 0))
    pet = Pet("Buddy", "Dog", "Golden Retriever", 3)
    task = Task("1", "Walk Buddy", pet, "Exercise", 30, Priority.HIGH, Frequency.DAILY)
    
    initial_count = len(owner.tasks)
    
    owner.add_task(task)
    
    assert len(owner.tasks) == initial_count + 1
    assert task in owner.tasks


def test_sorting_by_time():
    """Verify Scheduler.sort_tasks_by_time returns tasks in chronological order."""
    pet = Pet("Buddy", "Dog", "Golden Retriever", 3)
    owner = Owner("John Doe", "john@example.com", 8.0, time(8, 0), time(22, 0))
    t1 = Task("1", "Task A", pet, "General", 30, Priority.MEDIUM, Frequency.DAILY, preferred_start_hour=12)
    t2 = Task("2", "Task B", pet, "General", 30, Priority.HIGH, Frequency.DAILY, preferred_start_hour=8)
    t3 = Task("3", "Task C", pet, "General", 30, Priority.LOW, Frequency.DAILY, preferred_start_hour=10)
    owner.add_task(t1)
    owner.add_task(t2)
    owner.add_task(t3)
    scheduler = Scheduler(owner)

    sorted_tasks = scheduler.sort_tasks_by_time(owner.tasks)

    assert [t.task_id for t in sorted_tasks] == ["2", "3", "1"]


def test_recurring_task_creation():
    """Confirm that marking a daily task complete adds a new task due the next day."""
    pet = Pet("Buddy", "Dog", "Golden Retriever", 3)
    owner = Owner("John Doe", "john@example.com", 8.0, time(8, 0), time(22, 0))
    task = Task("1", "Daily Walk", pet, "Exercise", 30, Priority.HIGH, Frequency.DAILY, preferred_start_hour=8, due_date=date.today())
    owner.add_task(task)
    scheduler = Scheduler(owner)

    scheduler.mark_task_complete(task)

    assert task.is_completed
    new_tasks = [t for t in owner.tasks if t.task_id != "1"]
    assert len(new_tasks) == 1
    assert new_tasks[0].due_date == date.today() + timedelta(days=1)


def test_conflict_detection():
    """Verify duplicate start times are flagged as conflicts in the schedule."""
    pet = Pet("Buddy", "Dog", "Golden Retriever", 3)
    owner = Owner("John Doe", "john@example.com", 8.0, time(8, 0), time(22, 0))
    t1 = Task("1", "Walk", pet, "Exercise", 30, Priority.HIGH, Frequency.DAILY, preferred_start_hour=8, due_date=date.today())
    t2 = Task("2", "Brush", pet, "Grooming", 15, Priority.MEDIUM, Frequency.DAILY, preferred_start_hour=8, due_date=date.today())
    owner.add_task(t1)
    owner.add_task(t2)
    scheduler = Scheduler(owner)

    plan = scheduler.generate_plan()
    assert any("Potential overload" in c or "Same pet" in c for c in plan.conflicts)

