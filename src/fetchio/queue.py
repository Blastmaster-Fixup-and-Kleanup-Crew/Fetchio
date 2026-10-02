from __future__ import annotations

import asyncio
from collections import deque
from urllib.parse import urlparse


class CrawlQueue:
    """URL queue with deduplication and rate limiting."""

    def __init__(self, max_size: int = 10000) -> None:
        self.queue: deque[str] = deque()
        self.seen: set[str] = set()
        self.max_size = max_size
        self.lock = asyncio.Lock()

    async def add(self, url: str) -> bool:
        """Add URL to queue if not seen. Returns True if added."""
        normalized = self._normalize(url)
        async with self.lock:
            if normalized in self.seen or len(self.queue) >= self.max_size:
                return False
            self.seen.add(normalized)
            self.queue.append(normalized)
            return True

    async def add_many(self, urls: list[str]) -> int:
        """Add multiple URLs. Returns count added."""
        count = 0
        for url in urls:
            if await self.add(url):
                count += 1
        return count

    async def get(self) -> str | None:
        """Get next URL from queue."""
        async with self.lock:
            return self.queue.popleft() if self.queue else None

    async def size(self) -> int:
        """Get queue size."""
        async with self.lock:
            return len(self.queue)

    async def seen_count(self) -> int:
        """Get count of seen URLs."""
        async with self.lock:
            return len(self.seen)

    @staticmethod
    def _normalize(url: str) -> str:
        """Normalize URL for deduplication."""
        parsed = urlparse(url.lower())
        scheme = parsed.scheme or "https"
        netloc = parsed.netloc
        path = parsed.path.rstrip("/")
        return f"{scheme}://{netloc}{path}"
