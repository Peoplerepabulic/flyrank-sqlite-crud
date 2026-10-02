"""SQLite layer for the tasks API (BE-02).

- Database file lives at data/tasks.db (overridable via TASKS_DB).
- Schema is created automatically on startup (CREATE TABLE IF NOT EXISTS).
- Three sample tasks are inserted ONLY on first run (when the table is empty),
  so restarts never duplicate seed data.
"""
import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.environ.get("TASKS_DB", os.path.join(BASE_DIR, "data", "tasks.db"))

SCHEMA = """
CREATE TABLE IF NOT EXISTS tasks (
    id    INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    done  INTEGER NOT NULL DEFAULT 0
);
"""

SEED_TASKS = [
    ("Buy groceries", 0),
    ("Finish FlyRank BE-02", 0),
    ("Read a book", 1),
]


def get_conn() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create schema + seed sample data exactly once (first run only)."""
    conn = get_conn()
    try:
        conn.execute(SCHEMA)
        count = conn.execute("SELECT COUNT(*) AS n FROM tasks").fetchone()["n"]
        if count == 0:
            conn.executemany(
                "INSERT INTO tasks (title, done) VALUES (?, ?)", SEED_TASKS
            )
        conn.commit()
    finally:
        conn.close()


def row_to_task(row: sqlite3.Row) -> dict:
    return {"id": row["id"], "title": row["title"], "done": bool(row["done"])}
