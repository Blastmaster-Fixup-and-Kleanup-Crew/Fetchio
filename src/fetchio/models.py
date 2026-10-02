from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class CrawlStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"


class DocumentStatus(str, Enum):
    NEW = "new"
    CRAWLED = "crawled"
    INDEXED = "indexed"
    ERROR = "error"


@dataclass
class CrawlDocument:
    url: str
    title: str = ""
    text: str = ""
    links: list[str] = field(default_factory=list)
    score: float = 0.0
    status: DocumentStatus = DocumentStatus.NEW
    crawl_id: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, object]:
        return {
            "url": self.url,
            "title": self.title,
            "text": self.text,
            "links": self.links,
            "score": self.score,
            "status": self.status.value,
            "crawl_id": self.crawl_id,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class CrawlJob:
    id: str
    start_urls: list[str]
    allowed_domains: list[str]
    max_pages: int
    status: CrawlStatus = CrawlStatus.PENDING
    pages_crawled: int = 0
    errors: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "start_urls": self.start_urls,
            "allowed_domains": self.allowed_domains,
            "max_pages": self.max_pages,
            "status": self.status.value,
            "pages_crawled": self.pages_crawled,
            "errors": self.errors,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
