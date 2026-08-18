"""
Milo AI — Text Utilities
Fungsi-fungsi utilitas untuk pemrosesan teks, termasuk similarity
calculation dan string matching — semua diimplementasi dari nol.
"""

import math
from collections import Counter


class TextUtils:
    """Utilitas pemrosesan teks untuk Milo AI."""
    
    @staticmethod
    def levenshtein_distance(s1, s2):
        """
        Menghitung Levenshtein Distance (edit distance) antara dua string.
        Mengukur berapa banyak operasi (insert, delete, replace) yang diperlukan
        untuk mengubah s1 menjadi s2.
        
        Digunakan untuk typo correction.
        """
        if len(s1) < len(s2):
            return TextUtils.levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                # Biaya operasi
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    @staticmethod
    def similarity_ratio(s1, s2):
        """
        Menghitung rasio kemiripan antara dua string (0.0 - 1.0).
        Berdasarkan Levenshtein distance.
        """
        if not s1 and not s2:
            return 1.0
        if not s1 or not s2:
            return 0.0
        
        distance = TextUtils.levenshtein_distance(s1.lower(), s2.lower())
        max_len = max(len(s1), len(s2))
        
        return 1.0 - (distance / max_len)
    
    @staticmethod
    def cosine_similarity(vec1, vec2):
        """
        Menghitung Cosine Similarity antara dua vektor (dictionary).
        Digunakan untuk membandingkan representasi TF-IDF dari dua teks.
        
        Returns: float antara 0.0 (tidak mirip) dan 1.0 (identik)
        """
        # Dapatkan semua kata unik
        all_words = set(vec1.keys()) | set(vec2.keys())
        
        # Hitung dot product
        dot_product = sum(vec1.get(word, 0) * vec2.get(word, 0) for word in all_words)
        
        # Hitung magnitude
        magnitude1 = math.sqrt(sum(v ** 2 for v in vec1.values()))
        magnitude2 = math.sqrt(sum(v ** 2 for v in vec2.values()))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    @staticmethod
    def jaccard_similarity(set1, set2):
        """
        Menghitung Jaccard Similarity antara dua set.
        J(A,B) = |A ∩ B| / |A ∪ B|
        
        Returns: float antara 0.0 dan 1.0
        """
        if isinstance(set1, list):
            set1 = set(set1)
        if isinstance(set2, list):
            set2 = set(set2)
        
        if not set1 and not set2:
            return 1.0
        
        intersection = set1 & set2
        union = set1 | set2
        
        return len(intersection) / len(union) if union else 0.0
    
    @staticmethod
    def compute_tf(word_list):
        """
        Menghitung Term Frequency (TF) untuk setiap kata.
        TF(t) = (Jumlah kemunculan kata t) / (Total jumlah kata)
        
        Returns: dict {kata: tf_score}
        """
        tf_dict = {}
        word_count = Counter(word_list)
        total_words = len(word_list)
        
        if total_words == 0:
            return tf_dict
        
        for word, count in word_count.items():
            tf_dict[word] = count / total_words
        
        return tf_dict
    
    @staticmethod
    def compute_idf(documents):
        """
        Menghitung Inverse Document Frequency (IDF) untuk semua kata.
        IDF(t) = log(Total dokumen / Jumlah dokumen yang mengandung kata t)
        
        Args:
            documents: list of list of words
        
        Returns: dict {kata: idf_score}
        """
        idf_dict = {}
        total_docs = len(documents)
        
        if total_docs == 0:
            return idf_dict
        
        # Hitung di berapa dokumen setiap kata muncul
        all_words = set()
        for doc in documents:
            all_words.update(set(doc))
        
        for word in all_words:
            doc_count = sum(1 for doc in documents if word in doc)
            # Gunakan smoothed IDF untuk menghindari division by zero
            idf_dict[word] = math.log((total_docs + 1) / (doc_count + 1)) + 1
        
        return idf_dict
    
    @staticmethod
    def compute_tfidf(word_list, idf_dict):
        """
        Menghitung TF-IDF untuk sebuah dokumen.
        TF-IDF = TF * IDF
        
        Returns: dict {kata: tfidf_score}
        """
        tf = TextUtils.compute_tf(word_list)
        tfidf = {}
        
        for word, tf_score in tf.items():
            idf_score = idf_dict.get(word, 1.0)
            tfidf[word] = tf_score * idf_score
        
        return tfidf
    
    @staticmethod
    def find_closest_match(target, candidates, threshold=0.6):
        """
        Menemukan string paling mirip dari daftar kandidat.
        Digunakan untuk typo correction.
        
        Args:
            target: string target
            candidates: list of string kandidat
            threshold: minimum similarity ratio
        
        Returns: (best_match, similarity_score) atau (None, 0.0)
        """
        best_match = None
        best_score = 0.0
        
        for candidate in candidates:
            score = TextUtils.similarity_ratio(target, candidate)
            if score > best_score and score >= threshold:
                best_match = candidate
                best_score = score
        
        return best_match, best_score
    
    @staticmethod
    def extract_keywords(text, stopwords=None):
        """
        Mengekstrak kata-kata kunci dari teks (menghilangkan stopwords).
        
        Args:
            text: string teks input
            stopwords: set kata-kata yang diabaikan
        
        Returns: list of keywords
        """
        if stopwords is None:
            stopwords = set()
        
        words = text.lower().split()
        keywords = [w for w in words if w not in stopwords and len(w) > 1]
        
        return keywords
    
    @staticmethod
    def generate_ngrams(words, n=2):
        """
        Menghasilkan n-gram dari daftar kata.
        
        Args:
            words: list of words
            n: ukuran n-gram (default: bigram)
        
        Returns: list of n-gram strings
        """
        if len(words) < n:
            return []
        
        ngrams = []
        for i in range(len(words) - n + 1):
            ngram = " ".join(words[i:i + n])
            ngrams.append(ngram)
        
        return ngrams
    
    @staticmethod
    def normalize_text(text):
        """
        Normalisasi teks dasar: lowercase, hapus whitespace berlebih.
        """
        if not text:
            return ""
        
        text = text.lower().strip()
        # Hapus multiple spaces
        text = " ".join(text.split())
        
        return text
