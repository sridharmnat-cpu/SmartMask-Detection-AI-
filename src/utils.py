import os
import cv2
import time
from datetime import datetime
from src.config import (
    VIOLATION_DIR,
    COLOR_MASK_BGR,
    COLOR_NO_MASK_BGR,
    COLOR_OTHER_BGR
)

_last_screenshot_time = 0.0

def annotate_frame(
    frame,
    detections,
    timestamp_enabled: bool = True,
    stats_enabled: bool = True
):
    """
    Annotates the OpenCV frame with bounding boxes, labels, timestamp, and stats overlay.
    """
    annotated = frame.copy()
    h, w = annotated.shape[:2]
    
    # Draw detections
    for i, det in enumerate(detections, start=1):
        x1, y1, x2, y2 = det.bbox
        
        # Select color based on category
        if det.category == "mask":
            color = COLOR_MASK_BGR
        elif det.category == "no_mask":
            color = COLOR_NO_MASK_BGR
        else:
            color = COLOR_OTHER_BGR
            
        # Draw bounding box
        cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
        
        # Build text label (e.g. "P1 Mask 95%")
        label = f"P{i}  {det.class_name}  {det.confidence:.0%}"
        
        # Measure text size for background box
        (tw, th), _ = cv2.getTextSize(
            label,
            cv2.FONT_HERSHEY_SIMPLEX,
            0.52,
            2
        )
        
        label_y = max(y1 - 6, th + 10)
        
        # Draw label background box
        cv2.rectangle(
            annotated,
            (x1, label_y - th - 9),
            (x1 + tw + 12, label_y),
            color,
            -1
        )
        
        # Put text
        cv2.putText(
            annotated,
            label,
            (x1 + 6, label_y - 6),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.52,
            (255, 255, 255),
            1,
            cv2.LINE_AA
        )

    # Draw timestamp overlay (top left)
    if timestamp_enabled:
        ts_text = datetime.now().strftime("%d %b %Y  •  %H:%M:%S")
        cv2.rectangle(
            annotated,
            (10, 10),
            (250, 40),
            (7, 11, 20),
            -1
        )
        cv2.putText(
            annotated,
            ts_text,
            (18, 31),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 255),
            1,
            cv2.LINE_AA
        )

    # Draw detection stats summary bar (bottom left)
    if stats_enabled:
        total = len(detections)
        mask = sum(1 for d in detections if d.category == "mask")
        no_mask = sum(1 for d in detections if d.category == "no_mask")
        
        count_text = f"Persons: {total}  |  Mask: {mask}  |  No Mask: {no_mask}"
        
        # Draw background container
        box_width = min(w - 20, 440)
        cv2.rectangle(
            annotated,
            (10, h - 42),
            (10 + box_width, h - 10),
            (7, 11, 20),
            -1
        )
        cv2.putText(
            annotated,
            count_text,
            (18, h - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            (235, 240, 248),
            1,
            cv2.LINE_AA
        )
        
    return annotated

def save_violation_screenshot(frame, cooldown: float = 3.0, force: bool = False) -> str:
    """
    Saves the annotated frame as a violation screenshot if cooldown allows.
    
    Returns:
        The path of the saved file, or None if skipped/failed.
    """
    global _last_screenshot_time
    now = time.time()
    
    if not force and (now - _last_screenshot_time < cooldown):
        return None
        
    _last_screenshot_time = now
    
    filename = datetime.now().strftime("violation_%Y%m%d_%H%M%S.jpg")
    filepath = os.path.join(VIOLATION_DIR, filename)
    
    try:
        success = cv2.imwrite(filepath, frame)
        if success:
            return filepath
    except Exception as e:
        print(f"Screenshot save failure: {e}")
        
    return None
