# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

```
the UML diagram has four classes: 
1. Owner class: represents the user and their input data (pets).
2. Pet class: Represents an individual pet with health and basic info
3. Task class: Represents a single daily routine task.
4. Scheduler class: Central manager coordinating all tasks and schedules. 

- Each class has a single responsibilitiy.
- relationships: Owner -> pet -> task (through scheduler)
- supports multiple task types and pets
- Tracking - completion status helps monitor per care adherence
- Scalability - can handle multiple owners/pets. 
```

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.
```
Yes, my design evolved during implementation based on AI feedback. The original skeleton had no domain-specific error types, so the AI recommended adding three custom exception classes — `OwnershipError`, `TaskStateError`, and `ValidationError` — to give callers a way to distinguish between different failure modes (e.g., a pet not belonging to an owner vs. a task being in the wrong state vs. invalid input). Rather than raising a generic `ValueError` everywhere, each method now raises the exception that best describes what went wrong.
```
---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?
```
1. One tradeoff my scheduler makes is that conflict detection is intentionally lightweight: it only flags tasks for the same pet when date and time are an exact match, and it returns a warning message instead of blocking scheduling.

2. That tradeoff is reasonable here because it keeps the system simple, fast, and easy to understand for a class project, while still catching the most obvious scheduling mistakes without adding complex overlap logic.
```
---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

```
I used AI for brainstorming initial design, refactoring code structure, and debugging issues with scheduling logic.

The most helpful prompts were:
- Specific technical questions about error handling and exception design (e.g., "what custom exceptions should I create?")
- Requests for code review and suggestions on improving structure
- Asking for clarification on edge cases and tradeoffs in the scheduler logic
- Requests to explain or refactor existing code to be cleaner and more maintainable
```

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

```
When I asked Copilot to improve the task display layout, it suggested replacing the entire task section with a single st.dataframe() call. At first glance it looked clean, but I realized a static dataframe can't hold interactive elements. There's no way to put a checkbox, edit button, or delete button inside a st.dataframe() row. I verified this by checking the Streamlit docs and testing it quickly in the app, confirming the buttons simply didn't render. I rejected that suggestion and instead guided Copilot toward using st.columns() per task row, which allowed me to place the checkbox and action buttons inline. The AI optimized for visual simplicity, but I had to evaluate whether the output actually supported the interactivity the app needed.

```

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?
```
1. Adding pets and tasks with different inputs, task sorting by time, conflict detection when two tasks share the same time slot, the Build Schedule budget filter (full budget vs. tight budget), and the Mark Complete action updating task status

2. Because these are the core algorithms the app depends on if sorting is broken, the schedule is misleading; if conflict detection fails, a pet owner could miss a double-booking; and if the budget filter doesn't skip tasks correctly, the scheduler loses its main value. Testing confirmed which features worked and exposed real bugs like the time and priority dropdowns not saving, which would have silently corrupted every task a user created.

```
**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

```
I'm fairly confident that the scheduler works correctly for the core requirements. There are some refinements I would make, but for the purposes of this assignment, it accomplishes what was asked. 

If I had more time, I would test edge cases like:
- Scheduling tasks across different time zones
- Handling pets with very long names or special characters
- Testing with a large number of concurrent tasks (performance testing)
- Verifying boundary conditions for budget limits (exact amount vs. over budget)
- Testing task completion and rollover behavior across multiple days
```

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
```
I'm most satisfied with the scheduling logic and task management system. It took considerable time to refine, but the final implementation executes exactly as intended, handling complex scheduling scenarios and constraint resolution efficiently.
```

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
```
The entire UI. I would redesign it with a more user-friendly and intuitive interface that prioritizes clarity and ease of navigation for pet owners managing multiple pets and schedules.
```
**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

```
Working with AI during the design phase gave me more clarity and a better foundation for the project, resulting in a smoother workflow overall. By discussing design decisions and potential issues upfront, I could anticipate problems and structure the code more effectively before implementation, reducing rework and debugging time later.
```