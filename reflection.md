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
