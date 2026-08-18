"""
Milo AI — Knowledge Base Manager
Mengelola basis pengetahuan Milo, termasuk CRUD operations
dan pencarian berdasarkan keyword.
"""

import json
import os
from utils.config import Config


class KnowledgeBase:
    """Knowledge Base — mengelola pengetahuan Milo."""
    
    def __init__(self):
        self._knowledge = {}
        self._load_knowledge()
    
    def _load_knowledge(self):
        """Memuat knowledge base dari file JSON."""
        try:
            with open(Config.KNOWLEDGE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                self._knowledge = data.get("categories", {})
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"[KnowledgeBase] Warning: Gagal memuat knowledge: {e}")
            self._knowledge = {}
    
    def search(self, query, category=None):
        """
        Mencari informasi di knowledge base.
        
        Args:
            query: string kata kunci pencarian
            category: string kategori spesifik (opsional)
        
        Returns:
            list of matching results
        """
        results = []
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        categories_to_search = self._knowledge
        if category and category in self._knowledge:
            categories_to_search = {category: self._knowledge[category]}
        
        for cat_name, cat_data in categories_to_search.items():
            entries = cat_data.get("entries", {})
            
            if isinstance(entries, dict):
                results.extend(
                    self._search_dict(entries, query_lower, query_words, cat_name)
                )
            elif isinstance(entries, list):
                results.extend(
                    self._search_list(entries, query_lower, query_words, cat_name)
                )
        
        return results
    
    def _search_dict(self, entries, query, query_words, category):
        """Mencari di dictionary entries."""
        results = []
        
        for key, value in entries.items():
            key_lower = key.lower()
            
            # Match berdasarkan key
            if query in key_lower or key_lower in query:
                results.append({
                    "category": category,
                    "key": key,
                    "value": value,
                    "match_type": "key_match",
                })
            # Match berdasarkan value (jika string)
            elif isinstance(value, str) and query in value.lower():
                results.append({
                    "category": category,
                    "key": key,
                    "value": value,
                    "match_type": "value_match",
                })
            # Recursive search untuk nested dict
            elif isinstance(value, dict):
                nested = self._search_dict(value, query, query_words, category)
                results.extend(nested)
        
        return results
    
    def _search_list(self, entries, query, query_words, category):
        """Mencari di list entries."""
        results = []
        
        for i, entry in enumerate(entries):
            if isinstance(entry, str) and query in entry.lower():
                results.append({
                    "category": category,
                    "index": i,
                    "value": entry,
                    "match_type": "list_match",
                })
        
        return results
    
    def search_by_keywords(self, keywords, max_results=5):
        """
        Mencari informasi di knowledge base berdasarkan list kata kunci.
        Mengembalikan hasil yang paling relevan dengan scoring.
        
        Args:
            keywords: list of string kata kunci
            max_results: jumlah maksimal hasil
        
        Returns:
            list of dict dengan key: category, key, value, score
        """
        if not keywords:
            return []
        
        results = []
        keywords_lower = [k.lower() for k in keywords]
        
        for cat_name, cat_data in self._knowledge.items():
            entries = cat_data.get("entries", {})
            
            if isinstance(entries, dict):
                results.extend(
                    self._score_dict_entries(entries, keywords_lower, cat_name)
                )
            elif isinstance(entries, list):
                results.extend(
                    self._score_list_entries(entries, keywords_lower, cat_name)
                )
        
        # Urutkan berdasarkan score tertinggi
        results.sort(key=lambda x: x["score"], reverse=True)
        
        # Filter hasil yang scorenya > 0
        results = [r for r in results if r["score"] > 0]
        
        return results[:max_results]
    
    def _score_dict_entries(self, entries, keywords, category, parent_key=None):
        """Memberi skor pada dictionary entries berdasarkan keyword match."""
        results = []
        
        for key, value in entries.items():
            key_lower = key.lower()
            key_parts = set(key_lower.replace('_', ' ').split())
            score = 0
            
            # Hitung scoring
            for kw in keywords:
                kw_clean = kw.lower().strip()
                if not kw_clean:
                    continue
                
                # 1. Exact match pada key (prioritas tertinggi)
                if kw_clean == key_lower or kw_clean == key_lower.replace('_', ' '):
                    score += 10
                # 2. Kata kunci ada di bagian key
                elif kw_clean in key_parts:
                    score += 6
                # 3. Substring match pada key (hanya jika panjang kata >= 3)
                elif len(kw_clean) >= 3 and len(key_lower) >= 3 and (kw_clean in key_lower or key_lower in kw_clean):
                    score += 3
                
                # 4. Cek value jika string
                if isinstance(value, str):
                    val_lower = value.lower()
                    if f" {kw_clean} " in f" {val_lower} ":
                        score += 2
                    elif kw_clean in val_lower:
                        score += 1
            
            if score > 0:
                display_key = f"{parent_key} > {key}" if parent_key else key
                results.append({
                    "category": category,
                    "key": display_key,
                    "value": value,
                    "score": score,
                })
            
            # Recursive search untuk nested dict
            if isinstance(value, dict):
                nested = self._score_dict_entries(value, keywords, category, parent_key=key)
                results.extend(nested)
        
        return results
    
    def _score_list_entries(self, entries, keywords, category):
        """Memberi skor pada list entries berdasarkan keyword match."""
        results = []
        
        for entry in entries:
            if not isinstance(entry, str):
                continue
            
            entry_lower = entry.lower()
            score = 0
            
            for kw in keywords:
                if kw in entry_lower:
                    score += 1
            
            if score > 0:
                results.append({
                    "category": category,
                    "key": None,
                    "value": entry,
                    "score": score,
                })
        
        return results
    
    def get_random_entry(self, category):
        """Mengambil entri acak dari kategori tertentu."""
        import random
        
        if category not in self._knowledge:
            return None
        
        entries = self._knowledge[category].get("entries", {})
        
        if isinstance(entries, list) and entries:
            return random.choice(entries)
        elif isinstance(entries, dict) and entries:
            key = random.choice(list(entries.keys()))
            return {key: entries[key]}
        
        return None
    
    def get_category(self, category):
        """Mengembalikan semua entries dari kategori tertentu."""
        if category in self._knowledge:
            return self._knowledge[category].get("entries", {})
        return None
    
    def get_categories(self):
        """Mengembalikan daftar semua kategori."""
        return list(self._knowledge.keys())
    
    def add_entry(self, category, key, value):
        """Menambahkan entri baru ke knowledge base."""
        if category not in self._knowledge:
            self._knowledge[category] = {
                "description": f"Custom category: {category}",
                "entries": {}
            }
        
        entries = self._knowledge[category].get("entries", {})
        if isinstance(entries, dict):
            entries[key] = value
        elif isinstance(entries, list):
            entries.append(value)
    
    def save(self):
        """Menyimpan knowledge base ke file."""
        try:
            data = {"categories": self._knowledge}
            with open(Config.KNOWLEDGE_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"[KnowledgeBase] Error saving: {e}")
