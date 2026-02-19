import sqlite3
from datetime import datetime
import streamlit as st

DB_NAME = "kanban.db"

@st.cache_resource
def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            status TEXT NOT NULL,
            user_id TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()

def add_task(title, user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tasks (title, status, user_id, created_at)
        VALUES (?, ?, ?, ?)
    """, (title, "todo", user_id, datetime.now().isoformat()))
    conn.commit()

def get_tasks(status, user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, title FROM tasks
        WHERE status = ? AND user_id = ?
        ORDER BY created_at DESC
    """, (status, user_id))
    return cursor.fetchall()

def update_status(task_id, new_status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE tasks SET status = ? WHERE id = ?
    """, (new_status, task_id))
    conn.commit()

def delete_task(task_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM tasks WHERE id = ?
    """, (task_id,))
    conn.commit()
