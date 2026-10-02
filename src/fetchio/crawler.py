from __future__ import annotations

import asyncio
import json
import re
import uuid
from urllib.parse import urljoin, urlparse
from datetime import datetime

import aiohttp
from bs4 import BeautifulSoup

from .config import Settings
from .models import CrawlDocument, CrawlJob, CrawlStatus, DocumentStatus
from .queue import CrawlQueue
from .robots import RobotsManager


def normalize_url(url: str, base_url: str) -> str:
    parsed = urlparse(url)
    if not parsed.scheme:
        return urljoin(base_url, url)
    return url


def extract_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    text = soup.get_text(" ", strip=True)
    return re.sub(r"\s+", " ", text)[:5000]  # Limit text


def extract_title(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    title_tag = soup.title
    if title_tag is None:
        return ""
    return title_tag.get_text(" ", strip=True)[:256]


def extract_links(html: str, base_url: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    links: list[str] = []
    for link in soup.find_all("a", href=True):
        href = link["href"]
        if href.startswith("javascript:") or href.startswith("mailto:"):
            continue
        absolute = normalize_url(href, base_url)
        if absolute:
            links.append(absolute)
    return links[:100]  # Limit links per page


async def fetch_page(session: aiohttp.ClientSession, url: str, headers: dict[str, str], timeout: int) -> str:
    """Fetch a single page."""
    try:
        async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=timeout), ssl=False) as response:
            if response.status == 200:
                return await response.text()
    except Exception:
        pass
    return ""


class Crawler:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.robots = RobotsManager(settings.user_agent)
        self.jobs: dict[str, CrawlJob] = {}

    async def start_crawl(self, start_urls: list[str], allowed_domains: list[str], max_pages: int) -> str:
        """Start a new crawl job."""
        job_id = str(uuid.uuid4())
        job = CrawlJob(
            id=job_id,
            start_urls=start_urls,
            allowed_domains=allowed_domains,
            max_pages=max_pages,
            status=CrawlStatus.ACTIVE,
        )
        self.jobs[job_id] = job
        asyncio.create_task(self._crawl_worker(job))
        return job_id

    async def _crawl_worker(self, job: CrawlJob) -> None:
        """Crawl worker task."""
        try:
            queue = CrawlQueue()
            await queue.add_many(job.start_urls)

            headers = {"User-Agent": self.settings.user_agent}
            connector = aiohttp.TCPConnector(limit_per_host=self.settings.max_concurrent_requests)
            timeout = aiohttp.ClientTimeout(total=self.settings.request_timeout)

            async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
                workers = [
                    asyncio.create_task(self._worker_task(session, job, queue, headers, allowed_domains))
                    for allowed_domains in [job.allowed_domains] * self.settings.max_concurrent_requests
                ]
                await asyncio.gather(*workers)

            job.status = CrawlStatus.COMPLETED
            job.completed_at = datetime.utcnow()
        except Exception as e:
            job.status = CrawlStatus.FAILED
            job.completed_at = datetime.utcnow()

    async def _worker_task(self, session: aiohttp.ClientSession, job: CrawlJob, queue: CrawlQueue, headers: dict[str, str], allowed_domains: list[str]) -> None:
        """Individual worker task."""
        while job.pages_crawled < job.max_pages:
            url = await queue.get()
            if not url:
                await asyncio.sleep(0.1)
                continue

            # Check robots.txt
            if self.settings.database_url and not await self.robots.can_fetch(url):
                continue

            # Check domain
            parsed = urlparse(url)
            host = parsed.netloc.lower()
            if not any(host.endswith(domain.lower()) for domain in allowed_domains):
                continue

            # Fetch page
            html = await fetch_page(session, url, headers, self.settings.request_timeout)
            if not html:
                job.errors += 1
                continue

            # Parse and store
            title = extract_title(html)
            text = extract_text(html)
            links = extract_links(html, url)

            doc = CrawlDocument(
                url=url,
                title=title,
                text=text,
                links=links,
                score=1.0,
                status=DocumentStatus.CRAWLED,
                crawl_id=job.id,
                created_at=datetime.utcnow(),
            )

            job.pages_crawled += 1

            # Add new links to queue
            for link in links:
                if job.pages_crawled < job.max_pages:
                    await queue.add(link)

            await asyncio.sleep(self.settings.crawl_delay)

    def get_job(self, job_id: str) -> CrawlJob | None:
        """Get job by ID."""
        return self.jobs.get(job_id)

    def get_all_jobs(self) -> list[CrawlJob]:
        """Get all jobs."""
        return list(self.jobs.values())
