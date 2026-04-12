"""
utils/url_parser.py
Memvalidasi, membersihkan, dan mengekstrak metadata dari URL input user.
Dipanggil sebelum Scraper untuk memastikan URL valid dan aman diproses.
"""

import logging
import re
from typing import Optional
from urllib.parse import urlparse, urlunparse

logger = logging.getLogger(__name__)

# Ekstensi file yang bukan artikel berita
BLOCKED_EXTENSIONS = {
    ".pdf", ".doc", ".docx", ".xls", ".xlsx",
    ".zip", ".rar", ".exe", ".mp4", ".mp3",
    ".jpg", ".jpeg", ".png", ".gif", ".svg",
}

# Kueri parameter yang biasanya tidak mempengaruhi konten (boleh distrip)
STRIP_PARAMS = {"utm_source", "utm_medium", "utm_campaign", "utm_content",
                "utm_term", "fbclid", "gclid", "ref", "from"}


class URLParser:
    """
    Memvalidasi dan menormalkan URL sebelum di-scrape.
    Juga mengekstrak informasi dasar (domain, path, dll.) dari URL.
    """

    @staticmethod
    def validate(url: str) -> bool:
        """
        Periksa apakah URL valid dan aman untuk di-scrape.

        Args:
            url (str): URL yang akan divalidasi.

        Returns:
            bool: True jika valid.
        """
        if not url or not isinstance(url, str):
            logger.debug("[URLParser] URL kosong atau bukan string.")
            return False

        url = url.strip()
        parsed = urlparse(url)

        # Harus menggunakan http atau https
        if parsed.scheme not in ("http", "https"):
            logger.debug(f"[URLParser] Scheme tidak valid: {parsed.scheme}")
            return False

        # Harus memiliki domain
        if not parsed.netloc:
            logger.debug("[URLParser] Tidak ada domain/netloc.")
            return False

        # Domain minimal punya satu titik (misal: kompas.com)
        if "." not in parsed.netloc:
            logger.debug(f"[URLParser] Domain tidak valid: {parsed.netloc}")
            return False

        # Cek ekstensi yang diblokir
        path_lower = parsed.path.lower()
        if any(path_lower.endswith(ext) for ext in BLOCKED_EXTENSIONS):
            logger.debug(f"[URLParser] Ekstensi file diblokir: {parsed.path}")
            return False

        return True

    @staticmethod
    def normalize(url: str) -> str:
        """
        Normalisasi URL:
        - Pastikan ada scheme (tambah https:// jika tidak ada)
        - Hapus fragment (#...)
        - Hapus parameter UTM / tracking yang tidak perlu

        Args:
            url (str): URL mentah dari input user.

        Returns:
            str: URL yang sudah dinormalisasi.
        """
        url = url.strip()

        # Tambah scheme jika tidak ada
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        parsed = urlparse(url)

        # Hapus fragment
        # Filter query params — buang parameter tracking
        if parsed.query:
            clean_params = []
            for part in parsed.query.split("&"):
                key = part.split("=")[0].lower()
                if key not in STRIP_PARAMS:
                    clean_params.append(part)
            clean_query = "&".join(clean_params)
        else:
            clean_query = ""

        normalized = urlunparse((
            parsed.scheme,
            parsed.netloc.lower(),
            parsed.path,
            parsed.params,
            clean_query,
            "",          # fragment dihapus
        ))

        return normalized

    @staticmethod
    def extract_metadata(url: str) -> dict:
        """
        Ekstrak informasi metadata dari URL (tanpa fetch ke server).

        Args:
            url (str): URL yang akan dianalisis.

        Returns:
            dict: {scheme, domain, path, is_valid, normalized_url}
        """
        parsed = urlparse(url)
        is_valid = URLParser.validate(url)
        normalized = URLParser.normalize(url) if is_valid else url

        return {
            "scheme":         parsed.scheme,
            "domain":         parsed.netloc.lower(),
            "path":           parsed.path,
            "is_valid":       is_valid,
            "normalized_url": normalized,
        }

    @staticmethod
    def is_news_url(url: str) -> bool:
        """
        Heuristik sederhana untuk memeriksa apakah URL kemungkinan artikel berita
        berdasarkan struktur path (mengandung tanggal, slug, dll.).

        Returns:
            bool: True jika URL kemungkinan adalah halaman artikel berita.
        """
        parsed = urlparse(url)
        path = parsed.path

        # Path artikel biasanya mengandung pola tanggal atau slug panjang
        date_pattern  = re.compile(r"/\d{4}/\d{2}/\d{2}/")
        slug_pattern   = re.compile(r"/[a-z0-9]+(-[a-z0-9]+){3,}/")   # minimal 4 kata

        return bool(date_pattern.search(path) or slug_pattern.search(path))
