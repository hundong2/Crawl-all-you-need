from __future__ import annotations

import sqlite3
from pathlib import Path
from threading import Lock

from sitebooker.schemas import BuildResponse, JobStatusResponse


class JobStore:
    def __init__(self, db_path: str):
        self._db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS jobs (
                  job_id TEXT PRIMARY KEY,
                  status TEXT NOT NULL,
                  progress INTEGER NOT NULL,
                  detail TEXT NOT NULL,
                  result_json TEXT,
                  error TEXT,
                  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    def create_job(self, job_id: str) -> None:
        with self._lock:
            with self._connect() as conn:
                conn.execute(
                    """
                    INSERT INTO jobs(job_id, status, progress, detail)
                    VALUES(?, 'queued', 0, 'Queued')
                    """,
                    (job_id,),
                )

    def update_job(
        self,
        job_id: str,
        status: str,
        progress: int,
        detail: str,
        result: BuildResponse | None = None,
        error: str | None = None,
    ) -> None:
        result_json = result.model_dump_json() if result else None
        with self._lock:
            with self._connect() as conn:
                conn.execute(
                    """
                    UPDATE jobs
                    SET status = ?, progress = ?, detail = ?, result_json = ?, error = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE job_id = ?
                    """,
                    (status, progress, detail, result_json, error, job_id),
                )

    def get_job(self, job_id: str) -> JobStatusResponse | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT job_id, status, progress, detail, result_json, error FROM jobs WHERE job_id = ?",
                (job_id,),
            ).fetchone()
        if row is None:
            return None

        result = BuildResponse.model_validate_json(row["result_json"]) if row["result_json"] else None
        return JobStatusResponse(
            job_id=row["job_id"],
            status=row["status"],
            progress=row["progress"],
            detail=row["detail"],
            result=result,
            error=row["error"],
        )

    def list_jobs(self, limit: int = 20) -> list[JobStatusResponse]:
        limit = max(1, min(100, limit))
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT job_id, status, progress, detail, result_json, error
                FROM jobs
                ORDER BY updated_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        items: list[JobStatusResponse] = []
        for row in rows:
            result = BuildResponse.model_validate_json(row["result_json"]) if row["result_json"] else None
            items.append(
                JobStatusResponse(
                    job_id=row["job_id"],
                    status=row["status"],
                    progress=row["progress"],
                    detail=row["detail"],
                    result=result,
                    error=row["error"],
                )
            )
        return items
