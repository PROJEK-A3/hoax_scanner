"""
core/rss_fetcher.py
Mengambil artikel dari RSS Feed secara paralel menggunakan ThreadPoolExecutor.
"""

import feedparser
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


# 6 RSS Feed sumber berita Indonesia
DEFAULT_RSS_FEEDS = {
    "kompas":       "https://rss.kompas.com/breakingnews",
    "detik":        "https://rss.detik.com/index.php/detikcom",
    "tempo":        "https://rss.tempo.co/nasional",
    "cnnindonesia": "https://www.cnnindonesia.com/rss",
    "antaranews":   "https://www.antaranews.com/rss/terkini.xml",
    "republika":    "https://www.republika.co.id/rss",
}

MAX_ARTICLES_PER_FEED = 20


class RSSFetcher:
    """
    Mengambil daftar artikel dari beberapa RSS Feed secara paralel.

    Attributes:
        rss_feeds (dict): Mapping nama sumber -> URL RSS.
        timeout (int): Batas waktu request dalam detik.
    """

    def __init__(
        self,
        rss_feeds: Optional[dict] = None,
        timeout: int = 10,
    ):
        self.rss_feeds: dict = rss_feeds if rss_feeds is not None else DEFAULT_RSS_FEEDS
        self.timeout: int = timeout

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def fetch_all(self) -> list[dict]:
        """
        Ambil artikel dari SEMUA RSS Feed secara paralel.

        Returns:
            list[dict]: Gabungan semua artikel dari seluruh feed.
                        Setiap artikel adalah dict dengan key:
                        title, url, source, published, summary.
        """
        results: list[dict] = []

        with ThreadPoolExecutor(max_workers=len(self.rss_feeds)) as executor:
            future_map = {
                executor.submit(self._fetch_feed, name, url): name
                for name, url in self.rss_feeds.items()
            }

            for future in as_completed(future_map):
                source = future_map[future]
                try:
                    articles = future.result()
                    results.extend(articles)
                    logger.info(f"[RSSFetcher] {source}: {len(articles)} artikel")
                except Exception as exc:
                    logger.warning(f"[RSSFetcher] {source} gagal: {exc}")

        logger.info(f"[RSSFetcher] Total artikel terkumpul: {len(results)}")
        return results

    def fetch_one(self, url: str) -> list[dict]:
        """
        Ambil artikel dari SATU URL RSS Feed.

        Args:
            url (str): URL RSS Feed yang akan di-fetch.

        Returns:
            list[dict]: Daftar artikel dari feed tersebut.
        """
        source_name = self._resolve_source_name(url)
        return self._fetch_feed(source_name, url)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _fetch_feed(self, source_name: str, url: str) -> list[dict]:
        """Parse satu RSS feed dan kembalikan list artikel."""
        feed = feedparser.parse(url, request_headers={"User-Agent": "HoaxScan/1.0"})

        if feed.bozo and feed.bozo_exception:
            raise ValueError(f"Feed error: {feed.bozo_exception}")

        articles = []
        for entry in feed.entries[:MAX_ARTICLES_PER_FEED]:
            article = {
                "title":     entry.get("title", "").strip(),
                "url":       entry.get("link", "").strip(),
                "source":    source_name,
                "published": self._parse_date(entry),
                "summary":   self._get_summary(entry),
            }
            if article["url"]:          # skip jika tidak ada URL
                articles.append(article)

        return articles

    @staticmethod
    def _parse_date(entry) -> Optional[str]:
        """Konversi struct_time feedparser ke string ISO."""
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            try:
                dt = datetime(*entry.published_parsed[:6])
                return dt.isoformat()
            except Exception:
                pass
        return None

    @staticmethod
    def _get_summary(entry) -> str:
        """Ambil ringkasan/deskripsi dari entry RSS."""
        summary = entry.get("summary", "") or entry.get("description", "")
        # Hapus tag HTML sederhana
        import re
        return re.sub(r"<[^>]+>", "", summary).strip()

    def _resolve_source_name(self, url: str) -> str:
        """Cari nama sumber dari URL; fallback ke domain."""
        for name, feed_url in self.rss_feeds.items():
            if feed_url == url:
                return name
        from urllib.parse import urlparse
        return urlparse(url).netloc or "unknown"
