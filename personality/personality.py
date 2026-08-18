"""
Milo AI — Personality Engine
Membuat Milo terasa 'hidup' dengan karakter, mood, dan gaya bicara.
"""

import random
from .emotions import EmotionEngine


class Personality:
    """Personality Engine — memberikan karakter kepada Milo."""
    
    # Traits/sifat dasar Milo
    TRAITS = {
        "friendliness": 0.9,    # Seberapa ramah
        "humor": 0.7,           # Seberapa lucu
        "empathy": 0.85,        # Seberapa empati
        "curiosity": 0.8,       # Seberapa penasaran
        "enthusiasm": 0.85,     # Seberapa antusias
        "formality": 0.3,       # Seberapa formal (rendah = casual)
    }
    
    # Ekspresi tambahan berdasarkan emosi
    EXPRESSIONS = {
        "happy": [
            " ✨", " 😊", " 🎉", " 💫", " 🌟", " 😄", " 🥳"
        ],
        "excited": [
            " 🔥", " 🚀", " 💥", " ⚡", " 🎊", " 🤩"
        ],
        "empathetic": [
            " 💕", " 🤗", " 💙", " 🫂", " ❤️"
        ],
        "curious": [
            " 🤔", " 💭", " 🧐", " ❓"
        ],
        "playful": [
            " 😜", " 😆", " 🤣", " 😂", " 🎮"
        ],
        "sad": [
            " 😢", " 💔", " 😔", " 🥺"
        ],
        "concerned": [
            " 😟", " 😰", " 🙁", " 😮"
        ],
        "neutral": [
            " 🙂", " 👍", " ✌️"
        ],
    }
    
    # Filler words untuk membuat percakapan lebih natural
    FILLERS = {
        "casual": [
            "Hmm, ", "Nah, ", "Jadi gini, ", "Oke, ", 
            "Wah, ", "Hehe, ", "Eh, ", "Btw, ",
        ],
        "thinking": [
            "Hmm, coba Milo pikir ya... ", "Interesting! ",
            "Oh, ", "Ahh, ", "Mmm, ",
        ],
        "empathy": [
            "Milo ngerti kok, ", "Milo paham, ",
            "Iya ya, ", "Bener banget, ",
        ],
    }
    
    def __init__(self):
        self._emotion_engine = EmotionEngine()
        self._mood = "happy"
        self._style = "casual"   # casual, friendly, empathetic
    
    def process(self, response, intent, context):
        """
        Memproses respons melalui personality filter.
        Menambahkan sentuhan personal berdasarkan emosi dan traits Milo.
        
        Args:
            response: string respons dari ResponseEngine
            intent: string intent yang terdeteksi
            context: dict konteks percakapan
        
        Returns:
            string respons yang sudah dipersonalisasi
        """
        sentiment = context.get("sentiment", "neutral")
        
        # Update emosi berdasarkan interaksi
        emotion_state = self._emotion_engine.process_trigger(intent, sentiment)
        current_emotion = emotion_state["emotion"]
        
        # Update style berdasarkan emosi
        self._update_style(current_emotion, sentiment)
        
        # Tambahkan filler word sesekali (untuk kesan natural)
        if random.random() < 0.15 and not response.startswith(("Hmm", "Nah", "Jadi", "Oke", "Wah")):
            filler_type = "casual"
            if current_emotion in ("empathetic", "concerned"):
                filler_type = "empathy"
            elif current_emotion == "curious":
                filler_type = "thinking"
            
            fillers = self.FILLERS.get(filler_type, self.FILLERS["casual"])
            response = random.choice(fillers) + response[0].lower() + response[1:]
        
        return response
    
    def _update_style(self, emotion, sentiment):
        """Update gaya bicara berdasarkan emosi."""
        if emotion in ("empathetic", "concerned", "sad"):
            self._style = "empathetic"
        elif emotion in ("happy", "excited", "playful"):
            self._style = "friendly"
        else:
            self._style = "casual"
    
    def get_emotion_state(self):
        """Mengembalikan state emosi saat ini."""
        return self._emotion_engine.get_state()
    
    def get_emotion_engine(self):
        """Mengembalikan instance EmotionEngine."""
        return self._emotion_engine
    
    def get_style(self):
        """Mengembalikan gaya bicara saat ini."""
        return self._style
    
    def get_traits(self):
        """Mengembalikan traits/sifat Milo."""
        return self.TRAITS.copy()
    
    def get_mood(self):
        """Mengembalikan mood Milo saat ini."""
        return self._emotion_engine.get_emotion()
    
    def reset(self):
        """Reset personality ke default."""
        self._emotion_engine.reset()
        self._mood = "happy"
        self._style = "casual"
