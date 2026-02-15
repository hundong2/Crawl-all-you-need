from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import uuid
import os
from .crawler import crawler
from .llm_service import llm_service

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for results (replace with database for production)
results = {}

class CrawlRequest(BaseModel):
    url: str
    recursive: bool = False
    max_pages: int = 10
    enhance: bool = False

class LLMRequest(BaseModel):
    content_id: str
    provider: str
    model: str
    instruction: str

class ProcessedResponse(BaseModel):
    id: str
    content: str

@app.get("/")
async def root():
    return {"message": "Documentation Crawler API is running"}

@app.post("/crawl")
async def crawl_endpoint(request: CrawlRequest):
    try:
        content = await crawler.crawl_site(request.url, request.recursive, request.max_pages, request.enhance)
        content_id = str(uuid.uuid4())
        results[content_id] = {"original": content, "processed": None}
        return {"id": content_id, "content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process")
async def process_endpoint(request: LLMRequest):
    if request.content_id not in results:
        raise HTTPException(status_code=404, detail="Content not found")
    
    original_content = results[request.content_id]["original"]
    
    try:
        processed_content = await llm_service.process_content(
            request.provider, 
            request.model, 
            original_content, 
            request.instruction
        )
        results[request.content_id]["processed"] = processed_content
        return {"id": request.content_id, "content": processed_content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/models")
async def get_models():
    return {
        "google": ["gemini-flash-latest", "gemini-pro-latest", "gemini-2.0-flash", "gemini-2.5-flash", "gemini-2.5-pro"],
        "anthropic": ["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"],
        "openai": ["gpt-4-turbo", "gpt-4o", "gpt-3.5-turbo"]
    }

@app.get("/download/{content_id}")
async def download_content(content_id: str, type: str = "processed"):
    if content_id not in results:
        raise HTTPException(status_code=404, detail="Content not found")
    
    content = results[content_id].get(type)
    if not content:
        # Fallback to original if processed is requested but not available
        if type == "processed":
             content = results[content_id].get("original")

    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    return {"content": content, "filename": f"doc_{content_id}.md"}
