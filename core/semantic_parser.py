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
        
        # 8. User menanyakan fakta / pengetahuan
        is_concept_query = bool(re.search(
            r'\bapa (itu|arti|pengertian|definisi|makna|fungsi)\b|\bapa yang dimaksud\b|\bjelaskan tentang\b',
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
        }
