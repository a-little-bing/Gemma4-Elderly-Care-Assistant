# Gemma4 Elderly Care Assistant

基于多模态 AI 的老年人安全守护 Demo 系统。项目重点不是单纯跌倒检测，而是“AI 主动干预决策系统”：视觉检测、语音询问、语音识别、Gemma4 综合判断、报警决策统一协作。

## Tech Stack

- Frontend: HTML + CSS + JavaScript
- Backend API: PHP JSON REST API
- AI Backend: Python FastAPI
- Vision: OpenCV + YOLO adapter
- Speech: Whisper adapter
- LLM Decision: Gemma4 API adapter
- Realtime: Frontend polling, WebSocket-ready structure
- Storage: JSON files for demo state and logs

## Project Structure

```text
Gemma4-Elderly-Care-Assistant/
  api/
    index.php
    controllers/
    lib/
    storage/
  ai_backend/
    app.py
    requirements.txt
    services/
  config/
    app.example.json
  docs/
    api.md
  logs/
  public/
    index.html
    assets/css/style.css
    assets/js/app.js
```

## Quick Start

1. Start PHP API:

```powershell
cd C:\Users\35135\Desktop\Gemma4\Gemma4-Elderly-Care-Assistant
powershell -ExecutionPolicy Bypass -File scripts/start_php_server.ps1
```

Or double-click:

```text
scripts/start_php_server.bat
```

If your PHP is already in PATH, this also works:

```powershell
php -S 127.0.0.1:8080 router.php
```

If you use XAMPP and PHP is not in PATH, use:

```powershell
C:\xampp\php\php.exe -S 127.0.0.1:8080 router.php
```

2. Start Python AI backend:

```powershell
cd C:\Users\35135\Desktop\Gemma4\Gemma4-Elderly-Care-Assistant\ai_backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app:app --host 127.0.0.1 --port 8001 --reload
```

3. Open:

```text
http://127.0.0.1:8080
```

Important:

- Opening `public/index.html` directly can load the visual UI, but live JSON APIs require the PHP server.
- Use `http://127.0.0.1:8080`, not only a local `file://` page, when testing realtime data.
- If CSS does not appear, confirm that `public/assets/css/style.css` exists and refresh the browser with `Ctrl + F5`.

## Demo Flow

1. Frontend calls `GET /api/status` every 2 seconds.
2. User clicks demo buttons to simulate normal, suspected fall, no response, or emergency.
3. PHP API stores unified state in `api/storage/state.json`.
4. PHP API can call Python AI backend `/analyze` to make a decision.
5. Frontend renders video panel, active intervention, emergency alert, and logs.

## Python to PHP Communication

Python can push AI results into PHP:

```text
POST http://127.0.0.1:8080/api/ai-update
```

Full example:

[docs/python-php-communication.md](docs/python-php-communication.md)

## Notes

- The vision service now uses OpenCV to read images, videos, webcam frames, or data URLs, then runs the YOLO weights in `ai_backend/yolo/weights/best.pt`.
- The Whisper and Gemma4 services are adapter stubs designed for replacement with real models/API calls.
- All API responses use a unified JSON envelope.
- This repository is structured for VS Code development.
