
import streamlit as st
import cv2
import time

from streamlit_webrtc import (
    webrtc_streamer,
    VideoProcessorBase,
    RTCConfiguration,
    WebRtcMode,
)

from src.config import MODEL_PATH
from src.detector import load_model, run_inference
from src.utils import annotate_frame


# ============================================================
# PAGE HEADER
# ============================================================

st.markdown(
    '<div class="sm-badge">● LIVE MONITORING</div>',
    unsafe_allow_html=True
)

st.title("Live Camera")

st.caption(
    "Real-time face mask detection using your browser webcam."
)

st.write("---")


# ============================================================
# LOAD YOLO MODEL
# ============================================================

try:
    model = load_model(MODEL_PATH)
    model_loaded = True

except Exception as e:
    model = None
    model_loaded = False

    st.error(
        f"YOLO model could not be loaded: {e}"
    )


# ============================================================
# STATUS
# ============================================================

col1, col2, col3 = st.columns(3)

with col1:

    if model_loaded:
        st.success("● Model: LOADED")
    else:
        st.error("● Model: ERROR")


with col2:

    st.info("● Camera: BROWSER WEBCAM")


with col3:

    st.info("● Detection: YOLO ACTIVE")


# ============================================================
# WEBRTC CONFIGURATION
# ============================================================

RTC_CONFIGURATION = RTCConfiguration(
    {
        "iceServers": [
            {
                "urls": [
                    "stun:stun.l.google.com:19302"
                ]
            }
        ]
    }
)


# ============================================================
# VIDEO PROCESSOR
# ============================================================

class MaskDetectionProcessor(VideoProcessorBase):

    def __init__(self):

        self.model = model

        # Detection statistics
        self.total_persons = 0
        self.mask_count = 0
        self.no_mask_count = 0

        self.avg_confidence = 0.0

        # FPS
        self.last_time = time.time()
        self.fps = 0.0
        self.frame_counter = 0

    # ========================================================
    # RECEIVE FRAME
    # ========================================================

    def recv(self, frame):

        image = frame.to_ndarray(
            format="bgr24"
        )

        # ====================================================
        # YOLO DETECTION
        # ====================================================

        if self.model is not None:

            try:

                # --------------------------------------------
                # GET SETTINGS
                # --------------------------------------------

                conf_threshold = st.session_state.get(
                    "conf_threshold",
                    0.25
                )

                img_size = st.session_state.get(
                    "img_size",
                    640
                )

                # --------------------------------------------
                # RUN YOLO
                # --------------------------------------------

                detections, raw_result = run_inference(
                    model=self.model,
                    frame=image,
                    conf_threshold=conf_threshold,
                    imgsz=img_size
                )

                # --------------------------------------------
                # TOTAL DETECTIONS
                # --------------------------------------------

                self.total_persons = len(detections)

                # --------------------------------------------
                # MASK COUNT
                # --------------------------------------------

                self.mask_count = sum(
                    1
                    for d in detections
                    if d.category == "mask"
                )

                # --------------------------------------------
                # NO MASK COUNT
                # --------------------------------------------

                self.no_mask_count = sum(
                    1
                    for d in detections
                    if d.category == "no_mask"
                )

                # --------------------------------------------
                # AVERAGE CONFIDENCE
                # --------------------------------------------

                if self.total_persons > 0:

                    self.avg_confidence = (
                        sum(
                            d.confidence
                            for d in detections
                        )
                        / self.total_persons
                    )

                else:

                    self.avg_confidence = 0.0

                # --------------------------------------------
                # ANNOTATE FRAME
                # --------------------------------------------

                annotated = annotate_frame(
                    frame=image,
                    detections=detections,
                    timestamp_enabled=True,
                    stats_enabled=True
                )

            except Exception as e:

                annotated = image.copy()

                cv2.putText(
                    annotated,
                    "Detection Error",
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 0, 255),
                    2
                )

                print(
                    f"Detection error: {e}"
                )

        else:

            # =================================================
            # MODEL NOT LOADED
            # =================================================

            annotated = image.copy()

            cv2.putText(
                annotated,
                "YOLO MODEL NOT LOADED",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (0, 0, 255),
                2
            )

        # ====================================================
        # FPS CALCULATION
        # ====================================================

        self.frame_counter += 1

        current_time = time.time()

        elapsed = (
            current_time - self.last_time
        )

        if elapsed >= 1.0:

            self.fps = (
                self.frame_counter / elapsed
            )

            self.frame_counter = 0

            self.last_time = current_time

        # ====================================================
        # LIVE STATISTICS OVERLAY
        # ====================================================

        cv2.rectangle(
            annotated,
            (10, 10),
            (330, 125),
            (255, 255, 255),
            -1
        )

        # ----------------------------------------------------
        # FPS
        # ----------------------------------------------------

        cv2.putText(
            annotated,
            f"FPS: {self.fps:.1f}",
            (20, 38),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (20, 20, 20),
            2
        )

        # ----------------------------------------------------
        # PERSONS
        # ----------------------------------------------------

        cv2.putText(
            annotated,
            f"Persons: {self.total_persons}",
            (20, 62),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (20, 20, 20),
            2
        )

        # ----------------------------------------------------
        # MASK
        # ----------------------------------------------------

        cv2.putText(
            annotated,
            f"Mask: {self.mask_count}",
            (20, 86),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (0, 150, 0),
            2
        )

        # ----------------------------------------------------
        # NO MASK
        # ----------------------------------------------------

        cv2.putText(
            annotated,
            f"No Mask: {self.no_mask_count}",
            (20, 110),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (0, 0, 220),
            2
        )

        # ====================================================
        # RETURN FRAME
        # ====================================================

        return frame.from_ndarray(
            annotated,
            format="bgr24"
        )


# ============================================================
# LIVE CAMERA CARD
# ============================================================

with st.container(border=True):

    st.subheader("📷 Browser Webcam")

    st.write(
        "Click **START** below and allow camera permission "
        "when your browser asks."
    )

    # ========================================================
    # START WEBRTC
    # ========================================================

    if model_loaded:

        webrtc_ctx = webrtc_streamer(
            key="smartmask-live-camera",

            # IMPORTANT:
            # Use WebRtcMode enum instead of string
            mode=WebRtcMode.SENDRECV,

            rtc_configuration=RTC_CONFIGURATION,

            video_processor_factory=MaskDetectionProcessor,

            media_stream_constraints={
                "video": True,
                "audio": False,
            },

            async_processing=True,
        )

    else:

        st.error(
            "Camera cannot start because the "
            "YOLO model is not loaded."
        )


# ============================================================
# INFORMATION
# ============================================================

st.write("---")

st.info(
    "💡 For the deployed website, camera access happens "
    "through your browser. Click START and choose "
    "**Allow** when Chrome asks for camera permission."
)
```
