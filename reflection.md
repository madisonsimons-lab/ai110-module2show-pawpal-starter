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
- If yes, describe at least one change and why you made it.

Yes, my design changed during implementation in a few important ways.

One major change was moving toward a single source of truth for tasks. In my original skeleton, tasks could be tracked in more than one place, which risks data getting out of sync. I updated the design so the Scheduler owns task storage and query behavior. This made task management more consistent and reduced duplicate state.

I also added stronger relationship validation between objects. For example, when an owner adds a pet, the pet's ownerId must match the owner's id, and when assigning tasks, the task petId must match the selected pet. I made this change to protect data integrity and catch mistakes early.

Finally, I added indexing inside Scheduler (by task id, date, and pet id) to improve lookup efficiency. This was a design improvement for scalability so common operations (find, group, remove) do not rely only on full list scans.

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
