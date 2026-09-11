"""Command-line detection using the same services as the API."""
import argparse
import json
import sys
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.config import ROOT
from app.core.model_loader import load_detector
from app.services.image_inference import detect_image
from app.services.video_inference import detect_video


def main():
    parser = argparse.ArgumentParser()
    media = parser.add_mutually_exclusive_group(required=True)
    media.add_argument("--image", type=Path)
    media.add_argument("--video", type=Path)
    parser.add_argument("--model", type=Path, default=ROOT / "models/best.pt")
    parser.add_argument("--conf", type=float, default=0.25)
    args = parser.parse_args()
    if not 0 <= args.conf <= 1:
        parser.error("--conf must be between 0 and 1")
    detector = load_detector(args.model)
    destination = ROOT / "outputs/cli" / uuid4().hex
    service = detect_image if args.image else detect_video
    annotated, report = service(args.image or args.video, destination, detector, args.conf)
    print(json.dumps({"annotated": str(destination / annotated), "reports": str(destination), "report": report}, indent=2))


if __name__ == "__main__":
    main()
