from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field, HttpUrl


class Provider(str, Enum):
    openai = "openai"
    anthropic = "anthropic"
    google = "google"


class OutputFormat(str, Enum):
    md = "md"
    pdf = "pdf"
    epub = "epub"
    docx = "docx"


class BuildRequest(BaseModel):
    provider: Provider
    model: str = Field(min_length=2)
    root_url: HttpUrl
    output_formats: list[OutputFormat] = Field(default_factory=lambda: [OutputFormat.md])
    max_pages: int = Field(default=30, ge=1, le=300)
    max_depth: int = Field(default=2, ge=0, le=5)
    llm_refine: bool = False


class BuildResponse(BaseModel):
    run_id: str
    output_path: str
    manifest_path: str
    pages_collected: int
    failures: list[str]
    output_files: list[str] = Field(default_factory=list)


class ModelsResponse(BaseModel):
    provider: Provider
    models: list[str]


class JobCreateResponse(BaseModel):
    job_id: str
    status: str


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    progress: int
    detail: str
    result: BuildResponse | None = None
    error: str | None = None


class JobListResponse(BaseModel):
    jobs: list[JobStatusResponse]
