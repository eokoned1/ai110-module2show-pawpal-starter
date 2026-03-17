"""
PawPal+ | main.py
CLI demo — verifies backend logic before touching the Streamlit UI.
Run with: python main.py
"""

from pawpal_system import Owner, Pet, Task, Scheduler

# ---------------------------------------------------------------------------
# Setup: owner + two pets
# ---------------------------------------------------------------------------
owner = Owner(name="Alex", contact="alex@email.com")

buddy = Pet(name="Buddy", species="Dog", age=3)
luna  = Pet(name="Luna",  species="Cat", age=5)

owner.add_pet(buddy)
owner.add_pet(luna)

# ---------------------------------------------------------------------------
# Add tasks (intentionally out of order to test sorting)
# ---------------------------------------------------------------------------
buddy.add_task(Task(description="Evening walk",   time="18:00", frequency="daily",  priority="high"))
buddy.add_task(Task(description="Morning walk",   time="08:00", frequency="daily",  priority="high"))
buddy.add_task(Task(description="Flea medication",time="08:00", frequency="weekly", priority="medium"))  # conflict!

luna.add_task(Task(description="Feeding",         time="07:30", frequency="daily",  priority="high"))
luna.add_task(Task(description="Playtime",        time="15:00", frequency="daily",  priority="low"))

# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------
scheduler = Scheduler(owner)

print("=" * 50)
print(f"  PawPal+ — Today's Schedule for {owner.name}")
print("=" * 50)

sorted_tasks = scheduler.sort_by_time()
for task in sorted_tasks:
    priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(task.priority, "⚪")
    print(f"  {priority_icon} {task}")

# ---------------------------------------------------------------------------
# Conflict detection
# ---------------------------------------------------------------------------
print("\n--- Conflict Check ---")
conflicts = scheduler.detect_conflicts()
if conflicts:
    for warning in conflicts:
        print(warning)
else:
    print("No conflicts found.")

# ---------------------------------------------------------------------------
# Filtering: show only Buddy's tasks
# ---------------------------------------------------------------------------
print("\n--- Buddy's Tasks Only ---")
buddy_tasks = scheduler.filter_tasks(pet_name="Buddy")
for task in scheduler.sort_by_time(buddy_tasks):
    print(f"  {task}")

# ---------------------------------------------------------------------------
# Recurring task demo
# ---------------------------------------------------------------------------
print("\n--- Recurring Task Demo ---")
walk = buddy.get_tasks()[0]
print(f"Completing: {walk}")
next_task = scheduler.handle_recurring(walk)
if next_task:
    print(f"Next occurrence created: {next_task}")