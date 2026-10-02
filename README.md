# Tasks CRUD API — SQLite edition (FlyRank BE-02)

A tasks CRUD API migrated from in-memory storage (A1 baseline, kept as the
first commit) to **SQLite**. Endpoint behavior is unchanged — only the
storage layer moved to real SQL.

## Why SQLite

- **Zero-config:** a single file, no server to install or keep running —
  right-sized for a single-service assignment.
- **Real SQL:** every CRUD operation goes through actual `SELECT` / `INSERT` /
  `UPDATE` / `DELETE` statements, which is the point of BE-02.
- **Honest limits:** SQLite allows one writer at a time and lives on one disk.
  For a multi-instance service I'd move to Postgres (that's BE-04) — here it
  would be machinery I don't need.

## Database file

`data/tasks.db` (overridable with the `TASKS_DB` env var). The file is
gitignored — it's created automatically on first startup via
`CREATE TABLE IF NOT EXISTS`, and 3 sample tasks are seeded **only when the
table is empty**, so restarts never duplicate them.

## Run it

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/seed.py   # optional: seeds 3 sample tasks (idempotent)
.venv/bin/uvicorn app.main:app --port 8123
```

Then: `GET /tasks`, `GET /tasks/{id}`, `POST /tasks`, `PUT /tasks/{id}`,
`DELETE /tasks/{id}`. Interactive docs at `/docs`.

Error contract: unknown id → `404 {"error": "Task not found"}`;
`POST` without a title → `400 {"error": "title is required"}`.

## Viewing the database

Any SQLite viewer works; here is a real `sqlite3` session against the live
file:

```
$ sqlite3 data/tasks.db "SELECT id, title, done FROM tasks ORDER BY id;"
1|Buy groceries|0
2|Finish FlyRank BE-02|0
3|Read a book|1
```

## Sample SQL (hand-written, as practiced)

```sql
-- how many tasks are done?
SELECT COUNT(*) AS total,
       SUM(done) AS done_count
FROM tasks;

-- titles of completed tasks
SELECT title FROM tasks WHERE done = 1;

-- mark a task done
UPDATE tasks SET done = 1 WHERE id = 2;

-- remove a task
DELETE FROM tasks WHERE id = 3;
```

## Verified

- All endpoints return the same shapes/statuses as the A1 baseline
  (201 on create, 204 on delete, 404/400 error contract above).
- Killed and restarted the server: the 3 seeded tasks survived, no
  duplicates — persistence proven, seed proven idempotent.
