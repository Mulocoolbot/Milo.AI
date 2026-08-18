"""
Milo AI — Memory System
Sistem memori jangka pendek dan jangka panjang untuk Milo.
Short-term: konteks percakapan saat ini.
Long-term: informasi yang dipersist ke file (bertahan setelah restart).
"""

import json
import os
from datetime import datetime
from collections import deque
from utils.config import Config


class Memory:
    """Memory System — mengelola memori jangka pendek & panjang Milo."""
    
    def __init__(self):
        Config.ensure_directories()
        
        # Short-term memory (in-session, hilang saat restart)
        self._short_term = deque(maxlen=Config.SHORT_TERM_CAPACITY)
        
        # Long-term memory (persisted ke file)
        self._long_term = {}
        
        # User profile (persisted)
        self._user_profile = {}
        
        # Load persisted data
        self._load_long_term()
        self._load_user_profile()
    
    # === Short-Term Memory ===
    
    def remember_short(self, key, value, importance=0.5):
        """
        Menyimpan informasi ke short-term memory.
        
        Args:
            key: string kunci memori
            value: nilai yang disimpan
            importance: float 0.0-1.0 tingkat kepentingan
        """
        entry = {
            "key": key,
            "value": value,
            "importance": importance,
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "access_count": 0,
        }
        
        # Cek apakah key sudah ada, update jika ya
        for i, existing in enumerate(self._short_term):
            if existing["key"] == key:
                self._short_term[i] = entry
                return
        
        self._short_term.append(entry)
    
    def recall_short(self, key):
        """Mengambil informasi dari short-term memory."""
        for entry in self._short_term:
            if entry["key"] == key:
                entry["access_count"] += 1
                return entry["value"]
        return None
    
    def get_short_term_all(self):
        """Mengembalikan semua isi short-term memory."""
        return list(self._short_term)
    
    # === Long-Term Memory ===
    
    def remember_long(self, key, value, category="general"):
        """
        Menyimpan informasi ke long-term memory (persisted).
        
        Args:
            key: string kunci memori
            value: nilai yang disimpan
            category: string kategori memori
        """
        if category not in self._long_term:
            self._long_term[category] = {}
        
        self._long_term[category][key] = {
            "value": value,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "access_count": 0,
        }
        
        self._save_long_term()
    
    def recall_long(self, key, category=None):
        """Mengambil informasi dari long-term memory."""
        if category:
            cat_data = self._long_term.get(category, {})
            entry = cat_data.get(key)
            if entry:
                entry["access_count"] += 1
                self._save_long_term()
                return entry["value"]
            return None
        
        # Search across all categories
        for cat_data in self._long_term.values():
            if key in cat_data:
                cat_data[key]["access_count"] += 1
                self._save_long_term()
                return cat_data[key]["value"]
        
        return None
    
    def get_long_term_all(self, category=None):
        """Mengembalikan semua isi long-term memory."""
        if category:
            return self._long_term.get(category, {})
        return self._long_term.copy()
    
    # === User Profile ===
    
    def set_user_info(self, key, value):
        """Menyimpan informasi tentang user."""
        self._user_profile[key] = {
            "value": value,
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        self._save_user_profile()
    
    def get_user_info(self, key):
        """Mengambil informasi tentang user."""
        entry = self._user_profile.get(key)
        if entry:
            return entry["value"]
        return None
    
    def get_user_profile(self):
        """Mengembalikan profil user lengkap."""
        return {k: v["value"] for k, v in self._user_profile.items()}
    
    # === Memory Consolidation ===
    
    def consolidate(self):
        """
        Konsolidasi memori — memindahkan informasi penting 
        dari short-term ke long-term.
        """
        consolidated = 0
        
        for entry in self._short_term:
            # Pindahkan jika importance tinggi atau sering diakses
            if entry["importance"] >= 0.7 or entry["access_count"] >= 3:
                self.remember_long(
                    entry["key"], 
                    entry["value"], 
                    category="consolidated"
                )
                consolidated += 1
        
        return consolidated
    
    # === Persistence ===
    
    def _load_long_term(self):
        """Memuat long-term memory dari file."""
        try:
            if os.path.exists(Config.LONG_TERM_MEMORY_FILE):
                with open(Config.LONG_TERM_MEMORY_FILE, "r", encoding="utf-8") as f:
                    self._long_term = json.load(f)
        except (json.JSONDecodeError, IOError):
            self._long_term = {}
    
    def _save_long_term(self):
        """Menyimpan long-term memory ke file."""
        try:
            with open(Config.LONG_TERM_MEMORY_FILE, "w", encoding="utf-8") as f:
                json.dump(self._long_term, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"[Memory] Error saving long-term: {e}")
    
    def _load_user_profile(self):
        """Memuat profil user dari file."""
        try:
            if os.path.exists(Config.USER_PROFILE_FILE):
                with open(Config.USER_PROFILE_FILE, "r", encoding="utf-8") as f:
                    self._user_profile = json.load(f)
        except (json.JSONDecodeError, IOError):
            self._user_profile = {}
    
    def _save_user_profile(self):
        """Menyimpan profil user ke file."""
        try:
            with open(Config.USER_PROFILE_FILE, "w", encoding="utf-8") as f:
                json.dump(self._user_profile, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"[Memory] Error saving user profile: {e}")
    
    def clear_short_term(self):
        """Menghapus short-term memory."""
        self._short_term.clear()
    
    def clear_all(self):
        """Menghapus semua memori (hati-hati!)."""
        self._short_term.clear()
        self._long_term = {}
        self._user_profile = {}
        self._save_long_term()
        self._save_user_profile()
