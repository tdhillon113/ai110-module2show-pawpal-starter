# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?
    Owner is the top-level entity whose primary structural role is holding one or more 

    Pet objects: it acts as the entry point the Scheduler queries from. Pet serves a dual role as both a data container (name, type, breed, age) and a task manager, owning the task list directly and exposing add_task, remove_task, and get_tasks so that all task operations flow through the pet. 

    Task is the atomic unit of work, storing what needs to be done (description), when (due_by), how often (frequency), and whether it's finished (is_completed), while also owning its own state transitions through mark_complete, mark_incomplete, and is_due. 

    Scheduler is a stateless service class that depends on all three but owns none of them — it receives an Owner, walks down to their pets and tasks, and moves the data through a four-step pipeline: retrieve, organize, generate, and update status. The defining design choice was placing task ownership on Pet rather than Owner, which feels natural for a single-pet household but introduces scheduling complexity once multiple pets are involved.

**b. Design changes**

- Did your design change during implementation?
  Yes, significantly. The initial design had task ownership on Pet, but during Phase 2 I shifted to Owner owning all tasks directly for multi-pet scheduling flexibility.
- If yes, describe at least one change and why you made it.
  The Scheduler class evolved from a monolithic "retrieve-organize-generate-update" pipeline to focused methods: `generate_plan()`, `sort_tasks_by_time()`, `filter_tasks()`, and `mark_task_complete()`. This decoupling was necessary to support sorting/filtering independently and made testing each behavior easier. Additionally, I added `DailyPlan` as a return object and `detect_potential_conflicts()` / `detect_scheduled_conflicts()` as separate methods to keep conflict logic testable and non-fatal.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
  The scheduler considers owner availability (`wake_time`, `sleep_time`), task priority (HIGH/MEDIUM/LOW), preferred start hour, task duration, frequency (daily/weekly/as_needed), and due date. Pet reference ensures multi-pet conflict detection.
- How did you decide which constraints mattered most?
  I prioritized based on real pet owner workflow: time windows first (you can't schedule outside sleep time), then priority (urgent tasks go first), then preferred start hour (convenience), and finally recurrence (habituals like feeding).

**b. Tradeoffs**

- The scheduler currently checks for exact start-time overlaps and preferred-hour collisions but does not deeply model partial overlaps in a real-time timeline (e.g., task A 08:00-08:30 and task B 08:15-08:45 are still considered separately unless we manually detect them in conflict logic). This keeps the implementation lightweight and easy to understand, but it means some conflict cases may not be resolved optimally.
- This tradeoff is reasonable for a prototype where simplicity and fast iteration are more valuable than perfect scheduling. In a production version, we would upgrade to interval trees or a dedicated calendar library for robust conflict handling.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
  I used Copilot extensively for UML-to-code translation, method stub generation, docstring writing, and test drafting. Smart actions like "Generate tests" and "Generate documentation" were extremely efficient for bulk task creation.
- What kinds of prompts or questions were most helpful?
  Prompts with `#codebase` context were most effective (e.g., "Based on my classes, what are the edge cases to test?"). Specific, bounded questions like "How do I sort with a lambda key?" returned crisp answers faster than vague brainstorming.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
  Early on, Copilot suggested a complex recursive scheduling algorithm with dynamic programming to optimize task order. I rejected it because the added complexity would have made testing and reasoning about edge cases harder, and the project brief didn't require such optimization.
- How did you evaluate or verify what the AI suggested?
  I ran `python -m pytest` on each change and manually tested via `main.py` demo. I also traced code logic against my UML to ensure design consistency. Acceptance only happened if tests passed *and* the code fit my simplicity-first philosophy.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
  I'm most satisfied with the conflict detection system and the recurrence logic. Detecting conflicts without crashing and automatically regenerating recurring tasks (using `timedelta`) feels like the right balance of smart scheduling without overcomplicating the system.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
  I would add persistent storage (e.g., SQLite backend) so tasks survive session resets. I'd also implement stronger overlap detection using interval arithmetic, and add a REST API layer to decouple the scheduler from Streamlit so it can be reused in other UIs.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
  The biggest lesson is that AI accelerates iteration dramatically, but only if you own the architecture first. I began with a clear UML, then let Copilot fill in implementation details. This kept the system coherent and testable. Without that guardrail, AI suggestions alone would have drifted toward complexity and inconsistency.
