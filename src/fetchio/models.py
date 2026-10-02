from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class CrawlDocument:
    url: str
    title: str = ""
    text: str = ""
    links: list[str] = field(default_factory=list)
    score: float = 0.0

    def to_dict(self) -> dict[str, object]:
        return {
            "url": self.url,
            "title": self.title,
            "text": self.text,
            "links": self.links,
            "score": self.score,
        }
