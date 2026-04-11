"""
core/rss_fetcher.py
Ambil artikel dari 6 RSS Feed secara paralel.
Dipakai sebagai sumber artikel pembanding selain scraping langsung.
"""

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

import feedparser

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------
# 6 RSS Feed sumber berita terpercaya
# -----------------------------------------------------------------------
RSS_FEEDS = [
    ("kompas",       "https://rss.kompas.com/breakingnews"),
    ("detik",        "https://rss.detik.com/index.php/detikcom"),
    ("tempo",        "https://rss.tempo.co/nasional"),
    ("cnnindonesia", "https://www.cnnindonesia.com/rss"),
    ("antaranews",   "https://www.antaranews.com/rss/terkini.xml"),
    ("republika",    "https://www.republika.co.id/rss"),
]

MAX_PER_FEED = 20


def fetch_all_feeds() -> list[dict]:
    """
    Ambil artikel dari semua RSS Feed secara paralel.

    Returns:
        list[dict]: Gabungan artikel dari seluruh feed.
                    Tiap item: {"url": str, "title": str, "source": str, "published": str}
    """
    results = []

    with ThreadPoolExecutor(max_workers=len(RSS_FEEDS)) as executor:
        futures = {
            executor.submit(_fetch_one_feed, name, url): name
            for name, url in RSS_FEEDS
        }
        for future in as_completed(futures):
            source = futures[future]
            try:
                articles = future.result()
                results.extend(articles)
                logger.info(f"[RSSFetcher] {source}: {len(articles)} artikel")
            except Exception as e:
                logger.warning(f"[RSSFetcher] {source} gagal: {e}")

    logger.info(f"[RSSFetcher] Total: {len(results)} artikel")
    return results


def fetch_one_feed(url: str, source_name: str = "unknown") -> list[dict]:
    """
    Ambil artikel dari satu RSS Feed.

    Args:
        url (str): URL RSS Feed.
        source_name (str): Nama sumber (opsional, untuk label).

    Returns:
        list[dict]: Daftar artikel dari feed tersebut.
    """
    return _fetch_one_feed(source_name, url)


# -----------------------------------------------------------------------
# Internal helper
# -----------------------------------------------------------------------

def _fetch_one_feed(source_name: str, url: str) -> list[dict]:
    feed = feedparser.parse(url)

    if feed.bozo and feed.bozo_exception:
        raise ValueError(f"Feed error: {feed.bozo_exception}")

    articles = []
    for entry in feed.entries[:MAX_PER_FEED]:
        article_url = entry.get("link", "").strip()
        if not article_url:
            continue
        articles.append({
            "url":       article_url,
            "title":     entry.get("title", "").strip(),
            "source":    source_name,
            "published": _parse_date(entry),
        })

    return articles


def _parse_date(entry) -> str:
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        try:
            return datetime(*entry.published_parsed[:6]).isoformat()
        except Exception:
            pass
    return ""