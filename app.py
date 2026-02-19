import streamlit as st
from database import (
    init_db,
    add_task,
    get_tasks,
    update_status,
    delete_task
)

# ─────────────────────────────────────────────────────────────
# Page Setup
# ─────────────────────────────────────────────────────────────
st.set_page_config(page_title="Sil-workflow", layout="wide")
init_db()

# ─────────────────────────────────────────────────────────────
# CSS Styling
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background-color: #f4f6f8; }
    .column-header {
        background-color: #4a90e2;
        color: white;
        padding: 10px;
        border-radius: 6px;
        text-align: center;
        font-weight: bold;
        margin-bottom: 12px;
    }
    .task-card {
        background-color: white;
        padding: 12px;
        margin-bottom: 10px;
        border-radius: 8px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.08);
        font-size: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# Session State
# ─────────────────────────────────────────────────────────────
if "user_id" not in st.session_state:
    st.session_state.user_id = None

# Containers
login_container = st.empty()
main_container = st.empty()

# ─────────────────────────────────────────────────────────────
# Login
# ─────────────────────────────────────────────────────────────
if st.session_state.user_id is None:
    with login_container.container():
        st.title("Sil-workflow")
        username = st.text_input("Username", placeholder="Enter your username...")
        if st.button("Login", type="primary"):
            cleaned = username.strip()
            if cleaned:
                st.session_state.user_id = cleaned
                st.rerun()
    st.stop()

# ─────────────────────────────────────────────────────────────
# Main Application
# ─────────────────────────────────────────────────────────────
with main_container.container():
    user_id = st.session_state.user_id

    # Header + Logout
    col_title, col_logout = st.columns([6, 1])
    with col_title:
        st.title(f"Sil-workflow — {user_id}")
    with col_logout:
        if st.button("Logout"):
            st.session_state.user_id = None
            st.rerun()

    st.divider()

    # ── Add Task Form ───────────────────────────────────────────
    with st.form(key="add_task_form", clear_on_submit=True):
        st.subheader("Add New Task")
        new_task = st.text_input(
            "Task name",
            placeholder="What needs to be done?...",
            key="new_task_input"
        )
        submitted = st.form_submit_button("Add Task", type="primary", use_container_width=True)

    if submitted:
        cleaned_task = new_task.strip()
        if cleaned_task:
            add_task(cleaned_task, user_id)
            st.success(f"Added: **{cleaned_task}**", icon="✅")
            st.rerun()

    st.divider()

    # ── Kanban Board ────────────────────────────────────────────
    st.subheader("Your Kanban Board")
    col_todo, col_doing, col_done = st.columns(3)

    # To Do
    with col_todo:
        st.markdown('<div class="column-header">📝 To Do</div>', unsafe_allow_html=True)
        tasks = get_tasks("todo", user_id)
        for task_id, title in tasks:
            st.markdown(f'<div class="task-card">{title}</div>', unsafe_allow_html=True)
            b1, b2 = st.columns(2)
            with b1:
                if st.button("➡ Start", key=f"todo_start_{task_id}", use_container_width=True):
                    update_status(task_id, "doing")
                    st.rerun()
            with b2:
                if st.button("❌ Delete", key=f"todo_del_{task_id}", use_container_width=True):
                    delete_task(task_id)
                    st.rerun()

    # Doing
    with col_doing:
        st.markdown('<div class="column-header">⚡ Doing</div>', unsafe_allow_html=True)
        tasks = get_tasks("doing", user_id)
        for task_id, title in tasks:
            st.markdown(f'<div class="task-card">{title}</div>', unsafe_allow_html=True)
            b1, b2 = st.columns(2)
            with b1:
                if st.button("✓ Done", key=f"doing_done_{task_id}", use_container_width=True):
                    update_status(task_id, "done")
                    st.rerun()
            with b2:
                if st.button("❌ Delete", key=f"doing_del_{task_id}", use_container_width=True):
                    delete_task(task_id)
                    st.rerun()

    # Done
    with col_done:
        st.markdown('<div class="column-header">✅ Done</div>', unsafe_allow_html=True)
        tasks = get_tasks("done", user_id)
        for task_id, title in tasks:
            st.markdown(f'<div class="task-card">{title}</div>', unsafe_allow_html=True)
            b1, b2 = st.columns(2)
            with b1:
                if st.button("⬅ Reopen", key=f"done_reopen_{task_id}", use_container_width=True):
                    update_status(task_id, "doing")
                    st.rerun()
            with b2:
                if st.button("❌ Delete", key=f"done_del_{task_id}", use_container_width=True):
                    delete_task(task_id)
                    st.rerun()

    st.write("")  # bottom spacing