"""
Milo AI — Configuration Manager
Mengelola semua konfigurasi dan setting Milo secara terpusat.
"""

import os


class Config:
    """Konfigurasi terpusat untuk Milo AI."""
    
    # === Paths ===
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(BASE_DIR, "data")
    STORAGE_DIR = os.path.join(BASE_DIR, "storage")
    MEMORY_DIR = os.path.join(STORAGE_DIR, "memory")
    LOGS_DIR = os.path.join(STORAGE_DIR, "logs")
    
    # === Data Files ===
    INTENTS_FILE = os.path.join(DATA_DIR, "intents.json")
    RESPONSES_FILE = os.path.join(DATA_DIR, "responses.json")
    KNOWLEDGE_FILE = os.path.join(DATA_DIR, "knowledge.json")
    SLANG_DICT_FILE = os.path.join(DATA_DIR, "slang_dict.json")
    STOPWORDS_FILE = os.path.join(DATA_DIR, "stopwords_id.json")
    
    # === Memory Files ===
    LONG_TERM_MEMORY_FILE = os.path.join(MEMORY_DIR, "long_term.json")
    USER_PROFILE_FILE = os.path.join(MEMORY_DIR, "user_profile.json")
    WORD_BANK_FILE = os.path.join(MEMORY_DIR, "word_bank.json")
    
    # === Web & Lexicon Settings ===
    ENABLE_WEB_SEARCH = True          # Gunakan internet untuk mencari definisi/fakta baru
    WEB_TIMEOUT = 3.0                 # Timeout (detik) untuk HTTP requests
    
    # === Milo Identity ===
    MILO_NAME = "Milo"
    MILO_VERSION = "1.0.0"
    MILO_CREATOR = "Kreator"
    
    # === NLP Settings ===
    CONFIDENCE_THRESHOLD = 0.35       # Minimum confidence untuk intent match
    CONTEXT_WINDOW_SIZE = 10          # Jumlah percakapan terakhir yang disimpan
    MAX_NGRAM_SIZE = 3                # Ukuran n-gram maksimum
    SIMILARITY_METHOD = "cosine"      # Metode similarity: "cosine" atau "jaccard"
    
    # === Personality Settings ===
    DEFAULT_MOOD = "happy"            # Mood default Milo
    MOOD_DECAY_RATE = 0.1             # Seberapa cepat mood kembali ke default
    EMOJI_FREQUENCY = 0.7             # Probabilitas penggunaan emoji (0.0 - 1.0)
    
    # === Memory Settings ===
    SHORT_TERM_CAPACITY = 20          # Kapasitas short-term memory (jumlah entri)
    MEMORY_DECAY_THRESHOLD = 0.3      # Threshold untuk memory decay
    
    # === Display Settings ===
    MILO_PREFIX = "🤖 Milo"           # Prefix untuk output Milo
    USER_PREFIX = "👤 Kamu"           # Prefix untuk input user
    SEPARATOR = "─" * 50             # Separator line
    
    @classmethod
    def ensure_directories(cls):
        """Pastikan semua direktori yang diperlukan sudah ada."""
        directories = [
            cls.DATA_DIR,
            cls.STORAGE_DIR,
            cls.MEMORY_DIR,
            cls.LOGS_DIR,
        ]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    @classmethod
    def get_info(cls):
        """Mengembalikan informasi tentang konfigurasi Milo."""
        return {
            "name": cls.MILO_NAME,
            "version": cls.MILO_VERSION,
            "creator": cls.MILO_CREATOR,
            "confidence_threshold": cls.CONFIDENCE_THRESHOLD,
            "context_window": cls.CONTEXT_WINDOW_SIZE,
            "default_mood": cls.DEFAULT_MOOD,
        }
