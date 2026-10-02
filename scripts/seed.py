#!/usr/bin/env python3
"""Seed the tasks database. Idempotent: init_db() only inserts sample tasks
when the table is empty, so running this twice never duplicates data."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import DB_PATH, get_conn, init_db  # noqa: E402


def main() -> None:
    init_db()
    conn = get_conn()
    try:
        n = conn.execute("SELECT COUNT(*) AS n FROM tasks").fetchone()["n"]
    finally:
        conn.close()
    print(f"seeded OK: {n} task(s) in {DB_PATH}")


if __name__ == "__main__":
    main()
