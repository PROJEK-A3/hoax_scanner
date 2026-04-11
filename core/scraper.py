"""
core/scraper.py
Scraping konten artikel dari URL menggunakan newspaper3k.
newspaper3k secara otomatis menangani:
  - Download HTML
  - Ekstraksi judul, teks utama, gambar, author, tanggal
  - NLP dasar (summary, keywords)
"""
 
import logging
from newspaper import Article, Config
 
logger = logging.getLogger(__name__)
 
DEFAULT_CONFIG = Config()
DEFAULT_CONFIG.browser_user_agent = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)
DEFAULT_CONFIG.request_timeout = 10
DEFAULT_CONFIG.fetch_images = False     # tidak perlu download gambar
DEFAULT_CONFIG.memoize_articles = False
 
 
class Scraper:
    """
    Mengambil dan mengekstrak konten artikel dari sebuah URL berita
    menggunakan library newspaper3k.
 
    Attributes:
        headers (dict): HTTP headers tambahan (User-Agent, dll).
        timeout (int): Batas waktu request dalam detik.
    """
 
    def __init__(self, headers: dict = None, timeout: int = 10):
        self.headers: dict = headers or {}
        self.timeout: int = timeout
 
        # Buat config newspaper3k
        self._config = Config()
        self._config.browser_user_agent = (
            self.headers.get("User-Agent", DEFAULT_CONFIG.browser_user_agent)
        )
        self._config.request_timeout = self.timeout
        self._config.fetch_images = False
        self._config.memoize_articles = False
 
    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
 
    def scrape_url(self, url: str) -> str:
        """
        Download dan kembalikan teks utama artikel dari URL.
 
        Args:
            url (str): URL halaman berita.
 
        Returns:
            str: Teks isi artikel. String kosong jika gagal.
        """
        article = self._download_and_parse(url)
        if article is None:
            return ""
        return article.text
 
    def extract_text(self, html: str) -> str:
        """
        Ekstrak teks dari HTML mentah yang sudah ada (tanpa download ulang).
        Berguna jika HTML sudah diambil sebelumnya (misal dari RSSFetcher).
 
        Args:
            html (str): Konten HTML mentah.
 
        Returns:
            str: Teks artikel hasil ekstraksi.
        """
        if not html:
            return ""
        try:
            article = Article("", config=self._config, language="id")
            article.set_html(html)
            article.parse()
            return article.text
        except Exception as e:
            logger.warning(f"[Scraper] extract_text gagal: {e}")
            return ""
 
    def scrape_full(self, url: str) -> dict:
        """
        Download artikel dan kembalikan semua metadata sekaligus.
 
        Returns:
            dict dengan key:
              - url        : URL artikel
              - title      : Judul artikel
              - text       : Isi teks artikel
              - authors    : List nama penulis
              - publish_date: Tanggal publikasi (datetime / None)
              - top_image  : URL gambar utama
              - success    : True jika teks berhasil diambil
        """
        article = self._download_and_parse(url)
        if article is None:
            return {
                "url": url, "title": "", "text": "",
                "authors": [], "publish_date": None,
                "top_image": "", "success": False,
            }
 
        return {
            "url":          url,
            "title":        article.title or "",
            "text":         article.text or "",
            "authors":      article.authors or [],
            "publish_date": article.publish_date,
            "top_image":    article.top_image or "",
            "success":      bool(article.text),
        }
 
    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
 
    def _download_and_parse(self, url: str):
        """
        Download dan parse artikel dari URL menggunakan newspaper3k.
 
        Returns:
            Article object jika berhasil, None jika gagal.
        """
        try:
            article = Article(url, config=self._config, language="id")
            article.download()
            article.parse()
            logger.info(f"[Scraper] OK: {url}")
            return article
        except Exception as e:
            logger.warning(f"[Scraper] Gagal scrape {url}: {e}")
            return None