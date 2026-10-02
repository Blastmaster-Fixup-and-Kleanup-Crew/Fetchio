# Fetchio

Fetchio is a Python-based search engine and spiderbot project designed to crawl websites, extract document content, and provide a lightweight search index for discovered pages.

## Features

- Async website crawling with `aiohttp`
- HTML content extraction using BeautifulSoup
- Link discovery and page normalization
- Simple inverted-index search engine
- CLI for crawl and search workflows

## Project layout

```text
fetchio/
  __init__.py
  __main__.py
  cli.py
  config.py
  crawler.py
  indexer.py
  models.py
  search.py
requirements.txt
pyproject.toml
README.md
.gitignore
```

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m fetchio.cli crawl --start-url https://example.com --max-pages 25
python -m fetchio.cli search "example"
```

## Configuration

The crawler behavior is configured through `FetchioConfig` in `fetchio/config.py`.
You can customize the default start URLs, allowed domains, maximum pages, and request headers.

## Development notes

This repository is intentionally scaffolded as a clean starting point for a more complete spiderbot/search engine. It includes:

- crawler infrastructure
- indexing logic
- search ranking
- a CLI entrypoint

The next stages can include robots.txt handling, queue persistence, distributed crawling, and a real web UI.
