from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class FetchioConfig:
    start_urls: list[str] = field(
        default_factory=lambda: ["https://example.com"]
    )
    allowed_domains: list[str] = field(default_factory=lambda: ["example.com"])
    max_pages: int = 50
    respect_robots: bool = True
    user_agent: str = "FetchioBot/0.1 (+https://github.com/Blastmaster-Fixup-and-Kleanup-Crew/Fetchio)"
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
