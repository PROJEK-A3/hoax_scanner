import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.logger import setup_logger
from core.keyword_extractor import KeywordExtractor
from core.scraper import Scraper
from core.similarity import SimilarityEngine
from core.verdict import VerdictEngine
from database.db_manager import (
    DatabaseManager,
    insert_analisis,
    get_all_analisis,
    get_analisis_by_id,
    update_analisis,
    delete_analisis,
    delete_all_analisis
)
from utils.text_cleaner import TextCleaner

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

# DATABASE TEST
# init (auto create table)
db = DatabaseManager()

# INSERT
insert_analisis("berita hoax tentang politik", 7, "Tinggi")
insert_analisis("informasi valid dari pemerintah", 2, "Rendah")

# GET ALL
data = get_all_analisis()
print("ALL DATA:", data)

# GET BY ID (ambil id pertama kalau ada)
if data:
    first_id = data[0][0]
    one = get_analisis_by_id(first_id)
    print("GET BY ID:", one)

    # UPDATE
    update_analisis(first_id, 5, "Sedang")

    # DELETE (optional, coba kalau mau)
    # delete_analisis(first_id)

# DELETE ALL (optional, hati-hati )
# delete_all_analisis()

print("=== DONE DATABASE TEST ===")



# TEXT CLEANER TEST

cleaner = TextCleaner()

# input test
text = "Berita VIRAL!!! tentang penipuan online di media sosial 😱 123"

# proses
cleaned = cleaner.Cleaning(text)
tokens = cleaner.Tokenize(cleaned)

# output
print("Original :", text)
print("Cleaned  :", cleaned)
print("Tokens   :", tokens)

print("=== DONE TEXT CLEANER TEST ===")