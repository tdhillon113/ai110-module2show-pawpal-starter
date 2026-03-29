# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

Owner is the top-level entity whose primary structural role is holding one or more Pet objects — it acts as the entry point the Scheduler queries from. Pet serves a dual role as both a data container (name, type, breed, age) and a task manager, owning the task list directly and exposing add_task, remove_task, and get_tasks so that all task operations flow through the pet. Task is the atomic unit of work, storing what needs to be done (description), when (due_by), how often (frequency), and whether it's finished (is_completed), while also owning its own state transitions through mark_complete, mark_incomplete, and is_due. Finally, Scheduler is a stateless service class that depends on all three but owns none of them — it receives an Owner, walks down to their pets and tasks, and moves the data through a four-step pipeline: retrieve, organize, generate, and update status. The defining design choice was placing task ownership on Pet rather than Owner, which feels natural for a single-pet household but introduces scheduling complexity once multiple pets are involved.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.
The Scheduler class is responsible for too many things: retrieving tasks, organizing them, generating daily plans, and updating status. This violates the Single Responsibility Principle and creates a single point of failure/bottleneck.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- The scheduler currently checks for exact start-time overlaps and preferred-hour collisions but does not deeply model partial overlaps in a real-time timeline (e.g., task A 08:00-08:30 and task B 08:15-08:45 are still considered separately unless we manually detect them in conflict logic). This keeps the implementation lightweight and easy to understand, but it means some conflict cases may not be resolved optimally.
- This tradeoff is reasonable for a prototype where simplicity and fast iteration are more valuable than perfect scheduling. In a production version, we would upgrade to interval trees or a dedicated calendar library for robust conflict handling.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

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

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
