"""
PawPal+ | app.py
Streamlit UI — connects to pawpal_system.py backend.
Run with: streamlit run app.py
"""

import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")
st.caption("A smart pet care scheduling assistant.")

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
if "owner" not in st.session_state:
    st.session_state.owner = None

# ---------------------------------------------------------------------------
# Sidebar — Owner + Pet setup
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Setup")

    st.subheader("Owner Info")
    owner_name = st.text_input("Owner name", value="Alex")
    contact    = st.text_input("Contact email", value="")

    if st.button("Save Owner", use_container_width=True):
        st.session_state.owner = Owner(name=owner_name, contact=contact)
        st.success(f"Owner '{owner_name}' saved!")

    if st.session_state.owner:
        st.divider()
        st.subheader("Add a Pet")
        pet_name = st.text_input("Pet name", value="Buddy")
        species  = st.selectbox("Species", ["Dog", "Cat", "Bird", "Other"])
        age      = st.number_input("Age", min_value=0, max_value=30, value=3)

        if st.button("Add Pet", use_container_width=True):
            new_pet = Pet(name=pet_name, species=species, age=age)
            st.session_state.owner.add_pet(new_pet)
            st.success(f"Added {pet_name} the {species}!")

# ---------------------------------------------------------------------------
# Main area
# ---------------------------------------------------------------------------
if not st.session_state.owner:
    st.info("👈 Start by entering an owner name in the sidebar and clicking **Save Owner**.")
    st.stop()

owner = st.session_state.owner

# Pets overview
st.subheader(f"🐾 Pets for {owner.name}")
if not owner.pets:
    st.info("No pets yet — add one in the sidebar.")
else:
    cols = st.columns(len(owner.pets))
    for i, pet in enumerate(owner.pets):
        with cols[i]:
            st.metric(label=f"{pet.name}", value=pet.species, delta=f"Age {pet.age}")

st.divider()

# ---------------------------------------------------------------------------
# Add a Task
# ---------------------------------------------------------------------------
st.subheader("📋 Add a Task")

if not owner.pets:
    st.warning("Add a pet first before scheduling tasks.")
else:
    pet_names = [p.name for p in owner.pets]

    col1, col2 = st.columns(2)
    with col1:
        selected_pet = st.selectbox("Assign to pet", pet_names)
        description  = st.text_input("Task description", value="Morning walk")
        frequency    = st.selectbox("Frequency", ["once", "daily", "weekly"])
    with col2:
        time_input = st.time_input("Time")
        priority   = st.selectbox("Priority", ["low", "medium", "high"], index=1)

    if st.button("➕ Add Task", use_container_width=True):
        pet_obj  = next(p for p in owner.pets if p.name == selected_pet)
        new_task = Task(
            description=description,
            time=time_input.strftime("%H:%M"),
            frequency=frequency,
            priority=priority,
        )
        pet_obj.add_task(new_task)
        st.success(f"Task '{description}' added to {selected_pet}!")

st.divider()

# ---------------------------------------------------------------------------
# Filter controls
# ---------------------------------------------------------------------------
st.subheader("🔍 Filter Tasks")
col1, col2 = st.columns(2)
with col1:
    filter_pet = st.selectbox("Filter by pet", ["All"] + [p.name for p in owner.pets])
with col2:
    filter_status = st.selectbox("Filter by status", ["All", "Incomplete", "Complete"])

st.divider()

# ---------------------------------------------------------------------------
# Generate Schedule
# ---------------------------------------------------------------------------
st.subheader("📅 Today's Schedule")

if st.button("🗓️ Generate Schedule", use_container_width=True):
    all_tasks = owner.get_all_tasks()

    if not all_tasks:
        st.info("No tasks yet — add some above!")
    else:
        scheduler = Scheduler(owner)

        filtered = scheduler.filter_tasks(
            pet_name=None if filter_pet == "All" else filter_pet,
            completed=None if filter_status == "All" else (filter_status == "Complete"),
        )
        sorted_tasks = scheduler.sort_by_time(filtered)
        conflicts    = scheduler.detect_conflicts(filtered)

        # Conflict warnings
        if conflicts:
            for warning in conflicts:
                st.warning(warning)
        else:
            st.success("✅ No scheduling conflicts found!")

        # Task rows with complete buttons
        priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}
        st.markdown("---")
        for i, task in enumerate(sorted_tasks):
            col1, col2 = st.columns([4, 1])
            with col1:
                icon   = priority_icon.get(task.priority, "⚪")
                status = "✅" if task.completed else "⬜"
                st.write(
                    f"{status} {icon} `{task.time}` — **{task.description}** "
                    f"· {task.pet_name} · *{task.frequency}*"
                )
            with col2:
                if not task.completed:
                    if st.button("Done ✓", key=f"complete_{i}"):
                        next_task = scheduler.handle_recurring(task)
                        if next_task:
                            pet_obj = next(p for p in owner.pets if p.name == task.pet_name)
                            pet_obj.add_task(next_task)
                            st.success(f"✓ Done! Next '{task.description}' scheduled.")
                        else:
                            st.success(f"✓ '{task.description}' marked complete!")
                        st.rerun()