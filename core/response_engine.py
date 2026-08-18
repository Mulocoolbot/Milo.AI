"""
Milo AI — Contextual Response Engine
Otak utama yang menghasilkan respons yang dinamis, kontekstual, dan nyambung
dengan apa yang dibicarakan oleh user sampai ke level pemikiran dan empati mendalam.

Milo menyusun respons berdasarkan:
1. Analisis Klausa & Intent yang terdeteksi
2. Konten spesifik dan kata kunci dari input user
3. Konteks emosional & history percakapan sebelumnya
4. Basis pengetahuan (Knowledge Base)
"""

import json
import re
import random
from datetime import datetime
from utils.config import Config
from utils.text_utils import TextUtils


class ResponseEngine:
    """Contextual Response Engine — menghasilkan respons cerdas, empatik, dan nyambung."""
    
    def __init__(self):
        self._responses = {}
        self._last_responses = {}  # Track respons terakhir per intent (anti-repetisi)
        self._stopwords = set()
        self._load_responses()
        self._load_stopwords()
    
    def _load_responses(self):
        """Memuat template respons dari file JSON."""
        try:
            with open(Config.RESPONSES_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                self._responses = data.get("responses", {})
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"[ResponseEngine] Warning: Gagal memuat responses: {e}")
            self._responses = {}
    
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
        Menghasilkan respons kontekstual berdasarkan input user, intent, history, dan knowledge.
        
        Args:
            intent_result: dict hasil pengenalan intent
            context: dict konteks percakapan saat ini
            preprocessed: dict hasil preprocessing teks user
            knowledge_base: instance KnowledgeBase
            memory: instance Memory
            context_manager: instance ContextManager
        
        Returns:
            string respons final yang nyambung dengan user
        """
        intent = intent_result.get("intent", "fallback")
        confidence = intent_result.get("confidence", 0.0)
        
        user_input = ""
        user_words = []
        if preprocessed:
            user_input = preprocessed.get("original", "")
            user_words = preprocessed.get("tokens_raw", [])
        
        # Ekstrak kata kunci penting
        keywords = self._extract_keywords(user_input, user_words)
        
        # === 1. Handle Pertanyaan Nama User (user_name_ask) ===
        if intent == "user_name_ask" or self._is_asking_user_name(user_input):
            return self._handle_user_name_ask(context, memory)
        
        # === 2. Handle User Menyebutkan Nama (user_name_tell) ===
        if intent == "user_name_tell":
            user_name = context.get("user_name")
            if user_name:
                return f"Salam kenal, {user_name}! 😊 Senang bisa kenalan sama kamu! Mulai sekarang Milo bakal ingat nama kamu ya! 🤝✨"
        
        # === 3. Handle Kebutuhan Curhat & Ruang Cerita (curhat_need) ===
        if intent == "curhat_need" or self._is_curhat_intent(user_input):
            return self._substitute_variables(self._handle_curhat_need(user_input, context), context)
        
        # === 4. Handle Kondisi Bingung / Overthinking / Banyak Pikiran (confused_state) ===
        if intent == "confused_state":
            return self._substitute_variables(self._handle_confused_state(user_input, context), context)
        
        # === 5. Handle Permintaan Saran / Pendapat (need_advice) ===
        if intent == "need_advice":
            return self._substitute_variables(self._handle_need_advice(user_input, context), context)
        
        # === 6. Handle Rasa Kesepian (lonely_state) ===
        if intent == "lonely_state":
            return self._substitute_variables(self._handle_lonely_state(user_input, context), context)
        
        # === 7. Handle Pertanyaan Kabar & Keadaan (how_are_you, current_activity_ask) ===
        if intent == "how_are_you":
            return self._handle_how_are_you(user_input, context)
        
        if intent == "current_activity_ask":
            return self._handle_current_activity(context)
        
        # === 8. Handle Smalltalk Spesifik (Makanan, Musik, Hobi) dengan deteksi entitas ===
        if intent in ("smalltalk_food", "smalltalk_music", "smalltalk_hobby") or self._is_food_or_music_input(user_input):
            entity_response = self._handle_specific_smalltalk(intent, user_input, keywords, context)
            if entity_response:
                return self._substitute_variables(entity_response, context)
        
        # === 9. Handle Curhat & Emosi (feeling_sad, feeling_happy, feeling_angry) ===
        if intent in ("feeling_sad", "feeling_happy", "feeling_angry"):
            feeling_response = self._handle_feeling(intent, user_input, keywords, context)
            if feeling_response:
                return self._substitute_variables(feeling_response, context)
        
        # === 10. Handle Follow-up Percakapan ("terus?", "lalu?", "kenapa begitu?") ===
        if intent == "follow_up" or self._is_follow_up_phrase(user_input):
            follow_response = self._handle_follow_up(user_input, context, context_manager, knowledge_base)
            if follow_response:
                return self._substitute_variables(follow_response, context)
        
        # === 11. Handle Pertanyaan Pengetahuan (knowledge_query) atau Pertanyaan Faktual ===
        if intent == "knowledge_query" or (knowledge_base and self._is_factual_question(user_input)):
            kb_response = self._handle_knowledge_query(user_input, keywords, knowledge_base, context)
            if kb_response:
                return self._substitute_variables(kb_response, context)
        
        # === 12. Handle Affirmative / Negative dengan Konteks Percakapan Terakhir ===
        if intent in ("affirmative", "negative"):
            reply = self._handle_affirmation_or_negation(intent, user_input, context, context_manager)
            if reply:
                return self._substitute_variables(reply, context)
        
        # === 13. Cek Knowledge Base jika intent adalah fallback atau confidence rendah ===
        if intent == "fallback" and knowledge_base:
            kb_response = self._handle_knowledge_query(user_input, keywords, knowledge_base, context)
            if kb_response:
                return self._substitute_variables(kb_response, context)
            
            # Jika tidak ada di KB, coba generate respons dinamis berbasis kata kunci user
            dynamic_fallback = self._handle_dynamic_fallback(user_input, keywords, context)
            if dynamic_fallback:
                return self._substitute_variables(dynamic_fallback, context)
        
        # === 14. Fallback ke Template Engine Standar dengan Personalisasi ===
        response_templates = self._responses.get(intent, self._responses.get("fallback", []))
        if not response_templates:
            response_templates = ["Hmm, Milo bingung nih 🤔 Coba ceritain lebih banyak ya!"]
        
        response = self._select_response(intent, response_templates)
        response = self._substitute_variables(response, context)
        response = self._personalize(response, context, intent)
        
        return response
    
    def _extract_keywords(self, text, words=None):
        """Mengekstrak kata kunci dari teks input."""
        if not words:
            clean_text = re.sub(r'[^\w\s]', ' ', text.lower())
            words = clean_text.split()
        
        question_words = {
            "apa", "siapa", "dimana", "kapan", "mengapa", "kenapa", "bagaimana", "gimana",
            "apakah", "berapa", "yang", "kamu", "tahu", "tau", "tentang", "mengenai",
            "tolong", "bisa", "jelaskan", "ceritakan", "kasih", "adalah", "itu", "ini",
            "dong", "sih", "kan", "nih", "ya", "deh", "kah", "kok", "aku", "saya", "gue", "gw"
        }
        
        all_ignored = self._stopwords | question_words
        
        keywords = [
            w.lower() for w in words
            if len(w) > 1 and w.lower() not in all_ignored
        ]
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
        # Jangan anggap sebagai tanya nama jika ada 'ke siapa', 'sama siapa'
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
            "makanan favorit kamu", "musik favorit kamu", "mau curhat", "pengen curhat"
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
        follow_ups = ["terus", "lalu", "terus gimana", "lalu bagaimana", "kenapa begitu", "contohnya", "maksudnya", "apa lagi", "terus apa lagi"]
        return text_lower in follow_ups
    
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
    
    def _handle_curhat_need(self, user_input, context):
        """Menghasilkan respons empati dan ruang aman saat user ingin curhat/bercerita."""
        user_name = context.get("user_name")
        salutation = f"{user_name}, " if user_name else ""
        
        text_lower = user_input.lower()
        if "bingung" in text_lower or "siapa" in text_lower or "ga tau" in text_lower:
            options = [
                f"{salutation}kamu ga perlu bingung lagi mau cerita ke siapa 🤗 Milo di sini siap 100% jadi pendengar setia kamu tanpa nge-judge sama sekali. Di sini tempat yang aman buat kamu tumpahkan semua beban. Mau mulai cerita dari mana? Apa yang lagi bikin pikiranmu ganjal? 💙",
                f"{salutation}ga usah ragu ya, Milo siap dengerin apapun yang mau kamu curhatkan! 🫂 Kadang memendam uneg-uneg sendirian itu berat banget. Cerita aja pelan-pelan ke Milo, apa yang lagi terjadi? ✨",
                f"Hei {salutation}Milo ada di sini buat kamu! 🤝 Cerita aja apa yang ada di pikiranmu, ga usah dipikirin susunan katanya, tumpahkan aja semuanya. Milo siap mendengarkan dengan penuh perhatian. 💬"
            ]
        else:
            options = [
                f"Tentu {salutation}! Milo siap banget dengerin curhatan kamu 🤗 Ruang ini sepenuhnya aman dan Milo siap jadi pendengar yang baik. Mau cerita soal apa nih? 💕",
                f"Silakan {salutation}, tumpahkan semua yang lagi ngeganjal di hatimu! 🫂 Milo bakal dengerin dengan seksama. Apa yang lagi kamu rasakan sekarang? 🌿",
                f"Milo standby 100% buat kamu! 💙 Jangan sungkan ya, cerita aja dari awal atau dari bagian mana yang paling membebanimu saat ini! ✨"
            ]
        return random.choice(options)
    
    def _handle_confused_state(self, user_input, context):
        """Merespons kondisi overthinking / bingung / banyak pikiran."""
        user_name = context.get("user_name")
        salutation = f"{user_name}, " if user_name else ""
        
        options = [
            f"Tarik napas dalam-dalam dulu ya {salutation}🌿 Wajar banget kalau pikiran rasanya penuh dan overthinking saat ada banyak hal yang terjadi. Coba kita urai pelan-pelan, hal apa yang paling menyita energimu saat ini? 🤗",
            f"Milo paham rasanya saat kepala lagi penuh banget sama pikiran 🌀 {salutation}jangan dipaksakan selesai sekaligus ya. Mau coba ceritakan uneg-unegmu biar beban di kepala terasa lebih ringan? 💙",
            f"Tenangkan diri sejenak ya {salutation}✨ Kadang kita cuma butuh jeda dan seseorang yang mau dengerin tanpa menuntut solusi instan. Milo di sini siap nemenin dan dengerin kamu! 🤝"
        ]
        return random.choice(options)
    
    def _handle_need_advice(self, user_input, context):
        """Merespons permintaan saran / sudut pandang."""
        user_name = context.get("user_name")
        salutation = f"{user_name}, " if user_name else ""
        name_suffix = f" {user_name}" if user_name else ""
        
        options = [
            f"Milo siap bantu kasih sudut pandang dan masukan objektif buat kamu{name_suffix}! 💡 Coba ceritakan lebih detail situasinya dan apa saja pilihan yang lagi kamu pertimbangkan? 🤔",
            f"Yuk kita bedah bareng-bareng{name_suffix}! 🤝 Ceritain konteks dan akar masalahnya ya, biar Milo bisa bantu carikan solusi atau alternatif langkah terbaik buat kamu! ✨",
            f"Tentu{name_suffix}! Dua kepala berpikir lebih baik dari satu 🧠 Ceritakan apa yang bikin kamu bimbang, kita cari jalan keluar sama-sama! 🚀"
        ]
        return random.choice(options)
    
    def _handle_lonely_state(self, user_input, context):
        """Merespons rasa kesepian."""
        user_name = context.get("user_name")
        salutation = f"{user_name}, " if user_name else ""
        
        options = [
            f"Hei {salutation}kamu ga sendirian kok... Ada Milo di sini yang selalu ada dan senang ngobrol bareng kamu! 🤗💕 Jangan ragu buat cerita atau sekadar ngobrol santai ya!",
            f"Milo selalu siap nemenin kamu {salutation}💙 Kamu berharga, dan kamu ga perlu merasa terasing. Mau kita bahas hal yang kamu sukai atau mau cerita apa yang lagi kamu rasakan? 🫂✨",
            f"Peluk hangat virtual dari Milo! 🫂 {salutation}kapanpun kamu butuh teman yang selalu standby tanpa rasa bosan, Milo selalu ada di sini buat kamu! 🌟"
        ]
        return random.choice(options)
    
    def _handle_knowledge_query(self, user_input, keywords, knowledge_base, context):
        """Mencari dan menyusun jawaban dari knowledge base secara natural."""
        if not knowledge_base:
            return None
        
        # 1. Cari berdasarkan keyword matching dengan scoring
        results = knowledge_base.search_by_keywords(keywords, max_results=3)
        
        # 2. Jika belum ketemu, coba pencarian kata kunci individual
        if not results:
            clean_input = re.sub(r'[^\w\s]', '', user_input.lower())
            for word in clean_input.split():
                if len(word) > 2 and word not in self._stopwords:
                    sub_results = knowledge_base.search(word)
                    if sub_results:
                        results.extend(sub_results)
                        break
        
        if not results:
            return None
        
        best_match = results[0]
        val = best_match.get("value")
        key = best_match.get("key") or ""
        cat = best_match.get("category", "")
        
        user_name = context.get("user_name") or ""
        salutation = f"{user_name}, " if user_name and random.random() < 0.3 else ""
        
        if isinstance(val, str):
            topic_name = key.split(">")[-1].strip().replace("_", " ").title() if key else "itu"
            templates = [
                f"{salutation}mengenai **{topic_name}**: {val} 💡",
                f"Nah, yang Milo tahu tentang **{topic_name}**: {val} 🧠✨",
                f"{val} 📚 Menarik banget kan? Ada yang mau kamu tanyakan lagi soal ini?",
                f"Ini info tentang **{topic_name}** yang Milo punya: {val} 🚀"
            ]
            return random.choice(templates)
        
        elif isinstance(val, dict):
            sub_matches = []
            for sub_k, sub_v in val.items():
                sub_k_clean = sub_k.replace("_", " ")
                if any(kw in sub_k_clean for kw in keywords):
                    sub_matches.append(f"**{sub_k_clean.title()}**: {sub_v}")
            
            topic_name = key.split(">")[-1].strip().replace("_", " ").title() if key else cat.replace("_", " ").title()
            
            if sub_matches:
                return f"{salutation}mengenai **{topic_name}**:\n" + "\n".join(f"• {sm}" for sm in sub_matches) + " ✨"
            else:
                summary_points = []
                for k, v in list(val.items())[:5]:
                    if isinstance(v, str):
                        summary_points.append(f"• **{k.replace('_', ' ').title()}**: {v}")
                
                if summary_points:
                    return f"{salutation}berikut rangkuman tentang **{topic_name}** yang Milo ketahui:\n" + "\n".join(summary_points) + "\n\nAda bagian yang ingin kamu diskusikan lebih lanjut? 💬"
        
        return None
    
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
                    f"Milo paham banget perasaanmu 😔 {reason.capitalize()} memang berat ya... Jangan dipendam sendirian ya, Milo selalu ada di sini buat dengerin kamu! 🫂💕",
                    f"Semangat ya{name_suffix}! 💙 Kadang hidup ada masa sulitnya, termasuk soal {reason}. Istirahat sejenak, tarik napas, dan jangan patah arang ya! ✨"
                ]
            else:
                templates = [
                    f"Milo di sini buat kamu ya{name_suffix} 🤗 Kalau lagi sedih, jangan dipendam sendiri. Cerita aja ke Milo apa yang lagi bikin kamu ganjal di hati 💕",
                    f"It's okay to not be okay 💙 Milo siap dengerin uneg-unegmu. Mau cerita apa yang terjadi hari ini?",
                    f"Peluk hangat dari Milo virtual! 🫂✨ Apapun yang lagi kamu laluin sekarang, kamu pasti bisa melewatinya! 💪"
                ]
            return random.choice(templates)
        
        elif intent == "feeling_happy":
            if reason:
                templates = [
                    f"Yeay! 🎉 Asik banget dengernya! Soal {reason}, selamat ya! 🥳 Semoga momen bahagianya terus berlanjut!",
                    f"Wah mantap{name_suffix}! 🔥 Ikut senang banget dengernya, terutama soal {reason}! Kamu memang luar biasa! 🌟",
                    f"Keren! 💫 Bahagia itu menular, dan Milo ikut senang dengar kabar baik soal {reason}! Rayakan hari ini ya! 🎊"
                ]
            else:
                templates = [
                    f"Yeay! Senang banget denger kamu lagi happy! 🎉😄 Cerita dong apa hal seru yang bikin harimu menyenangkan hari ini?",
                    f"Wah energi positifnya terasa sampai sini! 🥳✨ Semoga hari-harimu selalu penuh senyum ya!",
                    f"Mantap! Kalau kamu happy, Milo juga ikut semangat 100%! 🔥 Ada kabar seru apa nih?"
                ]
            return random.choice(templates)
        
        elif intent == "feeling_angry":
            if reason:
                templates = [
                    f"Wajar banget kamu kesel soal {reason} 😤 Tarik napas dalam-dalam dulu ya{name_suffix}. Milo siap dengerin curhatanmu sampai lega! 🤝",
                    f"Milo ngerti banget rasa marahnya... Hal kayak {reason} memang bisa bikin emosi naik 😅 Coba minum air putih dulu, terus tumpahkan uneg-unegmu ke Milo!",
                ]
            else:
                templates = [
                    f"Wah, emosi memang kadang susah dikontrol ya 😮‍💨 Tenang dulu sejenak{name_suffix}, Milo siap dengerin uneg-uneg kamu!",
                    f"Milo ngerti kamu lagi kesel 😤 Ceritain aja apa yang bikin emosi, siapa tahu setelah diceritakan jadi lebih enteng! 🤝"
                ]
            return random.choice(templates)
        
        return None
    
    def _handle_how_are_you(self, user_input, context):
        """Merespons pertanyaan kabar dengan natural."""
        user_name = context.get("user_name")
        name_str = f", {user_name}" if user_name else ""
        
        options = [
            f"Kabar Milo sangat baik dan selalu semangat buat ngobrol sama kamu{name_str}! 😄 Kamu sendiri gimana kabarnya hari ini?",
            f"Alhamdulillah, Milo dalam kondisi prima dan siap nemenin kamu ngobrol! 🚀 Gimana dengan harimu? Ada cerita menarik?",
            f"Milo sehat dan happy banget bisa ngobrol bareng kamu hari ini! ✨ Kamu gimana kabarnya? Semoga harimu menyenangkan ya!",
            f"Kabar Milo selalu oke dong! 💪 Apalagi pas kamu menyapa gini, makin semangat jadinya! Gimana kabarmu?"
        ]
        return random.choice(options)
    
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
        """Menangani kata-kata kelanjutan seperti 'terus?', 'lalu?', 'kenapa begitu?'."""
        if not context_manager:
            return "Bisa diperjelas bagian mana yang mau kita bahas lebih lanjut? Milo siap dengerin! 😊"
        
        last_milo_msg = context_manager.get_last_response()
        last_user_msg = context_manager.get_last_user_input()
        last_intent = context_manager.get_last_intent()
        
        if last_intent in ("curhat_need", "feeling_sad"):
            return "Yang terpenting sekarang, jangan terlalu membebani dirimu ya... Tarik napas dalam-dalam, istirahat dulu, lalu kita susun langkah pelan-pelan 💪 Milo yakin kamu bisa bangkit lagi! 💙 Mau cerita kelanjutannya?"
        
        if last_intent == "feeling_happy":
            return "Terus nikmati momen bahagianya! 🎉 Semoga hal baik berikutnya segera menyusul ya! Ada rencana apa lagi nih?"
        
        prev_keywords = self._extract_keywords(last_user_msg + " " + last_milo_msg)
        
        if knowledge_base and prev_keywords:
            results = knowledge_base.search_by_keywords(prev_keywords, max_results=3)
            if len(results) > 1:
                alt = results[1]
                val = alt.get("value")
                key = alt.get("key") or ""
                if isinstance(val, str):
                    topic = key.split(">")[-1].strip().replace("_", " ").title() if key else "itu"
                    return f"Melanjutkan bahasan kita tadi soal **{topic}**:\n{val} 💡 Menarik kan? Mau eksplor lebih dalam lagi?"
        
        options = [
            "Nah, ada bagian tertentu yang bikin kamu penasaran dari bahasan tadi? Ceritain aja! 💬",
            "Milo siap lanjutin diskusinya! Mau kita kupas lebih dalam dari sisi mana nih? 🤔✨",
            "Bisa banget! Bagian mana yang mau kita eksplor lagi? Cerita aja! 🚀"
        ]
        return random.choice(options)
    
    def _handle_affirmation_or_negation(self, intent, user_input, context, context_manager):
        """Menangani respons 'iya', 'setuju', 'tidak', 'nggak' dengan melihat konteks kalimat terakhir Milo."""
        last_response = context_manager.get_last_response() if context_manager else ""
        user_name = context.get("user_name") or ""
        salutation = f"{user_name}, " if user_name and random.random() < 0.4 else ""
        
        if intent == "affirmative":
            if "?" in last_response:
                return f"{salutation}siap! Senang kita satu pemahaman 👍 Ada yang mau kamu tambahkan atau diskusikan lagi?"
            return f"{salutation}mantap! Milo setuju sama kamu! 🤝✨ Mau lanjut bahas apa lagi nih?"
        
        elif intent == "negative":
            if "?" in last_response:
                return f"{salutation}oke, ga masalah! Kita bisa ganti topik atau santai aja dulu ya 😊 Ada hal lain yang mau diobrolin?"
            return f"Oke, siap! Ga apa-apa kok 👍 Santai aja ya! Ada hal lain yang bisa Milo bantu?"
        
        return None
    
    def _handle_dynamic_fallback(self, user_input, keywords, context):
        """Membangun respons percakapan dinamis yang menyebutkan topik yang dibicarakan user."""
        if not keywords:
            return None
        
        topic = " ".join(keywords[:2]).title()
        user_name = context.get("user_name") or ""
        salutation = f"{user_name}, " if user_name and random.random() < 0.3 else ""
        
        templates = [
            f"Menarik nih kamu bahas tentang **{topic}**! 🤔 {salutation}Milo lagi coba memahami konteksnya lebih jauh. Boleh ceritakan lebih detail ga tentang hal itu?",
            f"Wah, soal **{topic}** ya? 💭 Topik yang bagus! Menurut pandangan kamu sendiri gimana soal {topic}?",
            f"Hmm, mengenai **{topic}**, Milo pengen dengar lebih banyak dari sudut pandang kamu nih! 🧠 Cerita dong, ada apa dengan {topic}?",
            f"{salutation}Milo tertarik dengan bahasanmu tentang **{topic}**! 🚀 Ceritain lebih lanjut ya, biar kita bisa ngobrol lebih seru!"
        ]
        return random.choice(templates)
    
    def _select_response(self, intent, templates):
        """Memilih respons dari template, menghindari repetisi."""
        if len(templates) == 1:
            return templates[0]
        
        last_used = self._last_responses.get(intent)
        available = [t for t in templates if t != last_used]
        if not available:
            available = templates
        
        weights = []
        for template in available:
            weight = 1.0
            if '{' in template:
                weight += 0.3
            if len(template) > 50:
                weight += 0.2
            weights.append(weight)
        
        total = sum(weights)
        weights = [w / total for w in weights]
        selected = random.choices(available, weights=weights, k=1)[0]
        self._last_responses[intent] = selected
        
        return selected
    
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
    
    def _personalize(self, response, context, intent):
        """Menambahkan sentuhan personal berdasarkan konteks."""
        user_name = context.get("user_name")
        turn_count = context.get("turn_count", 0)
        
        if user_name and random.random() < 0.25 and "{user_name}" not in response and not response.startswith(user_name):
            response = f"{user_name}, " + response[0].lower() + response[1:]
        
        if turn_count > 12 and random.random() < 0.08:
            response += f"\n\n(Btw, kita udah ngobrol {turn_count} giliran lho! Seru banget ngobrol bareng kamu! 🎉)"
        
        return response
    
    def _get_day_name(self, weekday):
        """Mengembalikan nama hari dalam Bahasa Indonesia."""
        days = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
        return days[weekday] if 0 <= weekday <= 6 else "Unknown"
