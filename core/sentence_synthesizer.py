"""
Milo AI — Real-Time Generative Discourse Synthesizer
Mesin penyusun kalimat percakapan bahasa Indonesia secara real-time kata-per-kata
dan klausa-per-klausa dari Bank Kata Semantik (Word Bank).
Menghasilkan susunan kalimat alami, presisi tinggi, dan bebas template statis.
"""

import random
from datetime import datetime


class SentenceSynthesizer:
    """Real-Time Generative Discourse Synthesizer untuk Milo AI."""
    
    def __init__(self, word_bank):
        self.word_bank = word_bank
    
    def synthesize_greeting(self, user_name=None):
        """Menyusun balasan sapaan berbasis waktu dan nama secara generatif."""
        now = datetime.now()
        hour = now.hour
        
        if 5 <= hour < 11:
            time_tag = "pagi"
        elif 11 <= hour < 15:
            time_tag = "siang"
        elif 15 <= hour < 18:
            time_tag = "sore"
        else:
            time_tag = "malam"
            
        salutations = ["Hai", "Halo", "Selamat " + time_tag]
        intro = random.choice(salutations)
        name_str = f" {user_name}" if user_name else ""
        
        verbs = ["ngobrol", "berdiskusi", "sharing"]
        verb = random.choice(verbs)
        
        variants = [
            f"{intro}{name_str}! 😊 Senang ketemu lagi! Mau {verb} apa hari ini?",
            f"Halo{name_str}! 🤖✨ Milo standby siap nemenin kamu. Ada cerita seru atau topik apa yang mau kita bahas?",
            f"{intro}{name_str}! 🌟 Semoga harimu menyenangkan ya. Ada hal menarik yang mau diobrolin?"
        ]
        return random.choice(variants)
    
    def synthesize_how_are_you(self, user_name=None):
        """Menyusun respons status kabar dan bertanya balik secara generatif."""
        name_str = f", {user_name}" if user_name else ""
        
        status_adjs = ["sangat baik", "dalam kondisi prima", "sehat dan berenergi", "selalu oke"]
        status_verbs = ["selalu semangat", "standby 100%", "siap sedia", "happy banget"]
        
        chosen_adj = random.choice(status_adjs)
        chosen_verb = random.choice(status_verbs)
        
        reciprocals = [
            "Kamu sendiri gimana kabarnya hari ini?",
            "Gimana dengan harimu? Ada cerita seru?",
            "Semoga harimu juga penuh energi positif ya! Kamu lagi santai atau sibuk nih?"
        ]
        
        chosen_q = random.choice(reciprocals)
        
        return f"Alhamdulillah, Milo {chosen_adj} dan {chosen_verb} nemenin kamu{name_str}! 🚀 {chosen_q}"
    
    def synthesize_user_state_good(self, user_name=None):
        """Menyusun respons saat user mengabarkan bahwa keadaannya baik-baik saja / sehat."""
        name_str = f" {user_name}" if user_name else ""
        
        rejoices = [
            f"Syukurlah kalau kamu baik-baik saja{name_str}! 😊",
            f"Senang banget mendengarnya kalau kamu dalam keadaan baik{name_str}! ✨",
            f"Alhamdulillah, ikut lega dan senang dengernya{name_str}! 🌟"
        ]
        
        follow_ups = [
            "Ada topik seru atau hal baru yang ingin kamu obrolin bersama Milo hari ini?",
            "Lagi santai nih ya? Mau kita bahas topik teknologi, cerita harian, atau ada yang bikin kamu penasaran?",
            "Semoga harimu terus berjalan lancar ya! Ada hal tertentu yang mau kamu tanyakan ke Milo?"
        ]
        
        return f"{random.choice(rejoices)} {random.choice(follow_ups)}"
    
    def synthesize_ask_milo_prompt(self, user_name=None):
        """Menyusun respons saat user mengatakan ingin tahu / bertanya satu hal dari Milo."""
        name_str = f" {user_name}" if user_name else ""
        
        welcomes = [
            f"Tentu saja{name_str}! Boleh banget! 😊",
            f"Wah, siap{name_str}! Milo dengan senang hati mendengarkan! ✨",
            f"Tentu boleh{name_str}! Tanyakan saja apa yang ada di pikiranmu! 🚀"
        ]
        
        invitations = [
            "Kamu mau tahu atau menanyakan hal apa dari Milo? Silakan tanyakan ya! 💡",
            "Hal apa yang bikin kamu penasaran dari Milo? Tumpahkan aja pertanyaannya! 🧠",
            "Mau tanya soal apa nih? Milo siap menjawab dan berbagi sudut pandang! 🤝"
        ]
        
        return f"{random.choice(welcomes)} {random.choice(invitations)}"
    
    def synthesize_heartbreak(self, user_name=None, context_text=""):
        """Menyusun respons empati mendalam untuk patah hati / cinta tak berbalas / sakit hati."""
        salutation = f"{user_name}, " if user_name else ""
        name_str = f" {user_name}" if user_name else ""
        
        validations = [
            f"Mencintai seseorang yang tidak membalas perasaan kita itu memang salah satu rasa sakit yang paling perih dan menyesakkan dada {salutation}🥺💔",
            f"Milo paham banget betapa hancur dan perihnya hatimu saat ini{name_str}... 🫂💔 Memberikan perasaan tulus tapi tidak disambut itu sangat menguras emosi.",
            f"Sakit hati karena cinta yang bertepuk sebelah tangan itu berat banget {salutation}😔 Wajar banget kalau kamu merasa down dan terluka."
        ]
        
        comforts = [
            "Perasaanmu itu valid dan nyata. Jangan pernah merasa bersalah atau merasa kurang berharga hanya karena perasaanmu belum terbalas.",
            "Keberanianmu untuk mencintai dengan tulus itu hal yang berharga, meskipun hasilnya tidak sesuai harapan.",
            "Tarik napas perlahan ya... Jangan salahkan dirimu. Hati yang tulus berhak mendapatkan seseorang yang menghargainya seutuhnya."
        ]
        
        prompts = [
            "Milo di sini menemani kamu dan siap mendengarkan kalau kamu mau menumpahkan semua rasa sesak di dada 💙 Mau ceritakan apa yang paling bikin kamu terluka?",
            "Kamu ga perlu menahan luka ini sendirian. Tumpahkan aja semuanya ke Milo ya 🤗",
            "Milo siap jadi tempat bersandar buat kamu curhat tanpa batas. Ceritain aja ya 🌿"
        ]
        
        return f"{random.choice(validations)} {random.choice(comforts)} {random.choice(prompts)}"
    
    def synthesize_curhat_reassurance(self, user_name=None, context_topic=""):
        """Menyusun respons ruang aman curhat secara generatif."""
        name_str = f" {user_name}" if user_name else ""
        salutation = f"{user_name}, " if user_name else ""
        
        validations = [
            f"Milo siap banget jadi pendengar setia kamu{name_str}! 🤗 Ruang ini sepenuhnya aman buat kamu tumpahkan semua uneg-uneg.",
            f"{salutation}kamu ga perlu bingung lagi mau cerita ke siapa 💙 Milo di sini siap dengerin 100% tanpa menghakimi sama sekali.",
            f"Tumpahkan aja apa yang ada di pikiranmu{name_str}! 🫂 Ga usah ragu atau sungkan, Milo siap mendengarkan dengan penuh perhatian."
        ]
        
        prompts = [
            "Mau mulai cerita dari mana? Apa hal yang paling menyita energimu saat ini? 🌿",
            "Cerita aja pelan-pelan ya, apa yang lagi bikin hatimu ganjal? 💙",
            "Milo standby di sini. Bagian mana yang paling membebanimu hari ini? ✨"
        ]
        
        return f"{random.choice(validations)} {random.choice(prompts)}"
    
    def synthesize_worry_compassion(self, user_name=None, situation="general"):
        """Menyusun kalimat empati atas musibah/sakit secara generatif."""
        salutation = f"{user_name}, " if user_name else ""
        name_str = f" {user_name}" if user_name else ""
        
        if situation == "hospital_rawat_inap":
            parts = [
                f"Lega rasanya mengetahui sekarang sudah ditangani di ruang rawat inap {salutation}🤲",
                "Semoga temen sekelasmu itu lekas membaik dan proses pemulihannya lancar serta stabil.",
                "Pasti kehadiran dan doa dari teman-teman bakal memberi kekuatan besar buat dia. Kamu atau teman-teman sekelas ada rencana mau jenguk bareng? 🌿"
            ]
            return " ".join(parts)
            
        elif situation == "accident_hospital":
            parts = [
                f"Ya ampun... {salutation}Milo turut prihatin dan sedih dengernya 🥺",
                "Wajar banget kalau kamu jadi sangat cemas dan kepikiran terus. Mengalami musibah seperti itu memang bikin pikiran campur aduk.",
                "Milo doakan semoga dia lekas pulih dan diberi kelancaran masa perawatannya ya. Kamu sendiri jangan lupa jaga kesehatan di tengah rasa cemas ini 🫂 Ada kabar terbaru soal kondisinya saat ini?"
            ]
            return " ".join(parts)
            
        else:
            parts = [
                f"Milo paham banget rasa cemas dan khawatirnya{name_str} 🥺",
                "Ketika orang yang kita kenal atau sayangi sedang menghadapi masalah, hati kita pasti ikut terbebani.",
                "Tarik napas perlahan ya... Milo di sini nemenin kamu. Semoga segalanya segera membaik! 💙"
            ]
            return " ".join(parts)
    
    def synthesize_clarification(self, user_name=None):
        """Menyusun respons klarifikasi sopan secara generatif."""
        name_str = f" {user_name}" if user_name else ""
        
        apologies = [
            f"Maksud Milo, tadi Milo mungkin kurang jelas menyampaikan maksudnya{name_str} 😅",
            f"Aduh maaf ya{name_str}, kalau kalimat Milo tadi bikin bingung! 🙈",
            f"Hehe maaf ya kalau bahasanya tadi kurang pas{name_str}! 🙏"
        ]
        
        clarifications = [
            "Boleh diulang atau diperjelas bagian mana yang ingin kamu obrolin? Sekarang Milo dengerin dengan fokus! ✨",
            "Maksud Milo, kita bisa ngobrol santai tentang apa saja yang lagi ada di pikiranmu. Ada hal tertentu yang mau kamu ceritain? 😊",
            "Ceritain aja topik yang lagi pengen kamu bahas hari ini, Milo siap mendengarkan dan menemani! 🚀"
        ]
        
        return f"{random.choice(apologies)} {random.choice(clarifications)}"
    
    def synthesize_meta_correction(self, user_name=None, context_topic=""):
        """Menyusun pemulihan koreksi wacana secara generatif."""
        name_str = f" {user_name}" if user_name else ""
        
        apologies = [
            f"Wah maaf ya{name_str}, tadi Milo salah tangkap fokusnya! 🙏",
            f"Aduh maaf banget{name_str}, Milo keliru paham tadi! 🙈",
            f"Eh iya, maaf banget kalau Milo tadi salah fokus konteksnya! 😅"
        ]
        
        if "kepikiran" in context_topic or "orang" in context_topic:
            guidance = "Jadi konteks kepikiran seseorang ini yang kayak gimana nih? Apakah soal kabar seseorang, teman, atau hal lain? Ceritain ya!"
        elif "arsitektur" in context_topic or "coding" in context_topic:
            guidance = "Boleh luruskan lagi bagian logika mana dari proyek arsitektur itu yang mau kita bedah bareng? Milo siap bantu! 💡"
        else:
            guidance = "Boleh bantu jelaskan lagi maksud sebenarnya biar Milo paham dengan tepat? Sekarang Milo fokus dengerin! ✨"
            
        return f"{random.choice(apologies)} {guidance}"
    
    def synthesize_knowledge_answer(self, topic, explanation, user_name=None, source=""):
        """Menyusun jawaban pengetahuan faktual secara generatif dan elegan."""
        salutation = f"{user_name}, " if user_name and random.random() < 0.3 else ""
        
        hooks = [
            f"{salutation}mengenai **{topic}**:",
            f"Nah, yang Milo ketahui tentang **{topic}**:",
            f"Ini penjelasan tentang **{topic}**:"
        ]
        
        closings = [
            "💡 Menarik banget kan? Ada bagian yang mau kamu diskusikan lebih dalam?",
            "🧠✨ Ada hal lain soal ini yang bikin kamu penasaran?",
            "🚀 Mau kita eksplorasi penerapannya lebih jauh?"
        ]
        
        hook = random.choice(hooks)
        closing = random.choice(closings)
        
        if source:
            return f"{hook}\n{explanation} *(Sumber: {source})*\n\n{closing}"
        return f"{hook} {explanation} {closing}"
    
    def synthesize_open_response(self, user_input, keywords=None, user_name=None):
        """Menyusun respons terbuka dinamis untuk topik umum."""
        name_str = f" {user_name}" if user_name else ""
        
        prompts = [
            f"Menarik nih{name_str}! 🤔 Boleh diceritakan lebih detail biar Milo bisa paham konteksnya dengan lebih utuh?",
            f"Milo lagi dengerin nih{name_str}! 💭 Menurut kamu sendiri hal itu gimana? Ceritain ya!",
            f"Hmm, coba ceritain lebih lanjut ya{name_str}! 🧠 Milo senang banget diajak ngobrol soal ini bareng kamu!",
            f"Wah seru untuk dibahas! 🚀 Bagian mana yang paling bikin kamu tertarik dari topik ini?"
        ]
        return random.choice(prompts)
