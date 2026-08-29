from ultralytics import YOLO

model = YOLO("yolov8n.pt")

model.train(
    data="Mask Wearing.v6-roboflow-train-v3.yolov8/data.yaml",
    epochs=10,
    imgsz=640
)