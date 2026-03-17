"""
PawPal+ | pawpal_system.py
Logic layer — all backend classes live here.
"""

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Optional


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------

@dataclass
class Task:
    """A single pet-care activity."""
    description: str
    time: str                        # "HH:MM" format
    frequency: str                   # "once" | "daily" | "weekly"
    priority: str = "medium"         # "low" | "medium" | "high"
    pet_name: str = ""
    due_date: date = field(default_factory=date.today)
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True

    def reschedule(self) -> "Task":
        """Return a new Task for the next occurrence based on frequency."""
        delta = timedelta(days=1) if self.frequency == "daily" else timedelta(weeks=1)
        return Task(
            description=self.description,
            time=self.time,
            frequency=self.frequency,
            priority=self.priority,
            pet_name=self.pet_name,
            due_date=self.due_date + delta,
            completed=False,
        )

    def __str__(self) -> str:
        status = "✓" if self.completed else "○"
        return f"[{status}] {self.time} — {self.description} ({self.pet_name}, {self.frequency})"


# ---------------------------------------------------------------------------
# Pet
# ---------------------------------------------------------------------------

@dataclass
class Pet:
    """A pet owned by an Owner; holds a list of Tasks."""
    name: str
    species: str
    age: int
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a Task to this pet and stamp the task with the pet's name."""
        task.pet_name = self.name
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a Task from this pet's list."""
        self.tasks.remove(task)

    def get_tasks(self) -> list[Task]:
        """Return all tasks for this pet."""
        return self.tasks

    def __str__(self) -> str:
        return f"{self.name} ({self.species}, age {self.age}) — {len(self.tasks)} task(s)"


# ---------------------------------------------------------------------------
# Owner
# ---------------------------------------------------------------------------

@dataclass
class Owner:
    """Manages a collection of Pets."""
    name: str
    contact: str = ""
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a Pet to this owner's roster."""
        self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        """Remove a Pet from this owner's roster."""
        self.pets.remove(pet)

    def get_all_tasks(self) -> list[Task]:
        """Return every Task across all pets as a flat list."""
        return [task for pet in self.pets for task in pet.get_tasks()]

    def __str__(self) -> str:
        return f"{self.name} — {len(self.pets)} pet(s)"


# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------

class Scheduler:
    """
    The 'brain' of PawPal+.
    Retrieves, sorts, filters, and validates tasks across all pets.
    """

    def __init__(self, owner: Owner) -> None:
        """Initialize the Scheduler with an Owner instance."""
        self.owner = owner

    def get_todays_tasks(self) -> list[Task]:
        """Return all tasks due today, across all pets."""
        today = date.today()
        return [t for t in self.owner.get_all_tasks() if t.due_date == today]

    def sort_by_time(self, tasks: Optional[list[Task]] = None) -> list[Task]:
        """Return tasks sorted chronologically by their HH:MM time attribute."""
        tasks = tasks if tasks is not None else self.owner.get_all_tasks()
        return sorted(tasks, key=lambda t: t.time)

    def filter_tasks(
        self,
        tasks: Optional[list[Task]] = None,
        pet_name: Optional[str] = None,
        completed: Optional[bool] = None,
    ) -> list[Task]:
        """Filter tasks by pet name and/or completion status."""
        tasks = tasks if tasks is not None else self.owner.get_all_tasks()
        if pet_name is not None:
            tasks = [t for t in tasks if t.pet_name == pet_name]
        if completed is not None:
            tasks = [t for t in tasks if t.completed == completed]
        return tasks

    def detect_conflicts(self, tasks: Optional[list[Task]] = None) -> list[str]:
        """Return warning strings for any tasks that share the same time slot."""
        tasks = tasks if tasks is not None else self.owner.get_all_tasks()
        seen: dict[str, Task] = {}
        warnings = []
        for task in tasks:
            if task.time in seen:
                other = seen[task.time]
                warnings.append(
                    f"⚠️ Conflict at {task.time}: '{task.description}' "
                    f"({task.pet_name}) vs '{other.description}' ({other.pet_name})"
                )
            else:
                seen[task.time] = task
        return warnings

    def handle_recurring(self, task: Task) -> Optional[Task]:
        """
        Mark a task complete and return its next occurrence if recurring.
        Returns None for one-time tasks.
        """
        task.mark_complete()
        if task.frequency in ("daily", "weekly"):
            return task.reschedule()
        return None