import argparse
import os

from ultralytics import YOLO


parser = argparse.ArgumentParser()

parser.add_argument(
    "--image",
    required=True,
    help="Path to input image"
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


model = YOLO(args.model)


results = model.predict(
    source=args.image,
    conf=args.conf
)


result = results[0]


print("\nDetections:")
print("--------------------")

for box in result.boxes:

    class_id = int(box.cls[0])
    confidence = float(box.conf[0])

    class_name = model.names[class_id]

    print(
        f"{class_name}: {confidence:.3f}"
    )


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


print("--------------------")
print("Detection completed")
print("Input :", args.image)
print("Output:", output_path)