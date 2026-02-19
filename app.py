import streamlit as st
from database import init_db, add_task, get_tasks, update_status, delete_task

# ────────────────────────────────────────────────
# Constants
# ────────────────────────────────────────────────
STATUSES = {
    "todo": "📝 To Do",
    "in_progress": "⚡ In Progress",
    "done": "✅ Done"
}

ACTION_LABELS = {
    "todo":        ("Start ▶", "in_progress"),
    "in_progress": ("Complete ✓", "done"),
    "done":        ("Reopen ↺", "in_progress"),   # or "todo" if preferred
}

# ────────────────────────────────────────────────
# Page & DB setup
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
        background: #4a90e2;
        color: white;
        padding: 12px;
        border-radius: 6px;
        text-align: center;
        font-weight: bold;
        margin-bottom: 16px;
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
    .empty-hint {
        color: #6c757d;
        font-style: italic;
        text-align: center;
        padding: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# ────────────────────────────────────────────────
# Session state
# ────────────────────────────────────────────────
if "user_id" not in st.session_state:
    st.session_state.user_id = None

# ────────────────────────────────────────────────
# Login
# ────────────────────────────────────────────────
if st.session_state.user_id is None:
    st.title("Workflow")
    username = st.text_input("Username", placeholder="your name …", max_chars=60)
    if st.button("Login", type="primary") and (cleaned := username.strip()):
        st.session_state.user_id = cleaned
        st.rerun()
    st.stop()

# ────────────────────────────────────────────────
# Main interface
# ────────────────────────────────────────────────
user_id = st.session_state.user_id

# Header + logout
c1, c2 = st.columns([8, 1])
with c1:
    st.title(f"Workflow  —  {user_id}")
with c2:
    if st.button("Logout"):
        st.session_state.user_id = None
        st.rerun()

st.divider()

# ── Add task form ────────────────────────────────────
with st.form(key="add_task", clear_on_submit=True):
    st.subheader("Add New Task")
    col_input, col_btn = st.columns([5, 2])
    with col_input:
        task_input = st.text_input(
            "Task",
            placeholder="What needs to be done? …",
            label_visibility="collapsed"
        )
    with col_btn:
        submitted = st.form_submit_button(
            "➕ Add",
            type="primary",
            use_container_width=True,
            disabled=not task_input.strip()
        )

# Handle submission **outside** the form context → fixes disappearing value issue
if submitted and (cleaned_task := task_input.strip()):
    add_task(cleaned_task, user_id)
    st.success(f"Added **{cleaned_task}**", icon="✅")
    st.rerun()

st.divider()

# ── Kanban board ─────────────────────────────────────
st.subheader("Tasks")

columns = st.columns(3)

for idx, (status_key, header_text) in enumerate(STATUSES.items()):
    with columns[idx]:
        st.markdown(f'<div class="column-header">{header_text}</div>', unsafe_allow_html=True)

        tasks = get_tasks(status_key, user_id)

        if not tasks:
            st.markdown('<div class="empty-hint">— nothing here yet —</div>', unsafe_allow_html=True)
            continue

        for task_id, title in tasks:
            st.markdown(f'<div class="task-card">{title}</div>', unsafe_allow_html=True)

            btn1, btn2 = st.columns(2)

            with btn1:
                label, next_status = ACTION_LABELS[status_key]
                if st.button(label, key=f"action_{status_key}_{task_id}", use_container_width=True):
                    update_status(task_id, next_status)
                    st.rerun()

            with btn2:
                if st.button("🗑 Delete", key=f"delete_{task_id}", use_container_width=True):
                    delete_task(task_id)
                    st.rerun()

st.markdown("<br>", unsafe_allow_html=True)