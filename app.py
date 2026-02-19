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
    "done":        {"label": "Reopen ↺", "next": "in_progress"},  # change to "todo" if you prefer
}

PRIORITY_COLORS = {
    "high":   {"border": "#dc3545", "bg": "#f8d7da", "text": "#721c24", "label": "High 🚨"},
    "medium": {"border": "#0d6efd", "bg": "#d1e7ff", "text": "#084298", "label": "Medium"},
    "low":    {"border": "#ffc107", "bg": "#fff3cd", "text": "#664d03", "label": "Low"},
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
        font-size: 1.05rem;
        position: relative;
        overflow: hidden;
    }
    .task-card.high   { border-left: 5px solid #dc3545; background: #fff5f5; }
    .task-card.medium { border-left: 5px solid #0d6efd; background: #f0f8ff; }
    .task-card.low    { border-left: 5px solid #ffc107; background: #fffef0; }
    .priority-badge {
        font-size: 0.8rem;
        padding: 2px 8px;
        border-radius: 12px;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 6px;
    }
    .priority-high   { background: #dc3545; color: white; }
    .priority-medium { background: #0d6efd; color: white; }
    .priority-low    { background: #ffc107; color: #212529; }
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

if "new_task_text" not in st.session_state:
    st.session_state.new_task_text = ""

if "new_task_priority" not in st.session_state:
    st.session_state.new_task_priority = "medium"

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

# ── Add task ────────────────────────────────────────────────
st.subheader("Add New Task")

col_input, col_prio, col_btn = st.columns([4, 2, 2])

with col_input:
    st.session_state.new_task_text = st.text_input(
        "Task description",
        value=st.session_state.new_task_text,
        placeholder="What needs to be done? …",
        label_visibility="collapsed",
        key="add_task_input"
    )

with col_prio:
    st.session_state.new_task_priority = st.selectbox(
        "Priority",
        options=["high", "medium", "low"],
        format_func=lambda x: PRIORITY_COLORS[x]["label"],
        index=["high", "medium", "low"].index(st.session_state.new_task_priority),
        label_visibility="collapsed",
        key="add_task_priority"
    )

with col_btn:
    if st.button(
        "➕ Add",
        type="primary",
        use_container_width=True,
        disabled=not st.session_state.new_task_text.strip()
    ):
        cleaned = st.session_state.new_task_text.strip()
        prio = st.session_state.new_task_priority
        try:
            add_task(cleaned, user_id, priority=prio)  # ← assumes add_task accepts priority
            st.success(f"Added: **{cleaned}** ({PRIORITY_COLORS[prio]['label']})", icon="✅")
            st.session_state.new_task_text = ""
            st.session_state.new_task_priority = "medium"
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")

st.divider()

# ── Kanban board ─────────────────────────────────────
st.subheader("Tasks")

cols = st.columns(3)

for i, (status_key, display_name) in enumerate(STATUSES.items()):
    with cols[i]:
        st.markdown(f'<div class="column-header">{display_name}</div>', unsafe_allow_html=True)

        # Assuming get_tasks now returns (id, title, priority)
        tasks = get_tasks(status_key, user_id)

        if not tasks:
            st.markdown('<div class="empty-hint">— nothing here yet —</div>', unsafe_allow_html=True)
            continue

        for row in tasks:
            task_id, title, priority = row if len(row) == 3 else (row[0], row[1], "medium")  # fallback

            prio_style = PRIORITY_COLORS.get(priority, PRIORITY_COLORS["medium"])
            badge_class = f"priority-{priority}"

            st.markdown(
                f'''
                <div class="task-card {priority}">
                    <div class="priority-badge {badge_class}">{prio_style["label"]}</div>
                    {title}
                </div>
                ''',
                unsafe_allow_html=True
            )

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
                        st.error(f"Error: {e}")

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
                        st.error(f"Error: {e}")

st.markdown("<br><br>", unsafe_allow_html=True)