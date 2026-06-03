from __future__ import annotations


class SpeechService:
    """Whisper adapter for elderly voice response recognition."""

    def transcribe(self, audio_path: str | None = None) -> dict:
        # Demo default: no reply. Replace with Whisper transcription result.
        return {
            "transcript": "",
            "intent": "none",
            "source": audio_path or "demo_microphone",
        }
