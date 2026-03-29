# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
My initial UML design focused on four main classes: Owner, Pet, Task, and Scheduler. I chose these classes because they matched the main actions the system needed to support, such as adding pets, creating tasks, and viewing scheduled responsibilities.

- What classes did you include, and what responsibilities did you assign to each?
The Owner class represents the person using the system. Its main responsibility is managing pets and connecting the rest of the system together. The Owner can add or remove pets, view pet information, and assign tasks related to each pet.

The Pet class is responsible for storing information about each pet, such as its name, type, breed, age, and notes. This class helps organize pet-specific details and keeps tasks connected to the correct animal.

The Task class handles individual responsibilities for a pet, such as feeding, walking, grooming, or appointments. Its responsibility is to store task details like the title, description, date, time, and completion status. It also allows tasks to be created, updated, marked complete, or deleted.

The Scheduler class is responsible for organizing tasks by date and time. Instead of owning the pets or tasks directly, it helps manage when tasks should happen. Its purpose is to collect tasks, show today’s tasks, show upcoming tasks, and keep everything arranged in a way that is easy for the owner to follow.
**b. Design changes**

- Did your design change during implementation?
Yes
- If yes, describe at least one change and why you made it.
Yes, my design changed during implementation in a few important ways.

One major change was moving toward clearer ownership boundaries. In my original sketch, Scheduler looked like it directly owned task storage. In my final implementation, tasks live inside each Pet, Owner aggregates tasks across pets, and Scheduler orchestrates behavior (sorting, filtering, conflict checks, recurrence actions) through Owner and Pet. This reduced relationship drift and made responsibilities cleaner.

I also added stronger relationship validation between objects. For example, when an owner adds a pet, the pet's ownerId must match the owner's id, and when assigning tasks, the task petId must match the selected pet. I made this change to protect data integrity and catch mistakes early.

Finally, I added an internal pet lookup map inside Owner (_petsById) to speed up pet retrieval and simplify assignment logic. That gave me a practical performance improvement while keeping the overall architecture easy to reason about.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
My scheduler considers due date, due time, completion state, recurrence frequency, recurrence end date, priority, and duration. It also supports pet-specific filtering and time-window filtering so a user can focus on a practical slice of the day.

- How did you decide which constraints mattered most?
I prioritized constraints that directly affect daily execution for a pet owner: chronological order first, then urgency at equal times (priority), then conflict awareness. I treated preferences as a future extension because they are useful, but time and conflict handling are core to producing a reliable day plan.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
One tradeoff my scheduler makes is using a lightweight warning system for exact same-time conflicts instead of trying to fully resolve every overlapping schedule automatically. If two tasks are both scheduled at 9:00 AM, the scheduler returns a warning message instead of crashing or attempting to reschedule one of them on its own.

- Why is that tradeoff reasonable for this scenario?
This tradeoff is reasonable for this project because it keeps the scheduling logic simple, readable, and easy to test. It also gives the pet owner valuable feedback without adding too much complexity too early. A more advanced system could compare full task durations, travel time, or user preferences, but for this version, warning the user about possible conflicts is enough to support good decisions without overengineering the solution.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
I used VS Code Copilot for class design refinement, test drafting, and implementation reviews. It was most useful for quickly generating structured unit tests, suggesting method-level refactors, and helping me wire UI behavior in app.py to backend scheduler methods.

- What kinds of prompts or questions were most helpful?
The most helpful prompts were specific and constraint-based, such as "add tests for sorting, recurrence, and conflict detection" or "update Streamlit display to use Scheduler methods and warning components." Prompts that named exact behaviors and acceptance criteria produced the best output.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
One suggestion I rejected was an architecture direction that implied Scheduler should fully own task storage and indexing. I modified that idea to keep task lists on Pet and use Owner for aggregation. That kept object responsibilities aligned with the domain and avoided duplicating task state across classes.

- How did you evaluate or verify what the AI suggested?
I verified suggestions against three checks: whether the design preserved clear class responsibilities, whether behavior matched my tests, and whether the UI could call methods without awkward workarounds. I treated passing tests as necessary but not sufficient; I also checked if the model remained understandable and maintainable.

**c. AI strategy reflection**

- Which Copilot features were most effective for building your scheduler?
Inline code completion and chat-driven test drafting were most effective. Inline completion helped with method scaffolds and repetitive model wiring, while chat was best for generating targeted tests and reviewing feature gaps.

- Give one example of an AI suggestion you rejected or modified to keep your system design clean.
I modified a suggestion to centralize all task storage in Scheduler. Instead, I preserved Pet as the owner of tasks and used Scheduler as an orchestration/service layer. This avoided split ownership and kept object interactions cleaner.

- How did using separate chat sessions for different phases help you stay organized?
Separate sessions helped me focus by phase: one for model and UML, one for tests, one for Streamlit UI integration, and one for documentation/reflection. That reduced context switching, made prompts more precise, and made it easier to verify each milestone before moving on.

- Summarize what you learned about being the "lead architect" when collaborating with powerful AI tools.
I learned that AI is strongest as an accelerator, not an authority. As lead architect, I still needed to set boundaries, define acceptance criteria, and reject suggestions that conflicted with system clarity. The best results came from giving AI specific goals, then validating every change against design intent and tests.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
I tested task completion state changes, daily and weekly recurrence creation, chronological sorting, filtering by pet/status/time window, overlap conflict detection, same-time warning detection, and combined filter behavior.

- Why were these tests important?
These tests cover the highest-risk scheduling behaviors: ordering correctness, recurrence side effects, and conflict visibility. They also verify the methods the Streamlit UI depends on, which reduced the chance of backend/UI mismatch.

**b. Confidence**

- How confident are you that your scheduler works correctly?
I am 4/5 confident based on passing automated tests for core behaviors and successful integration with the UI.

- What edge cases would you test next if you had more time?
Next, I would test month-end recurrence boundaries, very large task volumes, duplicate IDs across longer sessions, timezone or DST boundary behavior, and conflict resolution suggestions (not just warnings).

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
I am most satisfied with the consistency between backend logic, tests, UI behavior, and UML updates. The system now has a clear flow from model design to tested features to user-facing schedule output.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
I would add preference-aware optimization (owner availability, pet-specific constraints), richer conflict resolution recommendations, and persistence storage so tasks survive app restarts.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
Clear architecture decisions matter more than fast code generation. AI can speed implementation, but disciplined boundaries, targeted tests, and deliberate verification are what make the system reliable.

---

## 6. Prompt Comparison

For a complex algorithmic task, I compared approaches for weekly-task rescheduling and next-slot search logic.

- Prompt used: "Design modular Python logic for recurring weekly rescheduling and finding the next conflict-free slot for a pet scheduler."
- Comparison focus: readability, modularity, and ease of testing.

In this environment, I implemented and validated the final solution with GPT-5.3-Codex. I then compared two generated solution styles (a compact inline version vs a helper-function modular version). The modular style was more Pythonic for this project because it separated recurrence-date calculation, overlap checks, and persistence concerns into focused methods.

Why the modular approach won:

- Easier to unit test method-by-method.
- Safer to extend (for example, adding monthly edge-case handling or richer constraints later).
- Cleaner integration with Streamlit and persistence without duplicating logic.

The biggest lesson from the comparison was that "shorter" code is not always better scheduling code. For stateful systems, explicit helper methods improved both reliability and maintainability.
