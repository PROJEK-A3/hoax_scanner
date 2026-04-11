from utils.text_cleaner import TextCleaner
from rake_nltk import Rake

class KeywordExtractor: 
    def __init__(self): # constructor untuk class keywordExtractor
        self.cleaner = TextCleaner()
        self.rake = Rake()
        self.Maxword = 10
    
    def Preprocess(self, text:str): # method pemanggil method dari class TextCleaner untuuk preprocess
        return self.cleaner.Cleaning(text)
        
    def Extract(self, text:str): # method untuk mengambil keyword keyword penting 
        TeksBersih = self.Preprocess(text)
        self.rake.extract_keywords_from_text(TeksBersih)
        phrases = self.rake.get_ranked_phrases()
        hasil = phrases[:self.Maxword]
        return hasil
    
    def BuildQuery(self, Keyword: list): # methode untuk menggabungkan keyword menjadi string
        return ' '.join(Keyword)