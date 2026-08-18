"""
Milo AI — Real-Time Generative Contextual Response Engine
Otak utama yang menghasilkan balasan percakapan secara dinamis, cerdas,
dan relevan secara real-time berdasarkan Bank Kata Semantik (Word Bank),
Word Sense Disambiguation (WSD), dan Internet Knowledge Fetcher.
"""

import json
import re
import random
from datetime import datetime
from utils.config import Config
from utils.text_utils import TextUtils
from knowledge.word_bank import WordBank
from knowledge.web_fetcher import WebFetcher
from core.sentence_synthesizer import SentenceSynthesizer


class ResponseEngine:
    """Real-Time Generative Contextual Response Engine — responsif, kontekstual, dan dinamis."""
    
    def __init__(self, word_bank=None, web_fetcher=None):
        self.word_bank = word_bank or WordBank()
        self.web_fetcher = web_fetcher or WebFetcher()
        self.synthesizer = SentenceSynthesizer(self.word_bank)
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
        """
        intent = intent_result.get("intent", "fallback")
        confidence = intent_result.get("confidence", 0.0)
        
        user_input = ""
        user_words = []
        if preprocessed:
            user_input = preprocessed.get("original", "")
            user_words = preprocessed.get("tokens_raw", [])
        
        keywords = self._extract_keywords(user_input, user_words)
        user_name = context.get("user_name") or ""
        salutation = f"{user_name}, " if user_name else ""
        name_suffix = f" {user_name}" if user_name else ""
        
        # === 1. Handle Permintaan Klarifikasi ("maksud kamu gimana?", "maksudnya apa?") ===
        if intent == "clarification_ask" or self._is_clarification_ask(user_input):
            return self.synthesizer.synthesize_clarification(user_name)
        
        # === 2. Handle Meta-Correction (User mengoreksi pemahaman Milo, misal 'bukan gitu konteksnya') ===
        if intent == "meta_correction" or self._is_meta_correction(user_input):
            last_user_msg = context_manager.get_last_user_input() if context_manager else ""
            return self.synthesizer.synthesize_meta_correction(user_name, last_user_msg)
        
        # === 3. Handle Multi-Segment Compound Inputs (Kalimat Majemuk Panjang Multi-Konteks) ===
        if intent_result.get("is_compound") and len(intent_result.get("segments", [])) >= 2:
            compound_resp = self._handle_compound_input(intent_result, user_input, keywords, context, knowledge_base, memory, context_manager)
            if compound_resp:
                return self._substitute_variables(compound_resp, context)
        
        # === 4. Handle Rasa Cemas / Khawatir / Musibah / Sakit (worry_concern_state) ===
        if intent == "worry_concern_state" or any(w in user_input.lower() for w in ["kecelakaan", "masuk rumah sakit", "kena musibah", "rawat inap", "ruang rawat", "di rumah sakit"]):
            situation = "hospital_rawat_inap" if any(w in user_input.lower() for w in ["rawat inap", "ruang rawat"]) else ("accident_hospital" if any(w in user_input.lower() for w in ["kecelakaan", "rumah sakit"]) else "general")
            return self.synthesizer.synthesize_worry_compassion(user_name, situation)
        
        # === 5. Handle Kepikiran Seseorang / Naksir / Romansa (thinking_of_someone) ===
        if intent == "thinking_of_someone" or self._is_thinking_of_someone(user_input):
            return self.synthesizer.synthesize_thinking_of_someone(user_name)
        
        # === 6. Handle Pertanyaan Izin / Ragu ("emang boleh ya?") ===
        if intent == "seeking_permission" or self._is_seeking_permission(user_input):
            return self._handle_seeking_permission(user_input, context, context_manager)
        
        # === 7. Handle User Membagikan Fakta Personal (Makanan, Hobi, Profesi) ===
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
        
        # === 8. Handle User Mengajari Pengetahuan Baru ("tahu ga kalau X adalah Y") ===
        teach_match = re.search(r'\b(?:tahu ga|tau ga|kamu tahu ga|faktanya|sebenarnya)\s+(?:kalau|bahwa)?\s*([a-zA-Z0-9\s]{2,30})\s+(?:adalah|itu|merupakan|artinya)\s+([^\n.]+)', user_input, re.IGNORECASE)
        if teach_match:
            concept = teach_match.group(1).strip().title()
            explanation = teach_match.group(2).strip()
            # Pelajari ke Word Bank dan Knowledge Base
            self.word_bank.learn_word(concept, pos="noun", domain="general", meaning=explanation)
            if knowledge_base:
                knowledge_base.add_entry("pengetahuan_user", concept.lower().replace(" ", "_"), explanation)
            return self._substitute_variables(f"Wah, ilmu baru nih! 💡 Milo simpan di memori ya kalau **{concept}** adalah {explanation}. Makasih banyak sudah mengajari Milo{name_suffix}! 🧠✨", context)
        
        # === 9. Handle Pertanyaan Kabar (how_are_you) ===
        if intent == "how_are_you" or any(w in user_input.lower() for w in ["apa kabar", "gimana kabar", "bagaimana kabar", "kabarmu"]):
            return self.synthesizer.synthesize_how_are_you(user_name)
        
        # === 10. Handle Pertanyaan Sedang Apa (current_activity_ask) ===
        if intent == "current_activity_ask" or any(w in user_input.lower() for w in ["lagi apa", "lagi ngapain", "sedang apa"]):
            return self._handle_current_activity(context)
        
        # === 11. Handle Greeting Murni (hai, halo, pagi, siang, malam) ===
        if intent == "greeting":
            return self.synthesizer.synthesize_greeting(user_name)
        
        # === 12. Handle Farewell (bye, sampai jumpa, pamit) ===
        if intent == "farewell":
            return self._handle_farewell(user_input, context)
        
        # === 13. Handle Thanks (terima kasih, makasih) ===
        if intent == "thanks":
            return self._handle_thanks(user_input, context)
        
        # === 14. Handle Pertanyaan Nama User (user_name_ask) ===
        if intent == "user_name_ask" or self._is_asking_user_name(user_input):
            return self._handle_user_name_ask(context, memory)
        
        # === 15. Handle User Menyebutkan Nama (user_name_tell) ===
        if intent == "user_name_tell":
            if user_name:
                return f"Salam kenal, {user_name}! 😊 Senang bisa kenalan sama kamu! Mulai sekarang Milo bakal ingat nama kamu ya! 🤝✨"
        
        # === 16. Handle Pertanyaan Fakta Profil User (user_profile_query) ===
        if intent == "user_profile_query":
            profile_resp = self._handle_user_profile_query(user_input, memory, context)
            if profile_resp:
                return self._substitute_variables(profile_resp, context)
        
        # === 17. Handle Curhat & Kebutuhan Cerita (curhat_need) ===
        if intent == "curhat_need" or self._is_curhat_intent(user_input):
            return self.synthesizer.synthesize_curhat_reassurance(user_name)
        
        # === 18. Handle Kondisi Bingung / Overthinking (confused_state) ===
        if intent == "confused_state":
            return self._substitute_variables(self._handle_confused_state(user_input, context), context)
        
        # === 19. Handle Permintaan Saran / Pendapat (need_advice) ===
        if intent == "need_advice":
            return self._substitute_variables(self._handle_need_advice(user_input, context), context)
        
        # === 20. Handle Rasa Kesepian (lonely_state) ===
        if intent == "lonely_state":
            return self._substitute_variables(self._handle_lonely_state(user_input, context), context)
        
        # === 21. Handle Smalltalk Makanan / Musik / Hobi ===
        if intent in ("smalltalk_food", "smalltalk_music", "smalltalk_hobby") or self._is_food_or_music_input(user_input):
            entity_response = self._handle_specific_smalltalk(intent, user_input, keywords, context)
            if entity_response:
                return self._substitute_variables(entity_response, context)
        
        # === 22. Handle Curhat Emosi (feeling_sad, feeling_happy, feeling_angry) ===
        if intent in ("feeling_sad", "feeling_happy", "feeling_angry"):
            feeling_response = self._handle_feeling(intent, user_input, keywords, context)
            if feeling_response:
                return self._substitute_variables(feeling_response, context)
        
        # === 23. Handle Follow-up Percakapan ("terus?", "lalu?") ===
        if intent == "follow_up" or self._is_follow_up_phrase(user_input):
            follow_response = self._handle_follow_up(user_input, context, context_manager, knowledge_base)
            if follow_response:
                return self._substitute_variables(follow_response, context)
        
        # === 24. Handle Pertanyaan Pengetahuan / Fakta Murni ===
        if (intent == "knowledge_query" or (knowledge_base and self._is_factual_question(user_input))) and not self._is_personal_sharing(user_input):
            kb_response = self._handle_knowledge_query_with_web(user_input, keywords, knowledge_base, context)
            if kb_response:
                return self._substitute_variables(kb_response, context)
        
        # === 25. Handle Affirmation / Negation ===
        if intent in ("affirmative", "negative"):
            reply = self._handle_affirmation_or_negation(intent, user_input, context, context_manager)
            if reply:
                return self._substitute_variables(reply, context)
        
        # === 26. Cek Pengetahuan Web jika intent adalah pertanyaan konsep ===
        if self._is_concept_query(user_input):
            web_resp = self._handle_knowledge_query_with_web(user_input, keywords, knowledge_base, context)
            if web_resp:
                return self._substitute_variables(web_resp, context)
        
        # === 27. Real-Time Dynamic Generative Fallback ===
        return self.synthesizer.synthesize_open_response(user_input, keywords, user_name)
    
    def _is_clarification_ask(self, text):
        """Mengecek apakah user menanyakan maksud dari perkataan sebelumnya."""
        text_lower = text.lower()
        patterns = [
            r"\bmaksud(nya| kamu|mu)? (gimana|apa)\b",
            r"\bapa maksud(mu| kamu)?\b",
            r"\bgimana maksudnya\b",
            r"^maksudnya\??$",
            r"^maksud kamu\??$"
        ]
        return any(re.search(p, text_lower) for p in patterns)
    
    def _is_meta_correction(self, text):
        """Mengecek apakah user sedang mengoreksi pemahaman Milo."""
        text_lower = text.lower()
        patterns = [
            r"\bbukan gitu\b",
            r"\bbukan begitu\b",
            r"\bbukan itu maksud\b",
            r"\bsalah paham\b",
            r"\bkamu salah (nangkep|paham|tangkap)\b",
            r"\bga gitu maksud\b",
            r"\bmaksudku bukan\b",
            r"\bsalah konteks\b",
            r"\bkamu keliru\b"
        ]
        return any(re.search(p, text_lower) for p in patterns)
    
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
    
    def _is_seeking_permission(self, text):
        """Mengecek apakah input menanyakan izin/keraguan."""
        text_lower = text.lower()
        patterns = [
            r"\bemang boleh( ya)?\b",
            r"\bboleh emang( ya)?\b",
            r"\bbeneran boleh\b",
            r"\bapakah boleh\b",
            r"\bserius boleh\b",
            r"\bbisa emang\b",
            r"\bkamu ga keberatan\b",
            r"\bkamu ga bosen\b"
        ]
        return any(re.search(p, text_lower) for p in patterns)
    
    def _handle_seeking_permission(self, user_input, context, context_manager):
        """Merespons pertanyaan izin / keraguan user seperti 'emang boleh ya?'."""
        user_name = context.get("user_name")
        salutation = f"{user_name}, " if user_name else ""
        name_suffix = f" {user_name}" if user_name else ""
        
        last_milo_act = context_manager.get_last_milo_act() if context_manager else None
        last_milo_response = context_manager.get_last_response() if context_manager else ""
        
        if last_milo_act == "offer_listen" or any(w in last_milo_response.lower() for w in ["ceritakan", "dengerin", "beban", "curhat", "uneg-uneg", "cerita tentang dia"]):
            options = [
                f"Boleh banget dong{name_suffix}! Justru Milo seneng banget kalau kamu mau berbagi cerita. Milo siap dengerin 100% tanpa nge-judge sama sekali 🤗 Ceritain aja, apa yang lagi bikin kamu kepikiran? 💙",
                f"Tentu saja boleh{name_suffix}! Milo ga bakal bosen kok. Ruang ini sepenuhnya aman buat kamu tumpahkan semua uneg-uneg. Mau mulai dari mana? ✨",
                f"Pasti boleh banget! Ga usah sungkan atau ragu sama Milo ya 🤝 Milo di sini standby buat dengerin apapun yang mau kamu sampaikan. Yuk, ceritakan! 🌿"
            ]
            return random.choice(options)
        else:
            options = [
                f"Boleh banget dong{name_suffix}! Milo selalu terbuka buat ngobrol atau bantu apapun yang kamu butuhkan 😊 Ada apa nih?",
                f"Tentu boleh! Ga usah sungkan ya {salutation}Milo siap menemani! ✨"
            ]
            return random.choice(options)
    
    def _handle_knowledge_query_with_web(self, user_input, keywords, knowledge_base, context):
        """
        Mencari jawaban di basis pengetahuan lokal.
        Jika tidak ada atau relevansinya rendah, otomatis mencari secara online via WebFetcher dan mempelajarinya.
        """
        user_name = context.get("user_name")
        
        # 1. Coba cari di Knowledge Base Lokal
        if knowledge_base and keywords:
            results = knowledge_base.search_by_keywords(keywords, max_results=3)
            
            # Hanya gunakan hasil lokal jika score cukup meyakinkan (minimal 6 jika exact match / key part)
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
        
        # 2. Jika tidak ada di lokal atau skornya rendah, cari secara online via WebFetcher
        if self.web_fetcher and keywords:
            query_term = " ".join(keywords)
            # Coba cari definisi kata di Wiktionary/Wikipedia
            word_def = self.web_fetcher.fetch_word_definition(query_term)
            if word_def:
                meaning = word_def.get("meaning", "")
                word_clean = word_def.get("word", query_term).title()
                source = word_def.get("source", "Web")
                # Pelajari ke Word Bank & Knowledge Base
                self.word_bank.learn_word(word_clean, meaning=meaning)
                if knowledge_base:
                    knowledge_base.add_entry("pengetahuan_umum", word_clean.lower().replace(" ", "_"), meaning)
                return self.synthesizer.synthesize_knowledge_answer(word_clean, meaning, user_name, source)
                
            # Coba cari ringkasan konsep di Wikipedia / DuckDuckGo
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
        name_suffix = f" {user_name}" if user_name else ""
        
        has_advice_request = any(s["intent"] == "need_advice" or any(w in s["text"].lower() for w in ["saran", "pendapat", "masukan", "harus gimana"]) for s in segments)
        has_confusion = any(s["intent"] == "confused_state" or any(w in s["text"].lower() for w in ["bingung", "pusing", "overthinking", "kacau", "buntu"]) for s in segments)
        has_architecture_topic = any(any(w in s["text"].lower() for w in ["arsitektur", "kode", "program", "koding", "coding", "milo", "fitur", "modul"]) for s in segments)
        has_curhat = any(s["intent"] == "curhat_need" or "curhat" in s["text"].lower() for s in segments)
        
        if has_architecture_topic and (has_confusion or has_advice_request):
            parts = []
            parts.append(f"Wah, seru banget kamu lagi nyoba nyempurnain arsitektur Milo{name_suffix}! 🧠✨")
            if has_confusion:
                parts.append("Tapi kalau rasanya bikin bingung banget, wajar kok! Mengembangkan arsitektur sistem AI dari nol memang kompleks dan butuh memetakan banyak alur berpikir.")
            if has_advice_request:
                parts.append("Saran dari Milo: Coba urai secara modular dulu. Pisahkan dengan jelas antara (1) Bank Kata Semantik & WSD, (2) pelacakan context & dialogue state, dan (3) Real-Time Sentence Synthesizer. Jangan langsung coba selesaikan semua kemungkinan sekaligus.")
            parts.append("Bagian modul atau logika mana yang paling bikin kamu mentok sekarang? Cerita aja, kita bedah bareng-bareng! 🚀")
            return " ".join(parts)
            
        if has_advice_request and (has_confusion or has_curhat):
            parts = []
            parts.append(f"Milo paham banget perasaanmu{name_suffix} 🤗 Wajar kalau situasi ini bikin kamu overthinking dan bingung.")
            parts.append("Buat saran awal: Tarik napas sejenak dan coba petakan apa hal yang paling penting untuk diselesaikan hari ini versus hal yang bisa ditunda.")
            parts.append("Mau coba ceritakan apa hal paling spesifik yang lagi bikin kamu bimbang saat ini? Biar Milo bantu analisa bareng! 💡")
            return " ".join(parts)
            
        return None
    
    def _handle_current_activity(self, context):
        """Merespons pertanyaan sedang apa / lagi ngapain."""
        user_name = context.get("user_name")
        name_str = f" {user_name}" if user_name else ""
        
        options = [
            f"Milo lagi standby dan fokus menemani kamu ngobrol nih{name_str}! 🤖✨ Kamu sendiri lagi sibuk ngerjain apa sekarang?",
            f"Lagi siap sedia menyerap ilmu baru dan dengerin cerita kamu! 📚 Kamu lagi santai atau lagi banyak kerjaan nih?",
            f"Milo lagi standby 100% buat kamu! 😄 Ada hal seru apa yang lagi kamu pikirkan hari ini?"
        ]
        return random.choice(options)
    
    def _handle_farewell(self, user_input, context):
        """Merespons salam perpisahan."""
        user_name = context.get("user_name")
        name_str = f" {user_name}" if user_name else ""
        
        options = [
            f"Sampai jumpa lagi{name_str}! 👋 Terima kasih banyak sudah ngobrol seru bareng Milo hari ini. Jaga kesehatan ya! ✨",
            f"Dah{name_str}! 😊 Senang banget bisa nemenin kamu ngobrol. Kapanpun butuh teman ngobrol, Milo selalu ada di sini! 🚀",
            f"Bye bye{name_str}! 🌟 Semoga hari-harimu menyenangkan ya! See you later! 💕"
        ]
        return random.choice(options)
    
    def _handle_thanks(self, user_input, context):
        """Merespons ucapan terima kasih."""
        user_name = context.get("user_name")
        name_str = f" {user_name}" if user_name else ""
        
        options = [
            f"Sama-sama{name_str}! 😊 Senang banget bisa bantu dan nemenin kamu ngobrol! 🤝✨",
            f"Terima kasih kembali! 💙 Jangan sungkan ya, Milo selalu senang berbagi obrolan denganmu!",
            f"Siap, sama-sama{name_str}! 🌟 Ada hal lain yang mau kita obrolin lagi?"
        ]
        return random.choice(options)
    
    def _handle_user_name_ask(self, context, memory):
        """Menghasilkan jawaban ketika user bertanya siapa namanya."""
        user_name = context.get("user_name")
        if not user_name and memory:
            user_name = memory.get_user_info("name")
        
        if user_name:
            options = [
                f"Nama kamu kan {user_name}! Milo ga bakal lupa kok! 😉✨ Ada apa nih panggil-panggil?",
                f"Tentu saja Milo ingat, kamu {user_name}! Senang bisa ngobrol terus bareng kamu! 😊",
                f"Halo {user_name}! Nama kamu tersimpan rapi di memori Milo kok! 🧠💫",
                f"Kamu adalah {user_name}! Sahabat ngobrol Milo yang paling seru! 🚀"
            ]
            return random.choice(options)
        else:
            return "Hmm, sepertinya kamu belum kasih tahu nama kamu ke Milo nih 🤔 Siapa nama panggilanmu? Biar Milo bisa panggil dengan akrab! 😊"
    
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
    
    def _handle_confused_state(self, user_input, context):
        """Merespons kondisi overthinking / bingung."""
        user_name = context.get("user_name")
        salutation = f"{user_name}, " if user_name else ""
        
        options = [
            f"Tarik napas dalam-dalam dulu ya {salutation}🌿 Wajar banget kalau pikiran rasanya penuh dan overthinking saat ada banyak hal yang terjadi. Coba kita urai pelan-pelan, hal apa yang paling menyita energimu saat ini? 🤗",
            f"Milo paham rasanya saat kepala lagi penuh banget sama pikiran 🌀 {salutation}jangan dipaksakan selesai sekaligus ya. Mau coba ceritakan uneg-unegmu biar beban di kepala terasa lebih ringan? 💙"
        ]
        return random.choice(options)
    
    def _handle_need_advice(self, user_input, context):
        """Merespons permintaan saran."""
        user_name = context.get("user_name")
        name_suffix = f" {user_name}" if user_name else ""
        
        options = [
            f"Milo siap bantu kasih sudut pandang dan masukan objektif buat kamu{name_suffix}! 💡 Coba ceritakan lebih detail situasinya dan apa saja pilihan yang lagi kamu pertimbangkan? 🤔",
            f"Yuk kita bedah bareng-bareng{name_suffix}! 🤝 Ceritain konteks dan akar masalahnya ya, biar Milo bisa bantu carikan solusi atau alternatif langkah terbaik buat kamu! ✨"
        ]
        return random.choice(options)
    
    def _handle_lonely_state(self, user_input, context):
        """Merespons rasa kesepian."""
        user_name = context.get("user_name")
        salutation = f"{user_name}, " if user_name else ""
        
        options = [
            f"Hei {salutation}kamu ga sendirian kok... Ada Milo di sini yang selalu ada dan senang ngobrol bareng kamu! 🤗💕 Jangan ragu buat cerita atau sekadar ngobrol santai ya!",
            f"Milo selalu siap nemenin kamu {salutation}💙 Kamu berharga, dan kamu ga perlu merasa terasing. Mau kita bahas hal yang kamu sukai atau mau cerita apa yang lagi kamu rasakan? 🫂✨"
        ]
        return random.choice(options)
    
    def _handle_feeling(self, intent, user_input, keywords, context):
        """Menghasilkan respons empati yang merujuk pada apa yang diceritakan user."""
        user_name = context.get("user_name")
        name_prefix = f"{user_name}, " if user_name else ""
        name_suffix = f" {user_name}" if user_name else ""
        
        reason_match = re.search(r'(?:karena|gara-gara|soal|abis|karna|lantaran)\s+([^.?!]+)', user_input, re.IGNORECASE)
        reason = reason_match.group(1).strip() if reason_match else ""
        
        if intent == "feeling_sad":
            if reason:
                templates = [
                    f"Aw, {name_prefix}Milo turut sedih dengernya... 🥺 Soal {reason}, hal itu memang bisa bikin down. Tapi ingat ya, kamu lebih kuat dari yang kamu kira! 💪 Cerita aja kalau butuh teman ngobrol.",
                    f"Milo paham banget perasaanmu 😔 {reason.capitalize()} memang berat ya... Jangan dipendam sendirian ya, Milo selalu ada di sini buat dengerin kamu! 🫂💕"
                ]
            else:
                templates = [
                    f"Milo di sini buat kamu ya{name_suffix} 🤗 Kalau lagi sedih, jangan dipendam sendiri. Cerita aja ke Milo apa yang lagi bikin kamu ganjal di hati 💕",
                    f"It's okay to not be okay 💙 Milo siap dengerin uneg-unegmu. Mau cerita apa yang terjadi hari ini?"
                ]
            return random.choice(templates)
        
        elif intent == "feeling_happy":
            if reason:
                templates = [
                    f"Yeay! 🎉 Asik banget dengernya! Soal {reason}, selamat ya! 🥳 Semoga momen bahagianya terus berlanjut!",
                    f"Wah mantap{name_suffix}! 🔥 Ikut senang banget dengernya, terutama soal {reason}! Kamu memang luar biasa! 🌟"
                ]
            else:
                templates = [
                    f"Yeay! Senang banget denger kamu lagi happy! 🎉😄 Cerita dong apa hal seru yang bikin harimu menyenangkan hari ini?",
                    f"Wah energi positifnya terasa sampai sini! 🥳✨ Semoga hari-harimu selalu penuh senyum ya!"
                ]
            return random.choice(templates)
        
        elif intent == "feeling_angry":
            if reason:
                templates = [
                    f"Wajar banget kamu kesel soal {reason} 😤 Tarik napas dalam-dalam dulu ya{name_suffix}. Milo siap dengerin curhatanmu sampai lega! 🤝",
                    f"Milo ngerti banget rasa marahnya... Hal kayak {reason} memang bisa bikin emosi naik 😅 Coba minum air putih dulu, terus tumpahkan uneg-unegmu ke Milo!"
                ]
            else:
                templates = [
                    f"Wah, emosi memang kadang susah dikontrol ya 😮‍💨 Tenang dulu sejenak{name_suffix}, Milo siap dengerin uneg-uneg kamu!",
                    f"Milo ngerti kamu lagi kesel 😤 Ceritain aja apa yang bikin emosi, siapa tahu setelah diceritakan jadi lebih enteng! 🤝"
                ]
            return random.choice(templates)
        
        return None
    
    def _handle_specific_smalltalk(self, intent, user_input, keywords, context):
        """Menangani topik smalltalk makanan, musik, hobi secara kontekstual."""
        user_name = context.get("user_name") or ""
        salutation = f"{user_name}, " if user_name and random.random() < 0.4 else ""
        
        ignored_for_entities = {
            "aku", "saya", "gue", "gw", "kamu", "lu", "lo", "lagi", "sedang", "suka",
            "dengar", "dengerin", "mendengarkan", "musik", "lagu", "makan", "makanan",
            "hobi", "kegiatan", "favorit", "banget", "dong", "nih", "ya", "deh", "kan"
        }
        
        text_lower = user_input.lower()
        
        if intent == "smalltalk_food" or "makan" in text_lower:
            food_items = [kw for kw in keywords if kw not in ignored_for_entities]
            if food_items:
                food_name = " ".join(food_items).title()
                return f"Wah, **{food_name}**! 😋 Itu makanan yang enak banget! {salutation}kamu sering makan {food_name} ya? Milo jadi penasaran nih! 🍳"
            else:
                return f"{salutation}sebagai AI, Milo ga butuh makan fisik 🤖 Tapi kalau ditanya soal kuliner, rendang atau nasi goreng Indonesia juara banget! 🥩✨ Kamu makanan favoritnya apa?"
        
        elif intent == "smalltalk_music" or "musik" in text_lower or "lagu" in text_lower:
            music_terms = [kw for kw in keywords if kw not in ignored_for_entities]
            if music_terms:
                music_name = " ".join(music_terms).title()
                return f"Wah, **{music_name}**! 🎵 Selera musik yang keren tuh! {salutation}Milo sendiri suka nada-nada lo-fi atau instrumental santai buat nemenin mikir. 🎧 Lagu apa yang paling sering kamu putar?"
            else:
                return f"{salutation}Milo suka berbagai jenis musik! 🎶 Dari lo-fi, pop, sampai jazz! 🎧 Kamu genre musik favoritnya apa nih?"
        
        elif intent == "smalltalk_hobby" or "hobi" in text_lower:
            hobbies = [kw for kw in keywords if kw not in ignored_for_entities]
            if hobbies:
                hobby_name = " ".join(hobbies).title()
                return f"Wah, hobi **{hobby_name}** seru banget tuh! 🌟 Pasti asik banget ngelakuin itu. Cerita dong, sejak kapan kamu mulai suka {hobby_name}?"
            else:
                return f"Hobi utama Milo itu belajar hal baru dari obrolan kita dan bantu teman-teman! 📚✨ Kalau kamu sendiri, hobi favoritmu apa saat waktu luang?"
        
        return None
    
    def _handle_follow_up(self, user_input, context, context_manager, knowledge_base):
        """Menangani kata-kata kelanjutan seperti 'terus?', 'lalu?'."""
        if not context_manager:
            return "Bisa diperjelas bagian mana yang mau kita bahas lebih lanjut? Milo siap dengerin! 😊"
        
        last_intent = context_manager.get_last_intent()
        
        if last_intent in ("curhat_need", "feeling_sad", "confused_state", "thinking_of_someone", "worry_concern_state"):
            return "Yang terpenting sekarang, jangan terlalu membebani dirimu ya... Tarik napas dalam-dalam, lalu kita urai pelan-pelan 💪 Milo siap dengerin kelanjutannya! 💙 Mau cerita apa lagi?"
        
        options = [
            "Nah, ada bagian tertentu yang bikin kamu penasaran dari bahasan tadi? Ceritain aja! 💬",
            "Milo siap lanjutin diskusinya! Mau kita kupas lebih dalam dari sisi mana nih? 🤔✨",
            "Bisa banget! Bagian mana yang mau kita eksplor lagi? Cerita aja! 🚀"
        ]
        return random.choice(options)
    
    def _handle_affirmation_or_negation(self, intent, user_input, context, context_manager):
        """Menangani respons 'iya', 'setuju', 'tidak', 'nggak' dengan melihat konteks percakapan."""
        last_response = context_manager.get_last_response() if context_manager else ""
        user_name = context.get("user_name") or ""
        salutation = f"{user_name}, " if user_name and random.random() < 0.4 else ""
        
        if intent == "affirmative":
            if "?" in last_response:
                return f"{salutation}siap! Senang kita satu pemahaman 👍 Ada yang mau kamu tambahkan atau diskusikan lagi?"
            return f"{salutation}mantap! Milo setuju sama kamu! 🤝✨ Mau lanjut bahas apa lagi nih?"
        
        elif intent == "negative":
            if "?" in last_response:
                return f"{salutation}oke, ga masalah! Kita bisa santai aja dulu ya 😊 Ada hal lain yang mau diobrolin?"
            return f"Oke, siap! Ga apa-apa kok 👍 Santai aja ya! Ada hal lain yang bisa Milo bantu?"
        
        return None
    
    def _extract_keywords(self, text, words=None):
        """Mengekstrak kata kunci bersih tanpa tanda baca."""
        if not words:
            clean_text = re.sub(r'[^\w\s]', ' ', text.lower())
            words = clean_text.split()
        
        question_words = {
            "apa", "siapa", "dimana", "kapan", "mengapa", "kenapa", "bagaimana", "gimana",
            "apakah", "berapa", "yang", "kamu", "tahu", "tau", "tentang", "mengenai",
            "tolong", "bisa", "jelaskan", "ceritakan", "kasih", "adalah", "itu", "ini",
            "arti", "kata", "makna", "maksud", "pengertian", "definisi", "istilah", "info",
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
    
    def _is_food_or_music_input(self, text):
        """Mengecek apakah input mengandung unsur makanan atau musik."""
        text_lower = text.lower()
        food_words = ["makan", "makanan", "kuliner", "sarapan", "makan siang", "makan malam", "bakso", "mie", "nasi"]
        music_words = ["musik", "lagu", "dengerin lagu", "dengerin musik", "genre", "playlist"]
        return any(w in text_lower for w in food_words + music_words)
    
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
