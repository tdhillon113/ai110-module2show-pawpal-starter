import pytest
from pawpal_systems import Task, Pet, Owner, Priority, Frequency
from datetime import time


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
