"""
core/scraper.py
Scraping konten artikel dari URL menggunakan requests + BeautifulSoup.
"""

import logging
import re
import time
from typing import Optional

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


# Selector konten utama untuk portal berita Indonesia yang umum
CONTENT_SELECTORS = [
    # Selektor spesifik per portal (lebih akurat)
    {"name": "article", "class_": re.compile(r"article[-_]?(body|content|text)", re.I)},
    {"name": "div",     "class_": re.compile(r"detail[-_]?(text|body|content)", re.I)},
    {"name": "div",     "class_": re.compile(r"post[-_]?(body|content)", re.I)},
    {"name": "div",     "itemprop": "articleBody"},
    # Fallback generik
    {"name": "article"},
    {"name": "main"},
]

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

# Tag yang tidak mengandung konten artikel
NOISE_TAGS = [
    "script", "style", "noscript", "iframe",
    "nav", "header", "footer", "aside",
    "figure", "figcaption", "form", "button",
    "ins",   # iklan Google AdSense
]


class Scraper:
    """
    Mengambil dan mengekstrak teks konten artikel dari sebuah URL berita.

    Attributes:
        headers (dict): HTTP headers yang digunakan saat request.
        timeout (int): Batas waktu request dalam detik.
    """

    def __init__(
        self,
        headers: Optional[dict] = None,
        timeout: int = 10,
    ):
        self.headers: dict = headers if headers is not None else DEFAULT_HEADERS
        self.timeout: int = timeout
        self._session = requests.Session()
        self._session.headers.update(self.headers)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def scrape_url(self, url: str) -> str:
        """
        Ambil HTML mentah dari URL.

        Args:
            url (str): URL halaman berita.

        Returns:
            str: Konten HTML halaman. String kosong jika gagal.
        """
        try:
            response = self._session.get(url, timeout=self.timeout, allow_redirects=True)
            response.raise_for_status()
            response.encoding = response.apparent_encoding  # deteksi encoding otomatis
            logger.info(f"[Scraper] OK ({response.status_code}): {url}")
            return response.text
        except requests.exceptions.Timeout:
            logger.warning(f"[Scraper] Timeout: {url}")
        except requests.exceptions.TooManyRedirects:
            logger.warning(f"[Scraper] Too many redirects: {url}")
        except requests.exceptions.HTTPError as e:
            logger.warning(f"[Scraper] HTTP error {e.response.status_code}: {url}")
        except requests.exceptions.RequestException as e:
            logger.warning(f"[Scraper] Request gagal: {e}")
        return ""

    def extract_text(self, html: str) -> str:
        """
        Ekstrak teks bersih dari HTML artikel.

        Args:
            html (str): Konten HTML mentah.

        Returns:
            str: Teks artikel yang sudah dibersihkan dari noise.
        """
        if not html:
            return ""

        soup = BeautifulSoup(html, "lxml")

        # Hapus elemen noise terlebih dahulu
        for tag in soup(NOISE_TAGS):
            tag.decompose()

        # Coba temukan konten utama artikel
        content_element = self._find_content_element(soup)

        if content_element:
            paragraphs = content_element.find_all("p")
            if paragraphs:
                text = " ".join(p.get_text(separator=" ") for p in paragraphs)
            else:
                text = content_element.get_text(separator=" ")
        else:
            # Fallback: ambil semua <p> di halaman
            paragraphs = soup.find_all("p")
            text = " ".join(p.get_text(separator=" ") for p in paragraphs)

        return self._clean_whitespace(text)

    def scrape_full(self, url: str) -> dict:
        """
        Helper: fetch + extract sekaligus. Kembalikan dict lengkap.

        Returns:
            dict: {url, title, text, success}
        """
        html = self.scrape_url(url)
        if not html:
            return {"url": url, "title": "", "text": "", "success": False}

        soup = BeautifulSoup(html, "lxml")
        title = soup.title.string.strip() if soup.title else ""
        text  = self.extract_text(html)

        return {
            "url":     url,
            "title":   title,
            "text":    text,
            "success": bool(text),
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _find_content_element(self, soup: BeautifulSoup):
        """
        Cari elemen HTML yang paling mungkin berisi konten artikel
        berdasarkan CONTENT_SELECTORS yang telah didefinisikan.
        """
        for selector in CONTENT_SELECTORS:
            element = soup.find(**selector)
            if element:
                return element
        return None

    @staticmethod
    def _clean_whitespace(text: str) -> str:
        """Normalisasi whitespace berlebih."""
        text = re.sub(r"\s+", " ", text)
        return text.strip()
