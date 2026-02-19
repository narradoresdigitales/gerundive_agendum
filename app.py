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

ACTIONS = {
    "todo":        {"label": "Start ▶", "next": "in_progress"},
    "in_progress": {"label": "Complete ✓", "next": "done"},
    "done":        {"label": "Reopen ↺", "next": "in_progress"},  # ← change to "todo" if preferred
}

# ────────────────────────────────────────────────
# Setup
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
# Session state init
# ────────────────────────────────────────────────
if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "new_task_text" not in st.session_state:
    st.session_state.new_task_text = ""

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
# Main app
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

# ── Add task (non-form style – most reliable in many cases) ────────
st.subheader("Add New Task")

col_input, col_btn = st.columns([5, 2])

with col_input:
    st.session_state.new_task_text = st.text_input(
        "Task description",
        value=st.session_state.new_task_text,
        placeholder="What needs to be done? …",
        label_visibility="collapsed",
        key="add_task_input"
    )

with col_btn:
    if st.button(
        "➕ Add",
        type="primary",
        use_container_width=True,
        disabled=not st.session_state.new_task_text.strip()
    ):
        cleaned = st.session_state.new_task_text.strip()
        try:
            add_task(cleaned, user_id)
            st.success(f"Added: **{cleaned}**", icon="✅")
            st.session_state.new_task_text = ""           # clear input
            st.rerun()
        except Exception as e:
            st.error(f"Error adding task: {e}")

st.divider()

# ── Kanban board ─────────────────────────────────────
st.subheader("Tasks")

cols = st.columns(3)

for i, (status_key, display_name) in enumerate(STATUSES.items()):
    with cols[i]:
        st.markdown(f'<div class="column-header">{display_name}</div>', unsafe_allow_html=True)

        tasks = get_tasks(status_key, user_id)

        if not tasks:
            st.markdown('<div class="empty-hint">— nothing here yet —</div>', unsafe_allow_html=True)
            continue

        for task_id, title in tasks:
            st.markdown(f'<div class="task-card">{title}</div>', unsafe_allow_html=True)

            b1, b2 = st.columns(2)

            with b1:
                action = ACTIONS[status_key]
                if st.button(
                    action["label"],
                    key=f"act_{status_key}_{task_id}",
                    use_container_width=True
                ):
                    try:
                        update_status(task_id, action["next"])
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error updating status: {e}")

            with b2:
                if st.button(
                    "🗑 Delete",
                    key=f"del_{task_id}",
                    use_container_width=True
                ):
                    try:
                        delete_task(task_id)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error deleting task: {e}")

st.markdown("<br><br>", unsafe_allow_html=True)