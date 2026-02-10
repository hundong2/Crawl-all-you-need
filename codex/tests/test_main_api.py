import asyncio
import time
from pathlib import Path

from fastapi.testclient import TestClient

from sitebooker.config.env_loader import AppSecrets
from sitebooker.main import app
from sitebooker.schemas import BuildRequest
from sitebooker.services import job_queue
from sitebooker.services.job_store import JobStore


def test_create_build_job_endpoint_runs_in_event_loop(monkeypatch, tmp_path: Path) -> None:
    async def fake_build_book(payload, output_dir, secrets, on_progress=None):
        if on_progress:
            on_progress(35, "crawl")
        await asyncio.sleep(0)
        return {
            "run_id": "r-api",
            "output_path": str(tmp_path / "book.md"),
            "manifest_path": str(tmp_path / "manifest.json"),
            "pages_collected": 1,
            "failures": [],
            "output_files": ["book.md"],
        }

    monkeypatch.setattr(job_queue, "build_book", fake_build_book)

    store = JobStore(db_path=str(tmp_path / "jobs.db"))
    queue = job_queue.JobQueue(output_dir=str(tmp_path), secrets=AppSecrets(None, None, None), store=store)

    import sitebooker.main as main_module

    monkeypatch.setattr(main_module, "JOB_QUEUE", queue)

    payload = BuildRequest(
        provider="openai",
        model="gpt-4.1-mini",
        root_url="https://docs.github.com/en/copilot/how-tos/copilot-cli/install-copilot-cli",
    ).model_dump(mode="json")

    client = TestClient(app)
    response = client.post("/api/build/jobs", json=payload)
    assert response.status_code == 200

    job_id = response.json()["job_id"]

    deadline = time.time() + 3
    while time.time() < deadline:
        status = client.get(f"/api/build/jobs/{job_id}")
        assert status.status_code == 200
        body = status.json()
        if body["status"] == "completed":
            assert body["result"]["pages_collected"] == 1
            return
        time.sleep(0.05)

    raise AssertionError("Job did not complete in time")
