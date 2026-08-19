"""
Milo AI — Real-Time Generative Contextual Response Engine
Otak utama yang menghasilkan balasan percakapan secara dinamis, cerdas,
dan relevan secara real-time berdasarkan Bank Kata Semantik (Word Bank),
Word Sense Disambiguation (WSD), dan Internet Knowledge Fetcher.

CATATAN ARSITEKTUR:
Semua respons dihasilkan secara generatif oleh SentenceSynthesizer.
TIDAK ADA template pre-made atau responses.json yang digunakan.
File responses.json telah DIHAPUS dari codebase.
"""

import json
import re
import random
from datetime import datetime
from utils.config import Config
from utils.text_utils import TextUtils
from knowledge.word_bank import WordBank
from knowledge.web_fetcher import WebFetcher
from knowledge.web_search import WebSearch
from core.sentence_synthesizer import SentenceSynthesizer
from core.semantic_parser import SemanticParser


class ResponseEngine:
    """Real-Time Generative Contextual Response Engine — responsif, kontekstual, dan dinamis."""
    
    def __init__(self, word_bank=None, web_fetcher=None, web_search=None):
        self.word_bank = word_bank or WordBank()
        self.web_fetcher = web_fetcher or WebFetcher()
        self.web_search = web_search or WebSearch()
        self.synthesizer = SentenceSynthesizer(self.word_bank)
        self.semantic_parser = SemanticParser()
        self._stopwords = set()
        self._load_stopwords()
    
    def _load_stopwords(self):
        """Memuat daftar stopwords."""
        try:
            with open(Config.STOPWORDS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                self._stopwords = set(data.get("stopwords", []))
        except (FileNotFoundError, json.JSONDecodeError):
            self._stopwords = {"yang", "dan", "di", "ke", "dari", "ini", "itu", "dengan", "untuk", "adalah"}
    
    def generate(self, intent_result, context, preprocessed=None, knowledge_base=None, memory=None, context_manager=None):
        """
        Menghasilkan balasan percakapan real-time yang presisi dan bervariasi.
        Semua respons disusun secara generatif oleh SentenceSynthesizer — tanpa template pre-made.
        """
        intent = intent_result.get("intent", "fallback")
        confidence = intent_result.get("confidence", 0.0)
        
        user_input = ""
        user_words = []
        if preprocessed:
            user_input = preprocessed.get("original", "")
            user_words = preprocessed.get("tokens_raw", [])
        
        last_milo_act = context_manager.get_last_milo_act() if context_manager else None
        parsed = self.semantic_parser.parse(user_input, last_milo_act)
        
        keywords = self._extract_keywords(user_input, user_words)
        user_name = context.get("user_name") or ""
        name_suffix = f" {user_name}" if user_name else ""
        
        # === 1. Handle Permintaan Klarifikasi ("maksud kamu gimana?", "maksudnya apa?") ===
        if parsed["is_clarification"] or intent == "clarification_ask":
            return self.synthesizer.synthesize_clarification(user_name)
        
        # === 2. Handle Meta-Correction (User mengoreksi pemahaman Milo) ===
        if parsed["is_meta_correction"] or intent == "meta_correction":
            last_user_msg = context_manager.get_last_user_input() if context_manager else ""
            return self.synthesizer.synthesize_meta_correction(user_name, last_user_msg)
        
        # === 3. Handle User Menyatakan Ingin Tahu / Bertanya Sesuatu ke Milo ===
        if parsed["is_asking_milo"]:
            return self.synthesizer.synthesize_ask_milo_prompt(user_name)
        
        # === 4. Handle Respons Keadaan Baik User ("aku baik-baik saja milo") ===
        if parsed["is_user_state_good"] and not any(w in user_input.lower() for w in ["sakit", "sedih", "kecewa", "bingung"]):
            return self.synthesizer.synthesize_user_state_good(user_name)
        
        # === 5. Handle Permintaan Saran & Solusi dengan Deep Web Search & Cross-Validation ===
        if parsed["is_asking_advice"] or parsed["is_insisting_on_tips"] or parsed["has_specific_dilemma"] or intent == "need_advice":
            # Jika user menegaskan hanya minta tips (misal "cuman minta tips aja", "cuman minta tis")
            if parsed["is_insisting_on_tips"]:
                return self.synthesizer.synthesize_practical_micro_tips(user_name)
                
            search_input = user_input
            if len(user_input.split()) <= 4 and context_manager:
                sub_input = context_manager.get_last_substantial_user_input()
                if sub_input:
                    search_input = sub_input
                    
            research = self.web_search.deep_research(search_input, context.get("current_topic", ""))
            if research and research.get("validated_points"):
                return self.synthesizer.synthesize_researched_advice(user_name, research, search_input)
            return self.synthesizer.synthesize_need_advice(user_name)
            
        # === 6. Handle Cerita / Update Situasi Pengguna (is_story_sharing) ===
        if parsed["is_story_sharing"]:
            return self.synthesizer.synthesize_story_reflection(user_name, user_input)
            
        # === 7. Handle Patah Hati & Cinta Tak Berbalas (heartbreak) ===
        if parsed["is_heartbreak"]:
            return self.synthesizer.synthesize_heartbreak(user_name, user_input)
        
        # === 8. Handle Multi-Segment Compound Inputs ===
        if intent_result.get("is_compound") and len(intent_result.get("segments", [])) >= 2:
            compound_resp = self._handle_compound_input(intent_result, user_input, keywords, context, knowledge_base, memory, context_manager)
            if compound_resp:
                return self._substitute_variables(compound_resp, context)
        
        # === 9. Handle Rasa Cemas / Khawatir / Musibah / Sakit ===
        if intent == "worry_concern_state" or any(w in user_input.lower() for w in ["kecelakaan", "masuk rumah sakit", "kena musibah", "rawat inap", "ruang rawat", "di rumah sakit"]):
            situation = "hospital_rawat_inap" if any(w in user_input.lower() for w in ["rawat inap", "ruang rawat"]) else ("accident_hospital" if any(w in user_input.lower() for w in ["kecelakaan", "rumah sakit"]) else "general")
            return self.synthesizer.synthesize_worry_compassion(user_name, situation)
        
        # === 10. Handle Kepikiran Seseorang / Naksir / Romansa ===
        if intent == "thinking_of_someone" or self._is_thinking_of_someone(user_input):
            return self.synthesizer.synthesize_thinking_of_someone(user_name)
        
        # === 9. Handle Pertanyaan Izin / Ragu ("emang boleh ya?") ===
        if parsed["is_seeking_permission"] or intent == "seeking_permission":
            last_milo_response = context_manager.get_last_response() if context_manager else ""
            return self.synthesizer.synthesize_seeking_permission(user_name, last_milo_act, last_milo_response)
        
        # === 10. Handle Curhat Emosi (feeling_sad, feeling_happy, feeling_angry) ===
        if intent in ("feeling_sad", "feeling_happy", "feeling_angry") or any(w in user_input.lower() for w in ["sedih banget", "kecewa berat"]):
            feeling_response = self._handle_feeling(intent, user_input, keywords, context)
            if feeling_response:
                return feeling_response
        
        # === 11. Handle User Membagikan Fakta Personal (Makanan, Hobi, Profesi) ===
        if any(w in user_input.lower() for w in ["makanan favorit", "hobiku", "hobi saya", "pekerjaanku", "aku mahasiswa"]):
            facts = context_manager.extract_personal_facts(user_input) if context_manager else {}
            if facts and intent not in ("user_profile_query", "need_advice"):
                fact_desc = []
                if "favorite_food" in facts:
                    fact_desc.append(f"makanan favoritmu itu **{facts['favorite_food'].title()}**")
                if "hobby" in facts:
                    fact_desc.append(f"hobimu **{facts['hobby'].title()}**")
                if "occupation" in facts:
                    fact_desc.append(f"kamu {facts['occupation']}")
                if "current_project" in facts:
                    fact_desc.append(f"kamu lagi fokus {facts['current_project']}")
                
                if fact_desc:
                    raw_msg = f"Wah, asik banget! Milo catat di memori ya kalau " + " dan ".join(fact_desc) + f"! 🧠✨ Senang bisa kenal kamu lebih dekat{name_suffix}!"
                    return self._substitute_variables(raw_msg, context)
        
        # === 12. Handle User Mengajari Pengetahuan Baru ("tahu ga kalau X adalah Y") ===
        teach_match = re.search(r'\b(?:tahu ga|tau ga|kamu tahu ga|faktanya|sebenarnya)\s+(?:kalau|bahwa)?\s*([a-zA-Z0-9\s]{2,30})\s+(?:adalah|itu|merupakan|artinya)\s+([^\n.]+)', user_input, re.IGNORECASE)
        if teach_match:
            concept = teach_match.group(1).strip().title()
            explanation = teach_match.group(2).strip()
            self.word_bank.learn_word(concept, pos="noun", domain="general", meaning=explanation)
            if knowledge_base:
                knowledge_base.add_entry("pengetahuan_user", concept.lower().replace(" ", "_"), explanation)
            return self._substitute_variables(f"Wah, ilmu baru nih! 💡 Milo simpan di memori ya kalau **{concept}** adalah {explanation}. Makasih banyak sudah mengajari Milo{name_suffix}! 🧠✨", context)
        
        # === 13. Handle Pertanyaan Kabar (how_are_you) ===
        if intent == "how_are_you" or any(w in user_input.lower() for w in ["apa kabar", "gimana kabar", "bagaimana kabar", "kabarmu"]):
            return self.synthesizer.synthesize_how_are_you(user_name)
        
        # === 14. Handle Pertanyaan Pencipta / Pembuat Milo (identity_creator) ===
        if intent == "identity_creator" or any(w in user_input.lower() for w in ["diciptakan oleh siapa", "siapa penciptamu", "siapa pembuatmu", "siapa yang buat kamu", "siapa yang bikin kamu", "who created you", "diciptakan siapa"]):
            return self.synthesizer.synthesize_identity_creator(user_name)
        
        # === 15. Handle Pertanyaan Identitas Milo (identity_ask) ===
        if intent == "identity_ask" or any(w in user_input.lower() for w in ["siapa kamu", "kamu siapa", "who are you"]):
            return self.synthesizer.synthesize_identity_ask(user_name)
        
        # === 16. Handle Pertanyaan Sedang Apa (current_activity_ask) ===
        if intent == "current_activity_ask" or any(w in user_input.lower() for w in ["lagi apa", "lagi ngapain", "sedang apa"]):
            return self.synthesizer.synthesize_current_activity(user_name)
        
        # === 17. Handle Greeting Murni ===
        if intent == "greeting":
            return self.synthesizer.synthesize_greeting(user_name)
        
        # === 18. Handle Farewell ===
        if intent == "farewell":
            return self.synthesizer.synthesize_farewell(user_name)
        
        # === 19. Handle Thanks ===
        if intent == "thanks":
            return self.synthesizer.synthesize_thanks_reply(user_name)
        
        # === 20. Handle Pertanyaan Nama User (user_name_ask) ===
        if intent == "user_name_ask" or self._is_asking_user_name(user_input):
            return self.synthesizer.synthesize_user_name_ask(user_name)
        
        # === 21. Handle User Menyebutkan Nama (user_name_tell) ===
        if intent == "user_name_tell":
            if user_name:
                return self.synthesizer.synthesize_user_name_tell(user_name)
        
        # === 22. Handle Pertanyaan Fakta Profil User (user_profile_query) ===
        if intent == "user_profile_query":
            profile_resp = self._handle_user_profile_query(user_input, memory, context)
            if profile_resp:
                return self._substitute_variables(profile_resp, context)
        
        # === 23. Handle Curhat & Kebutuhan Cerita (curhat_need) ===
        if (intent == "curhat_need" or self._is_curhat_intent(user_input)) and not parsed["has_no_story"] and not parsed["is_asking_milo"]:
            return self.synthesizer.synthesize_curhat_reassurance(user_name)
        
        # === 24. Handle Kondisi Bingung / Overthinking (confused_state) ===
        if intent == "confused_state":
            return self.synthesizer.synthesize_confused_state(user_name)
        
        # === 25. Handle Permintaan Saran / Pendapat (need_advice) ===
        if intent == "need_advice":
            return self.synthesizer.synthesize_need_advice(user_name)
        
        # === 26. Handle Rasa Kesepian (lonely_state) ===
        if intent == "lonely_state":
            return self.synthesizer.synthesize_lonely_state(user_name)
        
        # === 27. Handle Smalltalk Makanan / Musik / Hobi ===
        if intent in ("smalltalk_food", "smalltalk_music", "smalltalk_hobby"):
            entity_response = self._handle_specific_smalltalk(intent, user_input, keywords, context)
            if entity_response:
                return entity_response
        
        # === 28. Handle Compliment & Insult ===
        if intent == "compliment":
            return self.synthesizer.synthesize_compliment_reply(user_name)
        if intent == "insult":
            return self.synthesizer.synthesize_insult_reply(user_name)
        
        # === 29. Handle Age, Capability, Weather, Time, Help, Joke, Philosophy ===
        if intent == "age_ask":
            return self.synthesizer.synthesize_age_ask(user_name)
        if intent == "capability_ask":
            return self.synthesizer.synthesize_capability_ask(user_name)
        if intent == "weather":
            return self.synthesizer.synthesize_weather(user_name)
        if intent == "time_ask":
            return self.synthesizer.synthesize_time_ask()
        if intent == "help":
            return self.synthesizer.synthesize_help(user_name)
        if intent == "joke":
            return self.synthesizer.synthesize_joke(user_name)
        if intent == "philosophy":
            return self.synthesizer.synthesize_philosophy(user_name)
        
        # === 30. Handle Follow-up Percakapan ("terus?", "lalu?") ===
        if intent == "follow_up" or self._is_follow_up_phrase(user_input):
            last_intent = context_manager.get_last_intent() if context_manager else None
            return self.synthesizer.synthesize_follow_up(user_name, last_intent)
        
        # === 31. Handle Pertanyaan Pengetahuan / Fakta Murni ===
        if (intent == "knowledge_query" or (knowledge_base and self._is_factual_question(user_input))) and not self._is_personal_sharing(user_input):
            kb_response = self._handle_knowledge_query_with_web(user_input, keywords, knowledge_base, context)
            if kb_response:
                return self._substitute_variables(kb_response, context)
        
        # === 32. Handle Affirmation / Negation ===
        if intent in ("affirmative", "negative"):
            last_response = context_manager.get_last_response() if context_manager else ""
            if intent == "affirmative":
                return self.synthesizer.synthesize_affirmation(user_name, last_response)
            else:
                return self.synthesizer.synthesize_negation(user_name, last_response)
        
        # === 33. Cek Pengetahuan Web jika intent adalah pertanyaan konsep ===
        if self._is_concept_query(user_input):
            web_resp = self._handle_knowledge_query_with_web(user_input, keywords, knowledge_base, context)
            if web_resp:
                return self._substitute_variables(web_resp, context)
        
        # === 34. Real-Time Dynamic Generative Fallback ===
        return self.synthesizer.synthesize_open_response(user_input, keywords, user_name)
    
    # ================================================================
    # HELPER METHODS (Deteksi Pola)
    # ================================================================
    
    def _is_thinking_of_someone(self, text):
        """Mengecek apakah user sedang kepikiran seseorang / romansa."""
        text_lower = text.lower()
        patterns = [
            r"\bkepikiran seseorang\b",
            r"\bkepikiran dia\b",
            r"\bselalu ada di pikiran\b",
            r"\blagi naksir\b",
            r"\bada orang yang (aku|gue|saya) (suka|pikirin)\b",
            r"\bmikirin seseorang\b",
            r"\bkepikiran gebetan\b",
            r"\bkangen seseorang\b"
        ]
        return any(re.search(p, text_lower) for p in patterns)
    
    def _handle_knowledge_query_with_web(self, user_input, keywords, knowledge_base, context):
        """
        Mencari jawaban di basis pengetahuan lokal.
        Jika tidak ada atau relevansinya rendah, otomatis mencari secara online via WebFetcher dan mempelajarinya.
        """
        user_name = context.get("user_name")
        
        # 1. Coba cari di Knowledge Base Lokal
        if knowledge_base and keywords:
            results = knowledge_base.search_by_keywords(keywords, max_results=3)
            
            if results and results[0].get("score", 0) >= 6:
                best_match = results[0]
                val = best_match.get("value")
                key = best_match.get("key") or ""
                if isinstance(val, str):
                    topic_name = key.split(">")[-1].strip().replace("_", " ").title() if key else "itu"
                    return self.synthesizer.synthesize_knowledge_answer(topic_name, val, user_name)
                elif isinstance(val, dict):
                    summary_points = [f"• **{k.replace('_', ' ').title()}**: {v}" for k, v in list(val.items())[:5] if isinstance(v, str)]
                    topic_name = key.split(">")[-1].strip().replace("_", " ").title() if key else "Topik"
                    if summary_points:
                        return f"Berikut rangkuman tentang **{topic_name}** yang Milo ketahui:\n" + "\n".join(summary_points) + "\n\nAda bagian yang ingin kamu diskusikan lebih lanjut? 💬"
        
        # 2. Jika tidak ada di lokal, cari secara online via WebFetcher
        if self.web_fetcher and keywords:
            query_term = " ".join(keywords)
            word_def = self.web_fetcher.fetch_word_definition(query_term)
            if word_def:
                meaning = word_def.get("meaning", "")
                word_clean = word_def.get("word", query_term).title()
                source = word_def.get("source", "Web")
                self.word_bank.learn_word(word_clean, meaning=meaning)
                if knowledge_base:
                    knowledge_base.add_entry("pengetahuan_umum", word_clean.lower().replace(" ", "_"), meaning)
                return self.synthesizer.synthesize_knowledge_answer(word_clean, meaning, user_name, source)
                
            concept_summary = self.web_fetcher.search_concept_summary(query_term)
            if concept_summary:
                topic_title = query_term.title()
                if knowledge_base:
                    knowledge_base.add_entry("pengetahuan_umum", topic_title.lower().replace(" ", "_"), concept_summary)
                return self.synthesizer.synthesize_knowledge_answer(topic_title, concept_summary, user_name, "Web")
                
        return None
    
    def _is_concept_query(self, text):
        """Mengecek apakah kalimat adalah pertanyaan konsep baru."""
        text_lower = text.lower()
        patterns = [
            r"\bapa (itu|arti|pengertian|definisi|makna)\b",
            r"\bapa yang dimaksud\b",
            r"\bjelaskan tentang\b",
            r"\binfo tentang\b"
        ]
        return any(re.search(p, text_lower) for p in patterns)
    
    def _handle_compound_input(self, intent_result, user_input, keywords, context, knowledge_base, memory, context_manager):
        """Menyusun respons terpadu untuk kalimat majemuk panjang multi-konteks."""
        segments = intent_result.get("segments", [])
        user_name = context.get("user_name")
        
        has_advice_request = any(s["intent"] == "need_advice" or any(w in s["text"].lower() for w in ["saran", "pendapat", "masukan", "harus gimana"]) for s in segments)
        has_confusion = any(s["intent"] == "confused_state" or any(w in s["text"].lower() for w in ["bingung", "pusing", "overthinking", "kacau", "buntu"]) for s in segments)
        has_architecture_topic = any(any(w in s["text"].lower() for w in ["arsitektur", "kode", "program", "koding", "coding", "milo", "fitur", "modul"]) for s in segments)
        has_curhat = any(s["intent"] == "curhat_need" or "curhat" in s["text"].lower() for s in segments)
        
        if has_architecture_topic and (has_confusion or has_advice_request):
            return self.synthesizer.synthesize_compound_architecture(user_name, has_confusion, has_advice_request)
            
        if has_advice_request and (has_confusion or has_curhat):
            return self.synthesizer.synthesize_compound_generic(user_name, has_confusion, has_curhat, has_advice_request)
            
        return None
    
    def _handle_feeling(self, intent, user_input, keywords, context):
        """Menghasilkan respons empati yang merujuk pada apa yang diceritakan user."""
        user_name = context.get("user_name")
        
        reason_match = re.search(r'(?:karena|gara-gara|soal|abis|karna|lantaran)\s+([^.?!]+)', user_input, re.IGNORECASE)
        reason = reason_match.group(1).strip() if reason_match else ""
        
        # Cek apakah ada unsur sakit hati, patah hati, atau cinta tak berbalas
        if any(w in user_input.lower() for w in ["mencintai", "sakit hati", "patah hati", "tidak mencintaiku", "cinta bertepuk", "ditolak", "cintaku", "putus cinta", "cinta tak berbalas"]):
            return self.synthesizer.synthesize_heartbreak(user_name, user_input)
            
        if intent == "feeling_sad" or "sedih" in user_input.lower() or "kecewa" in user_input.lower():
            return self.synthesizer.synthesize_feeling_sad(user_name, reason)
        
        elif intent == "feeling_happy":
            return self.synthesizer.synthesize_feeling_happy(user_name, reason)
        
        elif intent == "feeling_angry":
            return self.synthesizer.synthesize_feeling_angry(user_name, reason)
        
        return None
    
    def _handle_specific_smalltalk(self, intent, user_input, keywords, context):
        """Menangani topik smalltalk makanan, musik, hobi secara kontekstual."""
        user_name = context.get("user_name") or ""
        text_lower = user_input.lower()
        
        known_foods = ["nasi padang", "nasi goreng", "rendang", "sate", "bakso", "mie ayam", "soto", "pizza", "burger", "seblak", "martabak", "ayam goreng"]
        matched_food = None
        for kf in known_foods:
            if re.search(r'\b' + re.escape(kf) + r'\b', text_lower):
                matched_food = kf.title()
                break
        
        if intent == "smalltalk_food":
            return self.synthesizer.synthesize_smalltalk_food(user_name, matched_food)
        
        elif intent == "smalltalk_music":
            known_genres = ["pop", "rock", "jazz", "lofi", "lo-fi", "klasik", "kpop", "k-pop", "dangdut", "r&b", "indie"]
            matched_music = None
            for km in known_genres:
                if re.search(r'\b' + re.escape(km) + r'\b', text_lower):
                    matched_music = km.upper() if km in ("lofi", "kpop", "r&b") else km.title()
                    break
            return self.synthesizer.synthesize_smalltalk_music(user_name, matched_music)
        
        elif intent == "smalltalk_hobby":
            return self.synthesizer.synthesize_smalltalk_hobby(user_name)
        
        return None
    
    def _handle_user_profile_query(self, user_input, memory, context):
        """Merespons pertanyaan user tentang profil/fakta yang pernah diceritakan."""
        if not memory:
            return "Milo belum punya catatan lengkap soal itu. Ceritain dong lebih banyak tentang kamu! 😊"
        
        user_name = context.get("user_name")
        salutation = f"{user_name}, " if user_name else ""
        text_lower = user_input.lower()
        
        if "hobi" in text_lower:
            hobby = memory.get_user_info("hobby")
            if hobby:
                return f"{salutation}kamu pernah cerita kalau hobi kamu itu **{hobby.title()}**! 🎨 Masih sering ngelakuin itu?"
            return f"{salutation}kamu belum pernah kasih tahu hobi kamu ke Milo nih. Hobi kamu apa sih? Biar Milo catat di memori! 😊"
            
        if "makan" in text_lower or "kuliner" in text_lower:
            food = memory.get_user_info("favorite_food")
            if food:
                return f"{salutation}makanan favorit kamu kan **{food.title()}**! 😋 Milo masih ingat kok!"
            return f"{salutation}Milo belum tahu makanan favorit kamu. Kamu paling suka makan apa nih? 🍲"
            
        if "kuliah" in text_lower or "kerja" in text_lower or "profesi" in text_lower or "proyek" in text_lower or "project" in text_lower:
            occ = memory.get_user_info("occupation") or memory.get_user_info("current_project")
            if occ:
                return f"{salutation}kamu kan lagi sibuk dengan {occ}! 💼 Semangat terus ya dengan aktivitasmu!"
            return f"{salutation}kamu belum pernah cerita soal kuliah atau pekerjaanmu. Cerita dong sekarang kamu lagi sibuk apa? 🎓"
            
        all_info = memory.get_user_profile()
        if all_info:
            points = [f"• **{k.replace('_', ' ').title()}**: {v}" for k, v in all_info.items()]
            return f"{salutation}ini beberapa hal yang Milo ingat tentang kamu:\n" + "\n".join(points) + "\n\nAda hal baru yang mau kamu ceritakan? 🧠✨"
            
        return f"{salutation}Milo baru tahu nama kamu! Ceritain dong lebih banyak hal tentang kamu, misalnya hobi atau hal yang kamu sukai! ✨"
    
    # ================================================================
    # UTILITY METHODS
    # ================================================================
    
    def _extract_keywords(self, text, words=None):
        """Mengekstrak kata kunci bersih tanpa tanda baca."""
        if not words:
            clean_text = re.sub(r'[^\w\s]', ' ', text.lower())
            words = clean_text.split()
        
        question_words = {
            "apa", "siapa", "dimana", "kapan", "mengapa", "kenapa", "bagaimana", "gimana",
            "apakah", "berapa", "yang", "kamu", "tahu", "tau", "tentang", "mengenai",
            "tolong", "bisa", "jelaskan", "ceritakan", "kasih", "adalah", "itu", "ini",
            "arti", "kata", "makna", "maksud", "dimaksud", "pengertian", "definisi", "istilah", "info",
            "dengan", "artinya", "pengertiannya", "maksudnya", "definisinya",
            "dong", "sih", "kan", "nih", "ya", "deh", "kah", "kok", "aku", "saya", "gue", "gw", "emang", "hai", "halo"
        }
        
        all_ignored = self._stopwords | question_words
        
        keywords = []
        for w in words:
            clean_w = re.sub(r'[^\w]', '', w).lower()
            if len(clean_w) > 1 and clean_w not in all_ignored:
                keywords.append(clean_w)
                
        return keywords
    
    def _is_asking_user_name(self, text):
        """Mengecek apakah user menanyakan namanya sendiri ke AI."""
        text_lower = text.lower()
        patterns = [
            r"siapa nama (saya|aku|gue|gw)",
            r"nama (saya|aku|gue|gw) siapa",
            r"(kamu|lu|lo) (tau|tahu|ingat|inget) nama (saya|aku|gue|gw)",
            r"siapa namaku",
            r"namaku siapa",
            r"who am i",
            r"what is my name"
        ]
        if re.search(r'\b(ke|sama|dengan|pada)\s+siapa\b', text_lower):
            return False
        return any(re.search(p, text_lower) for p in patterns)
    
    def _is_curhat_intent(self, text):
        """Mengecek apakah user menyatakan ingin curhat/bercerita."""
        text_lower = text.lower()
        indicators = [
            "mau curhat", "pengen curhat", "curhat dong", "bingung mau cerita ke siapa",
            "bingung mau curhat ke siapa", "bingung ke siapa", "mau cerita", "pengen cerita",
            "butuh teman curhat", "butuh teman cerita", "ada yang mau aku ceritain",
            "bisa dengerin aku cerita", "dengerin ceritaku"
        ]
        return any(ind in text_lower for ind in indicators)
    
    def _is_factual_question(self, text):
        """Mengecek apakah teks adalah pertanyaan pengetahuan umum/fakta."""
        text_lower = text.lower()
        non_factual = [
            "apa kabar", "gimana kabar", "bagaimana kabar", "lagi apa", "lagi ngapain",
            "kamu lagi", "siapa kamu", "siapa namamu", "nama kamu siapa", "siapa nama saya",
            "kamu sehat", "apa yang bisa kamu lakukan", "bisa apa kamu", "hobi kamu apa",
            "makanan favorit kamu", "musik favorit kamu", "mau curhat", "pengen curhat", "emang boleh",
            "bukan gitu", "kepikiran seseorang", "selalu ada di pikiran", "maksud kamu", "maksudnya gimana"
        ]
        if any(nf in text_lower for nf in non_factual):
            return False
            
        indicators = [
            "apa itu", "apa yang dimaksud", "apa yang kamu ketahui tentang",
            "apa yang kamu tahu tentang", "jelaskan tentang", "ceritakan tentang",
            "siapa presiden", "ibukota", "planet", "apa arti", "apa fungsi",
            "apa kegunaan", "sejarah", "definisi", "pengertian", "planet terbesar",
            "tata surya", "apa yang kamu ketahui", "kapan kemerdekaan", "kemerdekaan",
            "kapan indonesia", "siapa penemu", "berapa jumlah", "apa nama"
        ]
        return any(ind in text_lower for ind in indicators)
    
    def _is_follow_up_phrase(self, text):
        """Mengecek apakah input adalah frasa tindak lanjut."""
        text_lower = text.strip().lower()
        follow_ups = ["terus", "lalu", "terus gimana", "lalu bagaimana", "kenapa begitu", "contohnya", "apa lagi", "terus apa lagi"]
        return text_lower in follow_ups
    
    def _is_personal_sharing(self, text):
        """Mengecek apakah user sedang membagikan perasaan/curhat/kondisi pribadi (bukan tanya info)."""
        text_lower = text.lower()
        indicators = [
            "aku lagi", "saya lagi", "gue lagi", "gw lagi", "pikiranku", "pikiran ku",
            "hatiku", "perasaanku", "kepikiran", "curhat", "naksir", "galau", "kesel",
            "marah", "sedih", "bingung banget", "capek banget", "overthinking", "ntah kenapa"
        ]
        return any(ind in text_lower for ind in indicators)
    
    def _substitute_variables(self, response, context):
        """Mengganti variabel dinamis dalam respons."""
        now = datetime.now()
        variables = {
            "{current_time}": now.strftime("%H:%M"),
            "{current_date}": now.strftime("%d %B %Y"),
            "{current_day}": self._get_day_name(now.weekday()),
            "{user_name}": context.get("user_name") or "teman",
            "{milo_name}": Config.MILO_NAME,
            "{turn_count}": str(context.get("turn_count", 0)),
        }
        for var, value in variables.items():
            response = response.replace(var, value)
        return response
    
    def _get_day_name(self, weekday):
        """Mengembalikan nama hari dalam Bahasa Indonesia."""
        days = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
        return days[weekday] if 0 <= weekday <= 6 else "Unknown"
