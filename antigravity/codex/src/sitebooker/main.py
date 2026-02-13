from __future__ import annotations

from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse

from sitebooker.config.env_loader import load_environment, load_runtime_settings, load_secrets
from sitebooker.schemas import (
    BuildRequest,
    BuildResponse,
    JobCreateResponse,
    JobListResponse,
    JobStatusResponse,
    ModelsResponse,
    Provider,
)
from sitebooker.services.book_builder import build_book
from sitebooker.services.job_queue import JobQueue
from sitebooker.services.job_store import JobStore
from sitebooker.services.provider_catalog import get_models

load_environment()
SECRETS = load_secrets()
ROOT_DIR = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT_DIR / "outputs"
WEB_DIR = Path(__file__).resolve().parent / "web"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
JOB_STORE = JobStore(db_path=str(OUTPUT_DIR / "sitebooker.db"))
JOB_QUEUE = JobQueue(output_dir=str(OUTPUT_DIR), secrets=SECRETS, store=JOB_STORE)

app = FastAPI(title="SiteBooker")


@app.get("/")
def index() -> FileResponse:
    return FileResponse(WEB_DIR / "index.html")


@app.get("/api/models/{provider}", response_model=ModelsResponse)
def list_models(provider: Provider) -> ModelsResponse:
    return ModelsResponse(provider=provider, models=get_models(provider))


@app.post("/api/build", response_model=BuildResponse)
async def api_build(payload: BuildRequest) -> BuildResponse:
    result = await build_book(payload, str(OUTPUT_DIR), SECRETS)
    return BuildResponse(**result)


@app.post("/api/build/jobs", response_model=JobCreateResponse)
async def create_build_job(payload: BuildRequest) -> JobCreateResponse:
    job = JOB_QUEUE.create_job(payload)
    return JobCreateResponse(job_id=job.job_id, status=job.status.value)


@app.get("/api/build/jobs/{job_id}", response_model=JobStatusResponse)
def get_build_job(job_id: str) -> JobStatusResponse:
    response = JOB_QUEUE.as_response(job_id)
    if response is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return response


@app.get("/api/build/jobs", response_model=JobListResponse)
def list_build_jobs(limit: int = Query(default=20, ge=1, le=100)) -> JobListResponse:
    return JobListResponse(jobs=JOB_QUEUE.list_jobs(limit=limit))


@app.get("/api/build/jobs/{job_id}/files")
def list_build_job_files(job_id: str) -> dict[str, object]:
    response = JOB_QUEUE.as_response(job_id)
    if response is None or response.result is None:
        raise HTTPException(status_code=404, detail="Completed job not found")
    output_path = Path(response.result.output_path)
    run_folder = output_path.parent
    files = sorted([p.name for p in run_folder.iterdir() if p.is_file()])
    return {"job_id": job_id, "files": files}


@app.get("/api/build/jobs/{job_id}/download/{filename}")
def download_build_job_file(job_id: str, filename: str) -> FileResponse:
    response = JOB_QUEUE.as_response(job_id)
    if response is None or response.result is None:
        raise HTTPException(status_code=404, detail="Completed job not found")
    output_path = Path(response.result.output_path)
    run_folder = output_path.parent
    target = (run_folder / filename).resolve()
    if target.parent != run_folder.resolve() or not target.exists() or not target.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(target)


def run() -> None:
    host, port = load_runtime_settings()
    uvicorn.run("sitebooker.main:app", host=host, port=port, reload=False)


if __name__ == "__main__":
    run()
