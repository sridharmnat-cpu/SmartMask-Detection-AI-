import streamlit as st
import cv2
import numpy as np
from PIL import Image
import pandas as pd
import traceback

from src.config import MODEL_PATH
from src.detector import load_model, run_inference
from src.utils import annotate_frame
from src.database import log_detection

st.markdown('<div class="sm-badge">● STATIC IMAGE ANALYSIS</div>', unsafe_allow_html=True)
st.title("Image Detection")
st.caption("Upload an image to perform face mask detection and compliance audits.")
st.write("---")

# ============================================================
# UPLOAD INPUT
# ============================================================
uploaded_file = st.file_uploader(
    "Choose an image file",
    type=["jpg", "jpeg", "png", "webp", "bmp"],
    help="Supported formats: JPG, JPEG, PNG, WEBP, BMP"
)

if uploaded_file is not None:
    # Read uploaded image bytes as OpenCV image
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    frame = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    if frame is None:
        st.error("Error: Could not decode uploaded image.")
    else:
        # Save a copy of the original image for comparison
        original_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Load model using global settings from st.session_state
        try:
            model = load_model(MODEL_PATH)

            # Perform inference
            with st.spinner("Analyzing image..."):
                detections, raw_result = run_inference(
                    model=model,
                    frame=frame,
                    conf_threshold=st.session_state.conf_threshold,
                    imgsz=st.session_state.img_size
                )

            # Render and annotate
            annotated_frame = annotate_frame(
                frame=frame,
                detections=detections,
                timestamp_enabled=False,  # Don't draw live timestamp overlay on static files
                stats_enabled=True
            )
            annotated_rgb = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)

            # Displays
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Original Image")
                st.image(original_rgb, width="stretch")
            with col2:
                st.subheader("Detected Output")
                st.image(annotated_rgb, width="stretch")

            # Log results to Database (sensible logging on upload completion)
            total = len(detections)
            masks = sum(1 for d in detections if d.category == "mask")
            no_masks = sum(1 for d in detections if d.category == "no_mask")
            avg_conf = sum(d.confidence for d in detections) / total if total > 0 else 0.0

            # Log to DB
            log_detection(
                source=uploaded_file.name,
                total_persons=total,
                mask_count=masks,
                no_mask_count=no_masks,
                confidence=avg_conf,
                alert_triggered=(no_masks > 0),
                screenshot_path=None  # No auto-screenshots for upload logs
            )

            # Check results and display structured table
            st.write("---")
            st.subheader("Detection Summary")

            if total == 0:
                st.info("No person detected in this image.")
            else:
                # Result banner
                if no_masks > 0:
                    st.markdown(
                        f'<div class="violation-banner"><h4 style="margin:0;color:#7F1D1D;">⚠ SAFETY VIOLATION</h4>'
                        f'<p style="margin:4px 0 0 0;">{no_masks} of {total} detected without a mask.</p></div>',
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        '<div class="safe-banner"><h4 style="margin:0;color:#14532D;">✓ MASK DETECTED — SAFE</h4>'
                        '<p style="margin:4px 0 0 0;">All detected persons are compliant.</p></div>',
                        unsafe_allow_html=True
                    )

                # Metric display
                col_m1, col_m2, col_m3, col_m4 = st.columns(4)
                col_m1.metric("Faces Detected", total)
                col_m2.metric("Mask Compliance", f"{masks}/{total}")
                col_m3.metric("No Mask Violations", no_masks)
                col_m4.metric("Avg Confidence", f"{avg_conf:.1%}")

                # Table format
                st.subheader("Detection Details")
                table_data = []
                for idx, det in enumerate(detections, start=1):
                    table_data.append({
                        "Person ID": f"P{idx}",
                        "Class Name": det.class_name,
                        "Category": det.category.upper().replace("_", " "),
                        "Confidence": f"{det.confidence:.1%}",
                        "Bounding Box (xyxy)": str(det.bbox)
                    })
                st.table(table_data)

        except Exception as e:
            st.error("Detection failed.")
            with st.expander("Technical Exception Details"):
                st.code(traceback.format_exc())
else:
    # Nice Empty State
    st.info("Please upload an image file in the selector above to analyze.")