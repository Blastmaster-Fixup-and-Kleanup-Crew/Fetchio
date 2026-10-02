from __future__ import annotations

import asyncio
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser


class RobotsManager:
    """Manages robots.txt caching and lookup."""

    def __init__(self, user_agent: str = "FetchioBot") -> None:
        self.user_agent = user_agent
        self.robots_cache: dict[str, RobotFileParser] = {}
        self.lock = asyncio.Lock()

    async def can_fetch(self, url: str) -> bool:
        """Check if URL can be fetched per robots.txt."""
        parsed = urlparse(url)
        base = f"{parsed.scheme}://{parsed.netloc}"

        async with self.lock:
            if base not in self.robots_cache:
                robot = RobotFileParser()
                robot.set_url(f"{base}/robots.txt")
                try:
                    robot.read()
                except Exception:
                    # If robots.txt doesn't exist or fails, allow access
                    robot = RobotFileParser()
                self.robots_cache[base] = robot

        return self.robots_cache[base].can_fetch(self.user_agent, url)
