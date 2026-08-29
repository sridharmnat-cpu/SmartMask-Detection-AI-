import streamlit as st
import cv2
import numpy as np
import os
import time
import tempfile
import traceback
import pandas as pd

from src.config import MODEL_PATH
from src.detector import load_model, run_inference
from src.utils import annotate_frame
from src.database import log_detection

st.markdown('<div class="sm-badge">● VIDEO FILE ANALYSIS</div>', unsafe_allow_html=True)
st.title("Video Detection & Analysis")
st.caption("Upload a pre-recorded security video file to scan for mask safety compliance.")
st.write("---")

uploaded_video = st.file_uploader(
    "Choose a video file",
    type=["mp4", "avi", "mov", "mkv"],
    help="Supported formats: MP4, AVI, MOV, MKV"
)

if uploaded_video is not None:
    # Save uploaded video bytes to a temporary file
    temp_dir = tempfile.gettempdir()
    input_path = os.path.join(temp_dir, f"input_{uploaded_video.name}")
    output_path = os.path.join(temp_dir, f"processed_{uploaded_video.name}")

    with open(input_path, "wb") as f:
        f.write(uploaded_video.read())

    st.info("Video uploaded. Initializing processor...")

    # Open video capture
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        st.error("Error: Could not open the uploaded video file.")
    else:
        # Extract properties
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # Guard against zero or NaN values
        if fps <= 0 or pd.isna(fps):
            fps = 25.0
        if total_frames <= 0:
            total_frames = 1

        # UI components for progress tracking
        progress_bar = st.progress(0.0)
        status_text = st.empty()

        # Statistics aggregations
        persons_history = []
        mask_history = []
        nomask_history = []
        conf_history = []

        # Define video writer
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        start_time = time.time()
        frame_idx = 0

        try:
            model = load_model(MODEL_PATH)

            # Use columns to display real-time progress stats
            col_stat1, col_stat2, col_stat3 = st.columns(3)
            p_lbl = col_stat1.empty()
            m_lbl = col_stat2.empty()
            nm_lbl = col_stat3.empty()

            # Read and process frames sequentially to prevent high memory usage
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                frame_idx += 1

                # Perform inference (no frame skipping for pre-recorded compliance reports)
                detections, raw_result = run_inference(
                    model=model,
                    frame=frame,
                    conf_threshold=st.session_state.conf_threshold,
                    imgsz=st.session_state.img_size
                )

                # Compute stats
                total_faces = len(detections)
                mask_faces = sum(1 for d in detections if d.category == "mask")
                no_mask_faces = sum(1 for d in detections if d.category == "no_mask")
                avg_conf = sum(d.confidence for d in detections) / total_faces if total_faces > 0 else 0.0

                persons_history.append(total_faces)
                mask_history.append(mask_faces)
                nomask_history.append(no_mask_faces)
                if total_faces > 0:
                    conf_history.append(avg_conf)

                # Annotate and write to output
                annotated = annotate_frame(
                    frame=frame,
                    detections=detections,
                    timestamp_enabled=False,
                    stats_enabled=True
                )
                out.write(annotated)

                # Update progress
                pct = frame_idx / total_frames
                progress_bar.progress(min(pct, 1.0))
                status_text.text(f"Processing frame {frame_idx}/{total_frames} ({pct:.1%})...")

                p_lbl.metric("Current Persons", total_faces)
                m_lbl.metric("Current Masks", mask_faces)
                nm_lbl.metric("Current Violations", no_mask_faces)

            # Close writer and readers
            cap.release()
            out.release()

            elapsed = time.time() - start_time
            avg_process_fps = frame_idx / elapsed if elapsed > 0 else 0

            status_text.success(f"Processing complete in {elapsed:.1f} seconds! (Avg Process Speed: {avg_process_fps:.1f} FPS)")

            # Compute session averages
            total_person_count = max(persons_history, default=0)
            avg_masks = np.mean(mask_history) if mask_history else 0.0
            avg_nomasks = np.mean(nomask_history) if nomask_history else 0.0
            avg_conf_total = np.mean(conf_history) if conf_history else 0.0
            total_violations = sum(1 for nm in nomask_history if nm > 0)

            # Display overall stats
            st.write("---")
            st.subheader("Video Scan Summary")
            col_o1, col_o2, col_o3, col_o4 = st.columns(4)
            col_o1.metric("Total Frames", frame_idx)
            col_o2.metric("Peak Face Count", total_person_count)
            col_o3.metric("Avg Violations / Frame", f"{avg_nomasks:.2f}")
            col_o4.metric("Avg Conf", f"{avg_conf_total:.1%}")

            # Log this video processing summary event in the Database
            log_detection(
                source=f"Video File: {uploaded_video.name}",
                total_persons=int(np.max(persons_history)) if persons_history else 0,
                mask_count=int(np.mean(mask_history)) if mask_history else 0,
                no_mask_count=int(np.mean(nomask_history)) if nomask_history else 0,
                confidence=float(avg_conf_total),
                alert_triggered=(total_violations > 0),
                screenshot_path=None
            )

            # Provide Download Button
            with open(output_path, "rb") as file_bytes:
                st.download_button(
                    label="Download Processed Video",
                    data=file_bytes,
                    file_name=f"processed_{uploaded_video.name}",
                    mime="video/mp4",
                    width="stretch"
                )

        except Exception as e:
            st.error("Detection failed.")
            with st.expander("Technical details:"):
                st.code(traceback.format_exc())
        finally:
            # Clean up input file to save disk space
            if os.path.exists(input_path):
                try:
                    os.remove(input_path)
                except Exception:
                    pass
else:
    st.info("Upload a video file (MP4, AVI, MOV) to execute compliance scanning.")