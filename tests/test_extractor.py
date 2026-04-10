import pytest
from core.KeywordExtractor import KeywordExtractor
from utils.TextCleaner import TextCleaner


class TestTextCleaner:
    """Test suite untuk TextCleaner class"""
    
    @pytest.fixture
    def cleaner(self):
        """Fixture untuk inisialisasi TextCleaner"""
        return TextCleaner()
    
    # Test LowerCase method
    def test_lowercase_basic(self, cleaner):
        """Test konversi teks ke huruf kecil"""
        result = cleaner.LowerCase("HELLO WORLD")
        assert result == "hello world"
    
    def test_lowercase_mixed_case(self, cleaner):
        """Test konversi teks dengan huruf campuran"""
        result = cleaner.LowerCase("HeLLo WoRLd")
        assert result == "hello world"
    
    def test_lowercase_already_lowercase(self, cleaner):
        """Test pada teks yang sudah huruf kecil"""
        result = cleaner.LowerCase("hello world")
        assert result == "hello world"
    
    def test_lowercase_with_numbers(self, cleaner):
        """Test konversi dengan angka"""
        result = cleaner.LowerCase("HELLO123WORLD")
        assert result == "hello123world"
    
    def test_lowercase_empty_string(self, cleaner):
        """Test dengan string kosong"""
        result = cleaner.LowerCase("")
        assert result == ""
    
    # Test RemoveStopWords method
    def test_remove_stopwords_basic(self, cleaner):
        """Test penghapusan stopwords dasar"""
        result = cleaner.RemoveStopWords("ini adalah sebuah test")
        # 'ini', 'adalah', 'sebuah' adalah stopwords
        assert "test" in result
        assert "ini" not in result
    
    def test_remove_stopwords_empty_string(self, cleaner):
        """Test dengan string kosong"""
        result = cleaner.RemoveStopWords("")
        assert result == ""
    
    def test_remove_stopwords_only_stopwords(self, cleaner):
        """Test dengan string yang hanya berisi stopwords"""
        result = cleaner.RemoveStopWords("yang dan atau")
        assert result.strip() == ""
    
    def test_remove_stopwords_with_content(self, cleaner):
        """Test dengan konten yang sesuai"""
        result = cleaner.RemoveStopWords("saya makan nasi")
        assert "makan" in result
        assert "nasi" in result
    
    # Test Stemmer method
    def test_stemmer_basic(self, cleaner):
        """Test stemming kata dasar"""
        result = cleaner.Stemmer("mengkonsumsi konsumsi konsumen")
        words = result.split()
        # Semua kata harus di-stem
        assert len(words) == 3
    
    def test_stemmer_empty_string(self, cleaner):
        """Test stemmer dengan string kosong"""
        result = cleaner.Stemmer("")
        assert result == ""
    
    def test_stemmer_single_word(self, cleaner):
        """Test stemmer dengan satu kata"""
        result = cleaner.Stemmer("makan")
        assert isinstance(result, str)
        assert len(result) > 0
    
    # Test Tokenize method
    def test_tokenize_basic(self, cleaner):
        """Test tokenisasi dasar"""
        result = cleaner.Tokenize("hello world test")
        assert result == ["hello", "world", "test"]
    
    def test_tokenize_single_word(self, cleaner):
        """Test tokenisasi satu kata"""
        result = cleaner.Tokenize("hello")
        assert result == ["hello"]
    
    def test_tokenize_empty_string(self, cleaner):
        """Test tokenisasi string kosong"""
        result = cleaner.Tokenize("")
        assert result == []
    
    def test_tokenize_multiple_spaces(self, cleaner):
        """Test tokenisasi dengan multiple spaces"""
        result = cleaner.Tokenize("hello  world   test")
        assert len(result) >= 3
    
    # Test Cleaning method (Integration test)
    def test_cleaning_basic(self, cleaner):
        """Test pembersihan teks dasar"""
        text = "Ini ADALAH sebuah TEST string!!!"
        result = cleaner.Cleaning(text)
        # Hasil harus lowercase dan tanpa tanda baca
        assert result == result.lower()
        assert "!" not in result
        assert "?" not in result
    
    def test_cleaning_with_special_characters(self, cleaner):
        """Test pembersihan dengan karakter khusus"""
        text = "Hello@#$%World!!!???"
        result = cleaner.Cleaning(text)
        assert "@" not in result
        assert "#" not in result
        assert "!" not in result
    
    def test_cleaning_with_numbers(self, cleaner):
        """Test pembersihan dengan angka"""
        text = "Hello123World456"
        result = cleaner.Cleaning(text)
        # Angka harus dihapus
        assert "123" not in result
        assert "456" not in result
    
    def test_cleaning_with_extra_spaces(self, cleaner):
        """Test pembersihan dengan multiple spaces"""
        text = "Hello     World     Test"
        result = cleaner.Cleaning(text)
        # Multiple spaces harus dikonversi jadi single space
        assert "     " not in result
    
    def test_cleaning_empty_string(self, cleaner):
        """Test pembersihan string kosong"""
        result = cleaner.Cleaning("")
        assert result == ""
    
    def test_cleaning_only_special_chars(self, cleaner):
        """Test pembersihan dengan hanya karakter khusus"""
        result = cleaner.Cleaning("!@#$%^&*()")
        assert result == ""


class TestKeywordExtractor:
    """Test suite untuk KeywordExtractor class"""
    
    @pytest.fixture
    def extractor(self):
        """Fixture untuk inisialisasi KeywordExtractor"""
        return KeywordExtractor()
    
    @pytest.fixture
    def sample_text(self):
        """Sample text untuk testing"""
        return "Berita hoax adalah berita palsu yang menyebarkan informasi tidak akurat"
    
    # Test Preprocess method
    def test_preprocess_basic(self, extractor, sample_text):
        """Test preprocessing dasar"""
        result = extractor.Preprocess(sample_text)
        # Hasil harus string
        assert isinstance(result, str)
        # Hasilnya harus lebih pendek atau sama dengan input (karena ada pembersihan)
        assert len(result) <= len(sample_text)
    
    def test_preprocess_returns_string(self, extractor):
        """Test bahwa preprocess mengembalikan string"""
        result = extractor.Preprocess("HELLO WORLD!!!")
        assert isinstance(result, str)
    
    def test_preprocess_empty_string(self, extractor):
        """Test preprocess dengan string kosong"""
        result = extractor.Preprocess("")
        assert result == ""
    
    # Test Extract method
    def test_extract_returns_list(self, extractor, sample_text):
        """Test bahwa extract mengembalikan list"""
        result = extractor.Extract(sample_text)
        assert isinstance(result, list)
    
    def test_extract_max_words(self, extractor, sample_text):
        """Test bahwa extract tidak melebihi Maxword"""
        result = extractor.Extract(sample_text)
        assert len(result) <= extractor.Maxword
    
    def test_extract_empty_text(self, extractor):
        """Test extract dengan teks kosong"""
        result = extractor.Extract("")
        assert isinstance(result, list)
    
    def test_extract_short_text(self, extractor):
        """Test extract dengan teks pendek"""
        result = extractor.Extract("berita hoax")
        assert isinstance(result, list)
    
    def test_extract_long_text(self, extractor):
        """Test extract dengan teks panjang"""
        long_text = "Hoax adalah informasi palsu yang menyebarkan berita bohong. " * 10
        result = extractor.Extract(long_text)
        assert isinstance(result, list)
        # Tidak boleh lebih dari Maxword
        assert len(result) <= extractor.Maxword
    
    # Test BuildQuery method
    def test_buildquery_basic(self, extractor):
        """Test buildquery dasar"""
        keywords = ["hoax", "berita", "palsu"]
        result = extractor.BuildQuery(keywords)
        assert result == "hoax berita palsu"
    
    def test_buildquery_single_keyword(self, extractor):
        """Test buildquery dengan satu keyword"""
        keywords = ["hoax"]
        result = extractor.BuildQuery(keywords)
        assert result == "hoax"
    
    def test_buildquery_empty_list(self, extractor):
        """Test buildquery dengan list kosong"""
        result = extractor.BuildQuery([])
        assert result == ""
    
    def test_buildquery_special_characters(self, extractor):
        """Test buildquery dengan karakter khusus"""
        keywords = ["hoax!", "berita@", "palsu#"]
        result = extractor.BuildQuery(keywords)
        assert "hoax!" in result
        assert "berita@" in result
    
    def test_buildquery_preserves_order(self, extractor):
        """Test bahwa buildquery mempertahankan urutan"""
        keywords = ["pertama", "kedua", "ketiga"]
        result = extractor.BuildQuery(keywords)
        assert result == "pertama kedua ketiga"
    
    # Integration tests
    def test_integration_full_pipeline(self, extractor, sample_text):
        """Test full pipeline dari text hingga query"""
        # Preprocess
        preprocessed = extractor.Preprocess(sample_text)
        assert isinstance(preprocessed, str)
        
        # Extract
        keywords = extractor.Extract(sample_text)
        assert isinstance(keywords, list)
        assert len(keywords) <= extractor.Maxword
        
        # BuildQuery
        if keywords:
            query = extractor.BuildQuery(keywords)
            assert isinstance(query, str)
    
    def test_integration_consistency(self, extractor, sample_text):
        """Test konsistensi ekstraksi keywords"""
        result1 = extractor.Extract(sample_text)
        result2 = extractor.Extract(sample_text)
        # Hasil ekstraksi harus konsisten
        assert result1 == result2
    
    def test_integration_preprocessing_effect(self, extractor):
        """Test efek preprocessing pada ekstraksi"""
        text1 = "HOAX BERITA PALSU"
        text2 = "hoax berita palsu"
        
        result1 = extractor.Extract(text1)
        result2 = extractor.Extract(text2)
        # Hasil harus sama karena preprocessing mengkonversi ke lowercase
        assert len(result1) == len(result2)


class TestIntegrationTextCleanerKeywordExtractor:
    """Integration tests untuk TextCleaner dan KeywordExtractor"""
    
    @pytest.fixture
    def resources(self):
        """Fixture untuk kedua class"""
        return {
            "cleaner": TextCleaner(),
            "extractor": KeywordExtractor()
        }
    
    def test_cleaner_output_used_by_extractor(self, resources):
        """Test bahwa output cleaner kompatibel dengan extractor"""
        text = "Ini adalah TEKS dengan TANDA BACA!!!"
        
        cleaner = resources["cleaner"]
        cleaned = cleaner.Cleaning(text)
        
        extractor = resources["extractor"]
        # Cleaned text harus bisa diproses oleh extractor
        result = extractor.Extract(cleaned)
        assert isinstance(result, list)
    
    def test_real_world_hoax_text(self, resources):
        """Test dengan teks hoax yang realistis"""
        hoax_text = """
        Berita bohong! Presiden telah mengumumkan kebijakan baru yang sangat penting.
        Informasi palsu ini tersebar di media sosial dengan cepat.
        Hoax seperti ini dapat menyebabkan kepanikan di masyarakat.
        """
        
        extractor = resources["extractor"]
        result = extractor.Extract(hoax_text)
        
        assert isinstance(result, list)
        assert len(result) <= 10
    
    def test_indonesian_text_processing(self, resources):
        """Test pemrosesan teks Indonesia"""
        indonesian_text = "Saya makan nasi kuning di rumah nenek dengan keluarga"
        
        cleaner = resources["cleaner"]
        extractor = resources["extractor"]
        
        # Process teks
        preprocessed = extractor.Preprocess(indonesian_text)
        keywords = extractor.Extract(indonesian_text)
        
        assert isinstance(preprocessed, str)
        assert isinstance(keywords, list)
