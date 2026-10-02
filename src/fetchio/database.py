from __future__ import annotations

from sqlalchemy import Column, String, Text, Float, DateTime, Integer, ForeignKey, create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()


class CrawlJobModel(Base):
    __tablename__ = "crawl_jobs"
    id = Column(String, primary_key=True)
    start_urls = Column(Text)  # JSON
    allowed_domains = Column(Text)  # JSON
    max_pages = Column(Integer)
    status = Column(String, default="pending")
    pages_crawled = Column(Integer, default=0)
    errors = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    documents = relationship("DocumentModel", back_populates="crawl_job")


class DocumentModel(Base):
    __tablename__ = "documents"
    id = Column(String, primary_key=True)
    url = Column(String, unique=True, index=True)
    title = Column(String)
    text = Column(Text)
    links = Column(Text)  # JSON
    score = Column(Float, default=0.0)
    status = Column(String, default="new")
    crawl_id = Column(String, ForeignKey("crawl_jobs.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    crawl_job = relationship("CrawlJobModel", back_populates="documents")


class SearchIndexModel(Base):
    __tablename__ = "search_index"
    id = Column(String, primary_key=True)
    term = Column(String, index=True)
    document_id = Column(String, ForeignKey("documents.id"))
    created_at = Column(DateTime, default=datetime.utcnow)


async def init_db(database_url: str) -> AsyncSession:
    """Initialize async database."""
    engine = create_async_engine(database_url, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
