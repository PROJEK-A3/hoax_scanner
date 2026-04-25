from utils.text_cleaner import TextCleaner
from rake_nltk import Rake
from database.logger import get_logger

logger = get_logger()


class KeywordExtractor:
    def __init__(self): # constructor untuk class keywordExtractor
        self.cleaner = TextCleaner()
        self.rake = Rake()
        self.Maxword = 10

    def Preprocess(self, text: str): # method pemanggil method dari class TextCleaner untuuk preprocess
        logger.info("PREPROCESS START")

        cleaned = self.cleaner.Cleaning(text)

        logger.info(f'PREPROCESS RESULT | text="{cleaned}"')

        return cleaned

    def Extract(self, text: str): # method untuk mengambil keyword keyword penting 
        try:
            logger.info(f'EXTRACT START | input="{text}"')

            TeksBersih = self.Preprocess(text)

            logger.info("RAKE PROCESS START")

            self.rake.extract_keywords_from_text(TeksBersih)

            logger.info("RAKE PROCESS DONE")

            phrases = self.rake.get_ranked_phrases()
            hasil = phrases[:self.Maxword]

            logger.info(f'EXTRACT RESULT | keywords={hasil}')

            return hasil

        except Exception as e:
            import traceback

            logger.error(f'EXTRACT ERROR | {repr(e)}')
            print("ERROR ASLI:", e)
            traceback.print_exc()
            
            return []

    def BuildQuery(self, Keyword: list): # methode untuk menggabungkan keyword menjadi string
        query = ' '.join(Keyword)

        logger.info(f'BUILD QUERY | query="{query}"')

        return query