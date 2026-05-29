import os
import re

# change later with your own path
os.environ["PATH"] += os.pathsep + r"C:\Users\jessl\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.1-full_build\bin"

import shutil
print("FFMPEG:", shutil.which("ffmpeg"))

import whisper
import pyttsx3
from ollama import chat
import json
import sounddevice as sd
import soundfile as sf
import numpy as np
from datetime import datetime
from fastapi import FastAPI
from pydantic import BaseModel

# Your API Key
# API_KEY = "AIzaSyAkRieBrRJw_iDRn1z1UoQ-r87gPSyZ9Kw"
WHISPER_MODEL = "tiny"
SAMPLE_RATE = 16000
RECORD_SECONDS = 7
LOG_FILE = "emergency_log.txt"


# sd.default.device = 1

# Init FastAPI
app = FastAPI()

def parse_json_response(text):
    # remove markdown fences
    text = re.sub(r"```json\s*", "", text)
    text = re.sub(r"```", "", text)
    
    match = re.search(r"\{.*?\}", text, re.DOTALL)
    
    if not match:
        raise ValueError("No JSON found")

    return json.loads(match.group())

EMERGENCY_WORDS = [
    "fall",
    "fell",
    "chest pain",
    "cannot move",
    "can't move",
    "difficulty breathing",
    "help me",
    "emergency",
    "dizzy",
    "severe pain"
]

def call_gemma(user_text):
    lower = user_text.lower()

    # Rule-based emergency detection
    for word in EMERGENCY_WORDS:
        if word in lower:
            return {
                "reply": "Please seek immediate help.",
                "is_emergency": True,
                "risk_level": "high"
            }

    prompt = SYSTEM_PROMPT + "\nUser: " + user_text

    response = chat(
        model="gemma3:1b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    text = response["message"]["content"]

    try:
        return parse_json_response(text)
    except Exception:
        print("Model returned non-JSON:")
        print(text)

        return {
            "reply": text,
            "is_emergency": False,
            "risk_level": "normal"
        }

SYSTEM_PROMPT = """
Classify the user's message.

Return ONLY JSON.

Example:

{"reply":"Glad to hear that.","is_emergency":false,"risk_level":"normal"}

Rules:
- fall, chest pain, cannot move, severe pain, difficulty breathing = high
- mild discomfort = low
- greeting or normal conversation = normal

No markdown.
No explanation.
JSON only.
"""
     

# Init tools
tts_engine = pyttsx3.init()

whisper_model = None

def get_whisper():
    global whisper_model

    if whisper_model is None:
        whisper_model = whisper.load_model(
            WHISPER_MODEL,
            download_root="./models"
        )

    return whisper_model


class UserTextInput(BaseModel):
    user_text: str

def text_to_speech(text):
    tts_engine.say(text)
    tts_engine.runAndWait()


def log_emergency(user_text, result):
    if result["risk_level"] == "high":
        time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log = f"[{time_str}] EMERGENCY\nUser: {user_text}\nReply: {result['reply']}\nLevel: {result['risk_level']}\n-----\n"
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log)
        print("￼ Emergency logged!")

# def record_audio(duration=RECORD_SECONDS):
#     print(f"\nListening {duration}s...")
#     audio = sd.rec(int(duration * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype="float32")
#     sd.wait()
#     print("Finish listening")
#     return audio.flatten()


def record_audio(duration=RECORD_SECONDS):
    print(f"\nListening {duration}s...")

    audio = sd.rec(
        int(duration * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="float32"
    )

    sd.wait()

    print("Finish listening")

    print("Max volume:", np.max(np.abs(audio)))

    return audio.flatten()

def speech_to_text(audio_np):
    model = get_whisper()

    sf.write("temp.wav", audio_np, SAMPLE_RATE)

    result = model.transcribe("temp.wav")
    print("Detected language:", result["language"])
    text = result["text"].strip()

    if os.path.exists("temp.wav"):
        os.remove("temp.wav")

    return text


# API for your HTML/PHP
@app.post("/api/analyze")
def analyze_text(data: UserTextInput):
    res = call_gemma(data.user_text)
    log_emergency(data.user_text, res)
    return res

# Voice mic mode
def voice_mode():
    print("===== Whisper Voice Assistant Ready =====")
    print("Press Enter to speak, type exit to quit")
    while True:
        cmd = input("\nEnter to listen: ")
        if cmd.lower() == "exit":
            break
        try:
            audio = record_audio()
        except Exception as e:
            print("Mic error:", e)
            continue
        
        text = speech_to_text(audio)
        
        print("You said:", repr(text)) 

        if not text.strip():
            print("No speech detected")
            continue
        
        try:
            result = call_gemma(text)
        except Exception as e:
            print("AI Error:", e)

            result = {
                "reply": "Sorry, I could not process that request.",
                "is_emergency": False,
                "risk_level": "normal"
            }
        print(json.dumps(result, indent=2))
        log_emergency(text, result)
        text_to_speech(result["reply"])

if __name__ == "__main__":
    print(sd.query_devices())
    voice_mode()
    
    


    