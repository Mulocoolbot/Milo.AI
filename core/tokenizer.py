"""
Milo AI — Tokenizer
Memecah kalimat menjadi token (kata/frasa) dan melakukan stemming sederhana
untuk Bahasa Indonesia.
"""

import json
import re
from utils.config import Config
from utils.text_utils import TextUtils


class Tokenizer:
    """Tokenizer — memecah teks menjadi token yang bermakna."""
    
    # Aturan imbuhan Bahasa Indonesia untuk stemming sederhana
    PREFIXES = ['meng', 'mem', 'men', 'meny', 'me', 'ber', 'be', 
                'di', 'ke', 'se', 'peng', 'pem', 'pen', 'peny', 'pe',
                'ter', 'per']
    SUFFIXES = ['kan', 'an', 'i', 'nya']
    
    def __init__(self):
        self._stopwords = set()
        self._load_stopwords()
    
    def _load_stopwords(self):
        """Memuat daftar stopwords dari file JSON."""
        try:
            with open(Config.STOPWORDS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                self._stopwords = set(data.get("stopwords", []))
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"[Tokenizer] Warning: Gagal memuat stopwords: {e}")
            self._stopwords = set()
    
    def tokenize(self, preprocessed_data):
        """
        Pipeline tokenisasi lengkap.
        
        Args:
            preprocessed_data: dict output dari Preprocessor.preprocess()
        
        Returns:
            dict berisi berbagai bentuk token
        """
        text = preprocessed_data.get("final", preprocessed_data.get("expanded", ""))
        
        if not text:
            return {
                "words": [],
                "filtered": [],
                "stemmed": [],
                "bigrams": [],
                "trigrams": [],
                "unique_words": set(),
            }
        
        # Step 1: Word tokenization
        words = self._word_tokenize(text)
        
        # Step 2: Filter stopwords
        filtered = self._filter_stopwords(words)
        
        # Step 3: Stemming sederhana
        stemmed = [self._simple_stem(w) for w in filtered]
        
        # Step 4: N-gram generation
        bigrams = TextUtils.generate_ngrams(words, 2)
        trigrams = TextUtils.generate_ngrams(words, 3)
        
        return {
            "words": words,               # Semua kata
            "filtered": filtered,          # Tanpa stopwords
            "stemmed": stemmed,            # Setelah stemming
            "bigrams": bigrams,            # Bigram
            "trigrams": trigrams,          # Trigram
            "unique_words": set(words),    # Kata unik
            "word_count": len(words),
        }
    
    def _word_tokenize(self, text):
        """Memecah teks menjadi kata-kata individual."""
        # Split berdasarkan whitespace dan punctuation
        # Tapi pertahankan kata-kata yang mengandung tanda hubung
        words = re.findall(r'\b\w+(?:-\w+)*\b', text.lower())
        return words
    
    def _filter_stopwords(self, words):
        """Menghapus stopwords dari daftar kata."""
        return [w for w in words if w not in self._stopwords and len(w) > 1]
    
    def _simple_stem(self, word):
        """
        Stemming sederhana untuk Bahasa Indonesia.
        Menghapus imbuhan (prefix dan suffix) dari kata.
        
        Catatan: Ini adalah implementasi sederhana, tidak se-akurat
        algoritma stemming penuh seperti Sastrawi.
        """
        if len(word) <= 3:
            return word
        
        original = word
        
        # Hapus suffix terlebih dahulu
        for suffix in self.SUFFIXES:
            if word.endswith(suffix) and len(word) - len(suffix) >= 3:
                word = word[:-len(suffix)]
                break
        
        # Hapus prefix
        for prefix in self.PREFIXES:
            if word.startswith(prefix) and len(word) - len(prefix) >= 3:
                word = word[len(prefix):]
                break
        
        # Jika hasilnya terlalu pendek, kembalikan kata asli
        if len(word) < 2:
            return original
        
        return word
    
    def is_stopword(self, word):
        """Cek apakah sebuah kata adalah stopword."""
        return word.lower() in self._stopwords
    
    def get_stopwords(self):
        """Mengembalikan set stopwords yang digunakan."""
        return self._stopwords.copy()
    
    def add_stopword(self, word):
        """Menambahkan stopword baru."""
        self._stopwords.add(word.lower())
    
    def remove_stopword(self, word):
        """Menghapus stopword."""
        self._stopwords.discard(word.lower())
