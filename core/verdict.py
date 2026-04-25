import whois, json
from datetime import datetime, timezone
from dataclasses import dataclass
from urllib.parse import urlparse
from core.similarity import SimilarityEngine
from core.keyword_extractor import KeywordExtractor

with open('core/trusted_domain.json', 'r') as f:
    TRUSTED_DOMAIN = json.load(f)
    TRUSTED_DOMAIN = TRUSTED_DOMAIN["domain"]
    
with open('core/sensational_word.json', 'r') as f:
    SENSATIONAL_WORD = json.load(f)
    SENSATIONAL_WORD = SENSATIONAL_WORD['sensational_word']

with open('core/citation.json', 'r') as f:
    CITATION_WORD = json.load(f)
    CITATION_WORD = CITATION_WORD['citation']

@dataclass
class SignalScores:
    similarity: float = 0
    source_citation:float = 0
    domain: float = 0
    sentiment: float = 0


class VerdictEngine:
    def __init__(self) -> None:
        """
        Menginisialisasi VerdictEngine dengan bobot yang telah ditentukan untuk setiap sinyal
        yang digunakan dalam evaluasi kredibilitas artikel.
        """
        self.weight = {
            "similarity": 0.40,  # Cosine similarity vs sumber terpercaya
            "domain": 0.25,  # Kredibilitas domain sumber
            "sentiment": 0.25,  # Netralitas sentimen teks
            "source_citation": 0.10,  # Kehadiran kutipan/sumber dalam teks
        }

    def evaluate(self, url:str, input_text:str, trusted_articles, labeling:bool=False):
        """
        Mengevaluasi skor kredibilitas sebuah artikel berdasarkan beberapa sinyal.

        Metode ini menghitung skor akhir dengan menggabungkan skor dari beberapa sinyal:
        - Usia dan kredibilitas domain
        - Sentimen (kandungan kata-kata sensasional)
        - Kemiripan konten dengan artikel dari sumber terpercaya
        - Adanya sitasi sumber (belum diimplementasikan)

        Args:
            url (str): URL artikel yang ingin diperiksa.
            input_text (str): Konten teks dari artikel yang akan dievaluasi.
            trusted_articles (list): Daftar artikel dari sumber terpercaya untuk perbandingan similaritas.
            labeling (bool, optional): Jika True, akan mengembalikan label "RENDAH"/"SEDANG"/"TINGGI"
                                       berdasarkan skor. Jika False, akan mengembalikan skor numerik.
                                       Defaults to False.

        Returns:
            float | str: Skor kredibilitas artikel (float antara 0.0 dan 1.0) jika `labeling` adalah False,
                         atau label "TINGGI"/"SEDANG"/"RENDAH" (str) jika `labeling` adalah True.
        """
        signals = SignalScores()
        
        signals.domain = self.calculate_domain_age(url)
        signals.source_citation = self.calculate_source_citation(input_text)
        signals.sentiment = self.calculate_sentiment(KeywordExtractor().Extract(input_text))
        signals.similarity = self.calculate_similarity(input_text, trusted_articles)

        final = (
            signals.domain * self.weight["domain"] +
            signals.similarity * self.weight["similarity"] +
            signals.sentiment * self.weight["sentiment"] +
            signals.source_citation * self.weight["source_citation"]
        )

        final = float(round(final,2))

        if labeling == True:
            if final > 0.7:
                return "RENDAH"
            elif final > 0.4:
                return "SEDANG"
            else:
                return "TINGGI"

        return final

    def calculate_domain_age(self, url:str) -> float:
        """
        Menghitung skor kredibilitas domain berdasarkan usia dan status terpercaya.

        Skor 1.0 diberikan jika:
        - Domain terdaftar di `TRUSTED_DOMAIN`.
        - Usia domain lebih dari 100 hari.

        Jika usia domain di bawah 100 hari, skor dihitung secara proporsional.
        Contoh: Usia 50 hari akan menghasilkan skor 0.5.

        Args:
            url (str): URL artikel yang akan diperiksa.

        Returns:
            float: Skor kredibilitas domain antara 0.0 dan 1.0.
        """
        
        domain = whois.whois(url)
        domain_creation_date = domain.creation_date  # type: ignore
        if isinstance(domain_creation_date, list):
            domain_creation_date = domain_creation_date[0]
            
        if domain_creation_date == None:
            return 0.0
        
        domain_age = datetime.now(timezone.utc) - domain_creation_date

        if domain_age.days < 100:
            return domain_age.days * 0.01
        return 0.0
    
    def calculate_sentiment(self, input_text:list[str]) ->float:
        """
        Menghitung skor sentimen berdasarkan jumlah kata sensasional yang ditemukan.
        Skor yang lebih tinggi menunjukkan lebih sedikit kata-kata sensasional (lebih netral).

        Args:
            input_text (list[str]): Daftar kata kunci dari teks artikel.

        Returns:
            float: Skor sentimen antara 0.0 dan 1.0.
        """
        if not input_text:
            return 1.0  # Dianggap netral jika tidak ada input

        found = 0
        for w in input_text:
            if w in SENSATIONAL_WORD:
                found+=1
        
        return 1.0 * (len(input_text)-found/len(input_text))
    
    def calculate_similarity(self, input_text:str, trusted_articles:list[dict[str,str]]) -> float:
        """
        Menghitung skor kemiripan teks input dengan daftar artikel terpercaya.
        Menggunakan SimilarityEngine untuk mendapatkan skor kemiripan tertinggi.

        Args:
            input_text (str): Konten teks dari artikel yang akan dievaluasi.
            trusted_articles (list[dict[str,str]]): Daftar artikel terpercaya untuk perbandingan.

        Returns:
            float: Skor kemiripan tertinggi antara 0.0 dan 1.0.
        """
        engine = SimilarityEngine()
        score = 0
        for art in trusted_articles:
            score += engine.compute(input_text, art["content"])

        return score/len(trusted_articles)

    def calculate_source_citation(self, input_text:str):
        """
        """
        if not input_text:
            return 1.0 

        found = 0
        for w in input_text:
            if w in CITATION_WORD:
                found+=1

        if found == 0:
            return 0.0
        elif found == 1:
            return 0.5
        elif found == 2:
            return 0.75
        else:
            return 1.0

    def give_label(self, score:float)->str:
        if score > 0.7:
            return "RENDAH"
        elif score > 0.4:
            return "SEDANG"
        else:
            return "TINGGI"