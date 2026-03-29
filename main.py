from pawpal_systems import *
from datetime import time

# Create pets
pet1 = Pet("Buddy", "Dog", "Golden Retriever", 3)
pet2 = Pet("Whiskers", "Cat", "Siamese", 2)

# Create owner
owner = Owner("John Doe", "john@example.com", 8.0, time(8, 0), time(22, 0))
owner.pets.append(pet1)
owner.pets.append(pet2)

# Create tasks
task1 = Task("1", "Walk Buddy", pet1, "Exercise", 30, Priority.HIGH, Frequency.DAILY)
task2 = Task("2", "Feed Whiskers", pet2, "Feeding", 10, Priority.MEDIUM, Frequency.DAILY)
task3 = Task("3", "Play with Buddy", pet1, "Play", 45, Priority.LOW, Frequency.WEEKLY)

# Add tasks to owner
owner.add_task(task1)
owner.add_task(task2)
owner.add_task(task3)

# Create scheduler
scheduler = Scheduler(owner)

# Generate and print plan
plan = scheduler.generate_plan()
print("Today's Schedule:")
print(plan.to_summary())

# Check budget
print(f"\nBudget check: {scheduler.check_budget()}")

# Explain plan
print(f"\nPlan explanation:\n{scheduler.explain_plan()}")