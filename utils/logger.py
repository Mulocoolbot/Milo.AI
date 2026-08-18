"""
Milo AI — Logger
Sistem logging untuk debug, monitoring, dan pencatatan percakapan.
"""

import os
import json
from datetime import datetime
from .config import Config


class MiloLogger:
    """Logger untuk Milo AI — mencatat percakapan dan aktivitas sistem."""
    
    def __init__(self):
        Config.ensure_directories()
        self._log_file = os.path.join(
            Config.LOGS_DIR,
            f"milo_log_{datetime.now().strftime('%Y%m%d')}.log"
        )
        self._conversation_log = []
    
    def log(self, level, message, data=None):
        """Mencatat log dengan level tertentu."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level.upper()}] {message}"
        
        if data:
            log_entry += f" | Data: {json.dumps(data, ensure_ascii=False)}"
        
        # Tulis ke file
        try:
            with open(self._log_file, "a", encoding="utf-8") as f:
                f.write(log_entry + "\n")
        except IOError:
            pass  # Silent fail jika tidak bisa menulis log
        
        return log_entry
    
    def info(self, message, data=None):
        """Log level INFO."""
        return self.log("INFO", message, data)
    
    def debug(self, message, data=None):
        """Log level DEBUG."""
        return self.log("DEBUG", message, data)
    
    def warning(self, message, data=None):
        """Log level WARNING."""
        return self.log("WARNING", message, data)
    
    def error(self, message, data=None):
        """Log level ERROR."""
        return self.log("ERROR", message, data)
    
    def log_conversation(self, role, message, metadata=None):
        """Mencatat percakapan (user atau Milo)."""
        entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "role": role,
            "message": message,
        }
        if metadata:
            entry["metadata"] = metadata
        
        self._conversation_log.append(entry)
        self.info(f"[{role}] {message}", metadata)
        
        return entry
    
    def get_conversation_log(self):
        """Mengembalikan log percakapan saat ini."""
        return self._conversation_log.copy()
    
    def save_conversation(self):
        """Menyimpan log percakapan ke file."""
        if not self._conversation_log:
            return
        
        filename = os.path.join(
            Config.LOGS_DIR,
            f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(self._conversation_log, f, ensure_ascii=False, indent=2)
            self.info(f"Conversation saved to {filename}")
        except IOError as e:
            self.error(f"Failed to save conversation: {e}")
    
    def clear_conversation_log(self):
        """Menghapus log percakapan dari memory."""
        self._conversation_log = []
