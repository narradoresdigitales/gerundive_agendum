import streamlit as st
from database import (
    init_db,
    add_task,
    get_tasks,
    update_status,
    delete_task
)

# --------------------------------------------------
# Page Setup
# --------------------------------------------------

st.set_page_config(
    page_title="workflow",
    layout="wide"
)

init_db()

# --------------------------------------------------
# Subtle Page Background Contrast
# --------------------------------------------------

st.markdown("""
<style>
.stApp {
    background-color: #f4f6f8;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# User Session Handling
# --------------------------------------------------

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if st.session_state.user_id is None:
    st.title("workflow")
    username = st.text_input("Enter your username")

    if st.button("Enter"):
        if username.strip():
            st.session_state.user_id = username.strip()
            st.rerun()

    st.stop()

user_id = st.session_state.user_id

# --------------------------------------------------
# Header
# --------------------------------------------------

st.title(f"workflow — {user_id}")

if st.button("Logout"):
    st.session_state.user_id = None
    st.rerun()

# --------------------------------------------------
# Add Task Section
# --------------------------------------------------

st.subheader("Add Task")
new_task = st.text_input("Task name", placeholder="Enter new task...")

if st.button("Add Task"):
    if new_task.strip():
        add_task(new_task.strip(), user_id)
        st.rerun()

st.divider()

# --------------------------------------------------
# Kanban Columns
# --------------------------------------------------

col1, col2, col3 = st.columns(3)

# ---------------- TO DO ----------------
with col1:
    st.header("📝 To Do")

    tasks = get_tasks("todo", user_id)

    for task_id, title in tasks:
        st.markdown(f"**{title}**")

        if st.button("➡ Move to Doing", key=f"todo_move_{task_id}"):
            update_status(task_id, "doing")
            st.rerun()

        if st.button("❌ Delete", key=f"todo_delete_{task_id}"):
            delete_task(task_id)
            st.rerun()

        st.divider()

# ---------------- DOING ----------------
with col2:
    st.header("⚡ Doing")

    tasks = get_tasks("doing", user_id)

    for task_id, title in tasks:
        st.markdown(f"**{title}**")

        if st.button("➡ Move to Done", key=f"doing_move_{task_id}"):
            update_status(task_id, "done")
            st.rerun()

        if st.button("❌ Delete", key=f"doing_delete_{task_id}"):
            delete_task(task_id)
            st.rerun()

        st.divider()

# ---------------- DONE ----------------
with col3:
    st.header("✅ Done")

    tasks = get_tasks("done", user_id)

    for task_id, title in tasks:
        st.markdown(f"**{title}**")

        if st.button("⬅ Move to Doing", key=f"done_move_{task_id}"):
            update_status(task_id, "doing")
            st.rerun()

        if st.button("❌ Delete", key=f"done_delete_{task_id}"):
            delete_task(task_id)
            st.rerun()

        st.divider()
