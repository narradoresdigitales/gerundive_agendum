import streamlit as st
from database import init_db, add_task, get_tasks, update_status, delete_task

# ────────────────────────────────────────────────
# Constants
# ────────────────────────────────────────────────
STATUSES = {
    "todo":        "📝 To Do",
    "in_progress": "⚡ In Progress",
    "done":        "✅ Done"
}

# ────────────────────────────────────────────────
# Page config & DB init
# ────────────────────────────────────────────────
st.set_page_config(page_title="Workflow", layout="wide")
init_db()

# ────────────────────────────────────────────────
# Styling
# ────────────────────────────────────────────────
st.markdown("""
    <style>
        .stApp { background-color: #f8f9fc; }
        .column-header {
            background-color: #4a90e2;
            color: white;
            padding: 12px;
            border-radius: 6px;
            text-align: center;
            font-weight: bold;
            margin: 0 0 16px 0;
            font-size: 1.15rem;
        }
        .task-card {
            background: white;
            padding: 14px 16px;
            margin-bottom: 12px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.07);
            border-left: 4px solid #4a90e2;
            font-size: 1.05rem;
        }
        .stButton > button { font-size: 0.95rem; }
    </style>
""", unsafe_allow_html=True)

# ────────────────────────────────────────────────
# Session state
# ────────────────────────────────────────────────
if "user_id" not in st.session_state:
    st.session_state.user_id = None

# ────────────────────────────────────────────────
# Login screen
# ────────────────────────────────────────────────
if st.session_state.user_id is None:
    st.title("Workflow")
    username = st.text_input("Username", placeholder="your name or nickname…", max_chars=50)
    if st.button("Login", type="primary", use_container_width=True) and username.strip():
        st.session_state.user_id = username.strip()
        st.rerun()
    st.stop()

# ────────────────────────────────────────────────
# Main app
# ────────────────────────────────────────────────
user_id = st.session_state.user_id

# Header + Logout
col1, col2 = st.columns([9, 1])
with col1:
    st.title(f"Workflow  —  {user_id}")
with col2:
    if st.button("Logout", use_container_width=True):
        st.session_state.user_id = None
        st.rerun()

st.divider()

# ── Add task ─────────────────────────────────────
with st.form("add_task_form", clear_on_submit=True):
    st.subheader("Add New Task")
    col_a, col_b = st.columns([5, 2])
    with col_a:
        new_task = st.text_input(
            "Task description",
            placeholder="What needs to be done? …",
            label_visibility="collapsed",
            key="new_task_input"
        )
    with col_b:
        submitted = st.form_submit_button(
            "➕ Add",
            type="primary",
            use_container_width=True,
            disabled=not new_task.strip()
        )

if submitted and (cleaned := new_task.strip()):
    add_task(cleaned, user_id)
    st.success(f"Task added: **{cleaned}**", icon="✅")
    st.rerun()

st.divider()

# ── Kanban board ─────────────────────────────────
st.subheader("Your Tasks")

cols = st.columns(3)

for status_key, header_text in STATUSES.items():
    with cols[list(STATUSES.keys()).index(status_key)]:
        st.markdown(f'<div class="column-header">{header_text}</div>', unsafe_allow_html=True)

        tasks = get_tasks(status_key, user_id)

        if not tasks:
            st.caption("— nothing here yet —")
            continue

        for task_id, title in tasks:
            st.markdown(f'<div class="task-card">{title}</div>', unsafe_allow_html=True)

            btn_col1, btn_col2 = st.columns(2)

            with btn_col1:
                if status_key == "todo":
                    if st.button("Start ▶", key=f"act_start_{task_id}", use_container_width=True):
                        update_status(task_id, "in_progress")
                        st.rerun()

                elif status_key == "in_progress":
                    if st.button("Complete ✓", key=f"act_done_{task_id}", use_container_width=True):
                        update_status(task_id, "done")
                        st.rerun()

                elif status_key == "done":
                    if st.button("Reopen ↺", key=f"act_reopen_{task_id}", use_container_width=True):
                        update_status(task_id, "in_progress")  # or "todo" — your choice
                        st.rerun()

            with btn_col2:
                if st.button("🗑 Delete", key=f"act_del_{task_id}", use_container_width=True):
                    delete_task(task_id)
                    st.rerun()

st.markdown("<br><br>", unsafe_allow_html=True)