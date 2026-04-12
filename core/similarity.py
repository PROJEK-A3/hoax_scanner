from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from utils.text_cleaner import TextCleaner

class SimilarityEngine:
    """
    Menghitung kemiripan antara teks berita input dengan artikel pembanding
    menggunakan TF-IDF dan Cosine Similarity.

    Cara kerja:
        1. Teks input + semua artikel dijadikan satu corpus
        2. TfidfVectorizer mengubah corpus menjadi matriks vektor
        3. Cosine similarity dihitung antara vektor input vs tiap artikel
        4. Skor dinormalisasi ke rentang 0.0 – 1.0
    """

    def __init__(self):
        self.cleaner = TextCleaner()
        self.vectorizer = TfidfVectorizer(
            max_features = 5000,
            ngram_range  = (1, 2),
            min_df       = 1,
            sublinear_tf = True,
            analyzer     = "word",
            token_pattern= r"(?u)\b\w+\b",
        )

    def compute(self, text_a: str, text_b: str) -> float:
        """
        Hitung cosine similarity antara dua teks.

        Parameters:
            text_a: Teks pertama (input user)
            text_b: Teks kedua (artikel pembanding)

        Returns:
            float: Skor kemiripan 0.0 – 1.0
        """
        if not text_a or not text_b:
            return 0.0

        clean_a = self.cleaner.Cleaning(text_a)
        clean_b = self.cleaner.Cleaning(text_b)

        if not clean_a or not clean_b:
            return 0.0

        try:
            matrix = self.vectorizer.fit_transform([clean_a, clean_b])
            score  = cosine_similarity(matrix[0:1], matrix[1:2])[0][0]  # type: ignore
            return float(round(score, 4))
        except Exception:
            return 0.0

    def rank_articles(self, input_text: str, articles: list) -> list:
        """
        Bandingkan teks input dengan banyak artikel sekaligus.
        Lebih efisien dari compute() karena vectorizer di-fit satu kali.

        Parameters:
            input_text: Teks berita yang ingin diverifikasi
            articles:   list[dict] dengan key 'judul', 'konten', 'url', 'sumber'

        Returns:
            list[dict]: Artikel + key 'similarity_score', urut skor tertinggi,
                        hanya artikel dengan skor >= 0.05
        """
        if not input_text or not articles:
            return []

        clean_input = self.cleaner.Cleaning(input_text)
        if not clean_input:
            return []

        cleaned_articles = []
        valid_indices    = []

        for i, art in enumerate(articles):
            konten  = art.get("konten", "") or art.get("snippet", "") or art.get("judul", "")
            cleaned = self.cleaner.Cleaning(konten)
            if cleaned:
                cleaned_articles.append(cleaned)
                valid_indices.append(i)

        if not cleaned_articles:
            return []

        try:
            corpus  = [clean_input] + cleaned_articles
            matrix  = self.vectorizer.fit_transform(corpus)
            scores  = cosine_similarity(matrix[0:1], matrix[1:])[0] # type: ignore
        except Exception as e:
            print(f"[SimilarityEngine] Error: {e}")
            return []

        results = []
        for rank_i, orig_i in enumerate(valid_indices):
            score = float(round(scores[rank_i], 4))
            if score >= 0.05:
                article_copy = dict(articles[orig_i])
                article_copy["similarity_score"] = score
                results.append(article_copy)

        results.sort(key=lambda x: x["similarity_score"], reverse=True)
        return results

    def get_top_score(self, ranked_articles: list) -> float:
        """Ambil skor similarity tertinggi dari hasil rank_articles()."""
        if not ranked_articles:
            return 0.0
        return ranked_articles[0].get("similarity_score", 0.0)

    def get_average_score(self, ranked_articles: list, top_n: int = 5) -> float:
        """Hitung rata-rata skor similarity dari top-N artikel."""
        if not ranked_articles:
            return 0.0
        top = ranked_articles[:top_n]
        return float(round(
            sum(a["similarity_score"] for a in top) / len(top), 4
        ))