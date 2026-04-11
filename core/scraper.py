"""
core/scraper.py
Tiga fungsi utama scraping untuk HoaxScan:
  1. scrape_user_url(url)          — scrape artikel dari URL user
  2. scrape_trusted_sources(title) — cari artikel serupa di 6 sumber terpercaya
  3. scrape_checkhoax(title)       — cari artikel serupa di situs cek hoax
"""

import logging
import urllib.parse
from difflib import SequenceMatcher

import requests
from bs4 import BeautifulSoup
from newspaper import Article, Config

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------
# Konfigurasi newspaper3k
# -----------------------------------------------------------------------
_config = Config()
_config.browser_user_agent = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)
_config.request_timeout = 10
_config.fetch_images    = False
_config.memoize_articles = False

_HEADERS = {"User-Agent": _config.browser_user_agent}

# -----------------------------------------------------------------------
# 6 Sumber berita terpercaya (search URL-nya)
# -----------------------------------------------------------------------
TRUSTED_SOURCES = [
    ("kompas",       "https://search.kompas.com/search/?q="),
    ("detik",        "https://www.detik.com/search/searchall?query="),
    ("tempo",        "https://www.tempo.co/search?q="),
    ("cnnindonesia", "https://www.cnnindonesia.com/search?query="),
    ("antaranews",   "https://www.antaranews.com/search/?q="),
    ("republika",    "https://www.republika.co.id/search/"),
]

# Situs cek hoax
CHECKHOAX_SOURCES = [
    ("turnbackhoax", "https://turnbackhoax.id/?s="),
    ("cekfakta",     "https://cekfakta.com/?s="),
]

# Minimal kemiripan judul agar dianggap "sama/mirip"
SIMILARITY_THRESHOLD = 0.5


# =======================================================================
# FUNGSI 1
# =======================================================================

def scrape_user_url(url: str) -> dict:
    """
    Scrape artikel dari URL yang dikirimkan user.

    Args:
        url (str): URL berita dari user.

    Returns:
        dict: {"url": str, "title": str, "content": str}
    """
    article = _fetch_article(url)

    return {
        "url":     url,
        "title":   article.title if article else "",
        "content": article.text  if article else "",
    }


# =======================================================================
# FUNGSI 2
# =======================================================================

def scrape_trusted_sources(title: str) -> list[dict]:
    """
    Cari artikel berjudul mirip di 6 sumber berita terpercaya,
    lalu scrape semuanya.

    Args:
        title (str): Judul dari artikel user (hasil scrape_user_url).

    Returns:
        list[dict]: List artikel yang cocok.
                    Tiap item: {"url": str, "title": str, "content": str}
                    Bisa kosong jika tidak ada yang mirip.
    """
    return _search_and_scrape(title, TRUSTED_SOURCES)


# =======================================================================
# FUNGSI 3
# =======================================================================

def scrape_checkhoax(title: str) -> list[dict]:
    """
    Cari artikel berjudul mirip di situs cek hoax,
    lalu scrape semuanya.

    Args:
        title (str): Judul dari artikel user (hasil scrape_user_url).

    Returns:
        list[dict]: List artikel yang cocok.
                    Tiap item: {"url": str, "title": str, "content": str}
                    Bisa kosong jika tidak ada yang cocok.
    """
    return _search_and_scrape(title, CHECKHOAX_SOURCES)


# =======================================================================
# Helper — dipakai bersama fungsi 2 & 3
# =======================================================================

def _search_and_scrape(title: str, sources: list[tuple]) -> list[dict]:
    """
    Untuk setiap sumber: cari URL kandidat → scrape → filter yang mirip.
    """
    results = []
    query   = _build_query(title)

    for source_name, search_base_url in sources:
        try:
            candidate_urls = _get_candidate_urls(
                search_base_url + query,
                source_name
            )
            for url in candidate_urls:
                article = _fetch_article(url)
                if article and _is_similar(title, article.title):
                    logger.info(f"[Scraper] Match ({source_name}): {article.title}")
                    results.append({
                        "url":     url,
                        "title":   article.title,
                        "content": article.text,
                    })
        except Exception as e:
            logger.warning(f"[Scraper] Error saat cari di {source_name}: {e}")

    logger.info(f"[Scraper] Total hasil dari '{title[:40]}...': {len(results)}")
    return results


def _fetch_article(url: str):
    """
    Download dan parse satu artikel pakai newspaper3k.
    Return Article object, atau None kalau gagal.
    """
    try:
        article = Article(url, config=_config, language="id")
        article.download()
        article.parse()
        return article
    except Exception as e:
        logger.warning(f"[Scraper] Gagal fetch {url}: {e}")
        return None


def _get_candidate_urls(search_url: str, source_name: str) -> list[str]:
    """
    Ambil URL-URL kandidat dari halaman hasil pencarian.
    Pakai BeautifulSoup untuk korek semua link artikel.
    Maksimal 5 URL per sumber.
    """
    try:
        resp = requests.get(search_url, headers=_HEADERS, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")

        urls = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if (
                href.startswith("http")
                and len(href) > 40          # URL artikel biasanya panjang
                and href not in urls
            ):
                urls.append(href)
            if len(urls) >= 5:
                break

        return urls

    except Exception as e:
        logger.warning(f"[Scraper] Gagal ambil hasil search {search_url}: {e}")
        return []


def _is_similar(title_a: str, title_b: str) -> bool:
    """
    Cek apakah dua judul cukup mirip.
    Pakai SequenceMatcher dengan threshold 0.5.
    """
    if not title_a or not title_b:
        return False
    ratio = SequenceMatcher(
        None,
        title_a.lower().strip(),
        title_b.lower().strip()
    ).ratio()
    return ratio >= SIMILARITY_THRESHOLD


def _build_query(title: str) -> str:
    """Ambil 8 kata pertama judul lalu encode jadi query string."""
    words = title.strip().split()[:8]
    return urllib.parse.quote(" ".join(words))