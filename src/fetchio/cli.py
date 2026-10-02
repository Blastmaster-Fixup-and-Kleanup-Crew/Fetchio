from __future__ import annotations

from pathlib import Path

from .indexer import SearchIndex


def load_index(data_path: str | Path) -> SearchIndex:
    return SearchIndex.from_file(str(data_path))


def search(data_path: str | Path, query: str, limit: int = 10) -> list[tuple[str, float]]:
    index = load_index(data_path)
    return index.search(query, limit=limit)
