from nltk.corpus import stopwords
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
import re

class TextCleaner:
    def Cosntructor (self): #Constructor untuk inisialisasi stopwords dan stemmer
        self.StopWords = set(stopwords.words('indonesian'))
        factory = StemmerFactory()
        self.stemmer = factory.create_stemmer()
        

    def LowerCase(self, text): # method untuk mengubah teks menjadi huruf kecil
        return text.lower()
    
    def Cleaning(self, Text): # method untuk membersihkan teks dari karakter(tanda baca) khusus dan angka
        text = self.LowerCase(Text)
        hasil = re.sub('[^a-zA-Z\s]', '', text)
        hasil = re.sub('\s+', ' ', hasil).strip()
        return hasil
    
    def RemoveStopWords(self, text): # method untuk menghapus stopwords dari teks
        kata = text.split()
        temp = []
        for i in kata:
            if i not in self.StopWords:
                temp.append(i)
        
        hasil =' '.join(temp)
        return hasil
    
    def Stemmer(self, text): # method untuk membuat kata menjadi kata dasar
        kata = text.split()
        temp = []
        for i in kata:
            temp.append(self.stemmer.stem(i))
        
        hasil = ' '.join(temp)
        return hasil
    
    
    
    