import streamlit as st
import cv2
import time
from datetime import datetime
import traceback

from src.config import MODEL_PATH
from src.detector import load_model, run_inference
from src.alerts import play_voice_alert, trigger_beep_alert
from src.utils import annotate_frame, save_violation_screenshot
from src.database import log_detection

# ============================================================
# STATE SETUP FOR CAMERA CONTROLS
# ============================================================
if "camera_active" not in st.session_state:
    st.session_state.camera_active = False

# ============================================================
# PAGE HEADER
# ============================================================
st.markdown('<div class="sm-badge">● LIVE MONITORING</div>', unsafe_allow_html=True)
st.title("Live Camera")
st.caption("Real-time face mask compliance monitoring. The cached YOLO model is loaded once and used to process the camera stream.")
st.write("---")

# ============================================================
# NON-INVASIVE STATUS PROBES (DISPLAY ONLY)
# ============================================================
try:
    load_model(MODEL_PATH)
    model_status_label = "Model: LOADED"
    model_dot = "dot-green"
except Exception:
    model_status_label = "Model: ERROR"
    model_dot = "dot-red"

if st.session_state.camera_active:
    camera_status_label = "Camera: STREAMING"
    camera_dot = "dot-green"
else:
    camera_status_label = "Camera: STANDBY"
    camera_dot = "dot-gray"

detection_status_label = "Detection: ACTIVE" if st.session_state.camera_active else "Detection: STANDBY"
detection_dot = "dot-green" if st.session_state.camera_active else "dot-gray"

# ============================================================
# CAMERA PANEL — WHITE BORDERED CARD
# ============================================================
with st.container(border=True):

    # --- Top row: status chips (left) + LIVE / STANDBY badge (right) ---
    live_badge_class = "on" if st.session_state.camera_active else "off"
    live_badge_text = "LIVE" if st.session_state.camera_active else "STANDBY"

    st.markdown(
        f"""
        <div style="display:flex; justify-content:space-between; align-items:center; padding: 10px 14px 4px 14px;">
            <div>
                <span class="status-chip"><span class="dot {camera_dot}"></span>{camera_status_label}</span>
                <span class="status-chip"><span class="dot {model_dot}"></span>{model_status_label}</span>
                <span class="status-chip"><span class="dot {detection_dot}"></span>{detection_status_label}</span>
            </div>
            <div class="live-badge {live_badge_class}"><span class="pulse"></span>{live_badge_text}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # --- Controller buttons ---
    col_ctrl1, col_ctrl2 = st.columns(2)
    with col_ctrl1:
        start_btn = st.button("Start Camera", width="stretch", disabled=st.session_state.camera_active)
        if start_btn:
            st.session_state.camera_active = True
            st.rerun()
    with col_ctrl2:
        stop_btn = st.button("Stop Camera", width="stretch", disabled=not st.session_state.camera_active)
        if stop_btn:
            st.session_state.camera_active = False
            st.rerun()

    # --- Alert Banner and Live Video Feed ---
    alert_placeholder = st.empty()
    video_placeholder = st.empty()

    # Show default banner when not active
    alert_placeholder.markdown('<div class="safe-banner">CAMERA STANDBY — PRESS START</div>', unsafe_allow_html=True)

    # --- Live statistics cards ---
    st.write("")
    col_m1, col_m2, col_m3, col_m4, col_m5, col_m6 = st.columns(6)
    metric_fps = col_m1.empty()
    metric_infer = col_m2.empty()
    metric_conf = col_m3.empty()
    metric_total = col_m4.empty()
    metric_mask = col_m5.empty()
    metric_nomask = col_m6.empty()

    # Populate placeholders with idle defaults so the cards render before the loop starts
    metric_fps.metric("FPS", "0.0")
    metric_infer.metric("Inference", "0 ms")
    metric_conf.metric("Confidence", "0.0%")
    metric_total.metric("Total Persons", 0)
    metric_mask.metric("Mask", 0)
    metric_nomask.metric("No Mask", 0)

# ============================================================
# MAIN CAMERA CAPTURE AND PROCESSING LOOP
# ============================================================
if st.session_state.camera_active:
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        cap.release()
        cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        st.error("Error: Could not access the webcam camera. Check if it's connected or in use by another app.")
        st.session_state.camera_active = False
    else:
        frame_count = 0
        last_detections = []

        fps_counter = 0
        fps_timer = time.time()
        current_fps = 0.0
        last_infer_time = 0.0

        last_log_time = 0.0
        db_log_cooldown = 4.0

        try:
            model = load_model(MODEL_PATH)

            while st.session_state.camera_active:
                ret, frame = cap.read()
                if not ret:
                    st.error("Failed to capture frame from webcam.")
                    break

                frame_count += 1
                now = time.time()

                run_infer_this_frame = (frame_count % st.session_state.get("frame_skip", 1) == 0)

                if run_infer_this_frame:
                    t_start = time.time()
                    try:
                        detections, raw_result = run_inference(
                            model=model,
                            frame=frame,
                            conf_threshold=st.session_state.get("conf_threshold", 0.25),
                            imgsz=st.session_state.get("img_size", 640)
                        )
                        last_detections = detections
                        last_infer_time = time.time() - t_start
                    except Exception as e:
                        print(f"Inference exception: {e}")
                        raise e
                else:
                    detections = last_detections

                annotated = annotate_frame(
                    frame=frame,
                    detections=detections,
                    timestamp_enabled=True,
                    stats_enabled=True
                )

                total_faces = len(detections)
                mask_faces = sum(1 for d in detections if d.category == "mask")
                no_mask_faces = sum(1 for d in detections if d.category == "no_mask")
                avg_conf = sum(d.confidence for d in detections) / total_faces if total_faces > 0 else 0.0

                frame_rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
                video_placeholder.image(frame_rgb, channels="RGB", use_container_width=True)

                if no_mask_faces > 0:
                    violation_conf = max((d.confidence for d in detections if d.category == "no_mask"), default=0.0)
                    ts_alert = datetime.now().strftime("%H:%M:%S")

                    alert_placeholder.markdown(
                        f"""
                        <div class="violation-banner">
                            <h4 style="margin: 0; color: #7F1D1D;">SAFETY ALERT</h4>
                            <p style="margin: 4px 0 0 0;">No mask detected! Compliance violation in progress.</p>
                            <small>Confidence: {violation_conf:.1%} | Time: {ts_alert}</small>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    trigger_beep_alert()

                    if st.session_state.get("voice_alert", False):
                        play_voice_alert(
                            message="Warning! No mask detected. Please wear a mask.",
                            cooldown=st.session_state.get("voice_cooldown", 5)
                        )

                    screenshot_saved_path = None
                    if st.session_state.get("auto_screenshot", False):
                        screenshot_saved_path = save_violation_screenshot(
                            frame=annotated,
                            cooldown=st.session_state.get("screenshot_cooldown", 5)
                        )

                    if (screenshot_saved_path is not None) or (now - last_log_time >= db_log_cooldown):
                        log_detection(
                            source="Live Camera (Violation)",
                            total_persons=total_faces,
                            mask_count=mask_faces,
                            no_mask_count=no_mask_faces,
                            confidence=avg_conf,
                            alert_triggered=True,
                            screenshot_path=screenshot_saved_path
                        )
                        last_log_time = now

                else:
                    alert_placeholder.markdown(
                        '<div class="safe-banner">No active safety violations detected.</div>',
                        unsafe_allow_html=True
                    )

                    if total_faces > 0 and (now - last_log_time >= db_log_cooldown):
                        log_detection(
                            source="Live Camera (Compliance)",
                            total_persons=total_faces,
                            mask_count=mask_faces,
                            no_mask_count=no_mask_faces,
                            confidence=avg_conf,
                            alert_triggered=False,
                            screenshot_path=None
                        )
                        last_log_time = now

                fps_counter += 1
                elapsed = now - fps_timer
                if elapsed >= 0.5:
                    current_fps = fps_counter / elapsed
                    fps_counter = 0
                    fps_timer = now

                metric_fps.metric("FPS", f"{current_fps:.1f}")
                metric_infer.metric("Inference", f"{last_infer_time*1000:.0f} ms")
                metric_conf.metric("Confidence", f"{avg_conf:.1%}")
                metric_total.metric("Total Persons", total_faces)
                metric_mask.metric("Mask", mask_faces)
                metric_nomask.metric("No Mask", no_mask_faces)

                time.sleep(0.005)

        except Exception as e:
            st.error("Detection failed.")
            st.session_state.camera_active = False
            with st.expander("Technical details:"):
                st.code(traceback.format_exc())
        finally:
            if 'cap' in locals() and cap is not None:
                cap.release()
            video_placeholder.empty()
            alert_placeholder.markdown('<div class="safe-banner">CAMERA STANDBY — PRESS START</div>', unsafe_allow_html=True)
            metric_fps.metric("FPS", "0.0")
            metric_infer.metric("Inference", "0 ms")
            metric_conf.metric("Confidence", "0.0%")
            metric_total.metric("Total Persons", 0)
            metric_mask.metric("Mask", 0)
            metric_nomask.metric("No Mask", 0)