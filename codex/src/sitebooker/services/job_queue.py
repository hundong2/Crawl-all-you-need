from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from enum import Enum
from uuid import uuid4

from sitebooker.config.env_loader import AppSecrets
from sitebooker.schemas import BuildRequest, BuildResponse, JobStatusResponse
from sitebooker.services.book_builder import build_book
from sitebooker.services.job_store import JobStore


class JobStatus(str, Enum):
    queued = "queued"
    running = "running"
    completed = "completed"
    failed = "failed"


@dataclass
class BuildJob:
    job_id: str
    status: JobStatus = JobStatus.queued
    progress: int = 0
    detail: str = "Queued"
    result: BuildResponse | None = None
    error: str | None = None
    task: asyncio.Task[None] | None = field(default=None, repr=False)


class JobQueue:
    def __init__(self, output_dir: str, secrets: AppSecrets, store: JobStore):
        self._output_dir = output_dir
        self._secrets = secrets
        self._store = store
        self._jobs: dict[str, BuildJob] = {}

    def create_job(self, payload: BuildRequest) -> BuildJob:
        job_id = str(uuid4())
        job = BuildJob(job_id=job_id)
        self._jobs[job_id] = job
        self._store.create_job(job_id)
        job.task = asyncio.create_task(self._run(job_id, payload))
        return job

    def get_job(self, job_id: str) -> BuildJob | None:
        return self._jobs.get(job_id)

    async def _run(self, job_id: str, payload: BuildRequest) -> None:
        job = self._jobs[job_id]
        try:
            job.status = JobStatus.running
            job.progress = 20
            job.detail = "Crawling and assembling content"
            self._store.update_job(job_id, job.status.value, job.progress, job.detail)

            def on_progress(progress: int, detail: str) -> None:
                job.progress = progress
                job.detail = detail
                self._store.update_job(job_id, job.status.value, progress, detail)

            raw_result = await build_book(payload, self._output_dir, self._secrets, on_progress=on_progress)

            job.progress = 95
            job.detail = "Finalizing artifacts"
            job.result = BuildResponse(**raw_result)
            job.status = JobStatus.completed
            job.progress = 100
            job.detail = "Completed"
            self._store.update_job(
                job_id,
                job.status.value,
                job.progress,
                job.detail,
                result=job.result,
            )
        except Exception as exc:
            job.status = JobStatus.failed
            job.progress = 100
            job.detail = "Failed"
            job.error = str(exc)
            self._store.update_job(
                job_id,
                job.status.value,
                job.progress,
                job.detail,
                error=job.error,
            )

    def as_response(self, job_id: str) -> JobStatusResponse | None:
        stored = self._store.get_job(job_id)
        if stored:
            return stored
        job = self.get_job(job_id)
        if not job:
            return None
        return JobStatusResponse(
            job_id=job.job_id,
            status=job.status.value,
            progress=job.progress,
            detail=job.detail,
            result=job.result,
            error=job.error,
        )

    def list_jobs(self, limit: int = 20) -> list[JobStatusResponse]:
        return self._store.list_jobs(limit=limit)
