# Elderly Voice Emergency Assistant

A local voice assistant that:
- Uses Whisper for speech-to-text
- Uses Gemma (via Ollama) for classification
- Detects emergency situations
- Speaks responses with TTS

---

## Features
- 🎤 Voice input (microphone)
- 🚨 Emergency detection (rule-based + AI)
- 🌐 REST API (FastAPI)
- 🤖 Fully offline AI (Ollama)

---

## Requirements
- Python 3.10+
- Ollama installed → https://ollama.com

---

## Setup

```bash
# install dependencies
pip install -r requirements.txt

# download model
ollama pull gemma3:1b

# run app
python main.py
```