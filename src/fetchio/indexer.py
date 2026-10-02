from __future__ import annotations

import asyncio
import json
import re
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from .config import FetchioConfig
from .models import CrawlDocument


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
    return re.sub(r"\s+", " ", text)


def extract_title(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    title_tag = soup.title
    if title_tag is None:
        return ""
    return title_tag.get_text(" ", strip=True)


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
    return links


async def fetch_page(session, url: str, headers: dict[str, str]) -> str:
    async with session.get(url, headers=headers, timeout=20) as response:
        response.raise_for_status()
        return await response.text()


async def crawl_site(config: FetchioConfig) -> list[CrawlDocument]:
    seen: set[str] = set()
    queue: asyncio.Queue[str] = asyncio.Queue()
    documents: list[CrawlDocument] = []

    for start_url in config.start_urls:
        queue.put_nowait(start_url)

    headers = {"User-Agent": config.user_agent}
    semaphore = asyncio.Semaphore(4)

    async def worker() -> None:
        while True:
            try:
                url = queue.get_nowait()
            except asyncio.QueueEmpty:
                return

            if url in seen:
                queue.task_done()
                continue

            seen.add(url)
            try:
                async with semaphore:
                    async with __import__("aiohttp").ClientSession() as session:
                        html = await fetch_page(session, url, headers)
            except Exception:
                queue.task_done()
                continue

            title = extract_title(html)
            text = extract_text(html)
            links = extract_links(html, url)

            doc = CrawlDocument(url=url, title=title, text=text, links=links, score=1.0)
            documents.append(doc)

            for link in links:
                parsed = urlparse(link)
                host = parsed.netloc.lower()
                if host and not any(host.endswith(domain.lower()) for domain in config.allowed_domains):
                    continue
                if link not in seen and len(documents) < config.max_pages:
                    queue.put_nowait(link)

            queue.task_done()

    workers = [asyncio.create_task(worker()) for _ in range(4)]
    await queue.join()
    for task in workers:
        task.cancel()
    await asyncio.gather(*workers, return_exceptions=True)

    return documents


def save_documents(documents: list[CrawlDocument], output_path: str) -> None:
    output = [doc.to_dict() for doc in documents]
    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(output, handle, indent=2, ensure_ascii=False)
