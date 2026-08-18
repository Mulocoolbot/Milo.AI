"""
Milo AI — Semantic Word Bank & Lexicon Engine
Bank Kata Semantik yang mengklasifikasikan kata berdasarkan kelas kata (POS),
domain makna (semantic field), polaritas sentimen, serta mendukung Word Sense Disambiguation (WSD)
untuk kata-kata yang memiliki lebih dari satu arti (polisemi).
"""

import json
import os
import re
import random
from utils.config import Config


class WordBank:
    """Semantic Word Bank & Lexicon Engine untuk generasi bahasa alami Milo AI."""
    
    def __init__(self):
        self._lexicon = {}
        self._polysemy = {}
        self._collocations = {}
        self._learned_words = {}
        self._init_base_lexicon()
        self._init_polysemy()
        self._load_learned_words()
    
    def _init_base_lexicon(self):
        """Inisialisasi leksikon dasar Bahasa Indonesia terstruktur."""
        self._lexicon = {
            # === NOUNS (Kata Benda) ===
            "noun": {
                "general": ["hal", "kabar", "cerita", "pikiran", "waktu", "hari", "momen", "langkah", "kondisi", "ruang", "topik", "sudut pandang"],
                "tech": ["arsitektur", "kode", "program", "koding", "logika", "modul", "algoritma", "sistem", "data", "teknologi", "komputer", "fitur", "aplikasi"],
                "emotion": ["beban", "uneg-uneg", "perasaan", "semangat", "kebahagiaan", "kekhawatiran", "kecemasan", "ketenangan", "energi", "doa"],
                "relation": ["teman", "sahabat", "orang", "gebetan", "seseorang", "teman sekelas", "pasangan", "keluarga"],
                "health": ["rumah sakit", "ruang rawat inap", "kesehatan", "kondisi", "perawatan", "dokter", "obat", "pemulihan", "musibah", "kecelakaan"],
                "education": ["kuliah", "tugas", "skripsi", "pelajaran", "kampus", "jurusan", "ilmu", "materi"],
                "food": ["makanan", "kuliner", "sarapan", "rendang", "nasi padang", "sate", "bakso", "nasi goreng", "kopi"]
            },
            # === VERBS (Kata Kerja) ===
            "verb": {
                "general": ["ngobrol", "berbagi", "mendengarkan", "memahami", "membahas", "melihat", "mencoba", "memulai", "melanjutkan", "berpikir", "menjelaskan"],
                "tech": ["ngoding", "mengembangkan", "menyempurnakan", "membedah", "mengurai", "membangun", "merancang", "mengecek", "memperbaiki", "mengoptimalkan"],
                "emotion": ["merasa", "kepikiran", "curhat", "khawatir", "cemas", "tenang", "berharap", "menemani", "mendoakan", "menguatkan"],
                "health": ["dirawat", "menjenguk", "sembuh", "pulih", "istirahat", "menangani", "menjaga"],
                "relation": ["naksir", "menyukai", "mengenal", "bertemu", "rindu", "mengingat", "berkomunikasi", "peduli"],
                "action_support": ["membantu", "mendampingi", "menemani", "mencari solusi", "berdiskusi"]
            },
            # === ADJECTIVES (Kata Sifat) ===
            "adjective": {
                "positive": ["hebat", "luar biasa", "keren", "seru", "semangat", "menarik", "prima", "senang", "bahagia", "lega", "stabil", "terbuka", "aman"],
                "empathetic": ["hangat", "tulus", "peduli", "sabar", "objektif", "setia", "siap sedia"],
                "negative_mild": ["bingung", "pusing", "overthinking", "bimbang", "berat", "penuh", "mentok", "sulit", "rumit", "campur aduk"],
                "negative_severe": ["cemas", "khawatir", "prihatin", "sedih", "kesel", "kecewa", "lelah", "down"],
                "complexity": ["modular", "kompleks", "terstruktur", "presisi", "fleksibel", "dinamis", "terpadu"]
            },
            # === ADVERBS (Kata Keterangan) ===
            "adverb": {
                "degree": ["banget", "sangat", "cukup", "terlalu", "sedikit", "sepenuhnya", "benar-benar", "sungguh"],
                "manner": ["pelan-pelan", "satu per satu", "secara modular", "dengan seksama", "langsung", "bersama-sama", "setia"],
                "time": ["sekarang", "saat ini", "tadi", "nanti", "segera", "selalu", "kapan saja", "hari ini"]
            },
            # === INTERJECTIONS & CONVERSATIONAL CONNECTORS ===
            "interjection": {
                "friendly": ["Wah", "Hai", "Halo", "Yeay", "Mantap", "Siap", "Tentu"],
                "empathy": ["Ya ampun", "Aduh", "Turut prihatin", "Peluk hangat", "Semangat ya", "Tenang"],
                "clarification": ["Maksud Milo", "Eh maaf ya", "Boleh luruskan", "Mari kita bedah"]
            },
            # === EMPATHY & VALIDATION PHRASES (Frasa Pembangun Empati) ===
            "empathy_phrase": [
                "Milo paham banget perasaanmu",
                "Wajar banget kalau kamu merasa begitu",
                "Ruang ini aman buat kamu tumpahkan semuanya",
                "Kamu ga perlu memendam uneg-uneg sendirian",
                "Milo selalu siap mendengarkan tanpa menghakimi",
                "Kadang kita butuh waktu sejenak untuk menarik napas",
                "Kehadiran dan kepedulianmu pasti sangat berarti"
            ],
            # === REASONING & ADVICE PHRASES (Frasa Penalaran & Solusi) ===
            "reasoning_phrase": [
                "Saran dari Milo: coba urai masalah ini secara modular",
                "Kita bisa petakan mana hal yang paling mendesak untuk diselesaikan",
                "Dua kepala berpikir selalu lebih baik dari satu",
                "Fokus pada langkah kecil yang bisa diambil hari ini",
                "Pisahkan antara hal yang bisa kamu kontrol dan yang di luar kendali"
            ]
        }
    
    def _init_polysemy(self):
        """
        Inisialisasi Bank Kata Polisemi (kata dengan banyak makna)
        beserta kata kunci konteks untuk Word Sense Disambiguation (WSD).
        """
        self._polysemy = {
            "bisa": {
                "ability": {
                    "meaning": "dapat / mampu / sanggup melakukan sesuatu",
                    "pos": "verb",
                    "domain": "action",
                    "context_clues": ["koding", "coding", "bantu", "ngobrol", "belajar", "selesai", "kerja", "bikin", "buat", "lakukan", "bicara", "paham", "jalan"]
                },
                "poison": {
                    "meaning": "zat racun yang dikeluarkan hewan (seperti ular/kalajengking)",
                    "pos": "noun",
                    "domain": "health",
                    "context_clues": ["ular", "racun", "patuk", "gigit", "hewan", "berbisa", "antiracun", "serangan", "darah", "mati"]
                }
            },
            "tahu": {
                "knowledge": {
                    "meaning": "mengerti / mengetahui / paham akan suatu hal",
                    "pos": "verb",
                    "domain": "cognition",
                    "context_clues": ["ga", "nggak", "soal", "tentang", "milo", "kamu", "info", "kabar", "maksud", "arti", "makna", "nama", "ilmu"]
                },
                "food": {
                    "meaning": "makanan olahan dari kedelai yang gurih",
                    "pos": "noun",
                    "domain": "food",
                    "context_clues": ["makan", "tempe", "goreng", "enak", "kedelai", "lauk", "rebus", "pedas", "warung", "resto", "sarapan"]
                }
            },
            "bunga": {
                "feeling": {
                    "meaning": "perasaan senang, berbunga-bunga, atau kasmaran",
                    "pos": "noun",
                    "domain": "romance",
                    "context_clues": ["hati", "berbunga", "senang", "naksir", "cinta", "bahagia", "kepikiran", "dia", "gebetan", "suka"]
                },
                "plant": {
                    "meaning": "bagian tanaman yang indah dan berwarna-warni",
                    "pos": "noun",
                    "domain": "nature",
                    "context_clues": ["taman", "mawar", "melati", "indah", "wangi", "mekar", "tumbuh", "tanaman", "pot", "kebun"]
                },
                "finance": {
                    "meaning": "imbalan jasa pinjaman uang atau deposito di bank",
                    "pos": "noun",
                    "domain": "finance",
                    "context_clues": ["bank", "pinjaman", "persen", "uang", "kredit", "angsuran", "cicilan", "bunga pinjaman", "biaya"]
                }
            },
            "kabur": {
                "escape": {
                    "meaning": "melarikan diri atau pergi diam-diam",
                    "pos": "verb",
                    "domain": "action",
                    "context_clues": ["lari", "pergi", "menghilang", "takut", "polisi", "kejaran", "malam", "rumah", "kabur dari"]
                },
                "blurry": {
                    "meaning": "kurang jelas, buram, atau tidak fokus (pandangan)",
                    "pos": "adjective",
                    "domain": "perception",
                    "context_clues": ["mata", "kacamata", "lihat", "fokus", "gambar", "buram", "penglihatan", "layar", "tulisan"]
                }
            },
            "rawat": {
                "hospital": {
                    "meaning": "perawatan medis atau rawat inap di rumah sakit",
                    "pos": "verb",
                    "domain": "health",
                    "context_clues": ["inap", "ruang", "rumah sakit", "dokter", "sembuh", "sakit", "pasien", "kamar", "kecelakaan", "medis", "obat"]
                },
                "maintenance": {
                    "meaning": "menjaga, merawat, atau memelihara benda/hewan",
                    "pos": "verb",
                    "domain": "daily_life",
                    "context_clues": ["kucing", "tanaman", "wajah", "kulit", "motor", "mobil", "barang", "rumah", "bunga"]
                }
            }
        }
    
    def _load_learned_words(self):
        """Memuat kata-kata baru yang dipelajari selama percakapan."""
        try:
            if os.path.exists(Config.WORD_BANK_FILE):
                with open(Config.WORD_BANK_FILE, "r", encoding="utf-8") as f:
                    self._learned_words = json.load(f)
        except Exception as e:
            self._learned_words = {}
    
    def save_learned_words(self):
        """Menyimpan kata-kata baru ke penyimpanan persisten."""
        try:
            Config.ensure_directories()
            with open(Config.WORD_BANK_FILE, "w", encoding="utf-8") as f:
                json.dump(self._learned_words, f, ensure_ascii=False, indent=2)
        except Exception as e:
            pass
    
    def disambiguate(self, word, context_words):
        """
        Word Sense Disambiguation (WSD):
        Mendeteksi arti dan makna kata polisemi berdasarkan kata-kata sekitar dalam konteks.
        
        Args:
            word: string kata yang ingin dicek
            context_words: list of string kata-kata konteks percakapan
            
        Returns:
            dict sense terbaik berisi meaning, pos, domain, score
        """
        word_lower = word.lower().strip()
        if word_lower not in self._polysemy:
            return None
            
        senses = self._polysemy[word_lower]
        context_set = {w.lower().strip() for w in context_words}
        
        best_sense_key = None
        best_score = -1
        
        for sense_key, sense_data in senses.items():
            clues = set(sense_data.get("context_clues", []))
            matches = context_set & clues
            score = len(matches)
            
            if score > best_score:
                best_score = score
                best_sense_key = sense_key
                
        # Jika tidak ada petunjuk cocok, pilih sense pertama sebagai default
        if not best_sense_key:
            best_sense_key = list(senses.keys())[0]
            
        result = senses[best_sense_key].copy()
        result["sense_key"] = best_sense_key
        result["match_confidence"] = best_score
        return result
    
    def learn_word(self, word, pos="noun", domain="general", meaning="", sentiment=0.0):
        """
        Menambahkan kata baru ke Bank Kata secara dinamis.
        """
        word_clean = word.lower().strip()
        if not word_clean or len(word_clean) < 2:
            return
            
        entry = {
            "word": word_clean,
            "pos": pos,
            "domain": domain,
            "meaning": meaning,
            "sentiment": sentiment,
            "learned_at": os.path.getmtime(Config.WORD_BANK_FILE) if os.path.exists(Config.WORD_BANK_FILE) else 0
        }
        
        self._learned_words[word_clean] = entry
        
        # Masukkan ke bucket lexicon aktif
        if pos not in self._lexicon:
            self._lexicon[pos] = {}
            
        if isinstance(self._lexicon[pos], dict):
            if domain not in self._lexicon[pos]:
                self._lexicon[pos][domain] = []
            if word_clean not in self._lexicon[pos][domain]:
                self._lexicon[pos][domain].append(word_clean)
        elif isinstance(self._lexicon[pos], list):
            if word_clean not in self._lexicon[pos]:
                self._lexicon[pos].append(word_clean)
                
        self.save_learned_words()
    
    def get_words(self, pos, domain=None):
        """Mengambil daftar kata dari Bank Kata berdasarkan POS dan domain."""
        if pos not in self._lexicon:
            return []
            
        bucket = self._lexicon[pos]
        if isinstance(bucket, list):
            return bucket.copy()
            
        if isinstance(bucket, dict):
            if domain and domain in bucket:
                return bucket[domain].copy()
            # Gabungkan semua domain jika domain tidak dispesifikasikan
            all_words = []
            for sub_list in bucket.values():
                if isinstance(sub_list, list):
                    all_words.extend(sub_list)
            return all_words
            
        return []
    
    def sample_word(self, pos, domain=None, default=""):
        """Mengambil satu kata acak dari kategori tertentu."""
        words = self.get_words(pos, domain)
        return random.choice(words) if words else default
    
    def get_word_count(self):
        """Mengembalikan total kata dalam Bank Kata."""
        total = 0
        for pos, bucket in self._lexicon.items():
            if isinstance(bucket, list):
                total += len(bucket)
            elif isinstance(bucket, dict):
                for sub in bucket.values():
                    if isinstance(sub, list):
                        total += len(sub)
        total += len(self._learned_words)
        return total
