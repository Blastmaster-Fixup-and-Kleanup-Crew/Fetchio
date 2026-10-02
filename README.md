# Fetchio

Fetchio is a Python-based search engine and spiderbot with a FastAPI backend, SQLite persistence, ranking and search features, and a Tailwind CSS dashboard.

## Features

- Asynchronous crawling with concurrency control
- URL normalization and deduplication
- robots.txt enforcement
- page extraction and link discovery
- TF-IDF indexing and ranked search
- crawl job monitoring
- SQLite-backed document persistence
- modern Tailwind frontend
- Docker deployment support

## Quick Start

```bash
git clone https://github.com/Blastmaster-Fixup-and-Kleanup-Crew/Fetchio.git
cd Fetchio
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
python -m fetchio
