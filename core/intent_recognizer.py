"""
Milo AI — Advanced Multi-Discourse Intent Recognizer
Mengenali maksud/niat dari input user tunggal maupun kalimat majemuk panjang (multi-discourse).
Mendukung segmentasi klausa, phrase proximity, TF-IDF cosine similarity, dan semantic guards.
Semua diimplementasi dari nol secara murni menggunakan Python.
"""

import json
import re
from utils.config import Config
from utils.text_utils import TextUtils


class IntentRecognizer:
    """Advanced Multi-Discourse Intent Recognizer — cerdas, modular, dan multi-konteks."""
    
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
    
    def segment_discourse(self, text):
        """
        Memecah teks panjang/kompleks menjadi unit-unit wacana (discourse units).
        Berdasarkan tanda baca kalimat (. ! ?) dan konjungsi koordinatif/subordinatif.
        """
        raw_chunks = re.split(r'[.!?;\n]+', text)
        segments = []
        
        for chunk in raw_chunks:
            chunk = chunk.strip()
            if not chunk:
                continue
            
            # Pisahkan dengan konjungsi seperti 'tapi', 'dan', 'terus', 'lalu', 'nih,'
            sub_chunks = re.split(r'\b(?:tapi|tetapi|namun|terus|lalu|kemudian|sedangkan|padahal)\b|,\s*(?:nih|dong|ya|kan)\b', chunk, flags=re.IGNORECASE)
            for sub in sub_chunks:
                sub = sub.strip()
                if len(sub) > 2:
                    segments.append(sub)
        
        return segments if len(segments) > 1 else [text.strip()]
    
    def recognize(self, tokenized_data, preprocessed_data=None):
        """
        Mengenali intent dari input yang sudah dipreprocess & ditokenisasi.
        Mendukung multi-segment analysis untuk kalimat majemuk panjang.
        """
        words = tokenized_data.get("words", [])
        if not words:
            return self._create_result("fallback", 0.0, "empty_input")
        
        raw_text = " ".join(words).lower()
        original_text = ""
        if preprocessed_data:
            original_text = preprocessed_data.get("original", "")
        
        # 1. Cek Multi-Discourse Segmentation
        discourse_segments = self.segment_discourse(original_text or raw_text)
        analyzed_segments = []
        
        if len(discourse_segments) > 1:
            for seg in discourse_segments:
                seg_words = seg.lower().split()
                if seg_words:
                    seg_intent = self._recognize_single_clause(seg_words, seg.lower())
                    analyzed_segments.append({
                        "text": seg,
                        "words": seg_words,
                        "intent": seg_intent["intent"],
                        "confidence": seg_intent["confidence"],
                        "matched_pattern": seg_intent.get("matched_pattern")
                    })
        
        # 2. Kenali intent utama dari seluruh teks / klausa fokus
        main_intent = self._recognize_single_clause(words, raw_text)
        
        # Jika ada segmentasi multi-discourse, pasang ke metadata
        if analyzed_segments:
            main_intent["is_compound"] = True
            main_intent["segments"] = analyzed_segments
            
            # Tentukan primary intent yang paling bernilai aksi (misal: advice, question, curhat, emotion)
            priority_order = [
                "need_advice", "curhat_need", "confused_state", "knowledge_query",
                "feeling_sad", "feeling_angry", "feeling_happy", "seeking_permission",
                "user_name_tell", "user_name_ask", "how_are_you", "current_activity_ask",
                "smalltalk_food", "smalltalk_music", "smalltalk_hobby"
            ]
            
            for p_intent in priority_order:
                matching_seg = next((s for s in analyzed_segments if s["intent"] == p_intent), None)
                if matching_seg:
                    main_intent["intent"] = p_intent
                    main_intent["confidence"] = max(main_intent["confidence"], matching_seg["confidence"])
                    break
        else:
            main_intent["is_compound"] = False
            main_intent["segments"] = []
        
        return main_intent
    
    def _recognize_single_clause(self, words, raw_text):
        """Mengenali intent dari satu klausa/kalimat."""
        focal_clause, clauses = self._extract_clauses(raw_text)
        
        # 1. Exact Match
        exact_full = self._exact_match(raw_text)
        if exact_full:
            return exact_full
        
        if focal_clause and focal_clause != raw_text:
            exact_focal = self._exact_match(focal_clause)
            if exact_focal:
                exact_focal["confidence"] = 0.98
                exact_focal["method"] = "exact_focal_clause"
                return exact_focal
        
        # 2. Phrase & N-Gram Proximity Match
        phrase_candidates = []
        if focal_clause and focal_clause != raw_text:
            focal_res = self._phrase_proximity_match(focal_clause.split(), focal_clause)
            if focal_res:
                focal_res["confidence"] = min(1.0, focal_res["confidence"] * 1.15)
                focal_res["method"] = "focal_phrase_match"
                phrase_candidates.append(focal_res)
        
        full_res = self._phrase_proximity_match(words, raw_text)
        if full_res:
            phrase_candidates.append(full_res)
        
        # 3. TF-IDF Match dengan Proximity Penalty
        tfidf_res = self._tfidf_match_with_span_penalty(words, raw_text)
        if tfidf_res:
            phrase_candidates.append(tfidf_res)
        
        # 4. Fuzzy Match
        fuzzy_res = self._fuzzy_match(raw_text)
        if fuzzy_res:
            phrase_candidates.append(fuzzy_res)
        
        if not phrase_candidates:
            return self._create_result("fallback", 0.0, "no_match")
        
        # 5. Semantic Intent Guards
        valid_candidates = []
        for cand in phrase_candidates:
            if self._passes_semantic_guard(cand["intent"], raw_text, words):
                valid_candidates.append(cand)
        
        if not valid_candidates:
            return self._create_result("fallback", 0.0, "failed_semantic_guards")
        
        best = max(valid_candidates, key=lambda x: x["confidence"])
        
        if best["intent"] == "greeting" and len(words) > 3 and len(valid_candidates) > 1:
            non_greetings = [c for c in valid_candidates if c["intent"] != "greeting"]
            if non_greetings:
                best = max(non_greetings, key=lambda x: x["confidence"])
        
        if best["confidence"] < Config.CONFIDENCE_THRESHOLD:
            return self._create_result("fallback", best["confidence"], "below_threshold")
        
        return best
    
    def _extract_clauses(self, text):
        """Memecah kalimat menjadi klausa berdasarkan kata sambung kontras."""
        pattern = r'\b(?:' + '|'.join(self.CONTRAST_CONJUNCTIONS) + r')\b'
        parts = re.split(pattern, text)
        clauses = [p.strip() for p in parts if p.strip()]
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
        """Mencocokkan pattern berdasarkan frasa utuh dan kedekatan posisi kata."""
        best_tag = None
        best_score = 0.0
        best_pattern = None
        
        input_lower = input_text.lower()
        
        for intent in self._intents:
            for pattern in intent.get("patterns", []):
                pattern_lower = pattern.lower().strip()
                pattern_words = pattern_lower.split()
                
                # 1. Exact Substring Match
                if f" {pattern_lower} " in f" {input_lower} " or input_lower.startswith(pattern_lower) or input_lower.endswith(pattern_lower) or pattern_lower == input_lower:
                    score = 0.96 if len(pattern_words) >= 2 else 0.88
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
                    
                    if matched_count >= len(pattern_words) * 0.75 and len(positions) >= 2:
                        span = max(positions) - min(positions) + 1
                        expected_span = len(pattern_words)
                        span_ratio = expected_span / span
                        if span_ratio >= 0.5:
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
        """TF-IDF Cosine Similarity dengan penalti jarak kata."""
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
        """Semantic Guards untuk memvalidasi intent."""
        text_lower = input_text.lower()
        word_set = set(words)
        
        # Guard 1: user_name_ask
        if intent_tag == "user_name_ask":
            name_indicators = {"nama", "namaku", "namamu", "panggilanku", "name"}
            if not (word_set & name_indicators or "who am i" in text_lower):
                return False
            if re.search(r'\b(ke|sama|dengan|pada)\s+siapa\b', text_lower):
                return False
        
        # Guard 2: identity_ask
        if intent_tag == "identity_ask":
            if not re.search(r'\b(kamu|lu|lo|kau|milo|anda)\b', text_lower) and "who are you" not in text_lower:
                return False
        
        # Guard 3: curhat_need
        if "curhat" in text_lower or re.search(r'\b(bingung|mau)\s+(cerita|curhat)\b', text_lower):
            if intent_tag in ("how_are_you", "user_name_ask", "identity_ask"):
                return False
        
        # Guard 4: seeking_permission vs affirmative
        if intent_tag == "affirmative":
            if re.search(r'\b(emang|apakah|beneran|serius)\s+boleh\b', text_lower) or "boleh ya" in text_lower or "boleh emang" in text_lower:
                return False
        
        # Guard 5: how_are_you
        if intent_tag == "how_are_you":
            if not ({"kabar", "kabarmu", "kabarnya"} & word_set or "how are you" in text_lower):
                return False
        
        # Guard 6: user_profile_query harus berupa pertanyaan
        if intent_tag == "user_profile_query":
            if not (any(w in text_lower for w in ["apa", "dimana", "mana", "ingat", "tahu"]) or "?" in text_lower):
                return False
            # Jika user sedang menyatakan faktanya (misal "makanan favoritku rendang") bukan menanyakan
            if not any(q in text_lower for q in ["apa", "mana", "kah", "?"]):
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
