import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.logger import setup_logger
from core.keyword_extractor import KeywordExtractor
from core.scraper import Scraper
from core.similarity import SimilarityEngine
from core.verdict import VerdictEngine



# aktifin logger
setup_logger()

# KEYWORD TEST
# buat objek
extractor = KeywordExtractor()

# input test
text = "Berita viral tentang penipuan online di media sosial"

# proses
keywords = extractor.Extract(text)
query = extractor.BuildQuery(keywords)

# tampilkan hasil
print("Keywords:", keywords)
print("Query:", query)

# SCRAPER TEST
scraper = Scraper()

# Trusted sources
print("\n--- Trusted Sources ---")
trusted = scraper.scrape_trusted_sources(text)

for data in trusted:
    print("\nTITLE:", data["title"])
    print("URL:", data["url"])


# Hoax check
print("\n--- Hoax Sources ---")
hoax = scraper.scrape_checkhoax(text)

for data in hoax:
    print("\nTITLE:", data["title"])
    print("URL:", data["url"])



# SIMILARITY TEST  
sim = SimilarityEngine()

text_input = "Berita viral tentang penipuan online di media sosial"

articles = [
    {
        "judul": "Kasus penipuan online meningkat",
        "konten": "Penipuan digital semakin marak di media sosial.",
        "url": "test1.com",
        "sumber": "kompas"
    },
    {
        "judul": "Tips menghindari penipuan",
        "konten": "Masyarakat diminta waspada terhadap modus penipuan online.",
        "url": "test2.com",
        "sumber": "detik"
    }
]

score = sim.compute(text_input, articles[0]["konten"])

ranked = sim.rank_articles(text_input, articles)

top_score = sim.get_top_score(ranked)
avg_score = sim.get_average_score(ranked)

print("Top:", top_score)
print("Avg:", avg_score)


# VERDICT TEST  
verdict = VerdictEngine()

url = "https://example.com"
text = "Berita viral tentang penipuan online di media sosial"

trusted_articles = [
    {"content": "Kasus penipuan online meningkat di Indonesia"},
    {"content": "Banyak masyarakat tertipu oleh berita hoax digital"}
]

# tanpa label
score = verdict.evaluate(url, text, trusted_articles)

# dengan label
label = verdict.evaluate(url, text, trusted_articles, labeling=True)

print("Final Score:", score)
print("Label:", label)