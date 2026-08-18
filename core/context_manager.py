"""
Milo AI — Context Manager
Mengelola konteks percakapan, termasuk tracking topik, sentimen,
dan entitas yang disebutkan oleh user.
"""

import re
from datetime import datetime
from collections import deque
from utils.config import Config


class ContextManager:
    """Context Manager — mengelola konteks dan state percakapan."""
    
    # Kata-kata kunci untuk deteksi sentimen sederhana
    POSITIVE_WORDS = {
        'senang', 'suka', 'bahagia', 'gembira', 'happy', 'seru', 'asik',
        'keren', 'bagus', 'mantap', 'oke', 'baik', 'hebat', 'luar biasa',
        'amazing', 'great', 'good', 'love', 'cinta', 'sayang', 'yeay',
        'hore', 'wow', 'top', 'jago', 'pintar', 'lucu', 'makasih',
        'terima kasih', 'thanks', 'semangat',
    }
    
    NEGATIVE_WORDS = {
        'sedih', 'marah', 'kesal', 'benci', 'galau', 'bosan', 'bete',
        'kecewa', 'sakit', 'susah', 'sulit', 'buruk', 'jelek', 'bodoh',
        'tolol', 'goblok', 'bego', 'sad', 'angry', 'hate', 'bad',
        'stress', 'depresi', 'nangis', 'takut', 'capek', 'lelah',
        'males', 'suntuk', 'sebel', 'jengkel', 'gondok', 'dongkol',
    }
    
    def __init__(self):
        self._conversation_history = deque(maxlen=Config.CONTEXT_WINDOW_SIZE)
        self._current_topic = None
        self._previous_topic = None
        self._current_sentiment = "neutral"
        self._entities = {}              # Entitas yang terdeteksi (nama, tempat, dll)
        self._turn_count = 0             # Jumlah giliran percakapan
        self._session_start = datetime.now()
        self._awaiting_context = []      # Konteks yang sedang ditunggu
        self._user_name = None           # Nama user jika sudah diketahui
    
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
        
        # Update history
        turn = {
            "turn": self._turn_count,
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "user_input": user_input,
            "intent": intent_result.get("intent", "unknown"),
            "confidence": intent_result.get("confidence", 0.0),
            "response": response,
        }
        self._conversation_history.append(turn)
        
        # Update topic
        new_topic = intent_result.get("intent", None)
        if new_topic and new_topic != "fallback":
            self._previous_topic = self._current_topic
            self._current_topic = new_topic
        
        # Update sentiment
        self._update_sentiment(preprocessed_data)
        
        # Extract entities
        self._extract_entities(user_input, intent_result)
    
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
            # Perlahan kembali ke neutral
            self._current_sentiment = "neutral"
    
    def _extract_entities(self, text, intent_result):
        """Mengekstrak entitas sederhana dari input (nama, waktu, dll)."""
        intent = intent_result.get("intent", "")
        
        # Ekstrak nama user
        if intent == "user_name_tell":
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
    
    def _extract_name(self, text):
        """Mengekstrak nama dari input user."""
        # Pattern umum untuk menyebutkan nama
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
                # Filter kata-kata yang bukan nama
                non_names = {'adalah', 'itu', 'ini', 'dong', 'deh', 'ya', 'sih',
                            'aja', 'banget', 'bisa', 'mau', 'milo'}
                if name.lower() not in non_names:
                    return name
        
        return None
    
    def get_context(self):
        """Mengembalikan konteks percakapan saat ini."""
        return {
            "current_topic": self._current_topic,
            "previous_topic": self._previous_topic,
            "sentiment": self._current_sentiment,
            "entities": self._entities.copy(),
            "turn_count": self._turn_count,
            "user_name": self._user_name,
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
        """Mengembalikan input user dari giliran terakhir."""
        if self._conversation_history:
            return self._conversation_history[-1].get("user_input", "")
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
                "turn": turn.get("turn", 0)
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
        # Tetap simpan user_name
