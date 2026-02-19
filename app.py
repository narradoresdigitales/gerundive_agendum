import streamlit as st
import json
import os

DATA_FILE = "data.json"

# -------------------------
# Utilities
# -------------------------

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"todo": [], "doing": [], "done": []}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def move_task(data, task, source, destination):
    data[source].remove(task)
    data[destination].append(task)
    save_data(data)

def delete_task(data, task, column):
    data[column].remove(task)
    save_data(data)

# -------------------------
# App UI
# -------------------------

st.title("My Kanban Board")

data = load_data()

# Add new task
st.subheader("Add Task")
new_task = st.text_input("Task name")

if st.button("Add"):
    if new_task.strip() != "":
        data["todo"].append(new_task.strip())
        save_data(data)
        st.rerun()

st.divider()

# Columns
col1, col2, col3 = st.columns(3)

# ---- TO DO ----
with col1:
    st.header("To Do")
    for task in data["todo"]:
        st.write(task)
        if st.button(f"➡ Move to Doing", key=f"todo_{task}"):
            move_task(data, task, "todo", "doing")
            st.rerun()
        if st.button(f"❌ Delete", key=f"del_todo_{task}"):
            delete_task(data, task, "todo")
            st.rerun()
        st.divider()

# ---- DOING ----
with col2:
    st.header("Doing")
    for task in data["doing"]:
        st.write(task)
        if st.button(f"➡ Move to Done", key=f"doing_{task}"):
            move_task(data, task, "doing", "done")
            st.rerun()
        if st.button(f"❌ Delete", key=f"del_doing_{task}"):
            delete_task(data, task, "doing")
            st.rerun()
        st.divider()

# ---- DONE ----
with col3:
    st.header("Done")
    for task in data["done"]:
        st.write(task)
        if st.button(f"⬅ Move to Doing", key=f"done_{task}"):
            move_task(data, task, "done", "doing")
            st.rerun()
        if st.button(f"❌ Delete", key=f"del_done_{task}"):
            delete_task(data, task, "done")
            st.rerun()
        st.divider()
