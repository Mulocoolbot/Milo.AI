"""
Milo AI — Response Engine
Otak utama yang menghasilkan respons berdasarkan intent, konteks,
dan personality Milo.
"""

import json
import random
from datetime import datetime
from utils.config import Config


class ResponseEngine:
    """Response Engine — menghasilkan respons yang natural dan kontekstual."""
    
    def __init__(self):
        self._responses = {}
        self._last_responses = {}  # Track respons terakhir per intent (anti-repetisi)
        self._load_responses()
    
    def _load_responses(self):
        """Memuat template respons dari file JSON."""
        try:
            with open(Config.RESPONSES_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                self._responses = data.get("responses", {})
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"[ResponseEngine] Warning: Gagal memuat responses: {e}")
            self._responses = {}
    
    def generate(self, intent_result, context):
        """
        Menghasilkan respons berdasarkan intent dan konteks.
        
        Args:
            intent_result: dict dari IntentRecognizer
            context: dict dari ContextManager.get_context()
        
        Returns:
            string respons final
        """
        intent = intent_result.get("intent", "fallback")
        confidence = intent_result.get("confidence", 0.0)
        
        # Ambil template respons untuk intent ini
        response_templates = self._responses.get(intent, self._responses.get("fallback", []))
        
        if not response_templates:
            return "Hmm, Milo bingung nih 🤔 Coba bilang yang lain ya?"
        
        # Pilih respons (hindari repetisi)
        response = self._select_response(intent, response_templates)
        
        # Substitusi variabel dinamis
        response = self._substitute_variables(response, context)
        
        # Tambahkan personalisasi berdasarkan konteks
        response = self._personalize(response, context, intent)
        
        return response
    
    def _select_response(self, intent, templates):
        """
        Memilih respons dari template, menghindari repetisi.
        Menggunakan weighted random selection.
        """
        if len(templates) == 1:
            return templates[0]
        
        # Hindari respons yang sama dengan terakhir kali
        last_used = self._last_responses.get(intent)
        
        available = [t for t in templates if t != last_used]
        if not available:
            available = templates
        
        # Weighted random — respons yang lebih panjang sedikit lebih diprioritaskan
        # (biasanya lebih kaya konten)
        weights = []
        for template in available:
            weight = 1.0
            # Respons dengan variabel sedikit lebih diprioritaskan (lebih personal)
            if '{' in template:
                weight += 0.3
            # Respons yang lebih panjang sedikit lebih bervariasi
            if len(template) > 50:
                weight += 0.2
            weights.append(weight)
        
        # Normalisasi weights
        total = sum(weights)
        weights = [w / total for w in weights]
        
        # Weighted random selection
        selected = random.choices(available, weights=weights, k=1)[0]
        
        # Simpan sebagai respons terakhir
        self._last_responses[intent] = selected
        
        return selected
    
    def _substitute_variables(self, response, context):
        """Mengganti variabel dinamis dalam template respons."""
        now = datetime.now()
        
        # Variabel yang tersedia
        variables = {
            "{current_time}": now.strftime("%H:%M"),
            "{current_date}": now.strftime("%d %B %Y"),
            "{current_day}": self._get_day_name(now.weekday()),
            "{user_name}": context.get("user_name") or "teman",
            "{milo_name}": Config.MILO_NAME,
            "{turn_count}": str(context.get("turn_count", 0)),
        }
        
        for var, value in variables.items():
            response = response.replace(var, value)
        
        return response
    
    def _personalize(self, response, context, intent):
        """Menambahkan sentuhan personal berdasarkan konteks."""
        user_name = context.get("user_name")
        turn_count = context.get("turn_count", 0)
        sentiment = context.get("sentiment", "neutral")
        
        # Jika sudah tahu nama user, kadang sisipkan nama
        if user_name and random.random() < 0.3 and "{user_name}" not in response:
            # Tambahkan nama di awal atau akhir sesekali
            if random.random() < 0.5:
                if not response.startswith(user_name):
                    response = f"{user_name}, " + response[0].lower() + response[1:]
        
        # Jika percakapan sudah panjang, tambahkan komentar tentang itu sesekali
        if turn_count > 10 and random.random() < 0.1:
            response += f"\n\n(Btw, kita udah ngobrol {turn_count} giliran lho! Seru ya! 🎉)"
        
        return response
    
    def _get_day_name(self, weekday):
        """Mengembalikan nama hari dalam Bahasa Indonesia."""
        days = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
        return days[weekday] if 0 <= weekday <= 6 else "Unknown"
    
    def get_available_intents(self):
        """Mengembalikan daftar intent yang punya template respons."""
        return list(self._responses.keys())
    
    def add_response(self, intent, response_text):
        """Menambahkan template respons baru untuk intent tertentu."""
        if intent not in self._responses:
            self._responses[intent] = []
        self._responses[intent].append(response_text)
    
    def get_response_count(self, intent):
        """Mengembalikan jumlah template respons untuk intent tertentu."""
        return len(self._responses.get(intent, []))
