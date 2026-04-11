import whois
from datetime import datetime, timezone
from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass
class SignalScores:
    similarity: float = 0
    source_citation = 0
    domain: float = 0


class VerdictEngine:
    def __init__(self) -> None:
        self.weight = {
            "similarity": 0.40,  # Cosine similarity vs sumber terpercaya
            "domain": 0.25,  # Kredibilitas domain sumber
            "sentiment": 0.15,  # Netralitas sentimen teks (Dey et al., 2016)
            "source_citation": 0.10,  # Kehadiran kutipan/sumber dalam teks
            "clickbait": 0.10,  # Absensi kata sensasional/clickbait
        }
        self.trusted_domain = [
            "kompas.com",
            "detik.com",
            "cnnindonesia.com",
            "antaranews.com",
            "bbc.com",
            "tempo.co",
        ]

    def calculate_domain_age(url: str):
        url = urlparse(url).netloc
        domain = whois.whois(url)
        domain_creation_date = domain.creation_date  # type: ignore
        domain_age = datetime.now(timezone.utc) - domain_creation_date
        if domain in TRUSTED_DOMAINS:
            return 1.0
        if domain_age < 100:
            return domain_age * 0.01

