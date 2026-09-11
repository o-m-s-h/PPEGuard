import argparse
import os
import sys
import cv2

from ultralytics import YOLO


# Allows scripts/detect.py to import app/
sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)


from app.services.reporting import (
    is_violation,
    get_severity,
    save_json_report,
    save_csv_report
)


# ============================================================
# ARGUMENTS
# ============================================================

parser = argparse.ArgumentParser()


parser.add_argument(
    "--image",
    help="Path to input image"
)


parser.add_argument(
    "--video",
    help="Path to input video"
)


parser.add_argument(
    "--model",
    default="models/best.pt",
    help="Path to YOLO model"
)


parser.add_argument(
    "--conf",
    type=float,
    default=0.25,
    help="Confidence threshold"
)


args = parser.parse_args()


if not args.image and not args.video:

    print("Please provide either --image or --video")

    exit()


# ============================================================
# LOAD MODEL
# ============================================================

model = YOLO(args.model)


# ============================================================
# IMAGE DETECTION
# ============================================================

if args.image:

    results = model.predict(
        source=args.image,
        conf=args.conf,
        verbose=False
    )


    result = results[0]


    # --------------------------------------------------------
    # SAVE ANNOTATED IMAGE
    # --------------------------------------------------------

    os.makedirs(
        "outputs/images",
        exist_ok=True
    )


    image_name = os.path.basename(
        args.image
    )


    output_path = os.path.join(
        "outputs/images",
        image_name
    )


    result.save(
        filename=output_path
    )


    # --------------------------------------------------------
    # CREATE VIOLATION REPORT
    # --------------------------------------------------------

    violations = []


    for box in result.boxes:

        class_id = int(
            box.cls[0]
        )


        confidence = float(
            box.conf[0]
        )


        class_name = model.names[
            class_id
        ]


        if is_violation(class_name):

            violations.append({

                "type": class_name,

                "confidence": round(
                    confidence,
                    4
                ),

                "severity": get_severity(
                    class_name
                ),

                "timestamp": None

            })


    # --------------------------------------------------------
    # JSON REPORT
    # --------------------------------------------------------

    report = {

        "input_file": args.image,

        "media_type": "image",

        "total_violations": len(
            violations
        ),

        "violations": violations

    }


    base_name = os.path.splitext(
        image_name
    )[0]


    json_path = save_json_report(
        report,
        base_name + ".json"
    )


    csv_path = save_csv_report(
        violations,
        base_name + ".csv"
    )


    print("\nImage detection completed.")

    print(
        "Annotated image:",
        output_path
    )

    print(
        "JSON report:",
        json_path
    )

    print(
        "CSV report:",
        csv_path
    )

    print(
        "Violations:",
        len(violations)
    )


# ============================================================
# VIDEO DETECTION
# ============================================================

if args.video:

    os.makedirs(
        "outputs/videos",
        exist_ok=True
    )


    cap = cv2.VideoCapture(
        args.video
    )


    if not cap.isOpened():

        print("Could not open video.")

        exit()


    fps = cap.get(
        cv2.CAP_PROP_FPS
    )


    width = int(
        cap.get(
            cv2.CAP_PROP_FRAME_WIDTH
        )
    )


    height = int(
        cap.get(
            cv2.CAP_PROP_FRAME_HEIGHT
        )
    )


    video_name = os.path.basename(
        args.video
    )


    output_path = os.path.join(
        "outputs/videos",
        video_name
    )


    fourcc = cv2.VideoWriter_fourcc(
        *"mp4v"
    )


    writer = cv2.VideoWriter(
        output_path,
        fourcc,
        fps,
        (width, height)
    )


    frame_count = 0

    violations = []


    while True:

        ret, frame = cap.read()


        if not ret:
            break


        frame_count += 1


        # ----------------------------------------------------
        # YOLO INFERENCE
        # ----------------------------------------------------

        results = model.predict(
            source=frame,
            conf=args.conf,
            verbose=False
        )


        result = results[0]


        # ----------------------------------------------------
        # DRAW BOUNDING BOXES
        # ----------------------------------------------------

        annotated_frame = result.plot()


        writer.write(
            annotated_frame
        )


        # ----------------------------------------------------
        # VIDEO TIMESTAMP
        # ----------------------------------------------------

        timestamp_seconds = (
            frame_count / fps
        )


        minutes = int(
            timestamp_seconds // 60
        )


        seconds = int(
            timestamp_seconds % 60
        )


        timestamp = (
            f"{minutes:02d}:"
            f"{seconds:02d}"
        )


        # ----------------------------------------------------
        # FIND VIOLATIONS
        # ----------------------------------------------------

        for box in result.boxes:

            class_id = int(
                box.cls[0]
            )


            confidence = float(
                box.conf[0]
            )


            class_name = model.names[
                class_id
            ]


            if is_violation(
                class_name
            ):

                violations.append({

                    "type": class_name,

                    "confidence": round(
                        confidence,
                        4
                    ),

                    "severity": get_severity(
                        class_name
                    ),

                    "timestamp": timestamp,

                    "frame": frame_count

                })


        print(
            f"Processed frame: {frame_count}",
            end="\r"
        )


    cap.release()

    writer.release()

    # ============================================================
    # AGGREGATE VIDEO VIOLATIONS
    # ============================================================

    grouped = {}


    for violation in violations:

        violation_type = violation["type"]
        timestamp = violation["timestamp"]

        minutes, seconds = map(
            int,
            timestamp.split(":")
        )

        total_seconds = minutes * 60 + seconds


        if violation_type not in grouped:

            grouped[violation_type] = {
                "severity": violation["severity"],
                "seconds": set()
            }


        grouped[violation_type]["seconds"].add(
            total_seconds
        )


    aggregated_events = []


    for violation_type, data in grouped.items():

        seconds_list = sorted(
            data["seconds"]
        )


        if not seconds_list:
            continue


        start = seconds_list[0]
        previous = seconds_list[0]


        for current in seconds_list[1:]:

            if current == previous + 1:

                previous = current

            else:

                start_minutes = start // 60
                start_seconds = start % 60

                end_minutes = previous // 60
                end_seconds = previous % 60


                aggregated_events.append({

                    "type": violation_type,

                    "severity": data["severity"],

                    "start_time": (
                        f"{start_minutes:02d}:"
                        f"{start_seconds:02d}"
                    ),

                    "end_time": (
                        f"{end_minutes:02d}:"
                        f"{end_seconds:02d}"
                    )

                })


                start = current
                previous = current


        start_minutes = start // 60
        start_seconds = start % 60

        end_minutes = previous // 60
        end_seconds = previous % 60


        aggregated_events.append({

            "type": violation_type,

            "severity": data["severity"],

            "start_time": (
                f"{start_minutes:02d}:"
                f"{start_seconds:02d}"
            ),

            "end_time": (
                f"{end_minutes:02d}:"
                f"{end_seconds:02d}"
            )

        })


    # ============================================================
    # SAVE VIDEO REPORTS
    # ============================================================

    report = {

        "input_file": args.video,

        "media_type": "video",

        "fps": fps,

        "frames_processed": frame_count,

        "total_violation_events": len(
            aggregated_events
        ),

        "violations": aggregated_events

    }


    base_name = os.path.splitext(
        video_name
    )[0]


    json_path = save_json_report(
        report,
        base_name + ".json"
    )


    csv_path = save_csv_report(
        aggregated_events,
        base_name + ".csv"
    )

    print(
        "Annotated video:",
        output_path
    )

    print(
        "JSON report:",
        json_path
    )

    print(
        "CSV report:",
        csv_path
    )

    print(
        "Violation detections:",
        len(violations)
    )