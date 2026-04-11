"""
utils/url_parser.py
Validasi dan normalisasi URL sebelum diproses scraper.
Dipanggil duluan sebelum scrape_user_url() untuk memastikan URL aman.
"""

import re
from urllib.parse import urlparse, urlunparse, urlencode, parse_qsl

# Ekstensi file yang bukan artikel berita
_BLOCKED_EXT = {
    ".pdf", ".doc", ".docx", ".xls", ".xlsx",
    ".zip", ".rar", ".exe", ".mp4", ".mp3",
    ".jpg", ".jpeg", ".png", ".gif",
}

# Parameter tracking yang tidak perlu
_TRACKING_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign",
    "utm_content", "utm_term", "fbclid", "gclid",
}


def validate(url: str) -> bool:
    """
    Cek apakah URL valid dan aman untuk di-scrape.

    Returns:
        bool: True jika valid.
    """
    if not url or not isinstance(url, str):
        return False

    parsed = urlparse(url.strip())

    if parsed.scheme not in ("http", "https"):
        return False

    if not parsed.netloc or "." not in parsed.netloc:
        return False

    if any(parsed.path.lower().endswith(ext) for ext in _BLOCKED_EXT):
        return False

    return True


def normalize(url: str) -> str:
    """
    Normalisasi URL:
    - Tambah https:// kalau tidak ada scheme
    - Hapus fragment (#...)
    - Buang parameter tracking (UTM, fbclid, dll)

    Returns:
        str: URL yang sudah bersih.
    """
    url = url.strip()

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    parsed = urlparse(url)

    # Filter query params — buang yang tracking
    clean_params = [
        (k, v) for k, v in parse_qsl(parsed.query)
        if k.lower() not in _TRACKING_PARAMS
    ]

    return urlunparse((
        parsed.scheme,
        parsed.netloc.lower(),
        parsed.path,
        parsed.params,
        urlencode(clean_params),
        "",   # fragment dihapus
    ))


def get_domain(url: str) -> str:
    """Ambil nama domain dari URL. Contoh: 'www.kompas.com' → 'kompas.com'"""
    netloc = urlparse(url).netloc.lower()
    # Buang www.
    return re.sub(r"^www\.", "", netloc)