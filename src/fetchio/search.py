from __future__ import annotations

import json
import math
import re
from collections import defaultdict

from .models import CrawlDocument


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z0-9]+", text.lower())


class SearchIndex:
    def __init__(self) -> None:
        self.documents: dict[str, CrawlDocument] = {}
        self.index: dict[str, set[str]] = defaultdict(set)

    def add_document(self, document: CrawlDocument) -> None:
        self.documents[document.url] = document
        terms = set(tokenize(document.title + " " + document.text))
        for term in terms:
            self.index[term].add(document.url)

    def search(self, query: str, limit: int = 10) -> list[tuple[str, float]]:
        query_terms = tokenize(query)
        if not query_terms:
            return []

        results: dict[str, float] = defaultdict(float)
        for term in query_terms:
            for url in self.index.get(term, set()):
                document = self.documents[url]
                tf = len(tokenize(document.title + " " + document.text))
                score = 1.0 + (math.log1p(tf) if tf > 0 else 0.0)
                results[url] += score

        ranked = sorted(results.items(), key=lambda item: item[1], reverse=True)
        return ranked[:limit]

    @classmethod
    def from_file(cls, path: str) -> "SearchIndex":
        index = cls()
        with open(path, "r", encoding="utf-8") as handle:
            documents = json.load(handle)
        for item in documents:
            document = CrawlDocument(
                url=item.get("url", ""),
                title=item.get("title", ""),
                text=item.get("text", ""),
                links=item.get("links", []),
                score=item.get("score", 0.0),
            )
            index.add_document(document)
        return index
