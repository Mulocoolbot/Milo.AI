"""
Milo AI — Emotion Engine
Simulasi emosi sederhana untuk Milo menggunakan state machine.
Emosi Milo berubah berdasarkan interaksi dengan user.
"""

import random
from datetime import datetime


class EmotionEngine:
    """Emotion Engine — mengelola state emosi Milo."""
    
    # Definisi emosi yang tersedia
    EMOTIONS = {
        "happy":       {"emoji": "😊", "intensity_range": (0.5, 1.0)},
        "excited":     {"emoji": "🎉", "intensity_range": (0.7, 1.0)},
        "neutral":     {"emoji": "🙂", "intensity_range": (0.3, 0.6)},
        "curious":     {"emoji": "🤔", "intensity_range": (0.4, 0.8)},
        "empathetic":  {"emoji": "🤗", "intensity_range": (0.5, 0.9)},
        "playful":     {"emoji": "😄", "intensity_range": (0.6, 1.0)},
        "sad":         {"emoji": "😢", "intensity_range": (0.3, 0.7)},
        "concerned":   {"emoji": "😟", "intensity_range": (0.4, 0.8)},
    }
    
    # Transisi emosi berdasarkan intent/sentimen user
    TRANSITIONS = {
        # (current_emotion, trigger) -> new_emotion
        "greeting":        "happy",
        "farewell":        "sad",
        "thanks":          "happy",
        "compliment":      "excited",
        "insult":          "sad",
        "feeling_happy":   "excited",
        "feeling_sad":     "empathetic",
        "feeling_angry":   "concerned",
        "joke":            "playful",
        "philosophy":      "curious",
        "help":            "empathetic",
        "how_are_you":     "happy",
    }
    
    def __init__(self, default_emotion="happy"):
        self._current_emotion = default_emotion
        self._intensity = 0.6           # Intensitas emosi (0.0 - 1.0)
        self._emotion_history = []      # Riwayat perubahan emosi
        self._decay_rate = 0.05         # Seberapa cepat emosi kembali ke default
        self._default_emotion = default_emotion
    
    def process_trigger(self, intent, sentiment="neutral"):
        """
        Memproses trigger dan mengubah emosi Milo jika diperlukan.
        
        Args:
            intent: string intent yang terdeteksi
            sentiment: string sentimen user (positive/negative/neutral)
        
        Returns:
            dict berisi state emosi baru
        """
        previous_emotion = self._current_emotion
        
        # Cek transisi berdasarkan intent
        new_emotion = self.TRANSITIONS.get(intent)
        
        if new_emotion:
            self._current_emotion = new_emotion
            # Sesuaikan intensitas
            emotion_data = self.EMOTIONS.get(new_emotion, {})
            intensity_range = emotion_data.get("intensity_range", (0.3, 0.7))
            self._intensity = random.uniform(*intensity_range)
        else:
            # Jika tidak ada transisi spesifik, sesuaikan berdasarkan sentimen
            if sentiment == "positive":
                self._current_emotion = "happy"
                self._intensity = min(1.0, self._intensity + 0.1)
            elif sentiment == "negative":
                self._current_emotion = "empathetic"
                self._intensity = min(1.0, self._intensity + 0.1)
            else:
                # Decay menuju default
                self._apply_decay()
        
        # Catat perubahan emosi
        if previous_emotion != self._current_emotion:
            self._emotion_history.append({
                "from": previous_emotion,
                "to": self._current_emotion,
                "trigger": intent,
                "timestamp": datetime.now().strftime("%H:%M:%S"),
            })
        
        return self.get_state()
    
    def _apply_decay(self):
        """Menerapkan decay — emosi perlahan kembali ke default."""
        if self._current_emotion != self._default_emotion:
            self._intensity -= self._decay_rate
            if self._intensity <= 0.3:
                self._current_emotion = self._default_emotion
                self._intensity = 0.5
    
    def get_state(self):
        """Mengembalikan state emosi saat ini."""
        emotion_data = self.EMOTIONS.get(self._current_emotion, {})
        
        return {
            "emotion": self._current_emotion,
            "emoji": emotion_data.get("emoji", "🙂"),
            "intensity": round(self._intensity, 2),
        }
    
    def get_emoji(self):
        """Mengembalikan emoji yang merepresentasikan emosi saat ini."""
        emotion_data = self.EMOTIONS.get(self._current_emotion, {})
        return emotion_data.get("emoji", "🙂")
    
    def get_emotion(self):
        """Mengembalikan nama emosi saat ini."""
        return self._current_emotion
    
    def get_intensity(self):
        """Mengembalikan intensitas emosi saat ini."""
        return self._intensity
    
    def get_history(self):
        """Mengembalikan riwayat perubahan emosi."""
        return self._emotion_history.copy()
    
    def set_emotion(self, emotion, intensity=None):
        """Set emosi secara manual."""
        if emotion in self.EMOTIONS:
            self._current_emotion = emotion
            if intensity is not None:
                self._intensity = max(0.0, min(1.0, intensity))
    
    def reset(self):
        """Reset emosi ke default."""
        self._current_emotion = self._default_emotion
        self._intensity = 0.6
        self._emotion_history = []
