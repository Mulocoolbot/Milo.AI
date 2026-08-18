"""
Milo AI — Kelas Utama
Kelas yang menyatukan semua modul dan mengorkestrasikan
alur percakapan dari input hingga output.

Pipeline: Input -> Preprocess -> Tokenize -> Recognize Intent 
          -> Generate Response -> Apply Personality -> Output
"""

import sys
import os

# Tambahkan root directory ke path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.preprocessor import Preprocessor
from core.tokenizer import Tokenizer
from core.intent_recognizer import IntentRecognizer
from core.response_engine import ResponseEngine
from core.context_manager import ContextManager
from knowledge.knowledge_base import KnowledgeBase
from knowledge.memory import Memory
from personality.personality import Personality
from utils.config import Config
from utils.logger import MiloLogger


class Milo:
    """
    Milo AI — Sistem AI Percakapan yang dibangun dari scratch.
    
    Menyatukan semua komponen:
    - Preprocessor: membersihkan input
    - Tokenizer: memecah teks menjadi token
    - IntentRecognizer: mengenali maksud user
    - ResponseEngine: menghasilkan respons
    - ContextManager: mengelola konteks percakapan
    - KnowledgeBase: basis pengetahuan
    - Memory: sistem memori (short-term & long-term)
    - Personality: kepribadian dan emosi
    """
    
    def __init__(self):
        """Inisialisasi semua modul Milo."""
        # Pastikan direktori ada
        Config.ensure_directories()
        
        # Inisialisasi modul-modul
        self.preprocessor = Preprocessor()
        self.tokenizer = Tokenizer()
        self.intent_recognizer = IntentRecognizer()
        self.response_engine = ResponseEngine()
        self.context_manager = ContextManager()
        self.knowledge_base = KnowledgeBase()
        self.memory = Memory()
        self.personality = Personality()
        self.logger = MiloLogger()
        
        # Load user profile dari memory
        saved_name = self.memory.get_user_info("name")
        if saved_name:
            self.context_manager.set_user_name(saved_name)
        
        self.logger.info("Milo AI initialized successfully! 🧠✨")
    
    def chat(self, user_input):
        """
        Proses input user dan hasilkan respons.
        Ini adalah method utama yang mengorkestrasikan semua modul.
        
        Args:
            user_input: string input dari user
        
        Returns:
            string respons dari Milo
        """
        if not user_input or not user_input.strip():
            return "Hmm, kamu nggak bilang apa-apa nih 🤔 Coba ketik sesuatu ya!"
        
        # Log input user
        self.logger.log_conversation("user", user_input)
        
        # === Step 1: Preprocessing ===
        preprocessed = self.preprocessor.preprocess(user_input)
        self.logger.debug("Preprocessed", {
            "original": preprocessed["original"],
            "final": preprocessed.get("final", ""),
        })
        
        # === Step 2: Tokenization ===
        tokenized = self.tokenizer.tokenize(preprocessed)
        self.logger.debug("Tokenized", {
            "words": tokenized["words"],
            "filtered": tokenized["filtered"],
        })
        
        # === Step 3: Intent Recognition ===
        intent_result = self.intent_recognizer.recognize(tokenized, preprocessed)
        self.logger.debug("Intent recognized", intent_result)
        
        # === Step 4: Context-aware adjustments ===
        intent_result = self._apply_context_adjustments(intent_result, self.context_manager.get_context(), preprocessed)
        
        # Re-fetch context after adjustments (name may have been set)
        context = self.context_manager.get_context()
        
        # === Step 5: Response Generation ===
        response = self.response_engine.generate(
            intent_result=intent_result,
            context=context,
            preprocessed=preprocessed,
            knowledge_base=self.knowledge_base,
            memory=self.memory,
            context_manager=self.context_manager
        )
        
        # === Step 6: Personality Processing ===
        response = self.personality.process(response, intent_result["intent"], context)
        
        # === Step 7: Post-processing ===
        response = self._post_process(response, intent_result, preprocessed)
        
        # === Step 8: Update Context & Memory ===
        self.context_manager.update(user_input, preprocessed, intent_result, response)
        self._update_memory(user_input, intent_result, preprocessed)
        
        # Log respons Milo
        self.logger.log_conversation("milo", response, {
            "intent": intent_result["intent"],
            "confidence": intent_result["confidence"],
        })
        
        return response
    
    def _apply_context_adjustments(self, intent_result, context, preprocessed):
        """Menyesuaikan intent berdasarkan konteks percakapan."""
        intent = intent_result["intent"]
        original_text = preprocessed.get("original", "")
        
        # Cek apakah ada penyebutan nama di input (misal "Halo namaku Mullo", "Hai nama saya...")
        extracted_name = self.context_manager._extract_name(original_text)
        if extracted_name:
            self.context_manager.set_user_name(extracted_name)
            self.memory.set_user_info("name", extracted_name)
            intent_result["intent"] = "user_name_tell"
            intent_result["confidence"] = 1.0
            return intent_result
        
        # Jika greeting tapi bukan turn pertama
        if intent == "greeting" and context["turn_count"] > 3:
            words = preprocessed.get("final", "").split()
            if len(words) <= 1 and words[0] in ("hai", "halo", "hey", "hi"):
                pass
        
        return intent_result
    
    def _post_process(self, response, intent_result, preprocessed):
        """Post-processing respons sebelum dikirim ke user."""
        # Jika intent adalah user_name_tell, pastikan nama sudah di-substitusi
        if intent_result["intent"] == "user_name_tell":
            user_name = self.context_manager.get_user_name()
            if user_name:
                response = response.replace("{user_name}", user_name)
            else:
                response = response.replace("{user_name}", "teman")
        
        return response
    
    def _update_memory(self, user_input, intent_result, preprocessed):
        """Update memori berdasarkan percakapan."""
        intent = intent_result["intent"]
        
        # Simpan topik percakapan ke short-term
        self.memory.remember_short(
            f"turn_{self.context_manager.get_context()['turn_count']}",
            {
                "input": user_input,
                "intent": intent,
            },
            importance=0.5 if intent != "fallback" else 0.2
        )
        
        # Jika user memberikan nama, simpan ke long-term
        if intent == "user_name_tell":
            name = self.context_manager.get_user_name()
            if name:
                self.memory.remember_long("user_name", name, "user_info")
                self.memory.set_user_info("name", name)
    
    def get_status(self):
        """Mengembalikan status Milo saat ini."""
        emotion = self.personality.get_emotion_state()
        context = self.context_manager.get_context()
        
        return {
            "name": Config.MILO_NAME,
            "version": Config.MILO_VERSION,
            "emotion": emotion,
            "mood": self.personality.get_mood(),
            "style": self.personality.get_style(),
            "context": {
                "current_topic": context["current_topic"],
                "sentiment": context["sentiment"],
                "turn_count": context["turn_count"],
                "user_name": context["user_name"],
            },
            "memory": {
                "short_term_count": len(self.memory.get_short_term_all()),
                "user_profile": self.memory.get_user_profile(),
            }
        }
    
    def reset(self):
        """Reset Milo ke keadaan awal."""
        self.context_manager.reset()
        self.personality.reset()
        self.memory.clear_short_term()
        self.logger.info("Milo has been reset! 🔄")
    
    def shutdown(self):
        """Shutdown Milo — simpan data dan bersihkan."""
        # Konsolidasi memori
        consolidated = self.memory.consolidate()
        self.logger.info(f"Consolidated {consolidated} memory entries")
        
        # Simpan conversation log
        self.logger.save_conversation()
        
        self.logger.info("Milo AI shutting down... Bye! 👋")
