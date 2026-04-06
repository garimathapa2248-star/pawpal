# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
--> A brief description of the initial UML design and the relationship between the different classes established are: 

The design consists of three primary classes that store the system's state:

PetProfile: Stores the pet’s "ideal" care standards, including baseline_tasks (essentials), optional_tasks, and a wellness_debt dictionary to track missed activities.

CareTask: Defines a single unit of work (e.g., a walk or feeding), holding metadata such as duration_minutes, effort_level, priority, and frequency.

OwnerBandwidth: Represents the user's physical constraints, specifically tracking remaining_minutes and energy_level to prevent burnout.

2. The Controller
ReSyncCoordinator: This is the top-level "Brain" of the system. It manages the entire scheduling flow. It holds two critical lists: candidate_tasks (the "pool" of possible activities) and scheduled_tasks (the final plan).

Action: It uses methods like generateDailyPlan() and resolveConflicts() to pull tasks from the pet, filter them through the owner's limits, and move the survivors into the final schedule.

3. Key Class Relationships 
The Hub (ReSyncCoordinator ➔ Owner): Unlike a flat structure, the Coordinator owns an Owner object. This Owner acts as the central hub.

Management (Owner ➔ PetProfile & OwnerBandwidth): The Owner class manages the PetProfile and has an OwnerBandwidth. This creates a clear chain of command: Coordinator ➔ Owner ➔ Pet/Capacity.

Composition (PetProfile ➔ CareTask): The PetProfile contains both baseline_tasks and optional_tasks. This signifies that a pet’s care plan is built entirely out of these individual CareTask objects.

Validation Logic (OwnerBandwidth ➔ CareTask): The OwnerBandwidth class is directly connected to the CareTask via the canFitTask() method. This allows the system to "ask" the bandwidth object if a specific task is physically possible before adding it to the schedule.

-------------------------------------------------------------------------------------------------------------------

- What classes did you include, and what responsibilities did you assign to each?

--> 1. PetProfile: The Advocate
Main Responsibility: Acts as the "Source of Truth" for the pet's specific needs.

Key Job: It defines what "perfect care" looks like by storing non-negotiable tasks (like meds) and tracking "Wellness Debt" (e.g., if a dog missed a walk yesterday, this class flags it as a high priority today).

Why it’s here: To ensure the pet's health isn't ignored just because the owner is busy.

2. CareTask: The Action Unit
Main Responsibility: Defines the "cost" and "requirements" of a single activity.

Key Job: It stores the duration, effort level, and category. It also performs "context checks" (e.g., checking if an outdoor walk is viable based on weather or location).

Why it’s here: To turn vague ideas like "exercise" into concrete, measurable data points that the system can move around.

3. OwnerBandwidth: The Reality Check
Main Responsibility: Represents the human constraints of the system.

Key Job: It tracks the "fuel tank" for the day—specifically how many minutes are available and the owner's self-reported energy level.

Why it’s here: To prevent the app from suggesting an hour-long training session when the owner only has 15 minutes and is feeling burnt out.

4. ReSyncCoordinator: The Decision Maker
Main Responsibility: The "Brain" that performs the triage logic.

Key Job: It negotiates between the PetProfile (the needs) and the OwnerBandwidth (the limits). It sorts all available CareTasks and generates a final, realistic plan.

Why it’s here: To handle the "heavy lifting" of decision-making so the busy owner doesn't have to manually figure out what to cut when life gets chaotic.

-------------------------------------------------------------------------------------------------------------------

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

Yes, the design evolved significantly during implementation to address real-world constraints and improve robustness.

One key change was adding contextual attributes to CareTask, such as weather and dependencies, and enhancing isViable() to check external factors like weather for outdoor tasks. Initially, viability was just a boolean flag, but this limited adaptability. The change was made because the original design didn't account for dynamic conditions (e.g., skipping walks in bad weather), which are crucial for a pet care app that needs to be practical and safe. This ensures tasks are only scheduled when feasible, reducing frustration for owners and improving pet welfare.

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?

The scheduler considers multiple constraints to ensure realistic and safe pet care planning:

- Time and Energy Limits: Owner's available minutes (remaining_minutes) and energy level must accommodate task duration and effort level via canFitTask().
- Task Priority: Tasks are prioritized as high, medium, or low, with high-priority tasks scheduled first.
- Pet Preferences: Owner-defined preferences (e.g., "no outdoor" or "no high effort") prevent scheduling tasks that violate them.
- Task Viability: Tasks must be viable based on weather (outdoor tasks skipped in rain/storm), availability, and status (not completed).
- Dependencies: Optional tasks require their dependency titles to be already scheduled.
- Wellness Debt: Pets with higher wellness debt in specific categories (e.g., exercise) get priority for related tasks.
- Pet Safety: All baseline tasks are mandatory and scheduled first, regardless of other constraints.

- How did you decide which constraints mattered most?

Constraints were prioritized based on a hierarchy that puts pet safety and owner feasibility first, then optimization. Baseline tasks (mandatory care) take absolute precedence to ensure essential pet needs are met. Owner bandwidth constraints (time and energy) act as hard limits to prevent over-scheduling. Pet preferences and viability checks provide safety guards against inappropriate tasks. Finally, priority, debt, and dependencies enable intelligent optimization within those bounds. This hierarchy emerged from iterative testing and real-world considerations—pet welfare cannot be compromised, but the system must remain practical for busy owners.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
The scheduler implements exact-match time detection for conflict resolution, checking only for tasks scheduled at identical times rather than considering overlapping durations based on task lengths.

- Why is that tradeoff reasonable for this scenario?
This approach keeps the system lightweight and performant for an MVP by avoiding complex duration-based overlap calculations, which would require additional computational overhead and data structures. For a minimum viable product focused on core scheduling functionality, exact-match detection provides sufficient conflict awareness while maintaining simplicity and fast execution, allowing for future enhancement to full duration logic as the system scales.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
    I treated the AI as a senior pair programmer. I used it for the initial 'skeleton' of my classes, but where it really shined was during refactoring and integration. For example, I used Copilot Edits to bridge the gap between my Python logic in pawpal_system.py and the Streamlit interface in app.py, ensuring that data 'flowed' correctly from the user input into the session state vault.

- What kinds of prompts or questions were most helpful?
    The most effective prompts were task-specific and context-heavy. Instead of asking broad questions, I used the #codebase tag to ask: 'Using my existing Pet class, how do I implement a lightweight conflict detection that returns a warning instead of a crash?' Narrowing the scope to specific files kept the AI's suggestions accurate and ready to implement immediately.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
There was a moment during the Sorting Logic phase where the AI suggested a very dense, one-liner lambda function to handle the time strings. While it was technically correct and 'Pythonic,' it was difficult to read at a glance. I rejected the 'clever' version and directed the AI to write a more explicit method. I realized that as the architect, maintainable code is better than 'magic' code if I can't explain exactly how the sort works to someone else, it shouldn't be in my app. 

**c. AI Strategy**

As the Lead Architect on this project, my collaboration with AI tools has been transformative, teaching me the power of strategic human-AI partnerships in software development.

**some additional points:**
Effective Features: Copilot Edits and the #codebase context were absolute game-changers for connecting the gap between our Streamlit UI and backend logic. By including #codebase in my prompts, I could reference specific files and methods, allowing the AI to understand the existing architecture and generate precise integrations. Copilot Edits enabled seamless, in-place modifications that maintained code consistency while rapidly connecting UI components to scheduler methods like sort_by_time() and detect_conflicts().


Organization: To maximize productivity, I structured our collaboration into focused chat sessions dedicated to specific domains: one for UI Design, another for Logic implementation, and a third for Testing. This approach prevented "context drift" where the AI might lose track of prior decisions across unrelated tasks. By keeping each session narrowly scoped, the AI remained highly focused, delivering targeted solutions that integrated seamlessly with the overall system architecture.

Lessons Learned: This experience reinforced that being a Lead Architect means owning the "Why"—defining the design principles, ensuring safety and scalability, and making judgment calls on tradeoffs like readability versus performance. Meanwhile, AI excels at the "How," handling syntax, boilerplate code, and rapid prototyping. Our partnership thrives when I provide strategic direction and the AI executes with precision, creating software that is both innovative and maintainable. This collaboration has not only accelerated development but also deepened my understanding of how human insight and AI capabilities can produce superior results together.

- How did you evaluate or verify what the AI suggested?
I evaluated every suggestion based on maintainability. If the AI suggested a complex piece of 'magic' code that I couldn't explain to a teammate in 10 seconds, I asked it to refactor for clarity. I prioritized code that was easy to debug over code that was technically 'shorter'.
---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
I focused on three critical pillars: Sorting, Recurrence, and Conflict Detection. I verified that tasks automatically arrange themselves chronologically, that completing a "Daily" or "Weekly" task triggers the creation of a future instance using timedelta, and that the Scheduler accurately flags overlapping times across different pets.
- Why were these tests important?
These tests were the "safety net" for the user experience. Without proper sorting, the app is disorganized; without recurrence, the app fails as a long-term planning tool; and without conflict detection, a pet owner might accidentally double-book themselves. Verifying these ensured the backend "brain" was actually smart enough for real-world use.

**b. Confidence**

- How confident are you that your scheduler works correctly?
I have a 5-star (100%) confidence level in the core logic. By using pytest to mathematically verify the outcomes and manually stress-testing the Streamlit UI with "bad" data inputs, I confirmed that the system handles the primary use cases and data flow without crashing or losing information.

- What edge cases would you test next if you had more time?
I would test overlapping durations (e.g., a 1-hour walk at 8:00 AM conflicting with an 8:30 AM feeding) and time zone transitions. Currently, the system only flags exact-time matches, so adding logic to handle the "length" of a task would be the next logical step for a more robust scheduling engine.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
I am most satisfied with the integration between the Backend and the UI. Seeing a complex Python method like detect_conflicts instantly trigger a clear, helpful st.warning in the browser made the project feel like a professional-grade application rather than just a coding exercise.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
I would redesign the Task objects to include a "Duration" attribute. This would allow the Scheduler to move beyond simple string-matching and instead use actual time-window logic to catch overlaps, making the conflict detection much more powerful and useful for busy pet owners.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
I learned that being the "Lead Architect" means I am responsible for the 'Why,' while the AI handles the 'How.' AI is an incredible tool for generating syntax and boilerplate quickly, but it requires human oversight to ensure the system remains readable, maintainable, and logically sound. Using AI didn't replace my thinking; it amplified my ability to execute a complex vision.
