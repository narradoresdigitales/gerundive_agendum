import streamlit as st
from database import (
    init_db,
    add_task,
    get_tasks,
    update_status,
    delete_task
)

# -------------------------
# Page Setup
# -------------------------
st.set_page_config(page_title="Sil-workflow", layout="wide")
init_db()

# -------------------------
# CSS Styling
# -------------------------
st.markdown("""
<style>
.stApp { background-color: #f4f6f8; }
.column-header {
    background-color: #4a90e2;
    color: white;
    padding: 8px;
    border-radius: 5px;
    text-align: center;
    font-weight: bold;
}
.task-card {
    background-color: white;
    padding: 10px;
    margin-bottom: 8px;
    border-radius: 6px;
    box-shadow: 0px 2px 4px rgba(0,0,0,0.1);
}
</style>
""", unsafe_allow_html=True)

# -------------------------
# Containers
# -------------------------
login_container = st.empty()
main_container = st.empty()

# -------------------------
# Session State
# -------------------------
if "user_id" not in st.session_state:
    st.session_state.user_id = None

# Flags for tracking UI changes (no rerun needed)
if "added_task" not in st.session_state:
    st.session_state.added_task = False
if "action_performed" not in st.session_state:
    st.session_state.action_performed = False

# -------------------------
# Login Section
# -------------------------
if st.session_state.user_id is None:
    with login_container.container():
        st.title("Sil-workflow")
        username = st.text_input("Username", key="login_username")
        if st.button("Login", key="login_button"):
            if username.strip():
                st.session_state.user_id = username.strip()
    st.stop()  # stop rendering main app until logged in

# -------------------------
# Main App Section
# -------------------------
with main_container.container():
    user_id = st.session_state.user_id

    # Header + Logout
    st.title(f"Sil-workflow — {user_id}")
    st.write("")
    if st.button("Logout", key="logout_button"):
        st.session_state.user_id = None
        st.stop()  # safely stop after logout

    st.write("")
    st.subheader("Add Task")
    st.write("")

    # Add Task Input
    new_task = st.text_input(
        "Task name",
        key="add_task_input",
        placeholder="Enter new task..."
    )
    if st.button("Add Task", key="add_task_button"):
        if new_task.strip():
            add_task(new_task.strip(), user_id)
            st.session_state.added_task = True
            st.session_state.add_task_input = ""  # clear input

    st.divider()
    st.write("")

    # ---------------- Kanban Columns ----------------
    col1, col2, col3 = st.columns(3)

    # --- TO DO ---
    with col1:
        st.markdown('<div class="column-header">📝 To Do</div>', unsafe_allow_html=True)
        tasks = get_tasks("todo", user_id)
        for task_id, title in tasks:
            st.markdown(f'<div class="task-card">{title}</div>', unsafe_allow_html=True)
            cols = st.columns([1,1])
            with cols[0]:
                if st.button("➡ Doing", key=f"todo_move_{task_id}"):
                    update_status(task_id, "doing")
                    st.session_state.action_performed = True
            with cols[1]:
                if st.button("❌ Delete", key=f"todo_delete_{task_id}"):
                    delete_task(task_id)
                    st.session_state.action_performed = True

    # --- DOING ---
    with col2:
        st.markdown('<div class="column-header">⚡ Doing</div>', unsafe_allow_html=True)
        tasks = get_tasks("doing", user_id)
        for task_id, title in tasks:
            st.markdown(f'<div class="task-card">{title}</div>', unsafe_allow_html=True)
            cols = st.columns([1,1])
            with cols[0]:
                if st.button("➡ Done", key=f"doing_move_{task_id}"):
                    update_status(task_id, "done")
                    st.session_state.action_performed = True
            with cols[1]:
                if st.button("❌ Delete", key=f"doing_delete_{task_id}"):
                    delete_task(task_id)
                    st.session_state.action_performed = True

    # --- DONE ---
    with col3:
        st.markdown('<div class="column-header">✅ Done</div>', unsafe_allow_html=True)
        tasks = get_tasks("done", user_id)
        for task_id, title in tasks:
            st.markdown(f'<div class="task-card">{title}</div>', unsafe_allow_html=True)
            cols = st.columns([1,1])
            with cols[0]:
                if st.button("⬅ Doing", key=f"done_move_{task_id}"):
                    update_status(task_id, "doing")
                    st.session_state.action_performed = True
            with cols[1]:
                if st.button("❌ Delete", key=f"done_delete_{task_id}"):
                    delete_task(task_id)
                    st.session_state.action_performed = True
