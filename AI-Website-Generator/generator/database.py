
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

DB_PATH = DATA_DIR / "generator.db"


def get_connection():
    connection = sqlite3.connect(DB_PATH, timeout=10)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS generation_jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reference_url TEXT NOT NULL,
                requirement TEXT NOT NULL,
                project_name TEXT NOT NULL,
                output_path TEXT,
                status TEXT NOT NULL DEFAULT 'pending',
                error_message TEXT,
                created_at TEXT NOT NULL
            )
        """)
        connection.commit()


def create_job(reference_url, requirement, project_name):
    created_at = datetime.now(timezone.utc).isoformat()

    with get_connection() as connection:
        cursor = connection.execute("""
            INSERT INTO generation_jobs (
                reference_url,
                requirement,
                project_name,
                status,
                created_at
            )
            VALUES (?, ?, ?, 'pending', ?)
        """, (reference_url, requirement, project_name, created_at))

        connection.commit()
        return cursor.lastrowid


def update_job(job_id, status, output_path=None, error_message=None):
    with get_connection() as connection:
        connection.execute("""
            UPDATE generation_jobs
            SET status = ?,
                output_path = ?,
                error_message = ?
            WHERE id = ?
        """, (status, output_path, error_message, job_id))
        connection.commit()


def get_jobs():
    with get_connection() as connection:
        rows = connection.execute("""
            SELECT *
            FROM generation_jobs
            ORDER BY id DESC
        """).fetchall()

        return [dict(row) for row in rows]


def get_job(job_id):
    with get_connection() as connection:
        row = connection.execute("""
            SELECT *
            FROM generation_jobs
            WHERE id = ?
        """, (job_id,)).fetchone()

        return dict(row) if row else None
