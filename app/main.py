"""Tasks CRUD API — BE-02: SQLite-backed (migrated from the in-memory baseline).

Endpoint behavior is identical to the A1 baseline; only the storage changed.
Every CRUD operation below goes through real SQL against data/tasks.db.

Error contract:
- unknown id          -> 404 {"error": "Task not found"}
- POST without title  -> 400 {"error": "title is required"}
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .db import get_conn, init_db, row_to_task
from .schemas import Task, TaskUpdate


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()  # create schema + seed (first run only)
    yield


app = FastAPI(title="Tasks API (SQLite)", lifespan=lifespan)


@app.get("/tasks", response_model=list[Task])
def list_tasks():
    conn = get_conn()
    try:
        rows = conn.execute("SELECT id, title, done FROM tasks ORDER BY id").fetchall()
        return [row_to_task(r) for r in rows]
    finally:
        conn.close()


@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int):
    conn = get_conn()
    try:
        row = conn.execute(
            "SELECT id, title, done FROM tasks WHERE id = ?", (task_id,)
        ).fetchone()
    finally:
        conn.close()
    if row is None:
        return JSONResponse(status_code=404, content={"error": "Task not found"})
    return row_to_task(row)


@app.post("/tasks", status_code=201)
async def create_task(request: Request):
    try:
        body = await request.json()
    except Exception:
        body = {}
    title = body.get("title") if isinstance(body, dict) else None
    if not title or not str(title).strip():
        return JSONResponse(status_code=400, content={"error": "title is required"})
    conn = get_conn()
    try:
        cur = conn.execute(
            "INSERT INTO tasks (title, done) VALUES (?, 0)", (str(title).strip(),)
        )
        conn.commit()
        task_id = cur.lastrowid
        row = conn.execute(
            "SELECT id, title, done FROM tasks WHERE id = ?", (task_id,)
        ).fetchone()
        return row_to_task(row)
    finally:
        conn.close()


@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, payload: TaskUpdate):
    conn = get_conn()
    try:
        row = conn.execute(
            "SELECT id, title, done FROM tasks WHERE id = ?", (task_id,)
        ).fetchone()
        if row is None:
            return JSONResponse(status_code=404, content={"error": "Task not found"})
        title = payload.title if payload.title is not None else row["title"]
        done = int(payload.done) if payload.done is not None else row["done"]
        conn.execute(
            "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
            (title, done, task_id),
        )
        conn.commit()
        updated = conn.execute(
            "SELECT id, title, done FROM tasks WHERE id = ?", (task_id,)
        ).fetchone()
        return row_to_task(updated)
    finally:
        conn.close()


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    conn = get_conn()
    try:
        cur = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        if cur.rowcount == 0:
            return JSONResponse(status_code=404, content={"error": "Task not found"})
        return JSONResponse(status_code=204, content=None)
    finally:
        conn.close()
