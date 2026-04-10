# Panduan Testing untuk Hoax Scanner

Dokumen ini menjelaskan bagaimana cara menjalankan dan memahami test suite untuk proyek Hoax Scanner.

## Instalasi Dependencies

Sebelum menjalankan tests, pastikan semua dependencies telah diinstal:

```bash
pip install -r requirements.txt
```

Atau install secara terpisah:

```bash
pip install pytest pytest-cov nltk Sastrawi rake-nltk
```

## Download NLTK Data

Beberapa tes memerlukan NLTK data. Jalankan perintah berikut untuk mengunduhnya:

```bash
python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt_tab')"
```

## Menjalankan Tests

### Menjalankan semua tests
```bash
pytest tests/test_extractor.py
```

### Menjalankan dengan verbose output
```bash
pytest tests/test_extractor.py -v
```

### Menjalankan test tertentu
```bash
# Test class tertentu
pytest tests/test_extractor.py::TestTextCleaner -v

# Test method tertentu
pytest tests/test_extractor.py::TestTextCleaner::test_lowercase_basic -v
```

### Menjalankan dengan coverage report
```bash
pytest tests/test_extractor.py --cov=core --cov=utils --cov-report=html
```

Output coverage report akan disimpan di folder `htmlcov/`.

### Menjalankan dengan pytest markers
```bash
# Menampilkan test collection tanpa menjalankan
pytest tests/test_extractor.py --collect-only
```

## Test Structure

Test suite terdiri dari 3 test class utama:

### 1. TestTextCleaner (22 tests)
Test untuk modul `utils/TextCleaner.py` yang menangani pembersihan teks:

- **LowerCase tests (5 tests)**: Menguji konversi ke huruf kecil
  - `test_lowercase_basic`: Konversi teks normal
  - `test_lowercase_mixed_case`: Teks dengan huruf campuran
  - `test_lowercase_already_lowercase`: Teks yang sudah lowercase
  - `test_lowercase_with_numbers`: Teks dengan angka
  - `test_lowercase_empty_string`: String kosong

- **RemoveStopWords tests (4 tests)**: Menguji penghapusan stopwords
  - `test_remove_stopwords_basic`: Penghapusan stopwords dasar
  - `test_remove_stopwords_empty_string`: String kosong
  - `test_remove_stopwords_only_stopwords`: Hanya stopwords
  - `test_remove_stopwords_with_content`: Dengan konten bermakna

- **Stemmer tests (3 tests)**: Menguji stemming kata
  - `test_stemmer_basic`: Stemming kata-kata
  - `test_stemmer_empty_string`: String kosong
  - `test_stemmer_single_word`: Satu kata

- **Tokenize tests (4 tests)**: Menguji tokenisasi teks
  - `test_tokenize_basic`: Tokenisasi normal
  - `test_tokenize_single_word`: Satu kata
  - `test_tokenize_empty_string`: String kosong
  - `test_tokenize_multiple_spaces`: Multiple spaces

- **Cleaning tests (6 tests)**: Test pipeline pembersihan lengkap
  - `test_cleaning_basic`: Pembersihan dasar
  - `test_cleaning_with_special_characters`: Karakter khusus
  - `test_cleaning_with_numbers`: Dengan angka
  - `test_cleaning_with_extra_spaces`: Multiple spaces
  - `test_cleaning_empty_string`: String kosong
  - `test_cleaning_only_special_chars`: Hanya karakter khusus

### 2. TestKeywordExtractor (16 tests)
Test untuk modul `core/KeywordExtractor.py` yang menangani ekstraksi keywords:

- **Preprocess tests (3 tests)**: Menguji preprocessing teks
  - `test_preprocess_basic`: Processing dasar
  - `test_preprocess_returns_string`: Mengembalikan string
  - `test_preprocess_empty_string`: String kosong

- **Extract tests (6 tests)**: Menguji ekstraksi keywords
  - `test_extract_returns_list`: Mengembalikan list
  - `test_extract_max_words`: Tidak melebihi Maxword
  - `test_extract_empty_text`: Teks kosong
  - `test_extract_short_text`: Teks pendek
  - `test_extract_long_text`: Teks panjang

- **BuildQuery tests (5 tests)**: Menguji pembangunan query
  - `test_buildquery_basic`: Query dasar
  - `test_buildquery_single_keyword`: Satu keyword
  - `test_buildquery_empty_list`: List kosong
  - `test_buildquery_special_characters`: Karakter khusus
  - `test_buildquery_preserves_order`: Urutan terjaga

- **Integration tests (2 tests)**: Menguji pipeline lengkap
  - `test_integration_full_pipeline`: Full pipeline test
  - `test_integration_consistency`: Konsistensi ekstraksi
  - `test_integration_preprocessing_effect`: Efek preprocessing

### 3. TestIntegrationTextCleanerKeywordExtractor (3 tests)
Test integrasi antara TextCleaner dan KeywordExtractor:

- `test_cleaner_output_used_by_extractor`: Output cleaner kompatibel
- `test_real_world_hoax_text`: Test dengan teks hoax realistis
- `test_indonesian_text_processing`: Test pemrosesan teks Indonesia

## Test Coverage

Total: **41 tests**

Breakdown:
- TextCleaner: 22 tests
- KeywordExtractor: 16 tests
- Integration: 3 tests

Setiap test dirancang untuk:
1. **Test basic functionality**: Memastikan fungsi bekerja dengan normal
2. **Test edge cases**: Memeriksa perilaku dengan input ekstrem
3. **Test integration**: Memastikan modul bekerja bersama dengan baik

## Interpretasi Hasil

### Successful Run
```
41 passed in 3.27s
```

### Failed Tests
Jika ada test yang gagal, akan ditampilkan:
```
FAILED tests/test_extractor.py::TestClassName::test_method_name
```

Untuk debugging, gunakan flag `-v` atau `--tb=long`.

## Best Practices

1. **Jalankan tests sebelum commit**: Pastikan semua tests pass
2. **Gunakan coverage**: Cek apakah code coverage sudah cukup
3. **Tulis tests untuk bug baru**: Sebelum fix, tulis test yang reproduce bug
4. **Maintain tests**: Update tests jika ada perubahan pada modul

## Troubleshooting

### ModuleNotFoundError
Pastikan working directory adalah root project dan install dependencies:
```bash
pip install -r requirements.txt
```

### Missing NLTK Data
Download NLTK data yang diperlukan:
```bash
python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt_tab')"
```

### Test Collection Errors
Pastikan file Python memiliki sintaks yang benar:
```bash
python -m py_compile utils/TextCleaner.py
python -m py_compile core/KeywordExtractor.py
```

## Tips Pengembangan

1. **Buat test sebelum implementasi (TDD)**: Membantu clarify requirements
2. **Gunakan fixtures**: Untuk setup yang sama di banyak tests
3. **Gunakan parametrize**: Untuk test multiple inputs
4. **Naming conventions**: Nama test harus descriptive

Contoh test baru dengan fixtures:
```python
@pytest.fixture
def my_fixture():
    return MyClass()

def test_something(my_fixture):
    result = my_fixture.method()
    assert result == expected_value
```
