from pawpal_system import CareTask, PetProfile, OwnerBandwidth, Owner, ReSyncCoordinator

def main():
    # Create owner with bandwidth (60 minutes, energy level 4)
    bandwidth = OwnerBandwidth(60, 60, 4, True)
    owner = Owner("Jordan", bandwidth)

    # Create first pet: Mochi (dog)
    mochi = PetProfile("Mochi", "dog", preferences=["no high effort"])
    mochi.addBaselineTask(CareTask("Feed", "Morning feeding", 10, "daily", 1, "Indoor", "Health", "high"))
    mochi.optional_tasks = [
        CareTask("Walk", "Evening walk", 30, "daily", 3, "Outdoor", "Exercise", "medium"),
        CareTask("Play", "Indoor play", 15, "daily", 2, "Indoor", "Enrichment", "low")
    ]
    mochi.recordWellnessDebt("Exercise", 2)
    owner.addPet(mochi)

    # Create second pet: Whiskers (cat)
    whiskers = PetProfile("Whiskers", "cat", preferences=["no outdoor"])
    whiskers.addBaselineTask(CareTask("Feed Cat", "Cat food", 5, "daily", 1, "Indoor", "Health", "high"))
    whiskers.optional_tasks = [
        CareTask("Brush", "Grooming session", 20, "daily", 2, "Indoor", "Enrichment", "medium"),
        CareTask("Laser Play", "Interactive play", 10, "daily", 1, "Indoor", "Enrichment", "low")
    ]
    whiskers.recordWellnessDebt("Enrichment", 1)
    owner.addPet(whiskers)

    # Create scheduler and generate plan
    scheduler = ReSyncCoordinator(owner)
    schedule = scheduler.generateDailyPlan()

    # Print Today's Schedule
    print("🐾 PawPal+ Today's Schedule for", owner.name)
    print("=" * 40)
    if schedule:
        for i, task in enumerate(schedule, 1):
            print(f"{i}. {task.summary()}")
    else:
        print("No tasks scheduled.")
    print(f"\nRemaining time: {owner.bandwidth.remaining_minutes} minutes")
    print(f"Remaining energy: {owner.bandwidth.energy_level}")

if __name__ == "__main__":
    main()
