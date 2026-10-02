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
        self.term_frequencies: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    def add_document(self, document: CrawlDocument) -> None:
        self.documents[document.url] = document
        terms = tokenize(document.title + " " + document.text)
        for term in terms:
            self.index[term].add(document.url)
            self.term_frequencies[term][document.url] += 1

    def search(self, query: str, limit: int = 20) -> list[tuple[str, float]]:
        query_terms = tokenize(query)
        if not query_terms:
            return []

        results: dict[str, float] = defaultdict(float)
        total_docs = len(self.documents)

        for term in query_terms:
            docs = self.index.get(term, set())
            idf = math.log(total_docs / len(docs)) if docs else 0

            for url in docs:
                tf = self.term_frequencies[term][url]
                results[url] += (1 + math.log(tf)) * idf

        ranked = sorted(results.items(), key=lambda item: item[1], reverse=True)
        return ranked[:limit]

    @classmethod
    def from_file(cls, path: str) -> "SearchIndex":
        index = cls()
        try:
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
        except FileNotFoundError:
            pass
        return index
