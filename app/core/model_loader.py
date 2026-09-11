from pathlib import Path
from threading import Lock


class Detector:
    """One model per application process; serialize access to its predictor."""

    def __init__(self, model):
        self.model = model
        self.lock = Lock()

    def predict(self, frame, confidence):
        with self.lock:
            return self.model.predict(source=frame, conf=confidence, verbose=False)[0]


def load_detector(path: Path):
    from ultralytics import YOLO

    if not path.is_file():
        raise RuntimeError(f"YOLO weights not found: {path}")
    return Detector(YOLO(str(path)))
