from __future__ import annotations

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from .config import Settings
from .crawler import Crawler
from .indexer import SearchIndex
from .models import CrawlDocument, CrawlJob


class CrawlRequest(BaseModel):
    start_urls: list[str]
    allowed_domains: list[str]
    max_pages: int = 50


class CrawlResponse(BaseModel):
    id: str
    status: str
    pages_crawled: int
    errors: int


class SearchRequest(BaseModel):
    query: str
    limit: int = 10


class SearchResult(BaseModel):
    url: str
    title: str
    score: float
    snippet: str


def create_app() -> FastAPI:
    settings = Settings()
    crawler = Crawler(settings)
    search_index = SearchIndex()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        yield

    app = FastAPI(title="Fetchio", version="0.2.0", lifespan=lifespan)

    @app.get("/api/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/api/crawl")
    async def start_crawl(request: CrawlRequest) -> CrawlResponse:
        job_id = await crawler.start_crawl(
            request.start_urls,
            request.allowed_domains,
            request.max_pages,
        )
        job = crawler.get_job(job_id)
        return CrawlResponse(
            id=job.id,
            status=job.status.value,
            pages_crawled=job.pages_crawled,
            errors=job.errors,
        )

    @app.get("/api/crawl/{job_id}")
    async def get_crawl_status(job_id: str) -> CrawlResponse:
        job = crawler.get_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        return CrawlResponse(
            id=job.id,
            status=job.status.value,
            pages_crawled=job.pages_crawled,
            errors=job.errors,
        )

    @app.get("/api/crawls")
    async def list_crawls() -> list[CrawlResponse]:
        jobs = crawler.get_all_jobs()
        return [
            CrawlResponse(
                id=job.id,
                status=job.status.value,
                pages_crawled=job.pages_crawled,
                errors=job.errors,
            )
            for job in jobs
        ]

    @app.post("/api/search")
    async def search(request: SearchRequest) -> list[SearchResult]:
        results = search_index.search(request.query, request.limit)
        return [
            SearchResult(
                url=url,
                title=search_index.documents[url].title,
                score=score,
                snippet=search_index.documents[url].text[:150] + "...",
            )
            for url, score in results
        ]

    # Serve frontend
    app.mount("/static", StaticFiles(directory="static"), name="static")

    @app.get("/")
    async def root() -> FileResponse:
        return FileResponse("static/index.html")

    return app


if __name__ == "__main__":
    import uvicorn
    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)
