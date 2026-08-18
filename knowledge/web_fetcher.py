"""
Milo AI — Internet Semantic & Knowledge Fetcher
Modul pencarian arti kata dan informasi fakta secara real-time via koneksi internet
menggunakan pustaka standar Python (urllib.request) tanpa dependensi library eksternal.
"""

import json
import urllib.request
import urllib.parse
import urllib.error
import re
import ssl
from utils.config import Config


class WebFetcher:
    """Internet Knowledge & Lexicon Fetcher untuk Milo AI."""
    
    def __init__(self):
        self._cache = {}
        self._timeout = getattr(Config, "WEB_TIMEOUT", 3.0)
        self._enabled = getattr(Config, "ENABLE_WEB_SEARCH", True)
        
        # Buat SSL context yang aman & fleksibel
        self._ssl_context = ssl.create_default_context()
        self._ssl_context.check_hostname = False
        self._ssl_context.verify_mode = ssl.CERT_NONE
    
    def fetch_word_definition(self, word):
        """
        Mencari definisi dan kelas kata dari Wiktionary atau Wikipedia Bahasa Indonesia.
        
        Args:
            word: string kata yang dicari
            
        Returns:
            dict berisi definition, pos, source atau None
        """
        if not self._enabled or not word:
            return None
            
        word_clean = word.strip().lower()
        if word_clean in self._cache:
            return self._cache[word_clean]
            
        # 1. Coba Wiktionary ID API
        encoded_word = urllib.parse.quote(word_clean)
        wikt_url = f"https://id.wiktionary.org/w/api.php?action=query&prop=extracts&explaintext=1&titles={encoded_word}&format=json"
        
        res = self._make_request(wikt_url)
        if res and "query" in res and "pages" in res["query"]:
            pages = res["query"]["pages"]
            for page_id, page_data in pages.items():
                if page_id != "-1" and "extract" in page_data:
                    raw_extract = page_data["extract"]
                    cleaned_def = self._clean_wiktionary_extract(raw_extract)
                    if cleaned_def:
                        result = {
                            "word": word_clean,
                            "meaning": cleaned_def,
                            "source": "Wiktionary Indonesia"
                        }
                        self._cache[word_clean] = result
                        return result
        
        # 2. Fallback ke Wikipedia ID API
        wiki_url = f"https://id.wikipedia.org/w/api.php?action=query&prop=extracts&exintro=1&explaintext=1&titles={encoded_word}&format=json"
        res_wiki = self._make_request(wiki_url)
        if res_wiki and "query" in res_wiki and "pages" in res_wiki["query"]:
            pages = res_wiki["query"]["pages"]
            for page_id, page_data in pages.items():
                if page_id != "-1" and "extract" in page_data:
                    extract = page_data["extract"].strip()
                    if extract:
                        first_sentence = extract.split(". ")[0] + "."
                        result = {
                            "word": word_clean,
                            "meaning": first_sentence,
                            "source": "Wikipedia Indonesia"
                        }
                        self._cache[word_clean] = result
                        return result
                        
        return None
    
    def search_concept_summary(self, query):
        """
        Mencari ringkasan konsep pengetahuan dari internet via Wikipedia ID atau DuckDuckGo.
        
        Args:
            query: string topik/pertanyaan
            
        Returns:
            string ringkasan atau None
        """
        if not self._enabled or not query:
            return None
            
        query_clean = query.strip()
        if query_clean in self._cache:
            return self._cache[query_clean].get("meaning")
            
        # 1. Coba Wikipedia ID
        encoded = urllib.parse.quote(query_clean)
        wiki_url = f"https://id.wikipedia.org/w/api.php?action=query&prop=extracts&exintro=1&explaintext=1&titles={encoded}&format=json"
        
        res = self._make_request(wiki_url)
        if res and "query" in res and "pages" in res["query"]:
            pages = res["query"]["pages"]
            for page_id, page_data in pages.items():
                if page_id != "-1" and "extract" in page_data:
                    extract = page_data["extract"].strip()
                    if extract:
                        sentences = extract.split(". ")
                        summary = ". ".join(sentences[:2]) + ("." if not sentences[0].endswith(".") else "")
                        self._cache[query_clean] = {"meaning": summary, "source": "Wikipedia"}
                        return summary
        
        # 2. Coba DuckDuckGo Instant Answer API
        ddg_url = f"https://api.duckduckgo.com/?q={encoded}&format=json&no_html=1&skip_disambig=1"
        res_ddg = self._make_request(ddg_url)
        if res_ddg and "AbstractText" in res_ddg and res_ddg["AbstractText"]:
            summary = res_ddg["AbstractText"]
            self._cache[query_clean] = {"meaning": summary, "source": "DuckDuckGo"}
            return summary
            
        return None
    
    def _make_request(self, url):
        """Melakukan HTTP request dengan timeout dan error handling aman."""
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "MiloAI/1.0 (Educational Conversational Agent)"}
            )
            with urllib.request.urlopen(req, timeout=self._timeout, context=self._ssl_context) as response:
                if response.status == 200:
                    data = response.read().decode("utf-8")
                    return json.loads(data)
        except Exception:
            return None
        return None
    
    def _clean_wiktionary_extract(self, text):
        """Membersihkan ekstrak teks dari format Wiktionary dan kamus."""
        lines = text.split("\n")
        meaning_lines = []
        for line in lines:
            line_s = line.strip()
            if not line_s or line_s.startswith("=="):
                continue
            if not any(header in line_s for header in ["Etimologi", "Pengucapan", "Kata turunan", "Terjemahan", "Pencarian"]):
                # Bersihkan nomor definisi & tag awalan (misal '(Kim) ·', '(Nomina)')
                clean_line = re.sub(r'^\d+\.\s*', '', line_s)
                clean_line = re.sub(r'^\([A-Za-z\s,]+\)\s*[·•\-]?\s*', '', clean_line)
                # Bersihkan sitasi kamus
                clean_line = re.split(r'“[^”]+” di Kamus Besar', clean_line)[0]
                clean_line = clean_line.strip().rstrip(";")
                if len(clean_line) > 5 and not clean_line.startswith("Kategori:"):
                    meaning_lines.append(clean_line)
                    if len(meaning_lines) >= 2:
                        break
        return "; ".join(meaning_lines) if meaning_lines else None
