# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
--> A brief description of the initial UML design and the relationship between the different classes established are: 

1. The Core Entities (Data Holders)
The design consists of three primary data-holding classes:

PetProfile: Stores the pet’s "ideal" care standards, including baseline_tasks (essentials) and wellness_debt (missed activities).

CareTask: Defines a single unit of work (e.g., a walk), holding metadata like duration, effort_level, and priority.

OwnerBandwidth: Represents the user's constraints, specifically remaining_minutes and energy_level.

2. The Controller (The Logic)
ReSyncCoordinator: This is the "Brain" of the system. It maintains a 1-to-1 relationship with both the PetProfile and the OwnerBandwidth.

Action: It pulls the "Candidate Tasks" from the pet, filters them through the owner's available "Bandwidth," and moves the survivors into the scheduled_tasks list.

3. Key Class Relationships
Composition (PetProfile ➔ CareTask): The PetProfile contains multiple CareTasks. This signifies that a pet’s care plan is built out of these individual task objects.

Association (ReSyncCoordinator ➔ All Classes): The Coordinator acts as the bridge. It "knows" the Pet, "knows" the Owner, and "schedules" the Tasks.

Validation (OwnerBandwidth ➔ CareTask): Through the canFitTask() method, the bandwidth class acts as a gatekeeper to ensure no task is scheduled that exceeds the owner's time or energy budget.

-------------------------------------------------------------------------------------------------------------------------

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

-------------------------------------------------------------------------------------------------------------------------

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

Yes, the design evolved significantly during implementation to address real-world constraints and improve robustness.

One key change was adding contextual attributes to CareTask, such as weather and dependencies, and enhancing isViable() to check external factors like weather for outdoor tasks. Initially, viability was just a boolean flag, but this limited adaptability. The change was made because the original design didn't account for dynamic conditions (e.g., skipping walks in bad weather), which are crucial for a pet care app that needs to be practical and safe. This ensures tasks are only scheduled when feasible, reducing frustration for owners and improving pet welfare.

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
The scheduler implements exact-match time detection for conflict resolution, checking only for tasks scheduled at identical times rather than considering overlapping durations based on task lengths.

- Why is that tradeoff reasonable for this scenario?
This approach keeps the system lightweight and performant for an MVP by avoiding complex duration-based overlap calculations, which would require additional computational overhead and data structures. For a minimum viable product focused on core scheduling functionality, exact-match detection provides sufficient conflict awareness while maintaining simplicity and fast execution, allowing for future enhancement to full duration logic as the system scales.

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
