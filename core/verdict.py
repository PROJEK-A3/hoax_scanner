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

@dataclass
class SignalScores:
    similarity: float = 0
    source_citation:float = 0
    domain: float = 0
    sentiment: float = 0


class VerdictEngine:
    def __init__(self) -> None:
        self.weight = {
            "similarity": 0.40,  # Cosine similarity vs sumber terpercaya
            "domain": 0.25,  # Kredibilitas domain sumber
            "sentiment": 0.25,  # Netralitas sentimen teks
            "source_citation": 0.10,  # Kehadiran kutipan/sumber dalam teks
        }

    def evaluate(self, url:str, input_text:str, trusted_articles, labeling:bool=False):
        signals = SignalScores()
        
        signals.domain = self.calculate_domain_age(url)
        signals.source_citation
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
                return "FAKTA"
            else:
                return "HOAX"

        return final

    def calculate_domain_age(self, url:str) -> float:
        url = urlparse(url).netloc
        domain = whois.whois(url)
        domain_creation_date = domain.creation_date  # type: ignore
        if isinstance(domain_creation_date, list):
            domain_creation_date = domain_creation_date[0]
        domain_age = datetime.now(timezone.utc) - domain_creation_date
        if url in TRUSTED_DOMAIN:
            return 1.0
        if domain_age.days < 100:
            return domain_age.days * 0.01
        return 0.0
    
    def calculate_sentiment(self, input_text:list[str]) ->float:
        found = 0
        for w in input_text:
            if w in SENSATIONAL_WORD:
                found+=1
        
        return 1.0 * (len(input_text)-found/len(input_text))
    
    # def labeling(self):
    #     if self.evaluate(url,input_text, trusted_articles) > .7
    
    def calculate_similarity(self, input_text:str, trusted_articles:list[dict[str,str]]) -> float:
        engine = SimilarityEngine()
        score = 0
        for art in trusted_articles:
            score += engine.compute(input_text, art["konten"])

        # for art in trusted_articles:
        #     score = engine.compute(input_text, art["konten"])
        #     print(f"  {art['sumber']:15s} -> {score:.4f} ({score*100:.1f}%)")
        return score