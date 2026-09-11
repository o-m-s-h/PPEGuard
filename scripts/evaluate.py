from ultralytics import YOLO


model = YOLO("models/best.pt")

metrics = model.val(
    data="data/data.yaml",
    split="test",
    workers=0
)

print("\nEvaluation Results")
print("------------------------")
print("mAP50     :", metrics.box.map50)
print("mAP50-95  :", metrics.box.map)
print("Precision :", metrics.box.mp)
print("Recall    :", metrics.box.mr)