"""
Milo AI — Context Manager
Mengelola konteks percakapan bertingkat, tracking topik, sentimen,
dialogue acts, dan entitas/fakta personal user.
"""

import re
from datetime import datetime
from collections import deque
from utils.config import Config


class ContextManager:
    """Context Manager — mengelola konteks dan state percakapan secara cerdas."""
    
    POSITIVE_WORDS = {
        'senang', 'suka', 'bahagia', 'gembira', 'happy', 'seru', 'asik',
        'keren', 'bagus', 'mantap', 'oke', 'baik', 'hebat', 'luar biasa',
        'amazing', 'great', 'good', 'love', 'cinta', 'sayang', 'yeay',
        'hore', 'wow', 'top', 'jago', 'pintar', 'lucu', 'makasih',
        'terima kasih', 'thanks', 'semangat', 'lega', 'puas'
    }
    
    NEGATIVE_WORDS = {
        'sedih', 'marah', 'kesal', 'benci', 'galau', 'bosan', 'bete',
        'kecewa', 'sakit', 'susah', 'sulit', 'buruk', 'jelek', 'bodoh',
        'tolol', 'goblok', 'bego', 'sad', 'angry', 'hate', 'bad',
        'stress', 'depresi', 'nangis', 'takut', 'capek', 'lelah',
        'males', 'suntuk', 'sebel', 'jengkel', 'gondok', 'dongkol',
        'pusing', 'overthinking', 'bingung', 'kacau', 'buntu'
    }
    
    def __init__(self):
        self._conversation_history = deque(maxlen=Config.CONTEXT_WINDOW_SIZE)
        self._current_topic = None
        self._previous_topic = None
        self._current_sentiment = "neutral"
        self._entities = {}              # Entitas yang terdeteksi (nama, tempat, fakta, dll)
        self._turn_count = 0             # Jumlah giliran percakapan
        self._session_start = datetime.now()
        self._awaiting_context = []      # Konteks yang sedang ditunggu
        self._user_name = None           # Nama user jika sudah diketahui
        self._last_milo_act = None       # Tindakan percakapan terakhir Milo (offer_listen, ask_question, dll)
    
    def update(self, user_input, preprocessed_data, intent_result, response):
        """
        Update konteks setelah setiap giliran percakapan.
        
        Args:
            user_input: string input original dari user
            preprocessed_data: dict dari Preprocessor
            intent_result: dict dari IntentRecognizer
            response: string respons dari Milo
        """
        self._turn_count += 1
        
        # Deteksi dialogue act dari respons Milo
        milo_act = self._detect_milo_act(response)
        self._last_milo_act = milo_act
        
        # Update history
        turn = {
            "turn": self._turn_count,
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "user_input": user_input,
            "intent": intent_result.get("intent", "unknown"),
            "confidence": intent_result.get("confidence", 0.0),
            "response": response,
            "milo_act": milo_act
        }
        self._conversation_history.append(turn)
        
        # Update topic
        new_topic = intent_result.get("intent", None)
        if new_topic and new_topic not in ("fallback", "affirmative", "negative"):
            self._previous_topic = self._current_topic
            self._current_topic = new_topic
        
        # Update sentiment
        self._update_sentiment(preprocessed_data)
        
        # Extract entities & personal facts
        self._extract_entities(user_input, intent_result)
    
    def _detect_milo_act(self, response):
        """Mendeteksi tipe tindakan percakapan yang baru saja dilakukan Milo."""
        res_lower = response.lower()
        
        # Menawarkan mendengarkan curhat / cerita
        if any(w in res_lower for w in ["ceritakan uneg-unegmu", "siap dengerin", "cerita aja", "mau cerita", "tempat yang aman", "tumpahkan"]):
            return "offer_listen"
        
        # Menanyakan pertanyaan langsung
        if "?" in response:
            if any(w in res_lower for w in ["makanan favorit", "hobi", "lagu apa", "lagi ngerjain apa", "lagi sibuk"]):
                return "ask_personal_question"
            return "ask_question"
        
        # Memberikan saran
        if any(w in res_lower for w in ["saran", "solusi", "coba urai", "langkah"]):
            return "give_advice"
            
        return "general_statement"
    
    def _update_sentiment(self, preprocessed_data):
        """Mendeteksi dan update sentimen user berdasarkan kata-kata."""
        text = preprocessed_data.get("final", preprocessed_data.get("expanded", ""))
        words = set(text.lower().split())
        
        positive_count = len(words & self.POSITIVE_WORDS)
        negative_count = len(words & self.NEGATIVE_WORDS)
        
        if positive_count > negative_count:
            self._current_sentiment = "positive"
        elif negative_count > positive_count:
            self._current_sentiment = "negative"
        else:
            self._current_sentiment = "neutral"
    
    def _extract_entities(self, text, intent_result):
        """Mengekstrak entitas sederhana dan fakta personal dari input."""
        intent = intent_result.get("intent", "")
        
        # Ekstrak nama user
        if intent == "user_name_tell" or not self._user_name:
            name = self._extract_name(text)
            if name:
                self._user_name = name
                self._entities["user_name"] = name
        
        # Deteksi penyebutan waktu
        time_patterns = [
            r'\b(pagi|siang|sore|malam)\b',
            r'\b(senin|selasa|rabu|kamis|jumat|sabtu|minggu)\b',
            r'\b(besok|kemarin|lusa|sekarang|nanti|tadi)\b',
        ]
        for pattern in time_patterns:
            match = re.search(pattern, text.lower())
            if match:
                self._entities["time_reference"] = match.group()
        
        # Deteksi fakta personal (pekerjaan/kampus/hobi/project)
        facts = self.extract_personal_facts(text)
        self._entities.update(facts)
    
    def extract_personal_facts(self, text):
        """Mengekstrak fakta profil personal dari percakapan."""
        facts = {}
        text_lower = text.lower()
        
        # 1. Pekerjaan / Status / Mahasiswa
        mhs_match = re.search(r'\b(?:aku|saya|gue|gw)\s+(?:seorang\s+|adalah\s+)?(mahasiswa[^\n,.]*|kuliah di[^\n,.]*|jurusan[^\n,.]*|programmer[^\n,.]*|software engineer[^\n,.]*)', text_lower)
        if mhs_match:
            facts["occupation"] = mhs_match.group(1).strip()
        
        # 2. Project / Aktivitas saat ini
        proj_match = re.search(r'\b(?:aku lagi|lagi nyoba|sedang)\s+([^\n,.]+?(?:arsitektur|skripsi|tugas|aplikasi|proyek|project|koding|coding)[^\n,.]*)', text_lower)
        if proj_match:
            facts["current_project"] = proj_match.group(1).strip()
            
        # 3. Makanan Favorit
        food_match = re.search(r'\b(?:makanan favorit(?:ku| saya)?|suka makan)\s+(?:adalah\s+)?([a-zA-Z\s]{3,25}?)(?=\s+(?:dan|serta|karena|tapi|hobiku|hobi)|[.,]|$)', text_lower)
        if food_match:
            facts["favorite_food"] = food_match.group(1).strip()
            
        # 4. Hobi
        hobby_match = re.search(r'\b(?:hobi(?:ku| saya)?|suka banget)\s+(?:adalah\s+)?([a-zA-Z\s]{3,25}?)(?=\s+(?:dan|serta|karena|tapi|makanan)|[.,]|$)', text_lower)
        if hobby_match:
            facts["hobby"] = hobby_match.group(1).strip()
            
        return facts
    
    def _extract_name(self, text):
        """Mengekstrak nama dari input user."""
        name_patterns = [
            r'(?:nama\s*(?:saya|aku|gue|gw)\s+(?:adalah\s+)?)([\w]+)',
            r'(?:(?:namaku|nama\s*ku)\s+(?:adalah\s+)?)([\w]+)',
            r'(?:panggil\s+(?:aku|saya|gue|gw)\s+)([\w]+)',
            r'(?:my\s+name\s+is\s+)([\w]+)',
            r'(?:call\s+me\s+)([\w]+)',
            r'(?:(?:aku|saya|gue|gw)\s+)([\w]+)$',
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, text.lower())
            if match:
                name = match.group(1).capitalize()
                non_names = {'adalah', 'itu', 'ini', 'dong', 'deh', 'ya', 'sih',
                            'aja', 'banget', 'bisa', 'mau', 'milo', 'lagi', 'sedang',
                            'baik', 'capek', 'bingung', 'senang', 'sedih'}
                if name.lower() not in non_names:
                    return name
        return None
    
    def get_last_milo_act(self):
        """Mengembalikan tindakan percakapan terakhir Milo."""
        return self._last_milo_act
    
    def set_last_milo_act(self, act):
        """Menyimpan tindakan percakapan terakhir Milo."""
        self._last_milo_act = act
    
    def get_context(self):
        """Mengembalikan konteks percakapan saat ini."""
        return {
            "current_topic": self._current_topic,
            "previous_topic": self._previous_topic,
            "sentiment": self._current_sentiment,
            "entities": self._entities.copy(),
            "turn_count": self._turn_count,
            "user_name": self._user_name,
            "last_milo_act": self._last_milo_act,
            "session_duration": str(datetime.now() - self._session_start),
            "history_size": len(self._conversation_history),
            "awaiting_context": self._awaiting_context,
        }
    
    def get_history(self, n=None):
        """Mengembalikan N percakapan terakhir."""
        history = list(self._conversation_history)
        if n:
            return history[-n:]
        return history
    
    def get_last_intent(self):
        """Mengembalikan intent dari percakapan terakhir."""
        if self._conversation_history:
            return self._conversation_history[-1].get("intent", None)
        return None
    
    def get_last_user_input(self):
        """Mengembalikan input user dari turn terakhir."""
        if self._conversation_history:
            return self._conversation_history[-1].get("user_input", "")
        return ""
        
    def get_last_substantial_user_input(self, min_words=4):
        """Mengambil input user terakhir dalam riwayat percakapan yang memiliki substansi/cerita bermakna."""
        for turn in reversed(self._conversation_history):
            inp = turn.get("user_input", "")
            if len(inp.split()) >= min_words and not any(phrase in inp.lower() for phrase in ["cuman minta", "minta tips aja", "nggak ada yang lain", "cuman itu"]):
                return inp
        return ""
    
    def get_last_response(self):
        """Mengembalikan respons Milo dari giliran terakhir."""
        if self._conversation_history:
            return self._conversation_history[-1].get("response", "")
        return ""
    
    def get_recent_exchanges(self, count=3):
        """Mengembalikan pertukaran pesan terakhir dalam format ringkas."""
        history = list(self._conversation_history)[-count:]
        return [
            {
                "user": turn.get("user_input", ""),
                "milo": turn.get("response", ""),
                "intent": turn.get("intent", ""),
                "turn": turn.get("turn", 0),
                "milo_act": turn.get("milo_act", "")
            }
            for turn in history
        ]
    
    def get_user_name(self):
        """Mengembalikan nama user jika diketahui."""
        return self._user_name
    
    def set_user_name(self, name):
        """Menyimpan nama user."""
        self._user_name = name
        self._entities["user_name"] = name
    
    def get_sentiment(self):
        """Mengembalikan sentimen user saat ini."""
        return self._current_sentiment
    
    def set_awaiting_context(self, context_list):
        """Menset konteks yang sedang ditunggu."""
        self._awaiting_context = context_list
    
    def clear_awaiting_context(self):
        """Menghapus konteks yang ditunggu."""
        self._awaiting_context = []
    
    def reset(self):
        """Reset semua konteks (mulai percakapan baru)."""
        self._conversation_history.clear()
        self._current_topic = None
        self._previous_topic = None
        self._current_sentiment = "neutral"
        self._entities = {}
        self._turn_count = 0
        self._session_start = datetime.now()
        self._awaiting_context = []
        self._last_milo_act = None
