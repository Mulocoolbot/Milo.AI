"""
Milo AI — Advanced Intent Recognizer
Mengenali maksud/niat dari input user menggunakan analisis klausa,
phrase contiguity, N-gram matching, TF-IDF cosine similarity, dan semantic guards.
Semua diimplementasi dari nol secara murni menggunakan Python.
"""

import json
import re
from utils.config import Config
from utils.text_utils import TextUtils


class IntentRecognizer:
    """Advanced Intent Recognizer — cerdas, sadar klausa, dan presisi tinggi."""
    
    # Kata sambung kontras yang menandai klausa fokus/utama
    CONTRAST_CONJUNCTIONS = ["tapi", "tetapi", "namun", "padahal", "cuma", "hanya saja", "sedangkan", "melainkan"]
    
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
        self._pattern_docs = []
        for intent in self._intents:
            for pattern in intent.get("patterns", []):
                words = pattern.lower().split()
                self._pattern_docs.append(words)
        
        if self._pattern_docs:
            self._idf_cache = TextUtils.compute_idf(self._pattern_docs)
    
    def recognize(self, tokenized_data, preprocessed_data=None):
        """
        Mengenali intent dari input yang sudah dipreprocess & ditokenisasi.
        
        Pipeline:
        1. Analisis Klausa (Clause Analysis)
        2. Exact Phrase Match
        3. Contiguous N-Gram / Phrase Proximity Match
        4. TF-IDF Match dengan Span-Distance Penalty
        5. Semantic Intent Guards (mencegah false positive)
        
        Args:
            tokenized_data: dict output dari Tokenizer
            preprocessed_data: dict output dari Preprocessor
        
        Returns:
            dict berisi tag intent, confidence score, dan metadata
        """
        words = tokenized_data.get("words", [])
        if not words:
            return self._create_result("fallback", 0.0, "empty_input")
        
        raw_text = " ".join(words).lower()
        original_text = ""
        if preprocessed_data:
            original_text = preprocessed_data.get("original", "").lower()
        
        # === 1. Analisis Klausa (Deteksi fokus kalimat) ===
        focal_clause, clauses = self._extract_clauses(raw_text)
        
        # === 2. Exact Match pada Full Text & Focal Clause ===
        exact_full = self._exact_match(raw_text)
        if exact_full:
            return exact_full
        
        if focal_clause and focal_clause != raw_text:
            exact_focal = self._exact_match(focal_clause)
            if exact_focal:
                exact_focal["confidence"] = 0.98
                exact_focal["method"] = "exact_focal_clause"
                return exact_focal
        
        # === 3. Phrase & N-Gram Proximity Match ===
        # Evaluasi terhadap kalimat penuh dan klausa fokus
        phrase_candidates = []
        
        # A. Cek klausa fokus terlebih dahulu (bobot lebih tinggi jika cocok)
        if focal_clause and focal_clause != raw_text:
            focal_res = self._phrase_proximity_match(focal_clause.split(), focal_clause)
            if focal_res:
                focal_res["confidence"] = min(1.0, focal_res["confidence"] * 1.15)
                focal_res["method"] = "focal_phrase_match"
                phrase_candidates.append(focal_res)
        
        # B. Cek seluruh kalimat
        full_res = self._phrase_proximity_match(words, raw_text)
        if full_res:
            phrase_candidates.append(full_res)
        
        # === 4. TF-IDF Match dengan Proximity Penalty ===
        tfidf_res = self._tfidf_match_with_span_penalty(words, raw_text)
        if tfidf_res:
            phrase_candidates.append(tfidf_res)
        
        # === 5. Fuzzy Match untuk typo correction ===
        fuzzy_res = self._fuzzy_match(raw_text)
        if fuzzy_res:
            phrase_candidates.append(fuzzy_res)
        
        if not phrase_candidates:
            return self._create_result("fallback", 0.0, "no_match")
        
        # === 6. Terapkan Semantic Intent Guards & Filter Candidates ===
        valid_candidates = []
        for cand in phrase_candidates:
            if self._passes_semantic_guard(cand["intent"], raw_text, words):
                valid_candidates.append(cand)
        
        if not valid_candidates:
            return self._create_result("fallback", 0.0, "failed_semantic_guards")
        
        # Ambil kandidat dengan skor tertinggi
        best = max(valid_candidates, key=lambda x: x["confidence"])
        
        # Jika kalimat panjang dan ada greeting di awal, jangan jadikan greeting sebagai intent utama
        if best["intent"] == "greeting" and len(words) > 3 and len(valid_candidates) > 1:
            non_greetings = [c for c in valid_candidates if c["intent"] != "greeting"]
            if non_greetings:
                best = max(non_greetings, key=lambda x: x["confidence"])
        
        if best["confidence"] < Config.CONFIDENCE_THRESHOLD:
            return self._create_result("fallback", best["confidence"], "below_threshold")
        
        return best
    
    def _extract_clauses(self, text):
        """Memecah kalimat menjadi klausa-klausa berdasarkan kata sambung kontras."""
        pattern = r'\b(?:' + '|'.join(self.CONTRAST_CONJUNCTIONS) + r')\b'
        parts = re.split(pattern, text)
        clauses = [p.strip() for p in parts if p.strip()]
        
        # Klausa terakhir biasanya adalah fokus utama dari ungkapan pengguna
        focal_clause = clauses[-1] if clauses else text
        return focal_clause, clauses
    
    def _exact_match(self, input_text):
        """Exact match terhadap pattern intent."""
        clean_input = input_text.strip()
        for intent in self._intents:
            for pattern in intent.get("patterns", []):
                if clean_input == pattern.lower().strip():
                    return self._create_result(
                        intent["tag"], 1.0, "exact_match",
                        matched_pattern=pattern
                    )
        return None
    
    def _phrase_proximity_match(self, words, input_text):
        """
        Mencocokkan pattern berdasarkan frasa utuh dan kedekatan posisi kata (proximity).
        Mencegah kata-kata terpisah jauh saling memicu intent palsu.
        """
        best_tag = None
        best_score = 0.0
        best_pattern = None
        
        input_lower = input_text.lower()
        
        for intent in self._intents:
            for pattern in intent.get("patterns", []):
                pattern_lower = pattern.lower().strip()
                pattern_words = pattern_lower.split()
                
                # 1. Exact Substring Match (Frasa utuh ada di dalam teks)
                if f" {pattern_lower} " in f" {input_lower} " or input_lower.startswith(pattern_lower) or input_lower.endswith(pattern_lower):
                    # Semakin panjang frasa, semakin tinggi kepercayaan
                    score = 0.95 if len(pattern_words) >= 2 else 0.88
                    if score > best_score:
                        best_score = score
                        best_tag = intent["tag"]
                        best_pattern = pattern
                    continue
                
                # 2. Sequential N-gram Match
                if len(pattern_words) >= 2:
                    matched_count = 0
                    positions = []
                    
                    for p_word in pattern_words:
                        if p_word in words:
                            matched_count += 1
                            positions.append(words.index(p_word))
                    
                    # Jika sebagian besar kata dalam pattern cocok
                    if matched_count >= len(pattern_words) * 0.75 and len(positions) >= 2:
                        # Hitung rentang posisi (span)
                        span = max(positions) - min(positions) + 1
                        expected_span = len(pattern_words)
                        
                        # Span penalty: jika kata-katanya berpencar jauh, skor turun drastis
                        span_ratio = expected_span / span
                        if span_ratio >= 0.5:  # Kata-kata relatif berdekatan
                            jaccard = matched_count / (len(pattern_words) + len(words) - matched_count)
                            score = 0.70 + (0.25 * span_ratio)
                            if score > best_score:
                                best_score = score
                                best_tag = intent["tag"]
                                best_pattern = pattern
        
        if best_tag and best_score > 0.35:
            return self._create_result(
                best_tag, best_score, "phrase_proximity_match",
                matched_pattern=best_pattern
            )
        return None
    
    def _tfidf_match_with_span_penalty(self, words, input_text):
        """TF-IDF Cosine Similarity dengan penalti jarak kata (span penalty)."""
        if not self._idf_cache:
            return None
        
        input_tfidf = TextUtils.compute_tfidf(words, self._idf_cache)
        best_tag = None
        best_score = 0.0
        best_pattern = None
        
        for intent in self._intents:
            intent_scores = []
            
            for pattern in intent.get("patterns", []):
                pattern_words = pattern.lower().split()
                pattern_tfidf = TextUtils.compute_tfidf(pattern_words, self._idf_cache)
                
                raw_similarity = TextUtils.cosine_similarity(input_tfidf, pattern_tfidf)
                
                # Cek overlap posisi kata untuk mencegah false match kata acak
                common_words = set(words) & set(pattern_words)
                if common_words:
                    if len(common_words) >= 2:
                        positions = [words.index(w) for w in common_words]
                        span = max(positions) - min(positions) + 1
                        proximity_factor = min(1.0, len(pattern_words) / span)
                    else:
                        proximity_factor = 0.7
                    
                    adjusted_similarity = raw_similarity * proximity_factor
                    intent_scores.append((adjusted_similarity, pattern))
            
            if intent_scores:
                max_score, max_pattern = max(intent_scores, key=lambda x: x[0])
                if max_score > best_score:
                    best_score = max_score
                    best_tag = intent["tag"]
                    best_pattern = max_pattern
        
        if best_tag and best_score > 0.35:
            return self._create_result(
                best_tag, best_score * 0.85, "tfidf_span_match",
                matched_pattern=best_pattern
            )
        return None
    
    def _fuzzy_match(self, input_text):
        """Fuzzy matching menggunakan Levenshtein distance."""
        best_tag = None
        best_score = 0.0
        best_pattern = None
        
        for intent in self._intents:
            for pattern in intent.get("patterns", []):
                score = TextUtils.similarity_ratio(input_text, pattern.lower())
                if score > best_score and score >= 0.70:
                    best_score = score
                    best_tag = intent["tag"]
                    best_pattern = pattern
        
        if best_tag:
            return self._create_result(
                best_tag, best_score * 0.8, "fuzzy_match",
                matched_pattern=best_pattern
            )
        return None
    
    def _passes_semantic_guard(self, intent_tag, input_text, words):
        """
        Semantic Guards: Aturan ketat untuk memvalidasi apakah intent masuk akal
        secara semantik terhadap konteks kalimat user.
        """
        text_lower = input_text.lower()
        word_set = set(words)
        
        # Guard 1: user_name_ask harus memiliki kata 'nama' atau frasa spesifik 'who am i'
        if intent_tag == "user_name_ask":
            name_indicators = {"nama", "namaku", "namamu", "panggilanku", "name"}
            if not (word_set & name_indicators or "who am i" in text_lower):
                return False
            # Jika ada kata 'ke siapa', 'sama siapa', 'dengan siapa' -> bukan tanya nama user!
            if re.search(r'\b(ke|sama|dengan|pada)\s+siapa\b', text_lower):
                return False
        
        # Guard 2: identity_ask harus ditujukan kepada bot ('kamu siapa', 'siapa kamu', 'siapa milo')
        if intent_tag == "identity_ask":
            if not re.search(r'\b(kamu|lu|lo|kau|milo|anda)\b', text_lower) and "who are you" not in text_lower:
                return False
        
        # Guard 3: curhat_need diprioritaskan jika ada kata 'curhat', 'cerita', 'uneg', 'bingung ke siapa'
        if "curhat" in text_lower or re.search(r'\b(bingung|mau)\s+(cerita|curhat)\b', text_lower):
            if intent_tag in ("how_are_you", "user_name_ask", "identity_ask"):
                return False
        
        # Guard 4: how_are_you harus mengandung 'kabar' atau frasa 'how are you'
        if intent_tag == "how_are_you":
            if not ({"kabar", "kabarmu", "kabarnya"} & word_set or "how are you" in text_lower or "sehat" in word_set):
                return False
        
        return True
    
    def _create_result(self, tag, confidence, method, matched_pattern=None):
        """Membuat result dictionary."""
        return {
            "intent": tag,
            "confidence": round(confidence, 4),
            "method": method,
            "matched_pattern": matched_pattern,
        }
    
    def get_all_intents(self):
        """Mengembalikan daftar semua intent."""
        return [intent["tag"] for intent in self._intents]
    
    def get_patterns_for_intent(self, tag):
        """Mengembalikan pattern untuk intent tertentu."""
        for intent in self._intents:
            if intent["tag"] == tag:
                return intent.get("patterns", [])
        return []
