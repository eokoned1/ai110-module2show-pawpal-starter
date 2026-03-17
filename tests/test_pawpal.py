"""
PawPal+ | tests/test_pawpal.py
Automated test suite — run with: python -m pytest
"""

from datetime import date, timedelta
from pawpal_system import Owner, Pet, Task, Scheduler


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_owner_with_pets():
    """Create a standard Owner with two pets for reuse across tests."""
    owner = Owner(name="Test Owner")
    buddy = Pet(name="Buddy", species="Dog", age=3)
    luna  = Pet(name="Luna",  species="Cat", age=5)
    owner.add_pet(buddy)
    owner.add_pet(luna)
    return owner, buddy, luna


# ---------------------------------------------------------------------------
# Task tests
# ---------------------------------------------------------------------------

def test_mark_complete_changes_status():
    """Completing a task should flip completed to True."""
    task = Task(description="Walk", time="08:00", frequency="daily")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_task_addition_increases_count():
    """Adding a task to a pet should increase its task count by 1."""
    pet = Pet(name="Buddy", species="Dog", age=3)
    assert len(pet.get_tasks()) == 0
    pet.add_task(Task(description="Walk", time="08:00", frequency="daily"))
    assert len(pet.get_tasks()) == 1


def test_task_stamped_with_pet_name():
    """A task's pet_name should be set when added to a pet."""
    pet  = Pet(name="Buddy", species="Dog", age=3)
    task = Task(description="Walk", time="08:00", frequency="daily")
    pet.add_task(task)
    assert task.pet_name == "Buddy"


# ---------------------------------------------------------------------------
# Sorting tests
# ---------------------------------------------------------------------------

def test_sort_by_time_returns_chronological_order():
    """Tasks should come back sorted earliest to latest."""
    owner, buddy, luna = make_owner_with_pets()
    buddy.add_task(Task(description="Evening walk", time="18:00", frequency="daily"))
    buddy.add_task(Task(description="Morning walk", time="08:00", frequency="daily"))
    luna.add_task( Task(description="Feeding",      time="07:30", frequency="daily"))

    scheduler = Scheduler(owner)
    sorted_tasks = scheduler.sort_by_time()
    times = [t.time for t in sorted_tasks]
    assert times == sorted(times)


# ---------------------------------------------------------------------------
# Recurrence tests
# ---------------------------------------------------------------------------

def test_daily_task_reschedules_to_tomorrow():
    """Completing a daily task should produce a new task for tomorrow."""
    task = Task(description="Walk", time="08:00", frequency="daily", due_date=date.today())
    next_task = task.reschedule()
    assert next_task.due_date == date.today() + timedelta(days=1)
    assert next_task.completed is False


def test_weekly_task_reschedules_to_next_week():
    """Completing a weekly task should produce a new task 7 days out."""
    task = Task(description="Bath", time="10:00", frequency="weekly", due_date=date.today())
    next_task = task.reschedule()
    assert next_task.due_date == date.today() + timedelta(weeks=1)


def test_handle_recurring_returns_none_for_once():
    """One-time tasks should not produce a next occurrence."""
    owner = Owner(name="Test")
    pet   = Pet(name="Buddy", species="Dog", age=2)
    owner.add_pet(pet)
    task  = Task(description="Vet visit", time="09:00", frequency="once")
    pet.add_task(task)

    scheduler = Scheduler(owner)
    result = scheduler.handle_recurring(task)
    assert result is None


# ---------------------------------------------------------------------------
# Conflict detection tests
# ---------------------------------------------------------------------------

def test_conflict_detected_for_same_time():
    """Two tasks at the same time should trigger a conflict warning."""
    owner, buddy, luna = make_owner_with_pets()
    buddy.add_task(Task(description="Walk",      time="08:00", frequency="daily"))
    buddy.add_task(Task(description="Medication", time="08:00", frequency="daily"))

    scheduler = Scheduler(owner)
    warnings  = scheduler.detect_conflicts()
    assert len(warnings) >= 1
    assert "08:00" in warnings[0]


def test_no_conflict_for_different_times():
    """Tasks at different times should produce no warnings."""
    owner, buddy, luna = make_owner_with_pets()
    buddy.add_task(Task(description="Walk",    time="08:00", frequency="daily"))
    buddy.add_task(Task(description="Feeding", time="09:00", frequency="daily"))

    scheduler = Scheduler(owner)
    warnings  = scheduler.detect_conflicts()
    assert len(warnings) == 0


# ---------------------------------------------------------------------------
# Filtering tests
# ---------------------------------------------------------------------------

def test_filter_by_pet_name():
    """Filtering by pet name should return only that pet's tasks."""
    owner, buddy, luna = make_owner_with_pets()
    buddy.add_task(Task(description="Walk",    time="08:00", frequency="daily"))
    luna.add_task( Task(description="Feeding", time="07:30", frequency="daily"))

    scheduler    = Scheduler(owner)
    buddy_tasks  = scheduler.filter_tasks(pet_name="Buddy")
    assert all(t.pet_name == "Buddy" for t in buddy_tasks)


def test_filter_by_completion_status():
    """Filtering by completed=False should exclude finished tasks."""
    owner, buddy, _ = make_owner_with_pets()
    t1 = Task(description="Walk",    time="08:00", frequency="daily")
    t2 = Task(description="Feeding", time="09:00", frequency="daily")
    buddy.add_task(t1)
    buddy.add_task(t2)
    t1.mark_complete()

    scheduler       = Scheduler(owner)
    incomplete      = scheduler.filter_tasks(completed=False)
    assert all(not t.completed for t in incomplete)