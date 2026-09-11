import math
from pathlib import Path

import cv2

from app.services.reporting import collect_violations, write_reports
from app.services.smoothing import aggregate_events


def detect_video(source: Path, destination: Path, detector, confidence=0.25, input_name=None):
    cap = cv2.VideoCapture(str(source))
    writer = None
    seconds_by_type = {}
    frames = 0
    detections = 0
    try:
        if not cap.isOpened():
            raise ValueError("The uploaded file is not a decodable video.")
        fps = cap.get(cv2.CAP_PROP_FPS)
        if not math.isfinite(fps) or fps <= 0:
            raise ValueError("Video must have a valid frame rate.")
        ok, frame = cap.read()
        if not ok:
            raise ValueError("Video contains no decodable frames.")
        height, width = frame.shape[:2]
        destination.mkdir(parents=True, exist_ok=True)
        writer = cv2.VideoWriter(str(destination / "annotated.mp4"), cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height))
        if not writer.isOpened():
            raise RuntimeError("Could not initialize the MP4 encoder.")
        while ok:
            result = detector.predict(frame, confidence)
            writer.write(result.plot())
            for violation in collect_violations(result):
                detections += 1
                seconds_by_type.setdefault(violation["type"], set()).add(int(frames / fps))
            frames += 1
            ok, frame = cap.read()
    finally:
        cap.release()
        if writer is not None:
            writer.release()
    events = aggregate_events(seconds_by_type)
    report = {
        "input_file": input_name or source.name,
        "media_type": "video",
        "fps": fps,
        "frames_processed": frames,
        "total_violation_detections": detections,
        "total_violation_events": len(events),
        "violations": events,
    }
    write_reports(report, destination)
    return "annotated.mp4", report
