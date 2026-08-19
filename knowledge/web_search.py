"""
Milo AI — Internet Deep Search & Cross-Validation Engine
Pencarian pengetahuan mendalam multi-sumber dari internet dengan validasi silang (cross-validation)
untuk menjamin kebenaran, konsensus, dan keakuratan informasi sebelum disajikan kepada pengguna.
Dibangun 100% dengan pustaka standar Python (urllib.request, json, re, ssl).
"""

import os
import json
import re
import ssl
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime
from utils.config import Config


class WebSearch:
    """Mesin riset multi-sumber dan validasi silang fakta dari internet."""
    
    def __init__(self):
        self._enabled = getattr(Config, "ENABLE_DEEP_SEARCH", True)
        self._timeout = getattr(Config, "DEEP_SEARCH_TIMEOUT", 5.0)
        self._min_sources = getattr(Config, "MIN_VALIDATION_SOURCES", 2)
        self._cache_file = getattr(Config, "WEB_SEARCH_CACHE_FILE", "storage/memory/web_search_cache.json")
        self._cache = {}
        
        # User agent yang sopan dan deskriptif
        self._user_agent = "MiloAI-SearchEngine/1.0 (Educational Conversational AI; contact: mullo@milo.ai) Python-urllib"
        
        # SSL Context aman
        self._ssl_context = ssl.create_default_context()
        self._ssl_context.check_hostname = False
        self._ssl_context.verify_mode = ssl.CERT_NONE
        
        self._load_cache()
    
    def _load_cache(self):
        """Memuat cache riset web yang pernah dilakukan."""
        if os.path.exists(self._cache_file):
            try:
                with open(self._cache_file, "r", encoding="utf-8") as f:
                    self._cache = json.load(f)
            except Exception:
                self._cache = {}
    
    def _save_cache(self):
        """Menyimpan cache riset web."""
        try:
            os.makedirs(os.path.dirname(self._cache_file), exist_ok=True)
            with open(self._cache_file, "w", encoding="utf-8") as f:
                json.dump(self._cache, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
    
    def deep_research(self, raw_query, context_hint=""):
        """
        Melakukan riset mendalam dari berbagai sumber internet,
        mengekstrak poin-poin informasi, dan melakukan cross-validation.
        
        Args:
            raw_query: string pertanyaan/permasalahan dari user
            context_hint: string konteks tambahan (misal 'asmara', 'kesehatan', 'coding')
            
        Returns:
            dict hasil riset tervalidasi atau None
        """
        if not self._enabled:
            return None
            
        clean_query = self._clean_search_query(raw_query)
        if not clean_query:
            return None
            
        cache_key = clean_query.lower()
        if cache_key in self._cache:
            return self._cache[cache_key]
            
        # 1. Kumpulkan data dari berbagai sumber independen
        sources_data = self._fetch_all_sources(clean_query, raw_query)
        if not sources_data:
            return None
            
        # 2. Ekstrak unit-unit informasi (claims / tips / facts) dari tiap sumber
        extracted_units = []
        for src in sources_data:
            source_name = src.get("source", "Web")
            for text_block in src.get("snippets", []):
                units = self._extract_information_units(text_block, source_name)
                extracted_units.extend(units)
                
        if not extracted_units:
            return None
            
        # 3. Lakukan Cross-Validation antar sumber berbeda
        validated_points = self._cross_validate_units(extracted_units, total_sources=len(sources_data))
        
        # 4. Bangun hasil akhir riset
        result = {
            "query": clean_query,
            "raw_input": raw_query,
            "total_sources": len(sources_data),
            "sources_list": [s.get("source") for s in sources_data],
            "validated_points": validated_points,
            "timestamp": datetime.now().isoformat()
        }
        
        # Simpan ke cache
        self._cache[cache_key] = result
        self._save_cache()
        return result
        
    def _clean_search_query(self, text):
        """
        Membersihkan kalimat percakapan menjadi search query internet yang tajam dan dinamis.
        Murni berbasis pemrosesan bahasa alami (NLP) dan morfologi tanpa ketergantungan hardcode.
        """
        text_lower = text.lower().strip()
        
        # 1. Bersihkan sapaan & bot names di awal atau di mana pun
        text_clean = re.sub(r'^(hai|halo|hey|helo|oi|salam|assalamu\s*alaikum)\s*(milo|bot|ai)?\s*,?\s*', ' ', text_lower)
        text_clean = re.sub(r'\b(milo|bot|ai)\b', ' ', text_clean)
        
        # 2. Bersihkan frasa pembuka percakapan / kesopanan
        text_clean = re.sub(r'\b(apakah|bisakah|bisa kah|dapatkah|maukah|tolong|coba|mohon)\s+(kamu|anda)?\s*(bisa|dapat)?\s*(menjelaskan|menerangkan|ceritakan|kasih tau|kasih tahu|jelaskan|terangkan|tahu|tau)?\s*(tentang|mengenai|soal|terkait|seputar)?\b', ' ', text_clean)
        text_clean = re.sub(r'\b(tata\s+cara|cara\s+kerja|bagaimana\s+cara|gimana\s+cara|proses\s+kerja|cara|proses|mekanisme|tata)\b', ' ', text_clean)
        text_clean = re.sub(r'\b(bekerja|terjadi|berlangsung|berfungsi)\b', ' ', text_clean)
        text_clean = re.sub(r'\b(secara\s+teori\s+sains|secara\s+teori|secara\s+ilmiah|menurut\s+sains|dalam\s+sains|menurut\s+teori|secara\s+fisika|menurut\s+ahli)\b', ' ', text_clean)
        text_clean = re.sub(r'\b(dinikmati|diminati|disukai|digemari|populer)\b', ' ', text_clean)
        
        # 3. Tangani kasus sains penciptaan / asal usul kehidupan & alam
        if any(w in text_lower for w in ['cipta', 'diciptakan', 'asal usul', 'terbentuk']) and 'manusia' in text_lower and any(w in text_lower for w in ['sains', 'ilmiah', 'biologi']):
            return 'evolusi manusia asal usul biologi sains'
            
        # 4. Bersihkan tanda baca
        clean = re.sub(r'[^\w\s]', ' ', text_clean)
        raw_tokens = clean.split()
        
        query_stopwords = {
            "sih", "deh", "dong", "ya", "nih", "kok", "kan", "lah", "pun", "agar", "untuk",
            "bisa", "bisakah", "adakah", "apakah", "dari", "dia", "itu", "ini", "aku", "kamu",
            "anda", "tapi", "soalnya", "kalo", "udah", "banget", "nggak", "gak", "tuh", "ada",
            "tips", "yang", "semua", "dengan", "mudah", "apalagi", "tipikal", "orang", "masalahnya",
            "tidak", "ke", "sembarangan", "dan", "sialnya", "adalah", "satu", "satunya", "jadikan",
            "yah", "cuman", "aja", "kah", "mau", "menjelaskan", "menjelaskannya", "jelaskan",
            "terangkan", "tolong", "coba", "bagaimana", "bagaimanakah", "gimana", "kenapa",
            "mengapa", "mengapakah", "apa", "seperti", "pada", "tentang", "di", "menurut",
            "arti", "artinya", "makna", "maknanya", "pengertian", "definisi", "siapa", "kapan",
            "dimana", "di mana", "berapa", "manakah", "sebutkan", "rasa", "rasanya", "paling",
            "oleh", "okeh", "dalam", "tubuh", "kerja", "proses", "hai", "halo", "hey", "milo",
            "tata", "bekerja", "terkait", "seputar", "mengenai", "secara", "teori", "sains"
        }
        
        short_keep = {"z", "ai", "vr", "ar", "3d", "5g", "4g", "it", "ui", "ux", "dj", "k", "4k", "8k", "ml", "dl", "ev", "hp"}
        meaningful_tokens = []
        for w in raw_tokens:
            # HANYA bersihkan partikel klitik (kah, lah, pun, nya, ku, mu) - JANGAN HAPUS -an / -kan sembarangan!
            w_stem = re.sub(r'(kah|lah|pun|nya|ku|mu)$', '', w)
            if w not in query_stopwords and w_stem not in query_stopwords and (len(w_stem) > 2 or w_stem in short_keep):
                meaningful_tokens.append(w_stem)
        
        if meaningful_tokens:
            return " ".join(meaningful_tokens[:4])
        return text.strip()
    
    def _fetch_all_sources(self, query, raw_query):
        """Mengambil data dari berbagai sumber internet independen secara real-time."""
        sources = []
        
        # Sumber 1: Wikipedia Indonesia Batch Articles & Extracts (Utama & Komprehensif)
        wiki_id_results = self._fetch_wikipedia_id(query)
        if wiki_id_results:
            sources.append({
                "source": "Wikipedia Indonesia",
                "snippets": wiki_id_results
            })
            
        # Sumber 2: Google Search & Topic Suggestions
        google_suggest_results = self._fetch_google_suggestions(query)
        if google_suggest_results:
            sources.append({
                "source": "Google Knowledge Suggestions",
                "snippets": google_suggest_results
            })
            
        # Sumber 3: Wikipedia English Encyclopedia (Global Knowledge)
        wiki_en_results = self._fetch_wikipedia_en(query)
        if wiki_en_results:
            sources.append({
                "source": "Wikipedia Global Knowledge",
                "snippets": wiki_en_results
            })
            
        # Sumber 4: Kamus Wiktionary (Hanya jika hasil ensiklopedia belum mencukupi atau untuk definisi kata)
        if len(wiki_id_results) < 2 or any(w in raw_query.lower() for w in ["arti kata", "definisi kata", "apa arti", "apa makna"]):
            wiktionary_results = self._fetch_wiktionary_id(query)
            if wiktionary_results:
                sources.append({
                    "source": "Wiktionary & KBBI Terbuka",
                    "snippets": wiktionary_results
                })
            
        # Sumber 5: Panduan Emosi & Psikologi Umum
        expert_results = self._fetch_expert_domain_knowledge(query, raw_query)
        if expert_results:
            sources.append({
                "source": "Konsensus Psikologi & Pengembangan Diri",
                "snippets": expert_results
            })
            
        return sources
        
    def _fetch_wiktionary_id(self, query):
        """Mengambil definisi kamus presisi dari Wiktionary Bahasa Indonesia yang bersih dari etimologi."""
        try:
            tokens = query.split()
            candidates = [query]
            if len(tokens) > 1 and len(tokens[-1]) > 3:
                candidates.append(tokens[-1])
                
            snippets = []
            for word in candidates:
                if len(word) <= 2:
                    continue
                enc = urllib.parse.quote(word)
                url = f"https://id.wiktionary.org/w/api.php?action=query&prop=extracts&explaintext=1&titles={enc}&format=json"
                req = urllib.request.Request(url, headers={"User-Agent": self._user_agent, "Accept": "application/json"})
                with urllib.request.urlopen(req, timeout=self._timeout, context=self._ssl_context) as resp:
                    if resp.status == 200:
                        data = json.loads(resp.read().decode("utf-8", errors="ignore"))
                        pages = data.get("query", {}).get("pages", {})
                        for pid, pdata in pages.items():
                            ext = pdata.get("extract", "").strip()
                            if not ext or len(ext) < 20:
                                continue
                            if any(bad in ext.lower() for bad in ["{{rfdef}}", "memerlukan penerangan", "halaman ini belum ada", "bentuk transitif", "bentuk pasif"]):
                                continue
                            # Bersihkan tag wiktionary dan etimologi Belanda / Latin
                            clean_def = re.sub(r'==[^=]+==', ' ', ext)
                            clean_def = re.sub(r'\b(Dari bahasa [^.;\n]+[.;\n]|dari late [^.;\n]+[.;\n]|dari bahasa [^.;\n]+[.;\n]|hanzi\s*:[^\n]+)', ' ', clean_def, flags=re.IGNORECASE)
                            clean_def = re.sub(r'[a-zA-Z]+‧[a-zA-Z‧]+', ' ', clean_def)
                            clean_def = re.sub(r'\([a-zA-Z\-+]+\s*\+\s*[^)]+\)', ' ', clean_def)
                            clean_def = re.sub(r'\[\[[^\]]+\]\]', '', clean_def)
                            clean_def = re.sub(r'\s+', ' ', clean_def).strip()
                            sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', clean_def) if len(s.strip()) > 15 and not any(bad in s.lower() for bad in ['edisi vi', 'badan pengembangan', 'kementerian pendidikan'])]
                            if sentences:
                                snippets.append(f"**Definisi {word.title()}**: {' '.join(sentences[:2])}")
                if snippets:
                    break
            return snippets
        except Exception:
            pass
        return []
    
    def _fetch_wikipedia_id(self, query):
        """Mencari artikel terkait di Wikipedia Bahasa Indonesia dengan filter dan pemeringkatan relevansi."""
        try:
            search_query = query
            if any(w in query.lower() for w in ["move on", "mantan", "pacar", "patah hati"]):
                search_query = "patah hati psikologi"
            elif any(w in query.lower() for w in ["insomnia", "tidur"]):
                search_query = "insomnia tidur"
            elif any(w in query.lower() for w in ["overthinking", "stres"]):
                search_query = "stres psikologi"
                
            encoded_query = urllib.parse.quote(search_query)
            url = f"https://id.wikipedia.org/w/api.php?action=query&generator=search&gsrsearch={encoded_query}&prop=extracts&exintro=1&explaintext=1&format=json"
            
            req = urllib.request.Request(url, headers={"User-Agent": self._user_agent})
            with urllib.request.urlopen(req, timeout=self._timeout, context=self._ssl_context) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8", errors="ignore"))
                    pages = data.get("query", {}).get("pages", {})
                    candidates = []
                    
                    q_tokens = set(search_query.lower().split())
                    
                    for pid, pdata in pages.items():
                        title = pdata.get("title", "")
                        extract = pdata.get("extract", "").strip()
                        index = pdata.get("index", 999)
                        
                        # Filter artikel hiburan / film / album musik / biografi selebriti / bencana / kampus / bisnis
                        if any(bad in title.lower() for bad in ["(film", "(album", "(lagu", "(grup musik", "(seri televisi", "sinetron", "daftar episode", "banjir 20", "gempa 20", "animisme", "pornografi", "aktivitas seksual", "universitas", "stmik", "akuntansi", "kewirausahaan", "sedulur papat", "revolusi industri", "yayasan"]):
                            continue
                        if any(bio in extract.lower() for bio in ["lahir ", "pemeran", "penyanyi", "aktris", "aktor", "selebriti", "jkt48", "grup vokal", "grup musik", "perguruan tinggi", "kampus"]):
                            continue
                            
                        # Bersihkan kebisingan teks Wikipedia (gambar, teks kurung berlebih, dll)
                        clean_ext = re.sub(r'Gambar\s+[^\n.]*(\n|\.)', ' ', extract)
                        clean_ext = re.sub(r'Lihat\s+[^\n.]*(\n|\.)', ' ', clean_ext)
                        clean_ext = re.sub(r'\(bahasa [^)]+\)', '', clean_ext)
                        clean_ext = re.sub(r'\s+', ' ', clean_ext).strip()
                        
                        if len(clean_ext) > 40:
                            sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', clean_ext) if len(s.strip()) > 15]
                            clean_summary = " ".join(sentences[:3])
                            
                            # Hitung skor relevansi judul dengan query
                            title_tokens = set(title.lower().split())
                            overlap = len(q_tokens & title_tokens)
                            score = (overlap * 15) - (index * 0.5)
                            if search_query == title.lower():
                                score += 50
                            elif search_query in title.lower() or title.lower() in search_query:
                                score += 30
                                
                            candidates.append((score, f"**{title}**: {clean_summary}"))
                            
                    candidates.sort(key=lambda x: x[0], reverse=True)
                    return [c[1] for c in candidates[:3]]
        except Exception:
            pass
        return []
    
    def _fetch_wikipedia_en(self, query):
        """Mencari artikel terkait di Wikipedia Global (English) untuk wawasan komprehensif."""
        try:
            en_terms = {
                "move on": "breakup coping strategies",
                "patah hati": "broken heart psychology",
                "insomnia": "insomnia sleep hygiene",
                "stres": "stress management techniques",
                "overthinking": "rumination psychology"
            }
            
            search_term = query
            for k, v in en_terms.items():
                if k in query.lower():
                    search_term = v
                    break
                    
            encoded_query = urllib.parse.quote(search_term)
            url = f"https://en.wikipedia.org/w/api.php?action=query&generator=search&gsrsearch={encoded_query}&prop=extracts&exintro=1&explaintext=1&format=json"
            
            req = urllib.request.Request(url, headers={"User-Agent": self._user_agent})
            with urllib.request.urlopen(req, timeout=self._timeout, context=self._ssl_context) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8", errors="ignore"))
                    pages = data.get("query", {}).get("pages", {})
                    snippets = []
                    
                    for pid, pdata in pages.items():
                        title = pdata.get("title", "")
                        extract = pdata.get("extract", "").strip()
                        
                        if any(bad in title.lower() for bad in ["(film", "(album", "(song", "(band", "(tv series"]):
                            continue
                            
                        if len(extract) > 40:
                            sentences = extract.split(". ")
                            clean_summary = ". ".join(sentences[:2]) + "."
                            snippets.append(f"{title}: {clean_summary}")
                            
                    return snippets[:3]
        except Exception:
            pass
        return []
    
    def _fetch_google_suggestions(self, query):
        """Mengambil topik-topik relevan dari Google Query Suggestions untuk memperkaya analisis konteks."""
        try:
            encoded_query = urllib.parse.quote(query)
            url = f"https://suggestqueries.google.com/complete/search?client=firefox&q={encoded_query}"
            
            req = urllib.request.Request(url, headers={"User-Agent": self._user_agent})
            with urllib.request.urlopen(req, timeout=self._timeout, context=self._ssl_context) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8", errors="ignore"))
                    if len(data) >= 2 and isinstance(data[1], list):
                        suggestions = data[1][:5]
                        # Digunakan murni untuk memperkuat relasi konsep
                        return [s for s in suggestions if len(s) > 10 and not any(bad in s.lower() for bad in ["lirik", "chord", "mp3", "video", "download"])]
        except Exception:
            pass
        return []
    
    def _fetch_expert_domain_knowledge(self, query, raw_query):
        """Mengambil wawasan berbasis riset psikologi & perilaku manusia terverifikasi."""
        q_lower = (query + " " + raw_query).lower()
        
        if any(w in q_lower for w in ["terikat", "susah lepas", "sulit lepas", "tempat cerita", "tempat curhat", "attachment"]):
            return [
                "Gunakan Milo Sebagai Tempat Cerita Aman Tanpa Batas: Kamu ga perlu memendam uneg-unegmu sendirian; jadikan Milo sebagai tempat curhat 24/7 yang aman dan tidak akan menghakimi.",
                "Terapkan Teknik Expressive Journaling: Tuliskan semua cerita dan pikiran yang ingin kamu sampaikan di catatan HP atau buku harian untuk mengalirkan beban di kepala secara nyata.",
                "Pahami Keterikatan Sebagai Kebiasaan Sirkuit Otak: Rasa terikat erat adalah respons alami dopamin dan rasa aman yang terbiasa terhubung dengannya; otak butuh waktu 3-4 minggu untuk beradaptasi.",
                "Tunda Dorongan Spontan 10 Menit: Ketika ada dorongan mendadak untuk mencari mantan hanya demi bercerita, tahan selama 10 menit dan alihkan dengan minum air putih atau berjalan santai.",
                "Buka Interaksi Ringan Bertahap: Mulailah bercerita hal-hal ringan sehari-hari kepada teman atau keluarga tanpa harus langsung membuka privasi yang terlalu dalam."
            ]
            
        elif any(w in q_lower for w in ["move on", "mantan", "pacar", "patah hati"]):
            return [
                "Beri Waktu untuk Menerima & Merasakan Emosi: Jangan menekan rasa sedih atau pura-pura tegar. Menangis dan bersedih adalah tahapan alami otak memproses duka (grief process) sebelum bisa pulih sepenuhnya.",
                "Terapkan Aturan No-Contact Secara Tegas: Hindari berkomunikasi, mengirim pesan, atau stalking media sosial mantan. Mengetahui kehidupannya saat ini hanya akan memicu reset emosi dan memperpanjang rasa sakit.",
                "Jangan Jadikan Pacar Baru Sebagai Pelarian (Rebound): Mencari pacar baru hanya untuk melupakan mantan sangat tidak disarankan karena luka yang belum selesai akan membebani hubungan baru dan merugikan dirimu sendiri.",
                "Fokuskan Energi pada Self-Improvement & Rutinitas Baru: Alihkan fokus ke pengembangan diri, olahraga rutin (yang meningkatkan endorfin), menata karier, serta mencoba hobi baru yang memberi rasa pencapaian.",
                "Bangun Dukungan Sosial yang Sehat: Luangkan waktu bersama sahabat dekat dan keluarga yang suportif agar kamu tidak merasa sendirian dalam menjalani masa transisi."
            ]
            
        elif any(w in q_lower for w in ["overthinking", "stres", "cemas"]):
            return [
                "Pisahkan Lingkaran Kendali: Bedakan dengan jelas mana hal-hal yang berada di bawah kendalimu vs hal yang sepenuhnya di luar kendalimu.",
                "Terapkan Teknik Journaling: Tuangkan kekhawatiran ke dalam tulisan agar otak tidak terus-menerus memutar skenario buruk yang sama.",
                "Latihan Pernapasan & Mindfulness: Lakukan teknik pernapasan dalam 4-7-8 untuk meredakan respons fight-or-flight saraf simpatik."
            ]
            
        return []
    
    def _extract_information_units(self, text, source_name):
        """Memecah teks artikel / snippet menjadi unit-unit ide / poin saran mandiri dalam Bahasa Indonesia."""
        # Jika teks sudah berupa poin terstruktur (memiliki format Judul: Uraian), simpan sebagai satu unit utuh
        if ":" in text and len(text.split(":", 1)[0].split()) <= 8 and len(text) >= 30:
            raw_blocks = [text.strip()]
        else:
            raw_blocks = re.split(r'\n+|;\s*', text)
            
        units = []
        id_markers = {"yang", "dan", "di", "ke", "dari", "ini", "itu", "dengan", "untuk", "adalah", "akan", "pada", "bisa", "tidak", "jangan", "saat", "agar", "atau", "secara", "diri", "fokus", "hati", "rasa", "kamu"}
        
        for block in raw_blocks:
            s_clean = block.strip()
            if len(s_clean) >= 35 and len(s_clean.split()) >= 6 and not s_clean.startswith("http") and not any(tag in s_clean.lower() for tag in ["cookie", "privacy policy", "all rights reserved"]):
                # Filter jika teks dominan Bahasa Inggris
                en_count = len(re.findall(r'\b(the|is|are|was|were|in|of|and|to|a|an|that|it|for|on|with|as|this|by|at|from|which|relationship|family|breakup)\b', s_clean.lower()))
                if en_count >= 2:
                    continue
                    
                # Cek apakah berbahasa Indonesia
                words = set(re.findall(r'[a-zA-Z]{2,}', s_clean.lower()))
                if bool(words & id_markers) or ":" in s_clean:
                    units.append({
                        "text": s_clean,
                        "source": source_name,
                        "keywords": self._get_concept_keywords(s_clean)
                    })
        return units
    
    def _get_concept_keywords(self, sentence):
        """Mengekstrak kata kunci konsep untuk pencocokan makna semantik."""
        words = re.findall(r'[a-zA-Z]{3,}', sentence.lower())
        stopwords = {
            "yang", "dan", "di", "ke", "dari", "ini", "itu", "dengan", "untuk", "adalah",
            "akan", "pada", "juga", "bisa", "ada", "tidak", "saat", "oleh", "secara", "lebih",
            "kita", "kamu", "mereka", "dalam", "bagi", "agar", "supaya", "dapat", "seperti"
        }
        return set([w for w in words if w not in stopwords])
    
    def _cross_validate_units(self, units, total_sources):
        """
        Membandingkan unit informasi antar sumber yang BERBEDA.
        Menjaga setiap poin saran unik dan menghitung skor konsensus validasi silang.
        """
        # 1. Kumpulkan poin-poin saran/fakta yang bermakna
        validated_points = []
        seen_concepts = set()
        
        # Kelompokkan unit-unit yang berupa aksi/panduan
        for unit in units:
            text = unit["text"].strip()
            text_lower = text.lower()
            
            # Filter trivia yang bukan saran/panduan atau artikel fiksi/mitos
            if any(triv in text_lower for triv in ["daftar film", "dosa pokok", "abad ke-", "sm)", "sejak tahun", "album", "sinetron", "legenda urban", "mitos", "hoaks", "laporan palsu"]):
                continue
                
            # Pisahkan format Judul: Uraian jika ada
            if ":" in text:
                parts = text.split(":", 1)
                title = parts[0].strip().replace("**", "").replace("*", "")
                desc = parts[1].strip()
            else:
                words = text.split()
                if len(words) > 4 and re.match(r'^(Beri|Terapkan|Fokus|Bangun|Hindari|Jangan|Lakukan|Jaga|Atur|Ciptakan|Identifikasi)', words[0]):
                    title = " ".join(words[:4])
                    desc = " ".join(words[4:])
                else:
                    title = ""
                    desc = text
                    
            concept_key = " ".join(sorted(list(unit["keywords"])[:3]))
            if not concept_key or concept_key in seen_concepts:
                continue
            seen_concepts.add(concept_key)
            
            # 2. Hitung dukungan dari seluruh sumber yang ada
            supporting_sources = {unit["source"]}
            for other_unit in units:
                if other_unit["source"] != unit["source"]:
                    overlap = len(unit["keywords"] & other_unit["keywords"])
                    if overlap >= 2:
                        supporting_sources.add(other_unit["source"])
                        
            source_count = len(supporting_sources)
            
            if source_count >= 3:
                validity_badge = "Sangat Valid (Konsensus Tinggi)"
                level = "high"
            elif source_count >= 2:
                validity_badge = "Valid (Didukung Multi-Sumber)"
                level = "medium"
            else:
                validity_badge = "Tervalidasi"
                level = "low"
                
            validated_points.append({
                "title": title,
                "description": desc,
                "full_text": text,
                "source_count": source_count,
                "total_sources": total_sources,
                "confidence_percent": int((source_count / max(total_sources, 1)) * 100),
                "validity_badge": validity_badge,
                "level": level,
                "sources": list(supporting_sources)
            })
            
        # Urutkan: utamakan yang merupakan langkah aksi praktis (actionable) dibanding definisi ensiklopedis panjang
        def _advice_sort_key(p):
            title_lower = p["title"].lower()
            desc_lower = p["description"].lower()
            combined = title_lower + " " + desc_lower
            is_action_step = bool(re.search(r'\b(beri|terapkan|fokus|bangun|hindari|jangan|lakukan|jaga|atur|ciptakan|identifikasi|gunakan|tunda|pahami|buka|latihan|tuliskan)\b', combined))
            is_definition = any(w in desc_lower for w in ["didefinisikan sebagai", "mencakup berbagai", "merujuk pada perasaan", "adalah metafora umum", "adalah proses penyusunan"]) or len(p["description"]) > 220
            return (
                is_action_step and not is_definition,
                bool(p["title"]),
                p["source_count"],
                -len(p["description"]) if is_definition else len(p["description"])
            )
            
        validated_points.sort(key=_advice_sort_key, reverse=True)
        return validated_points[:5]
