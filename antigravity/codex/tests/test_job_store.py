from pathlib import Path

from sitebooker.schemas import BuildResponse
from sitebooker.services.job_store import JobStore


def test_job_store_roundtrip(tmp_path: Path) -> None:
    store = JobStore(db_path=str(tmp_path / "jobs.db"))
    store.create_job("j1")
    store.update_job("j1", status="running", progress=55, detail="Working")

    status = store.get_job("j1")
    assert status is not None
    assert status.status == "running"
    assert status.progress == 55

    result = BuildResponse(
        run_id="r1",
        output_path="/tmp/book.md",
        manifest_path="/tmp/manifest.json",
        pages_collected=1,
        failures=[],
        output_files=["book.md"],
    )
    store.update_job("j1", status="completed", progress=100, detail="Done", result=result)

    listed = store.list_jobs(limit=5)
    assert len(listed) == 1
    assert listed[0].result is not None
    assert listed[0].result.output_files == ["book.md"]
