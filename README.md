# Fetchio

Fetchio is a production-ready Python-based search engine and spiderbot with a modern FastAPI backend and Tailwind CSS frontend.

## Features

✨ **Advanced Web Crawling**
- Async/concurrent crawling with configurable worker pools
- Automatic URL deduplication and normalization
- robots.txt compliance checking
- Politeness delays between requests
- Domain filtering and link extraction

🔍 **Intelligent Search**
- TF-IDF ranking algorithm
- Full-text indexing of crawled pages
- Real-time search results
- Configurable result limits

⚡ **FastAPI Backend**
- RESTful API for crawl and search operations
- Async request handling
- Real-time crawl job status tracking
- Health checks and monitoring

🎨 **Tailwind CSS Frontend**
- Modern, responsive UI
- Real-time job status updates
- Integrated search interface
- Dark theme with gradient accents

## Quick Start

### Installation

```bash
git clone https://github.com/Blastmaster-Fixup-and-Kleanup-Crew/Fetchio.git
cd Fetchio
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Configuration

```bash
cp .env.example .env
# Edit .env with your settings
```

### Running the Application

```bash
python -m fetchio
```

Then open http://localhost:8000 in your browser.

## API Endpoints

### Crawl Operations

**Start a Crawl**
```bash
POST /api/crawl
Content-Type: application/json

{
  "start_urls": ["https://example.com"],
  "allowed_domains": ["example.com"],
  "max_pages": 50
}
```

**Get Crawl Status**
```bash
GET /api/crawl/{job_id}
```

**List All Crawls**
```bash
GET /api/crawls
```

### Search Operations

**Search Crawled Pages**
```bash
POST /api/search
Content-Type: application/json

{
  "query": "search term",
  "limit": 10
}
```

## Project Structure

```
fetchio/
  api.py           # FastAPI application
  crawler.py       # Crawling engine & queue management
  indexer.py       # Search indexing & ranking
  models.py        # Data models
  queue.py         # URL queue with deduplication
  robots.py        # robots.txt handling
  database.py      # SQLAlchemy ORM models
  config.py        # Configuration management
  __main__.py      # Entry point

static/
  index.html       # Frontend UI
  app.js          # Frontend logic

requirements.txt   # Python dependencies
pyproject.toml     # Project metadata
```

## Development

Run tests:
```bash
pytest tests/
```

Run with hot reload:
```bash
python -m fetchio
```

## Future Enhancements

- [ ] Persistent job storage (SQLite/PostgreSQL)
- [ ] Distributed crawling with Celery
- [ ] Web UI for crawl visualization
- [ ] Advanced filtering and faceted search
- [ ] Crawl scheduling and automation
- [ ] Export results (JSON, CSV)
- [ ] Admin dashboard

## License

MIT
