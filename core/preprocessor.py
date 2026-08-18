"""
Milo AI — Text Preprocessor
Membersihkan dan menyiapkan input teks dari user sebelum diproses lebih lanjut.
Termasuk: normalisasi, ekspansi slang, dan koreksi typo sederhana.
"""

import json
import re
import os
from utils.config import Config


class Preprocessor:
    """Text Preprocessor — membersihkan dan menormalisasi input user."""
    
    def __init__(self):
        self._slang_dict = {}
        self._load_slang_dict()
    
    def _load_slang_dict(self):
        """Memuat kamus slang dari file JSON."""
        try:
            with open(Config.SLANG_DICT_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                self._slang_dict = data.get("slang", {})
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"[Preprocessor] Warning: Gagal memuat slang dict: {e}")
            self._slang_dict = {}
    
    def preprocess(self, text):
        """
        Pipeline preprocessing lengkap.
        
        Args:
            text: string input dari user
        
        Returns:
            dict berisi teks yang sudah diproses beserta metadata
        """
        if not text or not text.strip():
            return {
                "original": text,
                "cleaned": "",
                "normalized": "",
                "expanded": "",
                "tokens_raw": [],
            }
        
        original = text
        
        # Step 1: Basic cleaning
        cleaned = self._clean_text(text)
        
        # Step 2: Case normalization
        normalized = cleaned.lower()
        
        # Step 3: Expand slang/abbreviations
        expanded = self._expand_slang(normalized)
        
        # Step 4: Remove extra punctuation (tapi simpan untuk analisis sentiment)
        has_question = "?" in text
        has_exclamation = "!" in text
        has_ellipsis = "..." in text
        
        final = self._remove_extra_punctuation(expanded)
        
        return {
            "original": original,
            "cleaned": cleaned,
            "normalized": normalized,
            "expanded": expanded,
            "final": final,
            "tokens_raw": final.split(),
            "metadata": {
                "has_question": has_question,
                "has_exclamation": has_exclamation,
                "has_ellipsis": has_ellipsis,
                "word_count": len(final.split()),
                "char_count": len(final),
            }
        }
    
    def _clean_text(self, text):
        """Membersihkan teks dari karakter yang tidak diperlukan."""
        # Hapus multiple spaces
        text = re.sub(r'\s+', ' ', text)
        
        # Trim whitespace
        text = text.strip()
        
        # Hapus emoji unicode (simpan di metadata nanti kalau diperlukan)
        # Tapi kita keep emoji karena bisa jadi indikator sentiment
        
        return text
    
    def _expand_slang(self, text):
        """Mengekspansi slang/singkatan menjadi kata lengkap."""
        words = text.split()
        expanded_words = []
        
        for word in words:
            # Cek apakah kata ada di kamus slang
            clean_word = re.sub(r'[^\w]', '', word)  # Hapus punctuation untuk lookup
            
            if clean_word in self._slang_dict:
                expanded_words.append(self._slang_dict[clean_word])
            else:
                expanded_words.append(word)
        
        return " ".join(expanded_words)
    
    def _remove_extra_punctuation(self, text):
        """Menghapus tanda baca berlebih tapi tetap menjaga readability."""
        # Hapus tanda baca berulang (!!!! -> !, ???? -> ?)
        text = re.sub(r'([!?.])\1+', r'\1', text)
        
        # Hapus tanda baca di awal
        text = re.sub(r'^[^\w\s]+', '', text)
        
        # Hapus tanda baca selain yang berguna
        text = re.sub(r'[^\w\s?!.,]', '', text)
        
        # Bersihkan spaces
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def get_slang_dict(self):
        """Mengembalikan kamus slang yang digunakan."""
        return self._slang_dict.copy()
    
    def add_slang(self, slang, expansion):
        """Menambahkan entri slang baru ke kamus."""
        self._slang_dict[slang.lower()] = expansion.lower()
