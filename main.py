from core.verdict import VerdictEngine
from core.scraper import Scraper
from database.db_manager import DatabaseManager

scraper = Scraper()
verdict = VerdictEngine()
db_manager = DatabaseManager()

class Application:
    def __init__(self) -> None:
        pass
    
    def main(self):
        user_input = input("Masukkan url berita: ")
        user_input = scraper.scrape_url(user_input)
        judul = user_input["title"]
        konten = user_input["content"]
        url = user_input["url"]

        trusted_sources = scraper.scrape_trusted_sources(judul)
        checkhoax = scraper.scrape_checkhoax(judul)
        skor = verdict.evaluate(url, konten, trusted_sources)

        if checkhoax != []:
            print("Artikel tersebut terdeteksi hoax oleh checkhoax.id")
            print("Tingkat similaritas:", verdict.calculate_similarity(konten, checkhoax))
        else:
            print("level validitas:", skor)

        db_manager.connect()
        db_manager.insert_analisis(konten,skor,verdict.give_label(skor))  # type: ignore
        print(db_manager.get_all_analisis())
    
if __name__ == "__main__":
    Application().main()