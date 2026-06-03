from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Optional
from uuid import uuid4

from services.decision_service import DecisionService
from services.vision_service import VisionService
from services.speech_service import SpeechService
from services.php_bridge_service import PhpBridgeService

app = FastAPI(
    title="Gemma4 Elderly Care AI Backend",
    description="Multimodal AI backend for fall detection, speech recognition, and emergency decision making.",
    version="0.1.0",
)

vision_service = VisionService()
speech_service = SpeechService()
decision_service = DecisionService()
php_bridge_service = PhpBridgeService()


class AnalyzeRequest(BaseModel):
    """Payload sent by PHP API for multimodal decision analysis."""

    state: dict = Field(default_factory=dict)


class VisionFrameRequest(BaseModel):
    """Demo payload for frame analysis. Replace frame_path with camera frame bytes in production."""

    frame_path: Optional[str] = None


class SpeechRequest(BaseModel):
    """Demo payload for audio transcription. Replace audio_path with stream chunks in production."""

    audio_path: Optional[str] = None


class PipelineRequest(BaseModel):
    """Run one AI cycle and optionally push JSON result to PHP."""

    frame_path: Optional[str] = None
    audio_path: Optional[str] = None
    no_response_seconds: int = 0
    push_to_php: bool = True


@app.get("/health")
def health() -> dict:
    """Return backend health for integration checks."""
    return {"success": True, "service": "ai_backend", "status": "ok"}


@app.post("/vision/detect")
def detect_fall(payload: VisionFrameRequest) -> dict:
    """Run OpenCV + YOLO fall detection adapter."""
    result = vision_service.detect_fall(payload.frame_path)
    return {"success": True, "vision": result}


@app.post("/speech/transcribe")
def transcribe(payload: SpeechRequest) -> dict:
    """Run Whisper speech recognition adapter."""
    result = speech_service.transcribe(payload.audio_path)
    return {"success": True, "speech": result}


@app.post("/analyze")
def analyze(payload: AnalyzeRequest) -> dict:
    """Use Gemma4 decision adapter to evaluate whether emergency help is required."""
    decision = decision_service.analyze(payload.state)
    return {"success": True, "decision": decision}


@app.post("/pipeline/run")
def run_pipeline(payload: PipelineRequest) -> dict:
    """Run YOLO + Whisper + Gemma4 demo pipeline and POST JSON to PHP backend."""
    vision = vision_service.detect_fall(payload.frame_path)
    speech = speech_service.transcribe(payload.audio_path)
    state = {
        "vision": vision,
        "speech": speech,
        "context": {
            "no_response_seconds": payload.no_response_seconds,
        },
        "intervention": {
            "active": vision["fall_detected"],
            "voice_prompt": "Are you okay? Please answer if you can hear me."
            if vision["fall_detected"]
            else "System is monitoring.",
        },
    }
    decision = decision_service.analyze(state)
    update_payload = {
        "source": "python-ai-service",
        "pipeline_id": str(uuid4()),
        "vision": vision,
        "speech": speech,
        "context": state["context"],
        "intervention": state["intervention"],
        "decision": decision,
        "emergency": {
            "triggered": decision["emergency_alert"],
            "countdown_seconds": 0 if decision["emergency_alert"] else 10,
            "contact_status": "Notifying family" if decision["emergency_alert"] else "Standby",
        },
    }

    php_response = None
    error = None
    if payload.push_to_php:
        try:
            php_response = php_bridge_service.post_ai_update(update_payload)
        except Exception as exc:
            error = str(exc)

    return {
        "success": error is None,
        "payload": update_payload,
        "php_response": php_response,
        "error": error,
    }
