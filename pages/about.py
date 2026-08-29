import streamlit as st
from src.config import APP_TITLE, APP_SUBTITLE, MODEL_PATH

st.markdown('<div class="sm-badge">● PROJECT INFORMATION</div>', unsafe_allow_html=True)
st.title(f"About {APP_TITLE}")
st.caption(APP_SUBTITLE)
st.write("---")

st.markdown(
    """
    ### Overview
    **MASKGUARD AI** is a professional computer vision safety monitoring system. 
    It is designed to automate the compliance audit of face mask wearing guidelines in commercial, industrial, 
    and healthcare facilities.
    
    The application runs local deep learning inference models in real-time to locate individuals and classify their 
    mask-wearing state.
    
    ### Key Features
    - **Live Webcam Stream Monitoring**: Real-time camera processing with low latency frame skipping.
    - **Static Image Analysis**: Compliance auditing on static uploads with detail result tables.
    - **Video compliance scanning**: Analyze pre-recorded video logs frame-by-frame.
    - **Aural safety alerts**: Thread-isolated audio beeps and voice warning announcements ("Warning! No mask detected. Please wear a mask.").
    - **Automated violations archiving**: Capture screenshot logs of compliance violations automatically with cooldown buffers.
    - **Secure local databases**: SQLite tracking system logs timestamps, compliance metrics, and file paths.
    - **Interactive Analytics**: Historical trend and compliance distribution charting powered by Plotly.
    
    ### Technology Stack
    - **Main Interface**: [Streamlit](https://streamlit.io/)
    - **Core Vision Framework**: [Ultralytics YOLO](https://github.com/ultralytics/ultralytics) (v8 API)
    - **Image & Stream Capture**: OpenCV
    - **Database Processing**: SQLite3 & Pandas
    - **Plotting & Visualizations**: Plotly Express
    - **Text-to-Speech Synth**: `pyttsx3`
    
    ### Active Model Configurations
    - **YOLO Weights File**: `models/best.pt`
    - **Primary Detected Classes**:
      - `Mask` (Class ID 0)
      - `NO-Mask` (Class ID 1)
    """
)