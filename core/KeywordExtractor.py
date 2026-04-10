from utils.TextCleaner import TextCleaner
from rake_nltk import Rake

class KeywordExtractor:
    def __init__(self):
        self.cleaner = TextCleaner()
        self.rake = Rake()
        self.Maxword = 10
    
    def Preprocess(self, text):
        return self.cleaner.Cleaning(text)
        