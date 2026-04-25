from nltk.corpus import stopwords 
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
import re

from database.logger import get_logger

logger = get_logger()


class TextCleaner:
    def __init__(self): #Constructor untuk inisialisasi stopwords dan stemmer
        logger.info("TEXT CLEANER INIT")

        self.StopWords = set(stopwords.words('indonesian'))
        factory = StemmerFactory()
        self.stemmer = factory.create_stemmer()
        

    def LowerCase(self, text:str): # method untuk mengubah teks menjadi huruf kecil
        logger.info(f'LOWERCASE | input="{text[:30]}..."')

        result = text.lower()

        logger.info(f'LOWERCASE RESULT | "{result[:30]}..."')
        return result
    
    
    def Cleaning(self, Text:str): # method untuk membersihkan teks dari karakter(tanda baca) khusus dan angka
        logger.info(f'CLEANING START | input="{Text[:30]}..."')

        text = self.LowerCase(Text)

        hasil = re.sub('[^a-zA-Z\s]', '', text)
        hasil = re.sub('\s+', ' ', hasil).strip()

        logger.info(f'AFTER REGEX | "{hasil[:30]}..."')

        hasil = self.RemoveStopWords(hasil)
        hasil = self.Stemmer(hasil)

        logger.info(f'CLEANING RESULT | "{hasil[:30]}..."')

        return hasil
    
    
    def RemoveStopWords(self, text:str): # method untuk menghapus stopwords dari teks
        logger.info("REMOVE STOPWORDS START")

        kata = text.split()
        temp = []

        for i in kata:
            if i not in self.StopWords:
                temp.append(i)
        
        hasil =' '.join(temp)

        logger.info(f'REMOVE STOPWORDS RESULT | "{hasil[:30]}..."')
        return hasil
    
    
    def Stemmer(self, text:str): # method untuk membuat kata menjadi kata dasar
        logger.info("STEMMER START")

        kata = text.split()
        temp = []

        for i in kata:
            temp.append(self.stemmer.stem(i))
        
        hasil = ' '.join(temp)

        logger.info(f'STEMMER RESULT | "{hasil[:30]}..."')
        return hasil
    
    
    def Tokenize(self, text:str): # method unuk membuat string menjadi list kata
        logger.info(f'TOKENIZE | input="{text[:30]}..."')

        tokens = text.split()

        logger.info(f'TOKENIZE RESULT | total={len(tokens)}')
        return tokens