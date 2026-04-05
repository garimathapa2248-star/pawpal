# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

"""
The three main actions that this program is supposed to take ---> 
1) baseline pet audit : 
    the minimum viable care that is added when the program is first established and something that AI is not supposed to break afterwards 
2) adaptive daily schedule : 
    according to your time availability and importance of your tasks, it decides which tasks are essential than which and the ones that can be rescheduled
3) Emergency schedule  re-sync: the action for fixing the issues that have been disrupted by real-world delays. 
""""

- Briefly describe your initial UML design.

My initial UML design has 
- What classes did you include, and what responsibilities did you assign to each?
    - There are four main methods for my project: 
        1. PetProfile (The Standard Setter)

Responsibilities: Defining Non-Negotiables: Storing fixed-time tasks like insulin or breakfast.

Tracking Wellness Debt: Monitoring if the pet is "under-exercised" from previous days.

Prioritization: Flagging which needs are critical versus which are "bonus" (like a fancy grooming session).

2. CareTask (The Unit of Action)

Responsibilities: Metadata Storage: Holding the duration, effort level (1-5), and location (Indoor/Outdoor).

Context Check: Determining if it’s currently "viable." (e.g., A "Long Hike" task can mark itself as unavailable if the weather is set to "Stormy").

Categorization: Sorting itself into Health, Exercise, or Enrichment.

3. OwnerBandwidth (The Constraint Monitor)

Responsibilities: Resource Tracking: Managing the remaining minutes in the day.

State Management: Storing the owner’s self-reported energy levels.

Dynamic Updating: Allowing the user to "shave off" or "add" time as their workday shifts.

4. ReSyncCoordinator (The Decision Maker)

Responsibilities: Triage Logic: Comparing PetProfile needs against OwnerBandwidth limits.

Conflict Resolution: Deciding what to cut when time is low (e.g., keeping "Meds" but dropping "Training").

Transparency: Generating the "Why this plan?" explanation so the owner understands the logic behind the cuts.


**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

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
