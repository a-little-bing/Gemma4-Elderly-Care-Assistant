from __future__ import annotations

import base64
import time
from pathlib import Path
from typing import Any

import numpy as np


BASE_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = BASE_DIR.parent
DEFAULT_WEIGHTS = BASE_DIR / "yolo" / "weights" / "best.pt"
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
VIDEO_SUFFIXES = {".mp4", ".avi", ".mov", ".mkv", ".wmv"}


class VisionService:
    """OpenCV frame reader plus YOLO fall detection service."""

    def __init__(
        self,
        weights_path: str | Path = DEFAULT_WEIGHTS,
        *,
        conf: float = 0.45,
        iou: float = 0.45,
        imgsz: int = 640,
        webcam_index: int = 0,
    ) -> None:
        self.weights_path = Path(weights_path)
        self.conf = conf
        self.iou = iou
        self.imgsz = imgsz
        self.webcam_index = webcam_index
        self._model: Any | None = None

    def detect_fall(self, frame_path: str | None = None) -> dict:
        """Read one frame with OpenCV and run the YOLO fall model."""
        started_at = time.perf_counter()
        source = self._source_label(frame_path)

        try:
            frame = self._read_frame(frame_path)
            result = self._predict(frame)
            detections = self._to_api_detections(result, frame.shape)
            fall_detections = [item for item in detections if item["fall_detected"]]
            confidence = max(
                (item["confidence"] for item in fall_detections), default=0.0
            )
            elapsed = max(time.perf_counter() - started_at, 0.001)

            return {
                "fall_detected": bool(fall_detections),
                "confidence": confidence,
                "label": "fall" if fall_detections else self._top_label(detections),
                "fps": max(1, round(1 / elapsed)),
                "detections": detections,
                "source": source,
                "model": str(self.weights_path),
                "latency_ms": round(elapsed * 1000, 2),
                "frame": {
                    "width": int(frame.shape[1]),
                    "height": int(frame.shape[0]),
                },
            }
        except Exception as exc:
            return {
                "fall_detected": False,
                "confidence": 0.0,
                "label": "none",
                "fps": 0,
                "detections": [],
                "source": source,
                "model": str(self.weights_path),
                "error": str(exc),
            }

    def _source_label(self, source: str | None) -> str:
        if source is None or source == "":
            return f"webcam:{self.webcam_index}"
        if source.startswith("data:image"):
            return "data_url"
        return source

    def _load_model(self) -> Any:
        if self._model is None:
            if not self.weights_path.exists():
                raise FileNotFoundError(f"YOLO weights not found: {self.weights_path}")

            from ultralytics import YOLO

            self._model = YOLO(str(self.weights_path))
        return self._model

    def _predict(self, frame: np.ndarray) -> Any:
        model = self._load_model()
        return model.predict(
            source=frame,
            imgsz=self.imgsz,
            conf=self.conf,
            iou=self.iou,
            verbose=False,
        )[0]

    def _read_frame(self, source: str | None) -> np.ndarray:
        import cv2

        if source is None or source == "":
            return self._read_video_frame(str(self.webcam_index))

        if source.startswith("data:image"):
            return self._read_data_url(source)

        if source.isdigit() or source.startswith("webcam:"):
            camera = source.split(":", 1)[1] if ":" in source else source
            return self._read_video_frame(camera)

        path = self._resolve_path(source)
        suffix = path.suffix.lower()
        if suffix in IMAGE_SUFFIXES:
            frame = cv2.imread(str(path))
            if frame is None:
                raise RuntimeError(f"OpenCV cannot read image: {path}")
            return frame

        if suffix in VIDEO_SUFFIXES:
            return self._read_video_frame(str(path))

        raise ValueError(f"Unsupported OpenCV source: {source}")

    def _read_data_url(self, data_url: str) -> np.ndarray:
        import cv2

        _, encoded = data_url.split(",", 1)
        payload = base64.b64decode(encoded)
        buffer = np.frombuffer(payload, dtype=np.uint8)
        frame = cv2.imdecode(buffer, cv2.IMREAD_COLOR)
        if frame is None:
            raise RuntimeError("OpenCV cannot decode image data URL.")
        return frame

    def _read_video_frame(self, source: str) -> np.ndarray:
        import cv2

        capture_source: int | str = int(source) if source.isdigit() else source
        cap = cv2.VideoCapture(capture_source)
        try:
            if not cap.isOpened():
                raise RuntimeError(f"OpenCV cannot open video source: {source}")

            ok, frame = cap.read()
            if not ok or frame is None:
                raise RuntimeError(f"OpenCV cannot read frame from: {source}")
            return frame
        finally:
            cap.release()

    def _resolve_path(self, source: str) -> Path:
        path = Path(source)
        candidates = [path] if path.is_absolute() else [BASE_DIR / path, PROJECT_DIR / path]
        for candidate in candidates:
            if candidate.exists():
                return candidate.resolve()
        raise FileNotFoundError(f"OpenCV source not found: {source}")

    def _to_api_detections(self, result: Any, frame_shape: tuple[int, ...]) -> list[dict]:
        height, width = int(frame_shape[0]), int(frame_shape[1])
        names = result.names or {}
        detections = []

        for index, box in enumerate(result.boxes):
            class_id = int(box.cls[0])
            label = str(names.get(class_id, class_id))
            confidence = round(float(box.conf[0]), 6)
            x1, y1, x2, y2 = [float(value) for value in box.xyxy[0].tolist()]
            box_width = max(0.0, x2 - x1)
            box_height = max(0.0, y2 - y1)

            detections.append(
                {
                    "id": f"detection-{index + 1}",
                    "class_id": class_id,
                    "label": label,
                    "confidence": confidence,
                    "fall_detected": self._is_fall_label(label, class_id, names),
                    "x": round(x1 / width, 6),
                    "y": round(y1 / height, 6),
                    "width": round(box_width / width, 6),
                    "height": round(box_height / height, 6),
                    "bbox_xyxy": [
                        round(x1, 3),
                        round(y1, 3),
                        round(x2, 3),
                        round(y2, 3),
                    ],
                }
            )

        return detections

    def _is_fall_label(self, label: str, class_id: int, names: dict) -> bool:
        normalized = label.lower().replace("_", " ").replace("-", " ").strip()
        if "no fall" in normalized or "normal" in normalized:
            return False
        if "fall" in normalized:
            return True
        return class_id == 0 and len(names) == 1

    def _top_label(self, detections: list[dict]) -> str:
        if not detections:
            return "none"
        return max(detections, key=lambda item: item["confidence"])["label"]
