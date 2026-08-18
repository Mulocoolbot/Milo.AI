"""
Milo AI — Entry Point
Menjalankan Milo AI dalam mode terminal interaktif.

Usage:
    python main.py

Commands:
    /status  - Lihat status Milo saat ini
    /reset   - Reset percakapan
    /memory  - Lihat isi memori Milo
    /help    - Tampilkan bantuan
    /quit    - Keluar dari Milo
"""

import sys
import os
import json

# Tambahkan root directory ke path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from milo import Milo
from utils.config import Config


def print_banner():
    """Menampilkan banner welcome Milo AI."""
    banner = """
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║          🧠  M I L O   A I  v{version}  🧠              ║
║                                                          ║
║     Sistem AI Percakapan — Dibangun dari Scratch         ║
║     Pure Python • No External AI Libraries               ║
║                                                          ║
║     Ketik pesan untuk mulai ngobrol!                     ║
║     Ketik /help untuk melihat perintah tersedia          ║
║     Ketik /quit untuk keluar                             ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
    """.format(version=Config.MILO_VERSION)
    
    print(banner)


def print_help():
    """Menampilkan pesan bantuan."""
    help_text = """
╭──────────────── 📖 BANTUAN ────────────────╮
│                                             │
│  Perintah yang tersedia:                    │
│                                             │
│  /status  — Lihat status Milo saat ini      │
│  /reset   — Reset percakapan                │
│  /memory  — Lihat isi memori Milo           │
│  /debug   — Mode debug (lihat proses NLP)   │
│  /help    — Tampilkan bantuan ini           │
│  /quit    — Keluar dari Milo                │
│                                             │
│  Atau ketik apa saja untuk ngobrol! 💬      │
│                                             │
╰─────────────────────────────────────────────╯
"""
    print(help_text)


def print_status(milo):
    """Menampilkan status Milo."""
    status = milo.get_status()
    
    print(f"\n{Config.SEPARATOR}")
    print(f"  📊 STATUS MILO AI")
    print(Config.SEPARATOR)
    print(f"  Nama      : {status['name']} v{Config.MILO_VERSION}")
    print(f"  Emosi     : {status['emotion']['emotion']} {status['emotion']['emoji']}")
    print(f"  Intensitas: {'█' * int(status['emotion']['intensity'] * 10)}{'░' * (10 - int(status['emotion']['intensity'] * 10))} ({status['emotion']['intensity']})")
    print(f"  Mood      : {status['mood']}")
    print(f"  Style     : {status['style']}")
    print(f"  Topik     : {status['context']['current_topic'] or 'Belum ada'}")
    print(f"  Sentimen  : {status['context']['sentiment']}")
    print(f"  Turn      : {status['context']['turn_count']}")
    print(f"  User      : {status['context']['user_name'] or 'Belum diketahui'}")
    print(f"  Memori ST : {status['memory']['short_term_count']} entri")
    print(Config.SEPARATOR)
    print()


def print_memory(milo):
    """Menampilkan isi memori Milo."""
    short_term = milo.memory.get_short_term_all()
    user_profile = milo.memory.get_user_profile()
    
    print(f"\n{Config.SEPARATOR}")
    print(f"  🧠 MEMORI MILO")
    print(Config.SEPARATOR)
    
    print(f"\n  📋 Short-Term Memory ({len(short_term)} entri):")
    if short_term:
        for entry in short_term[-5:]:  # Tampilkan 5 terakhir
            print(f"    • [{entry['timestamp']}] {entry['key']}: {entry['value']}")
    else:
        print("    (kosong)")
    
    print(f"\n  👤 User Profile:")
    if user_profile:
        for key, value in user_profile.items():
            print(f"    • {key}: {value}")
    else:
        print("    (belum ada data)")
    
    print(Config.SEPARATOR)
    print()


def debug_chat(milo, user_input):
    """Mode debug — menampilkan proses NLP internal."""
    print(f"\n{'=' * 50}")
    print("🔍 DEBUG MODE")
    print(f"{'=' * 50}")
    
    # Preprocess
    preprocessed = milo.preprocessor.preprocess(user_input)
    print(f"\n📝 Preprocessing:")
    print(f"   Original  : {preprocessed['original']}")
    print(f"   Cleaned   : {preprocessed.get('cleaned', '')}")
    print(f"   Expanded  : {preprocessed.get('expanded', '')}")
    print(f"   Final     : {preprocessed.get('final', '')}")
    
    # Tokenize
    tokenized = milo.tokenizer.tokenize(preprocessed)
    print(f"\n🧩 Tokenization:")
    print(f"   Words     : {tokenized['words']}")
    print(f"   Filtered  : {tokenized['filtered']}")
    print(f"   Stemmed   : {tokenized['stemmed']}")
    print(f"   Bigrams   : {tokenized['bigrams'][:5]}")
    
    # Intent Recognition
    intent_result = milo.intent_recognizer.recognize(tokenized, preprocessed)
    print(f"\n🎯 Intent Recognition:")
    print(f"   Intent    : {intent_result['intent']}")
    print(f"   Confidence: {intent_result['confidence']}")
    print(f"   Method    : {intent_result['method']}")
    print(f"   Pattern   : {intent_result.get('matched_pattern', 'N/A')}")
    
    # Context
    context = milo.context_manager.get_context()
    print(f"\n📦 Context:")
    print(f"   Topic     : {context['current_topic']}")
    print(f"   Sentiment : {context['sentiment']}")
    print(f"   Turn      : {context['turn_count']}")
    
    # Emotion
    emotion = milo.personality.get_emotion_state()
    print(f"\n🎭 Emotion:")
    print(f"   State     : {emotion['emotion']} {emotion['emoji']}")
    print(f"   Intensity : {emotion['intensity']}")
    
    print(f"{'=' * 50}")
    
    # Kemudian generate respons normal
    response = milo.chat(user_input)
    return response


def main():
    """Main function — menjalankan Milo AI."""
    # Tampilkan banner
    print_banner()
    
    # Inisialisasi Milo
    print("⏳ Menginisialisasi Milo AI...")
    milo = Milo()
    print("✅ Milo AI siap!\n")
    
    # Check apakah user sudah dikenal
    saved_name = milo.memory.get_user_info("name")
    if saved_name:
        print(f"{Config.MILO_PREFIX}: Hai {saved_name}! 😊 Senang ketemu lagi! Mau ngobrol apa hari ini?\n")
    else:
        print(f"{Config.MILO_PREFIX}: Hai! 👋 Selamat datang! Milo siap ngobrol nih! Boleh tau nama kamu?\n")
    
    debug_mode = False
    
    # Main conversation loop
    while True:
        try:
            # Input dari user
            user_input = input(f"\n{Config.USER_PREFIX}: ").strip()
            
            if not user_input:
                continue
            
            # Handle commands
            if user_input.startswith("/"):
                command = user_input.lower().split()[0]
                
                if command in ("/quit", "/exit", "/q"):
                    print(f"\n{Config.MILO_PREFIX}: {milo.chat('bye bye')}")
                    milo.shutdown()
                    print("\n👋 Sampai jumpa! Terima kasih sudah ngobrol dengan Milo! 💕\n")
                    break
                
                elif command == "/help":
                    print_help()
                    continue
                
                elif command == "/status":
                    print_status(milo)
                    continue
                
                elif command == "/memory":
                    print_memory(milo)
                    continue
                
                elif command == "/reset":
                    milo.reset()
                    print(f"\n{Config.MILO_PREFIX}: Percakapan direset! 🔄 Mari mulai dari awal! 😊\n")
                    continue
                
                elif command == "/debug":
                    debug_mode = not debug_mode
                    status = "ON 🔍" if debug_mode else "OFF"
                    print(f"\n  ⚙️  Debug mode: {status}\n")
                    continue
                
                else:
                    print(f"\n  ⚠️  Perintah '{command}' tidak dikenali. Ketik /help untuk bantuan.\n")
                    continue
            
            # Generate response
            if debug_mode:
                response = debug_chat(milo, user_input)
            else:
                response = milo.chat(user_input)
            
            # Tampilkan respons
            print(f"\n{Config.MILO_PREFIX}: {response}")
        
        except KeyboardInterrupt:
            print(f"\n\n{Config.MILO_PREFIX}: Eh, mau pergi ya? 😢")
            milo.shutdown()
            print("👋 Bye bye! Sampai ketemu lagi!\n")
            break
        
        except EOFError:
            milo.shutdown()
            break
        
        except Exception as e:
            print(f"\n  ❌ Error: {e}")
            print("  Milo mengalami error, tapi tetap semangat! Coba lagi ya! 💪\n")


if __name__ == "__main__":
    main()
