import asyncio
from pathlib import Path

import pytest

from sitebooker.config.env_loader import AppSecrets
from sitebooker.schemas import BuildRequest
from sitebooker.services import job_queue
from sitebooker.services.job_store import JobStore


@pytest.mark.asyncio
async def test_job_queue_completes(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    async def fake_build_book(payload, output_dir, secrets, on_progress=None):
        if on_progress:
            on_progress(30, "stage-1")
        await asyncio.sleep(0)
        return {
            "run_id": "r1",
            "output_path": str(tmp_path / "book.md"),
            "manifest_path": str(tmp_path / "manifest.json"),
            "pages_collected": 2,
            "failures": [],
            "output_files": ["book.md"],
        }

    monkeypatch.setattr(job_queue, "build_book", fake_build_book)

    store = JobStore(db_path=str(tmp_path / "jobs.db"))
    queue = job_queue.JobQueue(output_dir=str(tmp_path), secrets=AppSecrets(None, None, None), store=store)
    payload = BuildRequest(
        provider="openai",
        model="gpt-4.1-mini",
        root_url="https://example.com/docs",
    )
    job = queue.create_job(payload)
    await job.task

    snapshot = queue.as_response(job.job_id)
    assert snapshot is not None
    assert snapshot.status == "completed"
    assert snapshot.progress == 100
    assert snapshot.result is not None

    history = queue.list_jobs(limit=10)
    assert len(history) == 1
    assert history[0].job_id == job.job_id
