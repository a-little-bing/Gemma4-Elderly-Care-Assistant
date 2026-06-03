# API Documentation

所有 PHP API 均返回统一 JSON：

```json
{
  "success": true,
  "message": "OK",
  "data": {},
  "timestamp": "2026-05-14T12:00:00+08:00"
}
```

## GET /api/status

返回当前系统状态，用于前端轮询刷新。

## GET /api/fall-detection

返回 YOLO 风格检测结果，用于前端 Canvas 绘制检测框。

查询参数：

```text
mode=camera|demo
```

## POST /api/status/analyze

将当前状态发送到 Python AI 后端 `/analyze`，并写回 Gemma4 决策结果。

## GET /api/gemma-decision

获取 Gemma4 当前推理结果。Python AI 服务不可用时，会自动使用 PHP 本地规则兜底。

## POST /api/emergency

触发紧急报警。

```json
{
  "source": "manual_dashboard",
  "reason": "Dashboard manual emergency trigger"
}
```

## GET /api/video-stream

返回视频流配置。当前前端直接使用浏览器摄像头或 `public/assets/videos/demo-fall.mp4`，后续可替换为 OpenCV MJPEG/WebSocket 流。

## POST /api/ai-update

接收 Python AI 服务输出的 JSON，合并并保存到系统状态。

Python 负责 YOLO / OpenCV / Whisper / Gemma4，PHP 负责 Web API / 日志 / 前端通信。

## POST /api/demo

请求体：

```json
{
  "scenario": "suspected_fall"
}
```

支持场景：

- `normal`
- `suspected_fall`
- `responded_ok`
- `no_response`
- `emergency`

## GET /api/logs

返回最近系统日志。

## Python AI Backend

### GET /health

AI 服务健康检查。

### POST /vision/detect

OpenCV + YOLO 跌倒检测适配器。

### POST /speech/transcribe

Whisper 语音识别适配器。

### POST /analyze

Gemma4 主动干预决策适配器。
