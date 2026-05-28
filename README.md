# Elderly Voice Emergency Assistant

A local voice assistant that:
- Uses Whisper for speech-to-text
- Uses Gemma (via Ollama) for classification
- Detects emergency situations
- Speaks responses with TTS

## Features
- Voice input (microphone)
- Emergency detection (rule-based + AI)
- JSON API (FastAPI)
- Offline AI (Ollama)

## Setup

```bash
pip install -r requirements.txt
ollama pull gemma3:1b
python main.py