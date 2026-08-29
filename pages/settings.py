import streamlit as st
from src.config import (
    DEFAULT_CONF,
    DEFAULT_IMGSZ,
    DEFAULT_FRAME_SKIP,
    DEFAULT_VOICE_ALERT,
    DEFAULT_VOICE_COOLDOWN,
    DEFAULT_AUTO_SCREENSHOT,
    DEFAULT_SCREENSHOT_COOLDOWN,
)

# Initialize session state safely
if "conf_threshold" not in st.session_state:
    st.session_state.conf_threshold = DEFAULT_CONF

if "img_size" not in st.session_state:
    st.session_state.img_size = DEFAULT_IMGSZ

if "frame_skip" not in st.session_state:
    st.session_state.frame_skip = DEFAULT_FRAME_SKIP

if "voice_alert" not in st.session_state:
    st.session_state.voice_alert = DEFAULT_VOICE_ALERT

if "voice_cooldown" not in st.session_state:
    st.session_state.voice_cooldown = DEFAULT_VOICE_COOLDOWN

if "auto_screenshot" not in st.session_state:
    st.session_state.auto_screenshot = DEFAULT_AUTO_SCREENSHOT

if "screenshot_cooldown" not in st.session_state:
    st.session_state.screenshot_cooldown = DEFAULT_SCREENSHOT_COOLDOWN
import os
import platform
import torch
from src.config import MODEL_PATH
from src.detector import load_model
from src.alerts import play_voice_alert

st.markdown('<div class="sm-badge">● SYSTEM CONFIGURATION</div>', unsafe_allow_html=True)
st.title("System Settings")
st.caption("Configure YOLO detector settings, safety alert parameters, and verify model resource status.")
st.write("---")

# Verify model loading status
try:
    load_model(MODEL_PATH)
    model_status = "● Model loaded successfully"
    model_status_color = "#16A34A"
except Exception as e:
    model_status = f"● Model load error: {e}"
    model_status_color = "#DC2626"

# ============================================================
# DETECTOR SETTINGS SECTION
# ============================================================
st.subheader("YOLO Detection Settings")
col_d1, col_d2 = st.columns(2)

with col_d1:
    conf = st.slider(
        "Confidence Threshold",
        min_value=0.10,
        max_value=1.00,
        value=st.session_state.conf_threshold,
        step=0.05,
        help="Minimum confidence required to classify and label detections."
    )
    st.session_state.conf_threshold = conf

    frame_skip = st.slider(
        "Frame Skipping Rate (Live Camera)",
        min_value=1,
        max_value=10,
        value=st.session_state.frame_skip,
        step=1,
        help="Higher values skip more frames to optimize FPS on low-end CPUs. 1 means no skipping."
    )
    st.session_state.frame_skip = frame_skip

with col_d2:
    imgsz = st.selectbox(
        "Inference Image Size",
        options=[320, 416, 512, 640],
        index=[320, 416, 512, 640].index(st.session_state.img_size),
        help="Inference frame dimensions. Default is 416. Smaller runs faster; larger is more accurate."
    )
    st.session_state.img_size = imgsz

# ============================================================
# ALERTS & ANNOUNCEMENTS SECTION
# ============================================================
st.write("---")
st.subheader("Voice & Screenshot Safety Alerts")

col_a1, col_a2 = st.columns(2)

with col_a1:
    voice_on = st.toggle(
        "Enable Voice Warnings",
        value=st.session_state.voice_alert,
        help="If enabled, a local spoken message plays when a person without a mask is detected."
    )
    st.session_state.voice_alert = voice_on

    voice_cooldown = st.slider(
        "Voice Alert Cooldown (seconds)",
        min_value=1,
        max_value=60,
        value=int(st.session_state.voice_cooldown),
        step=1,
        help="Minimum time to wait between spoken warning announcements."
    )
    st.session_state.voice_cooldown = float(voice_cooldown)

with col_a2:
    shot_on = st.toggle(
        "Enable Auto Violation Screenshots",
        value=st.session_state.auto_screenshot,
        help="If enabled, saves a picture to the violations/ directory when a compliance violation occurs."
    )
    st.session_state.auto_screenshot = shot_on

    shot_cooldown = st.slider(
        "Screenshot Cooldown (seconds)",
        min_value=1,
        max_value=60,
        value=int(st.session_state.screenshot_cooldown),
        step=1,
        help="Minimum time to wait between saving screenshot files."
    )
    st.session_state.screenshot_cooldown = float(shot_cooldown)

# Audio speech test button
st.write(" ")
if st.button("Test Voice Alert System", width="stretch"):
    success = play_voice_alert("Voice alert system working correctly.", cooldown=0.0, force=True)
    if success:
        st.success("Test voice triggered on background thread.")
    else:
        st.error("Audio player is busy or pyttsx3 could not run.")

# ============================================================
# DIAGNOSTICS & SYSTEM CONFIGURATION
# ============================================================
st.write("---")
st.subheader("Diagnostic Information")

col_s1, col_s2 = st.columns(2)

with col_s1:
    st.text_input("Active YOLO Model Path", value=MODEL_PATH, disabled=True)
    st.markdown(f"Status: <span style='color:{model_status_color}; font-weight:bold;'>{model_status}</span>", unsafe_allow_html=True)

with col_s2:
    device = "CUDA (GPU Acceleration)" if torch.cuda.is_available() else "CPU Mode"
    st.text_input("Hardware Device Allocation", value=device, disabled=True)

    details = f"OS: {platform.system()} {platform.release()} | Python: {platform.python_version()}"
    st.text_input("Environment Info", value=details, disabled=True)