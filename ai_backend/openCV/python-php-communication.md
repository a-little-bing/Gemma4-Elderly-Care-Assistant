# Python AI Service to PHP Backend Communication

## Data Direction

```text
Python AI Service
  YOLO / OpenCV / Whisper / Gemma4
        |
        | HTTP POST JSON
        v
PHP Backend /api/ai-update
        |
        | save api/storage/state.json + write logs
        v
Frontend Dashboard /api/status polling
```

## PHP Receiver

Endpoint:

```text
POST http://127.0.0.1:8080/api/ai-update
```

Example JSON:

```json
{
  "source": "python-ai-service",
  "pipeline_id": "demo-001",
  "vision": {
    "fall_detected": true,
    "confidence": 0.91,
    "label": "fall",
    "fps": 29,
    "detections": [
      {
        "id": "elderly-person-1",
        "label": "fall",
        "confidence": 0.91,
        "fall_detected": true,
        "x": 0.28,
        "y": 0.58,
        "width": 0.42,
        "height": 0.18
      }
    ]
  },
  "speech": {
    "transcript": "",
    "intent": "none"
  },
  "context": {
    "no_response_seconds": 65
  },
  "intervention": {
    "active": true,
    "voice_prompt": "Are you okay?"
  },
  "decision": {
    "risk_level": "high",
    "risk_score": 100,
    "emergency_alert": true,
    "action": "Trigger emergency rescue",
    "reason": "High confidence fall with no response."
  },
  "emergency": {
    "triggered": true,
    "countdown_seconds": 0,
    "contact_status": "Notifying family"
  }
}
```

## Python Sender

Start Python AI service:

```powershell
cd C:\Users\35135\Desktop\Gemma4\Gemma4-Elderly-Care-Assistant\ai_backend
pip install -r requirements.txt
uvicorn app:app --host 127.0.0.1 --port 8001 --reload
```

Run one AI cycle and push result to PHP:

```powershell
curl -X POST http://127.0.0.1:8001/pipeline/run ^
  -H "Content-Type: application/json" ^
  -d "{\"no_response_seconds\":65,\"push_to_php\":true}"
```

Run only OpenCV + YOLO vision detection:

```powershell
curl -X POST http://127.0.0.1:8001/vision/detect ^
  -H "Content-Type: application/json" ^
  -d "{\"frame_path\":\"yolo/inputs/test.jpg\"}"
```

For a webcam frame, use `"frame_path":"0"` or omit `frame_path` to use camera 0.

## Error Handling

- Python catches PHP POST errors and returns the error text in `/pipeline/run`.
- PHP validates that at least one of `vision`, `speech`, or `decision` exists.
- PHP saves valid state updates to `api/storage/state.json`.
- Frontend polls `/api/status`, `/api/fall-detection`, `/api/gemma-decision`, and `/api/logs`.
- If API polling fails, the dashboard shows `API Offline` and keeps the UI available.
