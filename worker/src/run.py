import os
import time
from datetime import datetime, timezone

import feedparser
import requests
from bs4 import BeautifulSoup
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

def ensure_schema():
    with engine.begin() as conn:
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS items (
            id SERIAL PRIMARY KEY,
            source TEXT NOT NULL,
            external_id TEXT NOT NULL,
            title TEXT NOT NULL,
            url TEXT NOT NULL,
            published_at TIMESTAMPTZ NULL,
            fetched_at TIMESTAMPTZ NOT NULL,
            UNIQUE (source, external_id)
        );
        """))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_items_published_at ON items(published_at);"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_items_source ON items(source);"))

def upsert_item(source, external_id, title, url, published_at):
    with engine.begin() as conn:
        conn.execute(
            text("""
            INSERT INTO items (source, external_id, title, url, published_at, fetched_at)
            VALUES (:source, :external_id, :title, :url, :published_at, :fetched_at)
            ON CONFLICT (source, external_id)
            DO UPDATE SET
              title = EXCLUDED.title,
              url = EXCLUDED.url,
              published_at = EXCLUDED.published_at,
              fetched_at = EXCLUDED.fetched_at;
            """),
            {
                "source": source,
                "external_id": external_id,
                "title": title,
                "url": url,
                "published_at": published_at,
                "fetched_at": datetime.now(timezone.utc),
            },
        )

def ingest_rss():
    rss_url = "http://feeds.bbci.co.uk/news/world/rss.xml"
    feed = feedparser.parse(rss_url)
    source = "BBC World RSS"

    for entry in feed.entries[:50]:
        external_id = entry.get("id") or entry.get("link")
        title = (entry.get("title") or "").strip()
        url = (entry.get("link") or "").strip()

        published_at = None
        if entry.get("published_parsed"):
            published_at = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)

        if external_id and title and url:
            upsert_item(source, external_id, title, url, published_at)

def ingest_html():
    source = "Hacker News"
    url = "https://news.ycombinator.com/"
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    for a in soup.select("span.titleline > a")[:50]:
        title = a.get_text(strip=True)
        link = (a.get("href") or "").strip()
        external_id = link
        if title and link:
            upsert_item(source, external_id, title, link, None)

def main():
    ensure_schema()
    while True:
        try:
            ingest_rss()
            ingest_html()
            print("Worker ok:", datetime.now(timezone.utc).isoformat())
        except Exception as e:
            print("Worker error:", e)
        time.sleep(60)  # every 1 minute

if __name__ == "__main__":
    main()

