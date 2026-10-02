from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """FastAPI application settings."""
    database_url: str = "sqlite+aiosqlite:///./data/fetchio.db"
    crawl_delay: float = 1.0
    request_timeout: int = 20
    max_concurrent_requests: int = 4
    max_pages_per_crawl: int = 1000
    user_agent: str = "FetchioBot/0.2 (+https://github.com/Blastmaster-Fixup-and-Kleanup-Crew/Fetchio)"
    data_dir: Path = Path("data")
    log_level: str = "INFO"

    class Config:
        env_file = ".env"


@dataclass
class FetchioConfig:
    start_urls: list[str] = field(default_factory=lambda: ["https://example.com"])
    allowed_domains: list[str] = field(default_factory=lambda: ["example.com"])
    max_pages: int = 50
    respect_robots: bool = True
    user_agent: str = "FetchioBot/0.2 (+https://github.com/Blastmaster-Fixup-and-Kleanup-Crew/Fetchio)"
    output_dir: Path = Path("data")

    def as_dict(self) -> dict[str, object]:
        return {
            "start_urls": self.start_urls,
            "allowed_domains": self.allowed_domains,
            "max_pages": self.max_pages,
            "respect_robots": self.respect_robots,
            "user_agent": self.user_agent,
            "output_dir": str(self.output_dir),
        }


def default_config() -> FetchioConfig:
    return FetchioConfig()
