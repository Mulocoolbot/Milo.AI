# 🧠 Milo AI v1.0.0

**Sistem AI Percakapan yang Dibangun dari Scratch**

Milo AI adalah chatbot percakapan yang dibangun sepenuhnya dari nol menggunakan Python murni, tanpa library AI/ML eksternal. Setiap komponen — dari tokenizer hingga intent recognizer — diimplementasi secara manual.

## ✨ Fitur

- **Percakapan Natural** — Mendukung Bahasa Indonesia & English
- **Pattern Matching + TF-IDF** — Kombinasi beberapa metode NLP
- **Context Awareness** — Memahami konteks percakapan
- **Memory System** — Short-term & long-term memory
- **Personality & Emotions** — Milo punya karakter dan emosi
- **Slang Understanding** — Memahami singkatan Indonesia (gw, yg, dll)
- **Anti-Repetisi** — Variasi respons agar tidak monoton

## 🚀 Cara Menjalankan

```bash
cd Milo_AI
python main.py
```

## 📖 Commands

| Command   | Fungsi                          |
|-----------|--------------------------------|
| `/status` | Lihat status Milo saat ini     |
| `/reset`  | Reset percakapan               |
| `/memory` | Lihat isi memori Milo          |
| `/debug`  | Toggle mode debug              |
| `/help`   | Tampilkan bantuan              |
| `/quit`   | Keluar dari Milo               |

## 🏗️ Arsitektur

```
Milo_AI/
├── main.py                 # Entry point
├── milo.py                 # Kelas utama (orchestrator)
├── core/                   # Modul inti NLP
│   ├── preprocessor.py     # Text cleaning
│   ├── tokenizer.py        # Tokenization & stemming
│   ├── intent_recognizer.py # Intent detection
│   ├── response_engine.py  # Response generation
│   └── context_manager.py  # Context tracking
├── knowledge/              # Knowledge & memory
│   ├── knowledge_base.py   # Knowledge manager
│   └── memory.py           # Memory system
├── personality/            # Personality & emotions
│   ├── personality.py      # Personality engine
│   └── emotions.py         # Emotion state machine
├── data/                   # Data statis (JSON)
│   ├── intents.json        # Intent patterns
│   ├── responses.json      # Response templates
│   ├── knowledge.json      # Knowledge base
│   ├── slang_dict.json     # Kamus slang
│   └── stopwords_id.json   # Stop words
└── utils/                  # Utilitas
    ├── config.py           # Configuration
    ├── logger.py           # Logging
    └── text_utils.py       # Text utilities
```

## 🧪 Teknologi

- **Bahasa**: Python 3.x (Pure — tanpa library AI eksternal)
- **NLP**: Pattern Matching, TF-IDF, Cosine Similarity, Levenshtein Distance
- **Data**: JSON-based storage
- **Arsitektur**: Modular, extensible

## 📝 Lisensi

Proyek pribadi — dibuat dengan ❤️ dari nol.
