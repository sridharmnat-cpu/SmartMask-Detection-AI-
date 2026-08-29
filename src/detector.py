import os
import streamlit as st
from ultralytics import YOLO

@st.cache_resource(show_spinner="Loading YOLO model...")
def load_model(model_path: str):
    """
    Loads the YOLO model and caches it to prevent reloading.
    """
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found at: {model_path}")
    
    # Load YOLO model
    model = YOLO(model_path)
    return model

class DetectionResult:
    def __init__(self, class_name: str, confidence: float, bbox: tuple, category: str):
        self.class_name = class_name
        self.confidence = confidence
        self.bbox = bbox  # (x1, y1, x2, y2)
        self.category = category  # 'mask', 'no_mask', 'other'

def classify_class_name(class_name: str) -> str:
    """
    Classifies a raw class name into 'mask', 'no_mask', or 'other'.
    Matches the original app classification logic.
    """
    name = class_name.lower().replace("_", "-")
    
    # Check 'no mask' variants first
    if (
        "no-mask" in name
        or "no mask" in name
        or "nomask" in name
        or name.startswith("no")
    ):
        return "no_mask"
        
    if "mask" in name:
        return "mask"
        
    return "other"

def run_inference(model, frame, conf_threshold: float = 0.50, imgsz: int = 416):
    """
    Runs YOLO inference on a frame/image.
    
    Returns:
        tuple (list of DetectionResult, original_yolo_result_object)
        
    Raises:
        Exception: Real exceptions from YOLO prediction to be handled upstream.
    """
    # Predict using YOLO (verbose=False to avoid cluttering logs)
    results = model.predict(
        frame,
        conf=conf_threshold,
        imgsz=imgsz,
        verbose=False
    )
    
    if not results or len(results) == 0:
        return [], None
        
    result_obj = results[0]
    detections = []
    
    if result_obj.boxes is not None:
        for box in result_obj.boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            
            # Map class ID to class name safely
            if isinstance(model.names, dict):
                class_name = model.names.get(cls_id, str(cls_id))
            else:
                class_name = model.names[cls_id]
                
            category = classify_class_name(class_name)
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            
            detections.append(
                DetectionResult(
                    class_name=class_name,
                    confidence=conf,
                    bbox=(x1, y1, x2, y2),
                    category=category
                )
            )
            
    return detections, result_obj
