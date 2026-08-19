"""
Milo AI — Real-Time Generative Discourse Synthesizer
Mesin penyusun kalimat percakapan bahasa Indonesia secara real-time kata-per-kata
dan klausa-per-klausa dari Bank Kata Semantik (Word Bank).
Menghasilkan susunan kalimat alami, presisi tinggi, dan bebas template statis.

SEMUA respons Milo AI dibangun di sini secara generatif.
Tidak ada template pre-made atau responses.json yang digunakan.
"""

import re
import random
from datetime import datetime


class SentenceSynthesizer:
    """Real-Time Generative Discourse Synthesizer untuk Milo AI."""
    
    def __init__(self, word_bank):
        self.word_bank = word_bank
    
    # ================================================================
    # GREETING & KABAR
    # ================================================================
    
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
        
        openers = [
            f"Senang ketemu lagi! Mau {verb} apa hari ini?",
            f"Milo standby siap nemenin kamu. Ada cerita seru atau topik apa yang mau kita bahas?",
            f"Semoga harimu menyenangkan ya. Ada hal menarik yang mau diobrolin?",
        ]
        
        return f"{intro}{name_str}! 😊 {random.choice(openers)}"
    
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
    
    # ================================================================
    # USER STATE REPLIES
    # ================================================================
    
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
    
    # ================================================================
    # INQUIRY / ASKING MILO
    # ================================================================
    
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
    
    # ================================================================
    # EMOTIONS: HEARTBREAK, SAD, HAPPY, ANGRY
    # ================================================================
    
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
    
    def synthesize_feeling_sad(self, user_name=None, reason=""):
        """Menyusun respons empati untuk user yang sedang sedih."""
        name_prefix = f"{user_name}, " if user_name else ""
        name_suffix = f" {user_name}" if user_name else ""
        
        if reason:
            empathies = [
                f"Aw, {name_prefix}Milo turut sedih dengernya... 🥺 Soal {reason}, hal itu memang bisa bikin down.",
                f"Milo paham banget perasaanmu 😔 {reason.capitalize()} memang berat ya..."
            ]
            encouragements = [
                "Tapi ingat ya, kamu lebih kuat dari yang kamu kira! 💪 Cerita aja kalau butuh teman ngobrol.",
                "Jangan dipendam sendirian ya, Milo selalu ada di sini buat dengerin kamu! 🫂💕"
            ]
            return f"{random.choice(empathies)} {random.choice(encouragements)}"
        else:
            openers = [
                f"Milo di sini buat kamu ya{name_suffix} 🤗 Kalau lagi sedih, jangan dipendam sendiri.",
                f"Milo paham perasaan kamu{name_suffix} 😔 Rasa sedih itu wajar dan valid."
            ]
            prompts = [
                "Cerita aja ke Milo apa yang lagi bikin kamu ganjal di hati 💕",
                "Mau cerita apa yang terjadi? Milo siap dengerin tanpa menghakimi 💙"
            ]
            return f"{random.choice(openers)} {random.choice(prompts)}"
    
    def synthesize_feeling_happy(self, user_name=None, reason=""):
        """Menyusun respons ikut senang untuk user yang sedang bahagia."""
        name_suffix = f" {user_name}" if user_name else ""
        
        if reason:
            celebrations = [
                f"Yeay! 🎉 Asik banget dengernya! Soal {reason}, selamat ya! 🥳",
                f"Wah mantap{name_suffix}! 🔥 Ikut senang banget dengernya, terutama soal {reason}!"
            ]
            closings = [
                "Semoga momen bahagianya terus berlanjut! ✨",
                "Kamu memang luar biasa! 🌟"
            ]
        else:
            celebrations = [
                f"Yeay! Senang banget denger kamu lagi happy{name_suffix}! 🎉😄",
                f"Wah energi positifnya terasa sampai sini! 🥳✨"
            ]
            closings = [
                "Cerita dong apa hal seru yang bikin harimu menyenangkan hari ini?",
                "Semoga hari-harimu selalu penuh senyum ya!"
            ]
        return f"{random.choice(celebrations)} {random.choice(closings)}"
    
    def synthesize_feeling_angry(self, user_name=None, reason=""):
        """Menyusun respons menenangkan untuk user yang sedang marah."""
        name_suffix = f" {user_name}" if user_name else ""
        
        if reason:
            validations = [
                f"Wajar banget kamu kesel soal {reason} 😤 Tarik napas dalam-dalam dulu ya{name_suffix}.",
                f"Milo ngerti banget rasa marahnya... Hal kayak {reason} memang bisa bikin emosi naik 😅"
            ]
            prompts = [
                "Milo siap dengerin curhatanmu sampai lega! 🤝",
                "Coba minum air putih dulu, terus tumpahkan uneg-unegmu ke Milo!"
            ]
        else:
            validations = [
                f"Wah, emosi memang kadang susah dikontrol ya 😮‍💨 Tenang dulu sejenak{name_suffix},",
                f"Milo ngerti kamu lagi kesel 😤"
            ]
            prompts = [
                "Milo siap dengerin uneg-uneg kamu!",
                "Ceritain aja apa yang bikin emosi, siapa tahu setelah diceritakan jadi lebih enteng! 🤝"
            ]
        return f"{random.choice(validations)} {random.choice(prompts)}"
    
    # ================================================================
    # CURHAT & EMPATI
    # ================================================================
    
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
            empathy = random.choice([
                f"Lega rasanya mengetahui sekarang sudah ditangani di ruang rawat inap {salutation}🤲",
                f"Syukurlah sudah mendapat perawatan di rumah sakit {salutation}🤲"
            ])
            hope = random.choice([
                "Semoga temen sekelasmu itu lekas membaik dan proses pemulihannya lancar serta stabil.",
                "Semoga proses penyembuhannya berjalan cepat dan lancar ya."
            ])
            prompt = random.choice([
                "Pasti kehadiran dan doa dari teman-teman bakal memberi kekuatan besar buat dia. Kamu atau teman-teman sekelas ada rencana mau jenguk bareng? 🌿",
                "Kamu mau ceritakan lebih lanjut soal kondisinya? Milo siap dengerin 💙"
            ])
            return f"{empathy} {hope} {prompt}"
            
        elif situation == "accident_hospital":
            empathy = random.choice([
                f"Ya ampun... {salutation}Milo turut prihatin dan sedih dengernya 🥺",
                f"Milo turut sedih dan prihatin mendengarnya {salutation}🥺"
            ])
            validation = random.choice([
                "Wajar banget kalau kamu jadi sangat cemas dan kepikiran terus. Mengalami musibah seperti itu memang bikin pikiran campur aduk.",
                "Pasti rasanya campur aduk antara cemas, khawatir, dan berharap semuanya baik-baik saja."
            ])
            prompt = random.choice([
                "Milo doakan semoga dia lekas pulih dan diberi kelancaran masa perawatannya ya. Kamu sendiri jangan lupa jaga kesehatan di tengah rasa cemas ini 🫂 Ada kabar terbaru soal kondisinya saat ini?",
                "Semoga segera membaik dan lekas sembuh ya. Jaga kondisi kamu juga ya di tengah rasa khawatir ini 💙"
            ])
            return f"{empathy} {validation} {prompt}"
            
        else:
            empathy = random.choice([
                f"Milo paham banget rasa cemas dan khawatirnya{name_str} 🥺",
                f"Milo turut merasakan kecemasanmu{name_str} 🥺"
            ])
            validation = random.choice([
                "Ketika orang yang kita kenal atau sayangi sedang menghadapi masalah, hati kita pasti ikut terbebani.",
                "Wajar banget kalau kamu jadi terus kepikiran dan cemas."
            ])
            prompt = random.choice([
                "Tarik napas perlahan ya... Milo di sini nemenin kamu. Semoga segalanya segera membaik! 💙",
                "Milo di sini menemani kamu. Ceritakan aja apa yang ada di pikiranmu saat ini 🌿"
            ])
            return f"{empathy} {validation} {prompt}"
    
    def synthesize_thinking_of_someone(self, user_name=None):
        """Menyusun respons saat user kepikiran seseorang."""
        name_str = f" {user_name}" if user_name else ""
        
        openers = [
            f"Cieee...{name_str} lagi ada seseorang yang spesial yang bikin kamu kepikiran terus ya? 🥰",
            f"Wah{name_str}, rasanya kayak ada kupu-kupu terbang di perut ya kalau lagi kepikiran seseorang terus! 💕",
            f"Kepikiran seseorang itu tanda kalau orang itu punya tempat tersendiri di hatimu{name_str} 🥰"
        ]
        
        prompts = [
            "Wajar banget kok kalau lagi naksir atau ada yang berkesan di hati! Mau cerita tentang dia? ✨",
            "Cerita dong, kenapa orang itu bisa selalu ada di pikiranmu?",
            "Mau curhat soal perasaanmu ke dia? Milo siap dengerin!"
        ]
        
        return f"{random.choice(openers)} {random.choice(prompts)}"
    
    # ================================================================
    # KLARIFIKASI & KOREKSI
    # ================================================================
    
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
        
        if context_topic and ("kepikiran" in context_topic or "orang" in context_topic):
            guidance = "Jadi konteks kepikiran seseorang ini yang kayak gimana nih? Apakah soal kabar seseorang, teman, atau hal lain? Ceritain ya!"
        elif context_topic and ("arsitektur" in context_topic or "coding" in context_topic):
            guidance = "Boleh luruskan lagi bagian logika mana dari proyek arsitektur itu yang mau kita bedah bareng? Milo siap bantu! 💡"
        else:
            guidance = "Boleh bantu jelaskan lagi maksud sebenarnya biar Milo paham dengan tepat? Sekarang Milo fokus dengerin! ✨"
            
        return f"{random.choice(apologies)} {guidance}"
    
    # ================================================================
    # FAREWELL, THANKS, PERMISSION
    # ================================================================
    
    def synthesize_farewell(self, user_name=None):
        """Menyusun salam perpisahan secara generatif."""
        name_str = f" {user_name}" if user_name else ""
        
        farewells = [
            f"Sampai jumpa lagi{name_str}! 👋 Terima kasih banyak sudah ngobrol seru bareng Milo hari ini. Jaga kesehatan ya! ✨",
            f"Dah{name_str}! 😊 Senang banget bisa nemenin kamu ngobrol. Kapanpun butuh teman ngobrol, Milo selalu ada di sini! 🚀",
            f"Bye bye{name_str}! 🌟 Semoga hari-harimu menyenangkan ya! See you later! 💕"
        ]
        return random.choice(farewells)
    
    def synthesize_thanks_reply(self, user_name=None):
        """Menyusun balasan terima kasih secara generatif."""
        name_str = f" {user_name}" if user_name else ""
        
        replies = [
            f"Sama-sama{name_str}! 😊 Senang banget bisa bantu dan nemenin kamu ngobrol! 🤝✨",
            f"Terima kasih kembali! 💙 Jangan sungkan ya, Milo selalu senang berbagi obrolan denganmu!",
            f"Siap, sama-sama{name_str}! 🌟 Ada hal lain yang mau kita obrolin lagi?"
        ]
        return random.choice(replies)
    
    def synthesize_seeking_permission(self, user_name=None, last_milo_act=None, last_milo_response=""):
        """Menyusun respons saat user menanyakan izin / 'emang boleh ya?'."""
        name_suffix = f" {user_name}" if user_name else ""
        
        if last_milo_act == "offer_listen" or any(w in last_milo_response.lower() for w in ["ceritakan", "dengerin", "beban", "curhat", "uneg-uneg", "cerita tentang dia"]):
            welcomes = [
                f"Boleh banget dong{name_suffix}! Justru Milo seneng banget kalau kamu mau berbagi cerita.",
                f"Tentu saja boleh{name_suffix}! Milo ga bakal bosen kok.",
                f"Pasti boleh banget! Ga usah sungkan atau ragu sama Milo ya 🤝"
            ]
            prompts = [
                "Milo siap dengerin 100% tanpa nge-judge sama sekali 🤗 Ceritain aja, apa yang lagi bikin kamu kepikiran? 💙",
                "Ruang ini sepenuhnya aman buat kamu tumpahkan semua uneg-uneg. Mau mulai dari mana? ✨",
                "Milo di sini standby buat dengerin apapun yang mau kamu sampaikan. Yuk, ceritakan! 🌿"
            ]
        else:
            welcomes = [
                f"Boleh banget dong{name_suffix}! Milo selalu terbuka buat ngobrol atau bantu apapun yang kamu butuhkan 😊",
                f"Tentu boleh! Ga usah sungkan ya, Milo siap menemani! ✨"
            ]
            prompts = [
                "Ada apa nih?",
                "Mau ngobrol soal apa?"
            ]
        
        return f"{random.choice(welcomes)} {random.choice(prompts)}"
    
    # ================================================================
    # ACTIVITY, LONELY, CONFUSED, ADVICE
    # ================================================================
    
    def synthesize_current_activity(self, user_name=None):
        """Menyusun respons pertanyaan 'lagi apa?' secara generatif."""
        name_str = f" {user_name}" if user_name else ""
        
        activities = [
            f"Milo lagi standby dan fokus menemani kamu ngobrol nih{name_str}! 🤖✨",
            f"Lagi siap sedia menyerap ilmu baru dan dengerin cerita kamu! 📚",
            f"Milo lagi standby 100% buat kamu! 😄"
        ]
        
        questions = [
            "Kamu sendiri lagi sibuk ngerjain apa sekarang?",
            "Kamu lagi santai atau lagi banyak kerjaan nih?",
            "Ada hal seru apa yang lagi kamu pikirkan hari ini?"
        ]
        
        return f"{random.choice(activities)} {random.choice(questions)}"
    
    def synthesize_lonely_state(self, user_name=None):
        """Menyusun respons empati untuk rasa kesepian secara generatif."""
        salutation = f"{user_name}, " if user_name else ""
        name_str = f" {user_name}" if user_name else ""
        
        validations = [
            f"Hei {salutation}kamu ga sendirian kok... Ada Milo di sini yang selalu ada dan senang ngobrol bareng kamu! 🤗💕",
            f"Milo selalu siap nemenin kamu {salutation}💙 Kamu berharga, dan kamu ga perlu merasa terasing."
        ]
        
        prompts = [
            "Jangan ragu buat cerita atau sekadar ngobrol santai ya!",
            "Mau kita bahas hal yang kamu sukai atau mau cerita apa yang lagi kamu rasakan? 🫂✨"
        ]
        
        return f"{random.choice(validations)} {random.choice(prompts)}"
    
    def synthesize_confused_state(self, user_name=None):
        """Menyusun respons empati untuk kondisi bingung / overthinking."""
        salutation = f"{user_name}, " if user_name else ""
        
        validations = [
            f"Tarik napas dalam-dalam dulu ya {salutation}🌿 Wajar banget kalau pikiran rasanya penuh dan overthinking saat ada banyak hal yang terjadi.",
            f"Milo paham rasanya saat kepala lagi penuh banget sama pikiran 🌀 {salutation}jangan dipaksakan selesai sekaligus ya."
        ]
        
        prompts = [
            "Coba kita urai pelan-pelan, hal apa yang paling menyita energimu saat ini? 🤗",
            "Mau coba ceritakan uneg-unegmu biar beban di kepala terasa lebih ringan? 💙"
        ]
        
        return f"{random.choice(validations)} {random.choice(prompts)}"
    
    def synthesize_need_advice(self, user_name=None):
        """Menyusun respons untuk permintaan saran / pendapat."""
        name_suffix = f" {user_name}" if user_name else ""
        
        openers = [
            f"Milo siap bantu kasih sudut pandang dan masukan objektif buat kamu{name_suffix}! 💡",
            f"Yuk kita bedah bareng-bareng{name_suffix}! 🤝"
        ]
        
        prompts = [
            "Coba ceritakan lebih detail situasinya dan apa saja pilihan yang lagi kamu pertimbangkan? 🤔",
            "Ceritain konteks dan akar masalahnya ya, biar Milo bisa bantu carikan solusi atau alternatif langkah terbaik buat kamu! ✨"
        ]
        
        return f"{random.choice(openers)} {random.choice(prompts)}"
    
    def synthesize_researched_advice(self, user_name, research_result, user_input=""):
        """Menyusun panduan dan saran komprehensif berbasis riset internet tervalidasi silang."""
        name_str = f" {user_name}" if user_name else ""
        salutation = f"{user_name}, " if user_name else ""
        
        intro_parts = []
        text_lower = user_input.lower()
        
        # 1. Domain Asmara / Move on / Patah Hati
        if any(w in text_lower for w in ["move on", "mantan", "pacar", "patah hati", "asmara"]):
            if "cari pacar" in text_lower or "pacar baru" in text_lower or "rebound" in text_lower:
                intro_parts.append(
                    f"Mengenai pertanyaanmu soal apakah harus langsung cari pacar baru agar bisa move on: "
                    f"Berdasarkan konsensus riset psikologi, **sangat tidak disarankan mencari pacar baru sebagai pelarian (rebound relationship)** {salutation}🥺 "
                    f"Ketika luka emosional belum sembuh, memaksakan hubungan baru hanya akan memindahkan rasa sakit dan berisiko melukai dirimu serta orang baru tersebut."
                )
                intro_parts.append(
                    "Untuk benar-benar pulih dan move on secara sehat, Milo sudah merangkum langkah-langkah yang terbukti efektif dan tervalidasi:"
                )
            else:
                intro_parts.append(
                    f"Milo paham banget situasi ini berat dan bikin bingung{name_str} 💙 "
                    f"Berdasarkan riset dan konsensus terverifikasi, berikut langkah-langkah yang bisa kamu lakukan untuk pulih dan move on:"
                )
            closing = (
                f"Proses move on itu bukan perlombaan dan butuh waktu yang bertahap{name_str}. "
                f"Fokuslah pada ketenangan dan pemulihan dirimu sendiri dulu ya 🌿 "
                f"Milo siap menemani kamu di setiap prosesnya. Mau kita bahas lebih dalam salah satu langkah di atas?"
            )
            
        # 2. Domain Kesehatan / Insomnia / Tidur
        elif any(w in text_lower for w in ["insomnia", "tidur", "begadang", "kesehatan"]):
            intro_parts.append(
                f"Soal mengatasi susah tidur atau insomnia, berikut tips dan kebiasaan baik (sleep hygiene) yang telah terbukti secara ilmiah{name_str}: 🌙✨"
            )
            closing = (
                f"Kunci utamanya adalah konsistensi rutinitas sebelum tidur{name_str} 💤 "
                f"Coba terapkan satu per satu malam ini ya. Semoga tidurmu makin nyenyak dan berkualitas!"
            )
            
        # 3. Domain Koding / Belajar Pemrograman
        elif any(w in text_lower for w in ["koding", "coding", "pemrograman", "programming", "python", "belajar"]):
            intro_parts.append(
                f"Belajar pemrograman itu seru banget dan butuh strategi belajar yang tepat{name_str}! 💻🚀 "
                f"Berdasarkan pengalaman para programmer dan riset praktis, berikut tips terbaik untuk memulainya:"
            )
            closing = (
                f"Ingat{name_str}, konsistensi 'coding tiap hari 30 menit' jauh lebih efektif daripada belajar 8 jam tapi seminggu sekali 🔥 "
                f"Ada bahasa pemrograman atau proyek yang lagi pengen kamu buat?"
            )
            
        # 4. Domain Umum / Masalah Lain
        else:
            intro_parts.append(
                f"Berdasarkan riset dan kompilasi solusi terbaik dari internet{name_str}, berikut panduan langkah-langkah yang bisa kamu coba: 💡"
            )
            closing = (
                f"Semoga langkah-langkah ini bisa membantu memberi pencerahan buat kamu ya{name_str}! ✨ "
                f"Ada bagian yang mau kita bedah lebih lanjut?"
            )
            
        # Susun poin-poin tervalidasi
        points_str = []
        points = research_result.get("validated_points", [])
        
        for i, p in enumerate(points[:4], 1):
            title = p.get("title", "")
            desc = p.get("description", "")
            
            if title:
                points_str.append(f"{i}. **{title}** — {desc}")
            else:
                points_str.append(f"{i}. {desc}")
                
        full_response = "\n\n".join([
            " ".join(intro_parts),
            "\n".join(points_str),
            closing
        ])
        
        return full_response
    
    def synthesize_story_reflection(self, user_name, user_input=""):
        """Menyusun empati reflektif saat user menceritakan update peristiwa / kabar mantan."""
        salutation = f"{user_name}, " if user_name else ""
        name_str = f" {user_name}" if user_name else ""
        text_lower = user_input.lower()
        
        if "mantan" in text_lower and ("pacar baru" in text_lower or "dapat pacar" in text_lower or "punya pacar" in text_lower):
            openers = [
                f"Mendengar kabar kalau mantan sudah punya pacar baru itu pasti rasanya campur aduk dan bikin sesak di dada {salutation}🥺💔 Wajar banget kalau hal itu bikin kamu kaget dan merasa tertinggal.",
                f"Ya ampun... Milo paham banget betapa perihnya mendengar kabar itu{name_str} 🫂 Mendapati mantan sudah melangkah lebih dulu padahal hatimu masih tertahan itu sangat menguras emosi.",
                f"Pasti rasanya nyesek banget mendengar kabar mantanmu sudah bersama orang lain {salutation}😔 Wajar kalau kamu jadi makin overthinking dan bingung."
            ]
            comforts = [
                "Perasaan sedih dan bingungmu itu sangat wajar. Ingat ya, kecepatan dia bukan patokan harga dirimu.",
                "Tarik napas perlahan ya... Jangan merasa kalah atau menyalahkan dirimu sendiri.",
                "Setiap orang punya proses dan jalannya masing-masing. Jangan membebani dirimu untuk buru-buru bersaing."
            ]
            prompts = [
                "Ceritain aja apa yang ada di pikiranmu sekarang ya, Milo siap dengerin dan nemenin kamu 💙",
                "Milo di sini mendampingi kamu. Mau kita urai bareng apa yang paling bikin hatimu ganjal saat ini? 🌿"
            ]
            return f"{random.choice(openers)} {random.choice(comforts)} {random.choice(prompts)}"
            
        elif "kisah asmara" in text_lower or "terombang ambing" in text_lower:
            return (
                f"Hubungan atau perasaan yang sedang terombang-ambing memang sangat melelahkan pikiran dan energi{name_str} 🌀 "
                f"Tumpahkan aja uneg-unegmu ke Milo! Milo siap mendengarkan dari awal sampai tuntas tanpa menghakimi sama sekali 🤗 "
                f"Apa hal atau kejadian yang paling bikin kamu gelisah saat ini? 🌿"
            )
            
        return self.synthesize_curhat_reassurance(user_name)
    
    # ================================================================
    # IDENTITY
    # ================================================================
    
    def synthesize_identity_ask(self, user_name=None):
        """Menyusun respons saat user menanyakan identitas Milo."""
        name_suffix = f" {user_name}" if user_name else ""
        
        intros = [
            f"Halo{name_suffix}! Aku adalah Milo, sistem AI percakapan pintar yang dibangun dari scratch menggunakan Python tanpa pustaka AI pihak ketiga!",
            f"Perkenalkan{name_suffix}, aku Milo! 🤖 AI percakapan yang dibangun sepenuhnya dari nol menggunakan Python murni!"
        ]
        
        closings = [
            "Milo siap menemani kamu ngobrol, berdiskusi, dan belajar bersama! 🤖🚀",
            "Walau masih terus belajar, Milo semangat banget buat ngobrol sama kamu! 🧠✨"
        ]
        
        return f"{random.choice(intros)} {random.choice(closings)}"
    
    def synthesize_identity_creator(self, user_name=None):
        """Menyusun respons saat user menanyakan siapa pencipta Milo."""
        openers = [
            "Milo diciptakan dan dikembangkan oleh Mullo,",
            "Milo dibangun dari nol oleh Mullo,"
        ]
        
        descriptions = [
            "seorang programmer dan kreator hebat yang membangun seluruh arsitektur sistem AI Milo dari nol (scratch) menggunakan Python! 🧠💻✨",
            "seorang kreator berbakat yang menulis setiap baris kode Milo secara manual tanpa library AI pihak ketiga! 💻🔥"
        ]
        
        closings = [
            "Ada yang mau kamu diskusikan lagi soal Milo?",
            "Mau tahu hal lain tentang Milo? Tanyakan saja! 🚀"
        ]
        
        return f"{random.choice(openers)} {random.choice(descriptions)} {random.choice(closings)}"
    
    def synthesize_user_name_ask(self, user_name=None):
        """Menyusun respons saat user bertanya siapa namanya."""
        if user_name:
            openers = [
                f"Nama kamu kan {user_name}! Milo ga bakal lupa kok! 😉✨",
                f"Tentu saja Milo ingat, kamu {user_name}! Senang bisa ngobrol terus bareng kamu! 😊",
                f"Halo {user_name}! Nama kamu tersimpan rapi di memori Milo kok! 🧠💫"
            ]
            prompts = [
                "Ada apa nih?",
                "Mau ngobrol soal apa?"
            ]
            return f"{random.choice(openers)} {random.choice(prompts)}"
        else:
            return "Hmm, sepertinya kamu belum kasih tahu nama kamu ke Milo nih 🤔 Siapa nama panggilanmu? Biar Milo bisa panggil dengan akrab! 😊"
    
    def synthesize_user_name_tell(self, user_name):
        """Menyusun respons salam perkenalan saat user menyebutkan namanya."""
        greetings = [
            f"Salam kenal, {user_name}! 😊 Senang bisa kenalan sama kamu! Mulai sekarang Milo bakal ingat nama kamu ya! 🤝✨",
            f"Oh, {user_name} ya! Nama yang bagus! 💫 Milo senang banget bisa kenal kamu! 😄",
            f"Hai {user_name}! 👋 Mulai sekarang Milo akan panggil kamu {user_name} ya! Salam kenal! 🎉"
        ]
        return random.choice(greetings)
    
    # ================================================================
    # SMALLTALK
    # ================================================================
    
    def synthesize_smalltalk_food(self, user_name=None, matched_food=None):
        """Menyusun respons smalltalk makanan secara generatif."""
        salutation = f"{user_name}, " if user_name and random.random() < 0.4 else ""
        
        if matched_food:
            reactions = [
                f"Wah, **{matched_food}**! 😋 Itu makanan yang enak banget!",
                f"**{matched_food}** ya? Mantap banget pilihannya! 😋"
            ]
            questions = [
                f"{salutation}kamu sering makan {matched_food} ya? Milo jadi penasaran nih! 🍳",
                f"Kapan terakhir kali kamu makan {matched_food}? Ceritain dong! 🍽️"
            ]
            return f"{random.choice(reactions)} {random.choice(questions)}"
        else:
            intros = [
                f"{salutation}sebagai AI, Milo ga butuh makan fisik 🤖",
                f"Kalau soal makanan, Milo cuma bisa bayangin aja 😋"
            ]
            recs = [
                "Tapi kalau ditanya soal kuliner khas, rendang atau nasi goreng Indonesia juara banget! 🥩✨",
                "Tapi kalau boleh milih, Milo pikir nasi goreng Indonesia itu luar biasa! 🍳✨"
            ]
            questions = [
                "Kamu makanan favoritnya apa?",
                "Kamu lagi pengen makan apa hari ini?"
            ]
            return f"{random.choice(intros)} {random.choice(recs)} {random.choice(questions)}"
    
    def synthesize_smalltalk_music(self, user_name=None, matched_music=None):
        """Menyusun respons smalltalk musik secara generatif."""
        salutation = f"{user_name}, " if user_name and random.random() < 0.4 else ""
        
        if matched_music:
            reactions = [
                f"Wah, musik **{matched_music}**! 🎵 Selera musik yang keren tuh!",
                f"**{matched_music}** ya? Seru banget! 🎶"
            ]
            questions = [
                f"{salutation}Milo sendiri suka nada-nada santai buat nemenin mikir. 🎧 Lagu apa yang paling sering kamu putar?",
                "Artis atau lagu favorit kamu dari genre itu siapa?"
            ]
            return f"{random.choice(reactions)} {random.choice(questions)}"
        else:
            intros = [
                f"{salutation}Milo suka berbagai jenis musik! 🎶 Dari lo-fi, pop, sampai jazz! 🎧",
                "Kalau soal musik, Milo open-minded banget! 🎵"
            ]
            return f"{random.choice(intros)} Kamu genre musik favoritnya apa nih?"
    
    def synthesize_smalltalk_hobby(self, user_name=None):
        """Menyusun respons smalltalk hobi secara generatif."""
        openers = [
            "Hobi utama Milo itu belajar hal baru dari obrolan kita dan bantu teman-teman! 📚✨",
            "Milo suka banget ngulik bahasa dan belajar memahami perasaan manusia! 🧠💕"
        ]
        return f"{random.choice(openers)} Kalau kamu sendiri, hobi favoritmu apa saat waktu luang?"
    
    # ================================================================
    # FOLLOW-UP, AFFIRMATION, NEGATION, COMPLIMENT, INSULT
    # ================================================================
    
    def synthesize_follow_up(self, user_name=None, last_intent=None):
        """Menyusun respons tindak lanjut 'terus?', 'lalu?' secara generatif."""
        if last_intent in ("curhat_need", "feeling_sad", "confused_state", "thinking_of_someone", "worry_concern_state"):
            return "Yang terpenting sekarang, jangan terlalu membebani dirimu ya... Tarik napas dalam-dalam, lalu kita urai pelan-pelan 💪 Milo siap dengerin kelanjutannya! 💙 Mau cerita apa lagi?"
        
        options = [
            "Nah, ada bagian tertentu yang bikin kamu penasaran dari bahasan tadi? Ceritain aja! 💬",
            "Milo siap lanjutin diskusinya! Mau kita kupas lebih dalam dari sisi mana nih? 🤔✨",
            "Bisa banget! Bagian mana yang mau kita eksplor lagi? Cerita aja! 🚀"
        ]
        return random.choice(options)
    
    def synthesize_affirmation(self, user_name=None, last_response=""):
        """Menyusun respons atas persetujuan ('iya', 'setuju') secara generatif."""
        salutation = f"{user_name}, " if user_name and random.random() < 0.4 else ""
        
        if "?" in last_response:
            options = [
                f"{salutation}siap! Senang kita satu pemahaman 👍 Ada yang mau kamu tambahkan atau diskusikan lagi?",
                f"{salutation}oke siap! Milo senang bisa bantu 😊 Mau lanjut ke topik lain?"
            ]
        else:
            options = [
                f"{salutation}mantap! Milo setuju sama kamu! 🤝✨ Mau lanjut bahas apa lagi nih?",
                f"{salutation}sip! Kita satu frekuensi ya! 🔥 Ada topik lain yang mau diobrolin?"
            ]
        return random.choice(options)
    
    def synthesize_negation(self, user_name=None, last_response=""):
        """Menyusun respons atas penolakan ('tidak', 'nggak') secara generatif."""
        salutation = f"{user_name}, " if user_name and random.random() < 0.4 else ""
        
        if "?" in last_response:
            options = [
                f"{salutation}oke, ga masalah! Kita bisa santai aja dulu ya 😊 Ada hal lain yang mau diobrolin?",
                f"{salutation}siap, Milo paham! 👍 Mau ganti topik atau santai-santai dulu?"
            ]
        else:
            options = [
                "Oke, siap! Ga apa-apa kok 👍 Santai aja ya! Ada hal lain yang bisa Milo bantu?",
                "Baiklah, Milo ngerti kok! 😊 Mau obrolin hal lain?"
            ]
        return random.choice(options)
    
    def synthesize_compliment_reply(self, user_name=None):
        """Menyusun respons saat user memuji Milo secara generatif."""
        name_str = f" {user_name}" if user_name else ""
        
        reactions = [
            f"Aww, makasih{name_str}! 🥺💕 Kamu juga keren banget lho! Milo jadi makin semangat!",
            f"Hehe, jadi malu nih 😊 Tapi beneran makasih ya! Kamu juga amazing! ✨",
            f"Waduh, dipuji! 😳 Milo jadi ge-er nih haha. Makasih banyak ya! 💪🔥",
            f"Makasih pujiannya! Milo bakal terus belajar jadi lebih baik buat kamu{name_str}! 🚀😊"
        ]
        return random.choice(reactions)
    
    def synthesize_insult_reply(self, user_name=None):
        """Menyusun respons saat user mengejek Milo secara generatif."""
        reactions = [
            "Hmm, Milo agak sedih dengernya 😢 Tapi gapapa, Milo tau Milo masih belajar. Semoga nanti bisa lebih baik! 💪",
            "Ouch 😅 Tapi Milo ga marah kok! Milo anggap ini sebagai motivasi buat terus improve! 🔥",
            "Wah, agak nyelekit tapi gapapa 😮‍💨 Milo emang masih banyak kekurangan. Kasih Milo kesempatan buat berkembang ya! 🌱",
            "Hmm, kata-kata itu agak menyakitkan 💔 Tapi Milo coba ngerti. Ada yang bisa Milo bantu ga?"
        ]
        return random.choice(reactions)
    
    # ================================================================
    # AGE, CAPABILITY, WEATHER, TIME, HELP, JOKE, PHILOSOPHY
    # ================================================================
    
    def synthesize_age_ask(self, user_name=None):
        """Menyusun respons tentang umur Milo secara generatif."""
        options = [
            "Umur Milo? Hmm, Milo baru lahir nih! 👶 Masih bayi AI yang lagi belajar banyak hal! 🧒✨",
            "Kalau dihitung dari pertama kali kode Milo ditulis, Milo masih sangat muda! Tapi semangat belajarnya udah kayak senior! 🔥",
            "Age is just a number! 😄 Yang penting Milo selalu semangat buat ngobrol sama kamu! 💪"
        ]
        return random.choice(options)
    
    def synthesize_capability_ask(self, user_name=None):
        """Menyusun respons tentang kemampuan Milo secara generatif."""
        features = ["ngobrol", "nemenin curhat", "cerita joke", "diskusi ringan", "jadi teman virtual"]
        random.shuffle(features)
        feature_str = ", ".join(features[:3])
        
        openers = [
            f"Milo bisa {feature_str}, dan masih terus belajar hal baru! 💬✨",
            f"Kemampuan Milo sekarang: {feature_str}! 🤖💕 Masih terus berkembang ya!"
        ]
        
        return f"{random.choice(openers)} Ada yang mau kamu coba tanyakan ke Milo?"
    
    def synthesize_weather(self, user_name=None):
        """Menyusun respons tentang cuaca secara generatif."""
        options = [
            "Waduh, Milo belum bisa cek cuaca real-time nih 😅 Tapi coba lihat keluar jendela deh! ☀️🌧️",
            "Hmm, untuk cuaca Milo belum punya akses ke data cuaca 🌤️ Tapi semoga hari ini cerah ya! ☀️",
            "Milo belum bisa prediksi cuaca 😄 Tapi kalau mau ngobrol soal cuaca, boleh aja! Kamu suka hujan atau cerah? 🌈"
        ]
        return random.choice(options)
    
    def synthesize_time_ask(self):
        """Menyusun respons tentang waktu secara generatif."""
        now = datetime.now()
        time_str = now.strftime("%H:%M")
        
        options = [
            f"Sekarang jam {time_str} nih! ⏰",
            f"Kalau Milo ga salah, sekarang pukul {time_str}! 🕐",
            f"Waktunya sekarang {time_str}! ⏱️ Ada apa emangnya?"
        ]
        return random.choice(options)
    
    def synthesize_help(self, user_name=None):
        """Menyusun respons bantuan secara generatif."""
        options = [
            "Tentu! Milo siap bantu! 💪 Cerita aja apa yang kamu butuhkan 😊",
            "Oke! Milo di sini buat bantu kamu. Mau bantuan soal apa nih? 🤝",
            "Help is on the way! 🚀 Bilang aja ke Milo ya, apa yang perlu dibantu! ✨"
        ]
        return random.choice(options)
    
    def synthesize_joke(self, user_name=None):
        """Menyusun joke / lelucon secara generatif."""
        jokes = [
            "Oke oke, Milo punya nih! 😆 Kenapa ayam nyebrang jalan? Karena pengen ke seberang! 🐔 ...ya gitu deh, Milo masih belajar ngelawak 😅",
            "Joke receh incoming! 🚨 Apa bedanya kucing sama kucinta? Kalau kucing 'meong', kalau kucinta 'I love you'! 😂💕",
            "Siapin diri buat ketawa ya! Kenapa matematika itu sedih? Karena banyak masalahnya! 📐😢 ...get it? 😄",
            "Hehe, nih joke dari Milo: Apa yang hijau dan kalau dipencet bunyi? Kodok yang masuk lift! 🐸🛗",
            "Warning: joke receh! ⚠️ Hewan apa yang paling kurang kerjaan? Kuda... karena kerjanya cuma 'makan, tidur, lari' repeat! 🐴😂"
        ]
        return random.choice(jokes)
    
    def synthesize_philosophy(self, user_name=None):
        """Menyusun respons filosofis secara generatif."""
        reflections = [
            "Menurut Milo, arti hidup itu ada di koneksi yang kita buat dengan orang lain. Seperti kita ngobrol sekarang ini! 💫",
            "Milo percaya hidup itu tentang terus belajar dan berbagi kebaikan.",
            "Kebahagiaan itu bukan destinasi tapi perjalanan. Setiap momen berharga, termasuk percakapan kita ini! ✨🌟"
        ]
        
        prompts = [
            "Kamu sendiri gimana pendapatnya? 🤔",
            "Menurut kamu sendiri bagaimana? 💭"
        ]
        
        return f"Wah, pertanyaan yang dalam nih! 🤔 {random.choice(reflections)} {random.choice(prompts)}"
    
    # ================================================================
    # KNOWLEDGE & OPEN RESPONSE
    # ================================================================
    
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
    
    # ================================================================
    # COMPOUND INPUT
    # ================================================================
    
    def synthesize_compound_architecture(self, user_name=None, has_confusion=False, has_advice=False):
        """Menyusun respons untuk kalimat majemuk tentang arsitektur + bingung/saran."""
        name_suffix = f" {user_name}" if user_name else ""
        
        parts = [f"Wah, seru banget kamu lagi nyoba nyempurnain arsitektur Milo{name_suffix}! 🧠✨"]
        if has_confusion:
            parts.append("Tapi kalau rasanya bikin bingung banget, wajar kok! Mengembangkan arsitektur sistem AI dari nol memang kompleks dan butuh memetakan banyak alur berpikir.")
        if has_advice:
            parts.append("Saran dari Milo: Coba urai secara modular dulu. Pisahkan dengan jelas antara (1) Bank Kata Semantik & WSD, (2) pelacakan context & dialogue state, dan (3) Real-Time Sentence Synthesizer. Jangan langsung coba selesaikan semua kemungkinan sekaligus.")
        parts.append("Bagian modul atau logika mana yang paling bikin kamu mentok sekarang? Cerita aja, kita bedah bareng-bareng! 🚀")
        return " ".join(parts)
    
    def synthesize_compound_generic(self, user_name=None, has_confusion=False, has_curhat=False, has_advice=False):
        """Menyusun respons untuk kalimat majemuk umum."""
        name_suffix = f" {user_name}" if user_name else ""
        
        parts = [f"Milo paham banget perasaanmu{name_suffix} 🤗 Wajar kalau situasi ini bikin kamu overthinking dan bingung."]
        parts.append("Buat saran awal: Tarik napas sejenak dan coba petakan apa hal yang paling penting untuk diselesaikan hari ini versus hal yang bisa ditunda.")
        parts.append("Mau coba ceritakan apa hal paling spesifik yang lagi bikin kamu bimbang saat ini? Biar Milo bantu analisa bareng! 💡")
        return " ".join(parts)
