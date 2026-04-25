from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from utils.text_cleaner import TextCleaner

from database.logger import get_logger

logger = get_logger()


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
        logger.info("SIMILARITY ENGINE INIT")

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
        logger.info("SIMILARITY COMPUTE START")

        if not text_a or not text_b:
            logger.warning("EMPTY INPUT TEXT")
            return 0.0

        clean_a = self.cleaner.Cleaning(text_a)
        clean_b = self.cleaner.Cleaning(text_b)

        logger.info(f'CLEAN TEXT A | "{clean_a[:50]}"')
        logger.info(f'CLEAN TEXT B | "{clean_b[:50]}"')

        if not clean_a or not clean_b:
            logger.warning("CLEAN RESULT EMPTY")
            return 0.0

        try:
            matrix = self.vectorizer.fit_transform([clean_a, clean_b])
            score  = cosine_similarity(matrix[0:1], matrix[1:2])[0][0]  # type: ignore

            final_score = float(round(score, 4))
            logger.info(f"SIMILARITY SCORE | {final_score}")

            return final_score

        except Exception as e:
            logger.error(f"SIMILARITY ERROR | {repr(e)}")
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
        logger.info("RANK ARTICLES START")

        if not input_text or not articles:
            logger.warning("EMPTY INPUT OR ARTICLES")
            return []

        clean_input = self.cleaner.Cleaning(input_text)
        logger.info(f'CLEAN INPUT | "{clean_input[:50]}"')

        if not clean_input:
            logger.warning("CLEAN INPUT EMPTY")
            return []

        cleaned_articles = []
        valid_indices    = []

        for i, art in enumerate(articles):
            konten  = art.get("konten", "") or art.get("snippet", "") or art.get("judul", "")
            cleaned = self.cleaner.Cleaning(konten)

            if cleaned:
                cleaned_articles.append(cleaned)
                valid_indices.append(i)

        logger.info(f'VALID ARTICLES COUNT | {len(cleaned_articles)}')

        if not cleaned_articles:
            logger.warning("NO VALID ARTICLES")
            return []

        try:
            corpus  = [clean_input] + cleaned_articles
            matrix  = self.vectorizer.fit_transform(corpus)
            scores  = cosine_similarity(matrix[0:1], matrix[1:])[0] # type: ignore

        except Exception as e:
            logger.error(f"RANK ERROR | {repr(e)}")
            return []

        results = []
        for rank_i, orig_i in enumerate(valid_indices):
            score = float(round(scores[rank_i], 4))

            if score >= 0.05:
                article_copy = dict(articles[orig_i])
                article_copy["similarity_score"] = score
                results.append(article_copy)

                logger.info(f'ARTICLE MATCH | score={score}')

        results.sort(key=lambda x: x["similarity_score"], reverse=True)

        logger.info(f'RANK DONE | total_match={len(results)}')
        return results

    def get_top_score(self, ranked_articles: list) -> float:
        """Ambil skor similarity tertinggi dari hasil rank_articles()."""
        logger.info("GET TOP SCORE")

        if not ranked_articles:
            logger.warning("NO RANKED ARTICLES")
            return 0.0

        top_score = ranked_articles[0].get("similarity_score", 0.0)
        logger.info(f"TOP SCORE | {top_score}")

        return top_score

    def get_average_score(self, ranked_articles: list, top_n: int = 5) -> float:
        """Hitung rata-rata skor similarity dari top-N artikel."""
        logger.info("GET AVERAGE SCORE")

        if not ranked_articles:
            logger.warning("NO RANKED ARTICLES")
            return 0.0

        top = ranked_articles[:top_n]

        avg = float(round(
            sum(a["similarity_score"] for a in top) / len(top), 4
        ))

        logger.info(f"AVERAGE SCORE | {avg}")
        return avg