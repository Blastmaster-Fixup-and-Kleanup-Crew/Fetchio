from __future__ import annotations

import argparse
import asyncio
from pathlib import Path

from .config import FetchioConfig, default_config
from .crawler import crawl_site, save_documents
from .search import search


async def run_crawl(args: argparse.Namespace) -> None:
    config = FetchioConfig(
        start_urls=[args.start_url],
        allowed_domains=[args.allowed_domain] if args.allowed_domain else ["example.com"],
        max_pages=args.max_pages,
        user_agent=args.user_agent,
        output_dir=Path(args.output_dir),
    )
    documents = await crawl_site(config)
    output_path = Path(args.output_dir) / "crawl.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    save_documents(documents, str(output_path))
    print(f"Crawled {len(documents)} pages -> {output_path}")


def run_search(args: argparse.Namespace) -> None:
    data_path = Path(args.data_path)
    if not data_path.exists():
        raise FileNotFoundError(f"No crawl data found at {data_path}")
    results = search(data_path, args.query, limit=args.limit)
    if not results:
        print("No matches found.")
        return
    for url, score in results:
        print(f"{score:.2f} | {url}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Fetchio CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    crawl_parser = subparsers.add_parser("crawl", help="crawl a website")
    crawl_parser.add_argument("--start-url", required=True, help="The starting page to crawl")
    crawl_parser.add_argument("--allowed-domain", default="example.com", help="Allowed domain for crawl")
    crawl_parser.add_argument("--max-pages", type=int, default=25, help="Maximum number of pages to collect")
    crawl_parser.add_argument("--user-agent", default="FetchioBot/0.1", help="User-Agent header")
    crawl_parser.add_argument("--output-dir", default="data", help="Directory to store crawl output")
    crawl_parser.set_defaults(func=lambda args: asyncio.run(run_crawl(args)))

    search_parser = subparsers.add_parser("search", help="search indexed crawl data")
    search_parser.add_argument("query", help="Search terms")
    search_parser.add_argument("--data-path", default="data/crawl.json", help="Crawl output file")
    search_parser.add_argument("--limit", type=int, default=10, help="Maximum number of results")
    search_parser.set_defaults(func=run_search)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
