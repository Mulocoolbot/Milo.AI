"""
Milo AI — Intent Recognizer
Mengenali maksud/niat dari input user menggunakan pattern matching,
TF-IDF, dan cosine similarity. Semua diimplementasi dari nol.
"""

import json
import re
from utils.config import Config
from utils.text_utils import TextUtils


class IntentRecognizer:
    """Intent Recognizer — mengidentifikasi intent dari input user."""
    
    def __init__(self):
        self._intents = []
        self._pattern_docs = []    # Semua pattern sebagai dokumen untuk IDF
        self._idf_cache = {}       # Cache IDF scores
        self._load_intents()
        self._build_idf_index()
    
    def _load_intents(self):
        """Memuat data intent dari file JSON."""
        try:
            with open(Config.INTENTS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                self._intents = data.get("intents", [])
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"[IntentRecognizer] Warning: Gagal memuat intents: {e}")
            self._intents = []
    
    def _build_idf_index(self):
        """Membangun index IDF dari semua pattern."""
        # Kumpulkan semua pattern sebagai dokumen
        self._pattern_docs = []
        for intent in self._intents:
            for pattern in intent.get("patterns", []):
                words = pattern.lower().split()
                self._pattern_docs.append(words)
        
        # Hitung IDF
        if self._pattern_docs:
            self._idf_cache = TextUtils.compute_idf(self._pattern_docs)
    
    def recognize(self, tokenized_data, preprocessed_data=None):
        """
        Mengenali intent dari input yang sudah ditokenisasi.
        Menggunakan kombinasi exact match, pattern match, dan TF-IDF similarity.
        
        Args:
            tokenized_data: dict output dari Tokenizer.tokenize()
            preprocessed_data: dict output dari Preprocessor.preprocess()
        
        Returns:
            dict berisi intent yang terdeteksi beserta confidence score
        """
        words = tokenized_data.get("words", [])
        filtered = tokenized_data.get("filtered", [])
        
        if not words:
            return self._create_result("fallback", 0.0, "empty_input")
        
        # Gabungkan kata kembali menjadi string untuk pattern matching
        input_text = " ".join(words)
        
        # === Strategy 1: Exact Match ===
        exact_result = self._exact_match(input_text)
        if exact_result:
            return exact_result
        
        # === Strategy 2: Pattern Keyword Match ===
        keyword_result = self._keyword_match(words)
        
        # === Strategy 3: TF-IDF Cosine Similarity ===
        tfidf_result = self._tfidf_match(words)
        
        # === Strategy 4: Fuzzy Match (untuk typo correction) ===
        fuzzy_result = self._fuzzy_match(input_text)
        
        # === Combine Results ===
        # Pilih hasil terbaik dari semua strategi
        candidates = []
        
        if keyword_result:
            candidates.append(keyword_result)
        if tfidf_result:
            candidates.append(tfidf_result)
        if fuzzy_result:
            candidates.append(fuzzy_result)
        
        if not candidates:
            return self._create_result("fallback", 0.0, "no_match")
        
        # Ambil kandidat dengan confidence tertinggi
        best = max(candidates, key=lambda x: x["confidence"])
        
        # Cek apakah confidence melewati threshold
        if best["confidence"] < Config.CONFIDENCE_THRESHOLD:
            return self._create_result("fallback", best["confidence"], "below_threshold")
        
        return best
    
    def _exact_match(self, input_text):
        """Exact match — cek apakah input persis sama dengan salah satu pattern."""
        for intent in self._intents:
            for pattern in intent.get("patterns", []):
                if input_text.strip() == pattern.lower().strip():
                    return self._create_result(
                        intent["tag"], 1.0, "exact_match",
                        matched_pattern=pattern
                    )
        return None
    
    def _keyword_match(self, words):
        """Keyword match — menghitung overlap kata antara input dan patterns."""
        best_tag = None
        best_score = 0.0
        best_pattern = None
        
        input_set = set(words)
        
        for intent in self._intents:
            for pattern in intent.get("patterns", []):
                pattern_words = set(pattern.lower().split())
                
                # Hitung Jaccard similarity
                score = TextUtils.jaccard_similarity(input_set, pattern_words)
                
                # Bonus jika semua kata pattern ada di input
                if pattern_words.issubset(input_set) and len(pattern_words) > 0:
                    score = max(score, 0.85)
                
                # Bonus untuk substring match (hanya untuk pattern >= 3 kata)
                if len(pattern.split()) >= 2 and pattern.lower() in " ".join(words):
                    score = max(score, 0.90)
                
                # Untuk single-word pattern, harus exact word match
                if len(pattern.split()) == 1 and len(pattern) > 1:
                    if pattern.lower() in words:
                        score = max(score, 0.85)
                
                if score > best_score:
                    best_score = score
                    best_tag = intent["tag"]
                    best_pattern = pattern
        
        if best_tag and best_score > 0.1:
            return self._create_result(
                best_tag, best_score, "keyword_match",
                matched_pattern=best_pattern
            )
        return None
    
    def _tfidf_match(self, words):
        """TF-IDF match — menggunakan cosine similarity pada vektor TF-IDF."""
        if not self._idf_cache:
            return None
        
        # Hitung TF-IDF untuk input
        input_tfidf = TextUtils.compute_tfidf(words, self._idf_cache)
        
        best_tag = None
        best_score = 0.0
        best_pattern = None
        
        for intent in self._intents:
            intent_scores = []
            
            for pattern in intent.get("patterns", []):
                pattern_words = pattern.lower().split()
                pattern_tfidf = TextUtils.compute_tfidf(pattern_words, self._idf_cache)
                
                # Hitung cosine similarity
                similarity = TextUtils.cosine_similarity(input_tfidf, pattern_tfidf)
                intent_scores.append((similarity, pattern))
            
            if intent_scores:
                # Ambil score tertinggi untuk intent ini
                max_score, max_pattern = max(intent_scores, key=lambda x: x[0])
                
                if max_score > best_score:
                    best_score = max_score
                    best_tag = intent["tag"]
                    best_pattern = max_pattern
        
        if best_tag and best_score > 0.1:
            return self._create_result(
                best_tag, best_score * 0.9, "tfidf_match",
                matched_pattern=best_pattern
            )
        return None
    
    def _fuzzy_match(self, input_text):
        """Fuzzy match — menggunakan Levenshtein distance untuk typo correction."""
        best_tag = None
        best_score = 0.0
        best_pattern = None
        
        for intent in self._intents:
            for pattern in intent.get("patterns", []):
                # Hitung similarity ratio
                score = TextUtils.similarity_ratio(input_text, pattern.lower())
                
                if score > best_score:
                    best_score = score
                    best_tag = intent["tag"]
                    best_pattern = pattern
        
        if best_tag and best_score > 0.6:
            return self._create_result(
                best_tag, best_score * 0.8, "fuzzy_match",
                matched_pattern=best_pattern
            )
        return None
    
    def _create_result(self, tag, confidence, method, matched_pattern=None):
        """Membuat result dictionary yang konsisten."""
        return {
            "intent": tag,
            "confidence": round(confidence, 4),
            "method": method,
            "matched_pattern": matched_pattern,
        }
    
    def get_all_intents(self):
        """Mengembalikan daftar semua intent yang tersedia."""
        return [intent["tag"] for intent in self._intents]
    
    def get_patterns_for_intent(self, tag):
        """Mengembalikan semua pattern untuk intent tertentu."""
        for intent in self._intents:
            if intent["tag"] == tag:
                return intent.get("patterns", [])
        return []
