from pawpal_systems import *
from datetime import time, date

# Create pets
pet1 = Pet("Buddy", "Dog", "Golden Retriever", 3)
pet2 = Pet("Whiskers", "Cat", "Siamese", 2)

# Create owner
owner = Owner("John Doe", "john@example.com", 8.0, time(8, 0), time(22, 0))
owner.pets.append(pet1)
owner.pets.append(pet2)

# Create tasks out of order (different priorities and preferred times)
task1 = Task("1", "Walk Buddy", pet1, "Exercise", 30, Priority.HIGH, Frequency.DAILY, preferred_start_hour=8, due_date=date.today())
task2 = Task("2", "Feed Whiskers", pet2, "Feeding", 10, Priority.MEDIUM, Frequency.DAILY, preferred_start_hour=12, due_date=date.today())
task3 = Task("3", "Play with Buddy", pet1, "Play", 45, Priority.LOW, Frequency.WEEKLY, preferred_start_hour=10, due_date=date.today())
task4 = Task("4", "Brush Buddy", pet1, "Grooming", 15, Priority.MEDIUM, Frequency.DAILY, preferred_start_hour=8, due_date=date.today())  # Same time as task1

# Add tasks to owner (out of order)
owner.add_task(task3)  # Low priority, 10am
owner.add_task(task1)  # High priority, 8am
owner.add_task(task2)  # Medium priority, 12pm
owner.add_task(task4)  # Medium priority, 8am (conflicts with task1)

# Create scheduler
scheduler = Scheduler(owner)

print("Initial tasks:")
for task in owner.tasks:
    print(f"- {task.name} (Due: {task.due_date}, Completed: {task.is_completed})")

# Mark a daily task complete
print("\nMarking 'Walk Buddy' complete...")
scheduler.mark_task_complete(task1)

print("Tasks after marking complete:")
for task in owner.tasks:
    print(f"- {task.name} (Due: {task.due_date}, Completed: {task.is_completed})")

# Demonstrate sorting by time
sorted_tasks = scheduler.sort_tasks_by_time(owner.tasks)
print("\nTasks sorted by preferred start time:")
for task in sorted_tasks:
    print(f"- {task.name} at {task.preferred_start_hour}:00")

# Demonstrate filtering
incomplete_tasks = scheduler.filter_tasks(owner.tasks, completed=False)
print(f"\nIncomplete tasks ({len(incomplete_tasks)}):")
for task in incomplete_tasks:
    print(f"- {task.name}")

buddy_tasks = scheduler.filter_tasks(owner.tasks, pet=pet1)
print(f"\nTasks for Buddy ({len(buddy_tasks)}):")
for task in buddy_tasks:
    print(f"- {task.name}")

# Generate and print plan
plan = scheduler.generate_plan()
print("\nToday's Schedule:")
print(plan.to_summary())

# Check budget
print(f"\nBudget check: {scheduler.check_budget()}")

# Explain plan
print(f"\nPlan explanation:\n{scheduler.explain_plan()}")