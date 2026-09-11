from pathlib import Path

import cv2
import numpy as np

from app.services.reporting import collect_violations, write_reports


def detect_image(source: Path, destination: Path, detector, confidence=0.25, input_name=None):
    frame = cv2.imdecode(np.frombuffer(source.read_bytes(), dtype=np.uint8), cv2.IMREAD_COLOR)
    if frame is None:
        raise ValueError("The uploaded file is not a decodable image.")
    result = detector.predict(frame, confidence)
    destination.mkdir(parents=True, exist_ok=True)
    ok, encoded = cv2.imencode(".jpg", result.plot())
    if not ok:
        raise RuntimeError("Could not encode the annotated image.")
    (destination / "annotated.jpg").write_bytes(encoded.tobytes())
    report = {
        "input_file": input_name or source.name,
        "media_type": "image",
        "violations": collect_violations(result),
    }
    report["total_violations"] = len(report["violations"])
    write_reports(report, destination)
    return "annotated.jpg", report
