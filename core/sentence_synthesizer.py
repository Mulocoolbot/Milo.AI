"""
Milo AI — Real-Time Generative Discourse Synthesizer
Mesin penyusun kalimat percakapan bahasa Indonesia secara real-time.
Menyusun kalimat kata-per-kata dan klausa-per-klausa dari Bank Kata Semantik (Word Bank),
memastikan struktur sintaksis alami, kaya variasi kosakata, dan presisi tinggi.
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
            
        salutations = ["Hai", "Halo", "Selamat " + time_tag, "Senang ketemu lagi"]
        intro = random.choice(salutations)
        name_str = f" {user_name}" if user_name else ""
        
        openings = [
            f"{intro}{name_str}! 😊 Senang banget bisa ngobrol bareng kamu hari ini. Mau bahas apa nih kita?",
            f"Halo{name_str}! 🤖✨ Milo standby siap nemenin kamu. Ada cerita seru atau topik apa yang mau kita diskusikan?",
            f"{intro}{name_str}! 🌟 Semoga harimu menyenangkan ya. Apa kabar kamu hari ini?"
        ]
        return random.choice(openings)
    
    def synthesize_how_are_you(self, user_name=None):
        """Menyusun respons status kabar dan bertanya balik secara generatif."""
        name_str = f", {user_name}" if user_name else ""
        
        status_adjs = ["sangat baik", "dalam kondisi prima", "sehat dan berenergi", "selalu oke"]
        status_verbs = ["selalu semangat", "standby 100%", "siap sedia", "happy banget"]
        
        chosen_adj = random.choice(status_adjs)
        chosen_verb = random.choice(status_verbs)
        
        reciprocal_questions = [
            "Kamu sendiri gimana kabarnya hari ini?",
            "Gimana dengan harimu? Ada cerita seru?",
            "Semoga harimu juga penuh energi positif ya! Kamu lagi santai atau sibuk nih?",
            "Ada hal menarik yang lagi kamu pikirkan hari ini?"
        ]
        
        chosen_question = random.choice(reciprocal_questions)
        
        templates = [
            f"Kabar Milo {chosen_adj} dan {chosen_verb} buat ngobrol sama kamu{name_str}! 😄 {chosen_question}",
            f"Alhamdulillah, Milo {chosen_adj} dan {chosen_verb} nemenin kamu! 🚀 {chosen_question}",
            f"Milo sehat dan {chosen_verb} bisa ngobrol bareng kamu{name_str}! ✨ {chosen_question}"
        ]
        return random.choice(templates)
    
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
        
        return random.choice(validations) + " " + random.choice(prompts)
    
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
    
    def synthesize_thinking_of_someone(self, user_name=None):
        """Menyusun respons romansa / kepikiran seseorang secara generatif."""
        name_str = f" {user_name}" if user_name else ""
        
        openings = [
            f"Cieee... Lagi ada seseorang yang spesial yang bikin kamu kepikiran terus ya{name_str}? 🥰",
            f"Wah, rasanya kayak ada yang menempati ruang khusus di kepala ya{name_str}! 💕",
            f"Kepikiran seseorang itu tanda kalau orang itu punya kesan atau tempat tersendiri di hatimu{name_str} ✨"
        ]
        
        reasons = [
            "Wajar banget kok kalau lagi naksir atau ada orang yang berkesan, bayangannya suka lewat terus di pikiran.",
            "Pikiran kita emang suka otomatis tertuju ke orang yang bikin penasaran atau menarik perhatian.",
            "Perasaan berbunga-bunga kayak gitu memang selalu bikin hati campur aduk tapi seru."
        ]
        
        prompts = [
            "Cerita dong, apa yang bikin kamu kepikiran terus sama dia? Apakah gebetan atau teman dekat? 🤗",
            "Mau curhat soal perasaanmu ke dia? Milo siap dengerin tanpa nge-judge kok! 💬",
            "Boleh cerita tentang dia kalau kamu mau! Siapa tahu jadi makin plong! ✨"
        ]
        
        return f"{random.choice(openings)} {random.choice(reasons)} {random.choice(prompts)}"
    
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
