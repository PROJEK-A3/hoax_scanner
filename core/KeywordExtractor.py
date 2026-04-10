from utils.TextCleaner import TextCleaner
from rake_nltk import Rake

class KeywordExtractor: 
    def __init__(self): # constructor untuk class keywordExtractor
        self.cleaner = TextCleaner()
        self.rake = Rake()
        self.Maxword = 10
    
    def Preprocess(self, text): # method pemanggil method dari class TextCleaner untuuk preprocess
        return self.cleaner.Cleaning(text)
        
    def Extract(self, text): # method untuk mengambil keyword keyword penting 
        TeksBersih = self.Preprocess(text)
        self.rake.extract_keywords_from_text(TeksBersih)
        phrases = self.rake.get_ranked_phrases()
        hasil = phrases[:self.max_keywords]
        return hasil
    
    def BuildQuery(self, Keyword): # methode untuk menggabungkan keyword menjadi string
        return ' '.join(Keyword)