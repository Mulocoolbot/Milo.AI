"""
Milo AI — Semantic Parser & Discourse Act Analyzer
Menganalisis kalimat masukan pengguna menjadi komponen semantik presisi:
tindak tutur (discourse act), negasi, status emosi, dan fokus topik.
"""

import re


class SemanticParser:
    """Semantic Parser untuk membedah maksud dan struktur kalimat pengguna."""
    
    def parse(self, text, previous_milo_act=None):
        """
        Membedah kalimat pengguna secara semantik.
        
        Args:
            text: string masukan dari pengguna
            previous_milo_act: tindak tutur Milo pada turn sebelumnya
            
        Returns:
            dict hasil analisis semantik
        """
        text_clean = text.lower().strip()
        
        has_negation = bool(re.search(r'\b(nggak|ga|tidak|belum|bukan|tak|takde|gak)\b', text_clean))
        
        # 1. User menyatakan ingin bertanya sesuatu ke Milo ("mau tau satu hal dari kamu", "mau tanya")
        is_asking_milo = bool(re.search(
            r'\b(mau|ingin|pengen|boleh)\s+(tahu|tau|tanya|nanya|dengar)\s+(satu hal|sesuatu|soal|tentang|dari kamu|ke kamu)\b'
            r'|\b(mau|ingin|pengen)\s+(tahu|tau|tanya|nanya)\b'
            r'|\bada yang mau (aku|saya|gue|gw) (tanya|tahu|tau|tanyakan)\b',
            text_clean
        ))
        
        # 2. User merespons kabar dalam keadaan baik ("aku baik-baik saja", "kabar baik", "alhamdulillah sehat")
        is_user_state_good = bool(re.search(
            r'\b(baik-baik saja|baik baik saja|kabar baik|sehat|alhamdulillah baik|alhamdulillah sehat|lagi santai|lagi senang|aman-aman saja|aman kok)\b',
            text_clean
        )) and not bool(re.search(r'\b(kurang|tidak|nggak|ga)\s+(baik|sehat)\b', text_clean))
        
        # 3. User menyatakan sedang sakit hati / patah hati / cinta tak berbalas
        is_heartbreak = bool(re.search(
            r'\b(sakit hati|patah hati|tidak mencintai(ku)?|cinta bertepuk|tak berbalas|cintaku bertepuk|ditolak|diputusin)\b'
            r'|\b(mencintai|suka|naksir)\s+(sama|ke)?\s*(orang|dia|seseorang)\s+yang\s+(tidak|nggak|ga)\s+(mencintai|suka|peduli)\b',
            text_clean
        ))
        
        # 4. User menyatakan tidak ada cerita / tidak mau curhat
        has_no_story = bool(re.search(
            r'\b(nggak|ga|tidak|bukan)\s+(ada|punya|mau)?\s*(cerita|curhat|masalah|uneg-uneg)\b'
            r'|\b(ga ada apa-apa|tidak ada apa-apa|santai aja|biasa aja kok)\b',
            text_clean
        ))
        
        # 5. User meminta klarifikasi
        is_clarification = bool(re.search(
            r'\bmaksud(nya| kamu|mu)? (gimana|apa)\b|\bapa maksud(mu| kamu)?\b|\bgimana maksudnya\b|^maksudnya\??$|^maksud kamu\??$',
            text_clean
        ))
        
        # 6. User melakukan meta-koreksi
        is_meta_correction = bool(re.search(
            r'\b(bukan gitu|bukan begitu|bukan itu maksud|salah paham|salah konteks|salah nangkep|kamu keliru)\b',
            text_clean
        ))
        
        # 7. User menanyakan izin / ragu
        is_seeking_permission = bool(re.search(
            r'\b(emang|apakah|beneran|serius)\s+boleh\b|\bboleh emang\b|\bboleh ya\b',
            text_clean
        ))
        
        # 8. User menanyakan fakta / pengetahuan / penjelasan ilmiah / tren / hobi / fenomena / medis & penyakit
        is_concept_query = bool(re.search(
            r'\b(apa (itu|arti|pengertian|definisi|makna|fungsi|kegunaan)|apa yang dimaksud (dengan)?)\b'
            r'|\bapa yang terjadi (di saat|saat|ketika|jika|pada)\b'
            r'|\b([a-z0-9_]+)\s+apa\s+(yang|paling|bisa|cocok|bagus|terbaik|terkenal|populer|diminati|disukai|dinikmati)\b'
            r'|\b(olahraga|makanan|minuman|musik|lagu|game|teknologi|wisata|kuliner|pekerjaan|jurusan|hobi|buku|film|baju|pakaian)\s+(apa|mana|terbaik|populer|favorit|tren|trend)\b'
            r'|\b(siapa|kapan|dimana|di mana|ke mana|kemana|dari mana|darimana|berapa|seberapa|apakah|manakah|adakah|apa saja|sebutkan|rekomendasi)\b'
            r'|\b(penciptaan|diciptakan|tercipta|asal usul|evolusi)\s+(manusia|kehidupan|alam semesta|bumi|makhluk hidup|[a-z0-9_]+)\b'
            r'|\b(mengidap|menderita|terkena|gejala|penyebab|dampak|akibat)\s+(penyakit|gangguan|sindrom|virus|bakteri|[a-z0-9_]+)\b'
            r'|\b(penyakit|sindrom|gangguan|virus|bakteri)\s+[a-z0-9_]+\b'
            r'|\b(bagaimana|gimana)\s+([a-z0-9_]+\s+)*(bisa|terjadi|bekerja|punah|terbang|bernafas|bernapas|berfungsi|dibuat|terbentuk|diciptakan|cara)\b'
            r'|\b(kenapa|mengapa)\s+[a-z0-9_]+\b'
            r'|\b(bisa kah|bisakah|tolong|coba|mau)?\s*(menjelaskan|jelaskan|terangkan|ceritakan)\s+(tentang|bagaimana|proses|cara|kenapa|mengapa|soal)?\b'
            r'|\b(proses|cara kerja|mekanisme|siklus)\s+([a-z0-9_]+)\b'
            r'|\b(tren|trend|populer|favorit|disukai|diminati|dinikmati)\s+([a-z0-9_]+\s+)*(gen z|milenial|anak muda|orang|masyarakat)\b',
            text_clean
        )) and not bool(re.search(r'\b(kenapa|mengapa|kok)\s+(ada|bisa ada|nyambung ke|muncul)\b|\bapa hubungannya\b', text_clean)) and not is_clarification and not is_seeking_permission and not is_meta_correction
        
        # 9. User meminta saran / solusi / langkah praktis ("memberiku saran", "harus gimana", "gimana caranya", "tips belajar")
        is_asking_advice = bool(re.search(
            r'\b(memberi(ku)?|kasih(kan)?|butuh|minta)?\s*(saran|solusi|tips|masukan|langkah|panduan|nasehat)\b'
            r'|\b(apa yang harus|harus gimana|gimana caranya|apa aku harus|apakah harus|menurut (kamu|mu) gimana)\b'
            r'|\b(nggak tau|ga tau|bingung) (caranya|harus gimana|langkahnya)\b'
            r'|\bgimana (ya|sih|dong)?\s*(cara|caranya|tips)\b'
            r'|\b(ada )?tips (belajar|mengatasi|cara|untuk|koding|coding|pemrograman|tidur|kesehatan)\b',
            text_clean
        )) and not is_concept_query
        
        # 10. User sedang menceritakan peristiwa / update situasi ("aku baru saja mendapat kabar kalau mantan...")
        is_story_sharing = bool(re.search(
            r'\b(baru saja|tadi|kemarin|barusan|dapat kabar|denger kabar|ternyata|ceritanya)\b'
            r'|\b(aku mau cerita|pengen cerita|kisah asmara|tentang mantan|pacar baru)\b',
            text_clean
        )) and not is_asking_advice
        
        # 11. Pertanyaan spesifik user (misal "apakah harus cari pacar baru?")
        has_specific_dilemma = bool(re.search(
            r'\b(apa(kah)? (aku|saya|gue)?\s*(harus|perlu|mesti)?\s*(cari|punya|pacaran|balikan|hubungi|chat|stalking))\b',
            text_clean
        ))
        
        # 12. User menegaskan bahwa detail sudah cukup dan hanya minta tips (kalimat pendek penegasan)
        is_short = len(text_clean.split()) <= 10
        is_insisting_on_tips = is_short and bool(re.search(
            r'^(yah |ya )?(cuman|hanya|cuma)\s+(minta|butuh|pengen)?\s*(tips|tis|saran|langkah)\s*(aja|saja)?(\.|\!)?$'
            r'|\b(nggak ada|ga ada|tidak ada)\s+(yang lain|cerita lain|detail lain)\b'
            r'|^(yah |ya )?(cuman|hanya|cuma)\s+itu\s+(sih)?\s*(detail|ceritanya)?',
            text_clean
        ))
        
        # 13. User mempertanyakan ketidaksesuaian/hubungan topik dari respons sebelumnya ("kenapa ada kewirausahaan?", "apa hubungannya X dengan Y?")
        is_discrepancy_query = bool(re.search(
            r'\b(kenapa|mengapa|kok)\s+(ada|bisa ada|nyambung ke|muncul|bahas)\b'
            r'|\bapa hubungannya\b'
            r'|\bnggak nyambung\b|\bga nyambung\b|\bapa korelasi\b',
            text_clean
        ))
        
        return {
            "text": text,
            "has_negation": has_negation,
            "is_asking_milo": is_asking_milo,
            "is_user_state_good": is_user_state_good,
            "is_heartbreak": is_heartbreak,
            "has_no_story": has_no_story,
            "is_clarification": is_clarification,
            "is_meta_correction": is_meta_correction,
            "is_seeking_permission": is_seeking_permission,
            "is_concept_query": is_concept_query,
            "is_asking_advice": is_asking_advice,
            "is_story_sharing": is_story_sharing,
            "has_specific_dilemma": has_specific_dilemma,
            "is_insisting_on_tips": is_insisting_on_tips,
            "is_discrepancy_query": is_discrepancy_query,
        }
