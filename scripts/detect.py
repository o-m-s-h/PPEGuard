import argparse
import os
import cv2

from ultralytics import YOLO


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


model = YOLO(args.model)


# ============================================================
# IMAGE DETECTION
# ============================================================

if args.image:

    results = model.predict(
        source=args.image,
        conf=args.conf
    )

    result = results[0]

    os.makedirs(
        "outputs/images",
        exist_ok=True
    )

    image_name = os.path.basename(args.image)

    output_path = os.path.join(
        "outputs/images",
        image_name
    )

    result.save(
        filename=output_path
    )

    print("Image detection completed.")
    print("Input :", args.image)
    print("Output:", output_path)


# ============================================================
# VIDEO DETECTION
# ============================================================

if args.video:

    os.makedirs(
        "outputs/videos",
        exist_ok=True
    )


    # Open input video
    cap = cv2.VideoCapture(args.video)


    if not cap.isOpened():

        print("Could not open video.")

        exit()


    # Get original video properties
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


    # Video codec
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


    while True:

        ret, frame = cap.read()


        if not ret:
            break


        frame_count += 1


        # Run YOLO on current frame
        results = model.predict(
            source=frame,
            conf=args.conf,
            verbose=False
        )


        result = results[0]


        # Draw YOLO bounding boxes
        annotated_frame = result.plot()


        # Write frame to output video
        writer.write(
            annotated_frame
        )


        print(
            f"Processed frame: {frame_count}",
            end="\r"
        )


    cap.release()

    writer.release()


    print("\nVideo detection completed.")
    print("Input :", args.video)
    print("Output:", output_path)