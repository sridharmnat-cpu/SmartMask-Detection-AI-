
import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


# ============================================================
# PAGE CONFIG — MUST BE THE FIRST STREAMLIT COMMAND
# ============================================================
st.set_page_config(
    page_title="SmartMask Detection AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# IMPORTS
# ============================================================
from src.config import (
    DEFAULT_CONF,
    DEFAULT_IMGSZ,
    DEFAULT_FRAME_SKIP,
    DEFAULT_VOICE_ALERT,
    DEFAULT_VOICE_COOLDOWN,
    DEFAULT_AUTO_SCREENSHOT,
    DEFAULT_SCREENSHOT_COOLDOWN,
    APP_TITLE,
    APP_SUBTITLE
)

from src.database import init_db


# ============================================================
# INITIALIZE DATABASE
# ============================================================
init_db()


# ============================================================
# INITIALIZE SESSION STATE
# ============================================================
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


# ============================================================
# GLOBAL APPEARANCE
# ============================================================
st.markdown(
    """
    <style>

    /* ========================================================
       GOOGLE FONT
       ======================================================== */

    @import url(
        'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap'
    );


    /* ========================================================
       ROOT VARIABLES
       ======================================================== */

    :root {
        --sm-bg: #F4F6F9;
        --sm-panel: #FFFFFF;
        --sm-border: #E4E8EF;

        --sm-text: #0F172A;
        --sm-text-secondary: #64748B;

        --sm-accent: #2563EB;
        --sm-accent-hover: #1D4ED8;
        --sm-accent-soft: #EFF4FF;

        --sm-success: #16A34A;
        --sm-success-soft: #ECFDF3;

        --sm-danger: #DC2626;
        --sm-danger-soft: #FEF2F2;

        --sm-warning: #D97706;

        --sm-radius: 18px;

        --sm-shadow:
            0 1px 2px rgba(15, 23, 42, 0.05),
            0 6px 16px rgba(15, 23, 42, 0.05);
    }


    /* ========================================================
       BASE APP
       ======================================================== */

    .stApp {
        background-color: var(--sm-bg);
        color: var(--sm-text);
    }

    .block-container {
        max-width: 1280px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }


    /* ========================================================
       GLOBAL FONT
       ======================================================== */

    body,
    .stApp,
    p,
    span,
    label {
        font-family: 'Inter', sans-serif;
    }


    /* ========================================================
       SIDEBAR
       ======================================================== */

    [data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid var(--sm-border);
        font-family: 'Inter', sans-serif;
    }


    /* ========================================================
       SIDEBAR BRANDING
       ======================================================== */

    .sidebar-brand {
        text-align: center;
        padding: 8px 0 18px 0;
    }

    .sidebar-logo {
        font-size: 32px;
        line-height: 1.2;
        margin-bottom: 4px;
    }

    .sidebar-title {
        font-size: 16px;
        font-weight: 800;
        color: #0F172A !important;
        letter-spacing: -0.01em;
        line-height: 1.2;
    }

    .sidebar-subtitle {
        font-size: 12px;
        font-weight: 600;
        color: #2563EB !important;
        margin-top: 2px;
        line-height: 1.2;
    }

    .sidebar-description {
        font-size: 11px;
        font-weight: 500;
        color: #64748B !important;
        margin-top: 7px;
        line-height: 1.4;
    }

    .sidebar-divider {
        height: 1px;
        background-color: #E4E8EF;
        margin: 0 0 8px 0;
    }


    /* ========================================================
       SIDEBAR NAVIGATION
       ======================================================== */

    [data-testid="stSidebarNav"] {
        padding-top: 0.5rem;
    }

    [data-testid="stSidebarNav"] a {
        border-radius: 10px !important;
        color: #374151 !important;
        background-color: transparent !important;
        font-weight: 600 !important;
        margin: 2px 6px;
    }

    [data-testid="stSidebarNav"] a span,
    [data-testid="stSidebarNav"] a p {
        color: #374151 !important;
        font-weight: 600 !important;
    }

    [data-testid="stSidebarNav"] a svg {
        color: #374151 !important;
        fill: #374151 !important;
    }


    /* ========================================================
       SIDEBAR NAVIGATION — HOVER
       ======================================================== */

    [data-testid="stSidebarNav"] a:hover {
        background-color: #EFF4FF !important;
        color: #2563EB !important;
    }

    [data-testid="stSidebarNav"] a:hover span,
    [data-testid="stSidebarNav"] a:hover p {
        color: #2563EB !important;
    }

    [data-testid="stSidebarNav"] a:hover svg {
        color: #2563EB !important;
        fill: #2563EB !important;
    }


    /* ========================================================
       SIDEBAR NAVIGATION — ACTIVE PAGE
       ======================================================== */

    [data-testid="stSidebarNav"] a[aria-current="page"] {
        background-color: #EFF4FF !important;
        color: #2563EB !important;
        font-weight: 700 !important;
    }

    [data-testid="stSidebarNav"] a[aria-current="page"] span,
    [data-testid="stSidebarNav"] a[aria-current="page"] p {
        color: #2563EB !important;
        font-weight: 700 !important;
    }

    [data-testid="stSidebarNav"] a[aria-current="page"] svg {
        color: #2563EB !important;
        fill: #2563EB !important;
    }


    /* ========================================================
       SIDEBAR HEADINGS / TEXT
       ======================================================== */

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] h4,
    [data-testid="stSidebar"] h5,
    [data-testid="stSidebar"] h6 {
        color: #111827 !important;
    }

    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label {
        color: #111827;
    }


    /* ========================================================
       TYPOGRAPHY
       ======================================================== */

    h1,
    h2,
    h3,
    h4,
    h5,
    h6 {
        color: var(--sm-text) !important;
        font-family: 'Inter', sans-serif;
        font-weight: 700;
    }

    h1 {
        font-size: 26px !important;
    }

    h2 {
        font-size: 19px !important;
    }

    h3 {
        font-size: 16px !important;
    }

    [data-testid="stCaptionContainer"] {
        color: var(--sm-text-secondary) !important;
    }

    hr {
        border-color: var(--sm-border) !important;
    }


    /* ========================================================
       KPI CARDS
       ======================================================== */

    .kpi-card {
        background-color: var(--sm-panel);
        border: 1px solid var(--sm-border);
        border-radius: var(--sm-radius);
        padding: 22px;
        text-align: center;
        margin: 5px;
        transition:
            transform 0.15s ease,
            box-shadow 0.15s ease;
        box-shadow: var(--sm-shadow);
    }

    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow:
            0 4px 10px rgba(15, 23, 42, 0.08),
            0 12px 28px rgba(15, 23, 42, 0.06);
    }

    .kpi-title {
        font-size: 11px;
        font-weight: 700;
        color: var(--sm-text-secondary);
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 8px;
    }

    .kpi-value {
        font-size: 24px;
        font-weight: 800;
        color: var(--sm-text);
    }

    .kpi-value.safe {
        color: var(--sm-success);
    }

    .kpi-value.violation {
        color: var(--sm-danger);
    }

    .kpi-value.accent {
        color: var(--sm-accent);
    }


    /* ========================================================
       STATUS PANEL
       ======================================================== */

    .status-panel {
        background-color: var(--sm-panel);
        border: 1px solid var(--sm-border);
        border-radius: var(--sm-radius);
        padding: 20px;
        margin-bottom: 12px;
        box-shadow: var(--sm-shadow);
    }

    .status-indicator {
        font-size: 12px;
        font-weight: 700;
        margin: 6px 0;
    }

    .status-card {
        background-color: var(--sm-panel);
        border: 1px solid var(--sm-border);
        border-radius: var(--sm-radius);
        padding: 16px 20px;
        margin: 5px;
        display: flex;
        align-items: center;
        gap: 10px;
        box-shadow: var(--sm-shadow);
    }

    .status-dot {
        height: 9px;
        width: 9px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 8px;
    }

    .status-dot.online {
        background-color: var(--sm-success);
        box-shadow: 0 0 6px rgba(22, 163, 74, 0.5);
    }

    .status-dot.offline {
        background-color: var(--sm-danger);
        box-shadow: 0 0 6px rgba(220, 38, 38, 0.5);
    }

    .status-label {
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        color: var(--sm-text-secondary);
    }


    /* ========================================================
       ALERT BANNERS
       ======================================================== */

    .violation-banner {
        background-color: var(--sm-danger-soft);
        border: 1px solid #FCA5A5;
        border-radius: 16px;
        color: #7F1D1D;
        padding: 18px;
        text-align: center;
        margin: 10px 0;
        font-weight: 600;
    }

    .safe-banner {
        background-color: var(--sm-success-soft);
        border: 1px solid #86EFAC;
        border-radius: 16px;
        color: #14532D;
        padding: 18px;
        text-align: center;
        margin: 10px 0;
        font-weight: 600;
    }


    /* ========================================================
       HERO / HEADER
       ======================================================== */

    .app-header {
        padding: 10px 0 20px 0;
        border-bottom: 1px solid var(--sm-border);
        margin-bottom: 24px;
    }

    .app-header h1 {
        font-size: 26px;
        margin: 0;
        font-weight: 800;
        letter-spacing: -0.02em;
    }

    .app-header p {
        color: var(--sm-text-secondary);
        font-size: 14px;
        margin-top: 4px;
        font-weight: 500;
    }

    .sm-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background-color: var(--sm-accent-soft);
        color: var(--sm-accent);
        border: 1px solid #C7D9FE;
        border-radius: 999px;
        padding: 5px 14px;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        margin-bottom: 12px;
    }


    /* ========================================================
       CAMERA / VIDEO / IMAGE
       ======================================================== */

    [data-testid="stImage"] img {
        border-radius: 18px !important;
        border: 1px solid var(--sm-border);
        box-shadow: var(--sm-shadow);
    }

    video {
        border-radius: 18px !important;
        border: 1px solid var(--sm-border);
        box-shadow: var(--sm-shadow);
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: var(--sm-panel);
        border: 1px solid var(--sm-border) !important;
        border-radius: 20px !important;
        box-shadow: var(--sm-shadow);
        padding: 4px;
    }


    /* ========================================================
       STATUS CHIPS
       ======================================================== */

    .status-chip {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background-color: #F8FAFC;
        border: 1px solid var(--sm-border);
        border-radius: 999px;
        padding: 5px 12px;
        font-size: 12px;
        font-weight: 600;
        color: var(--sm-text);
        margin-right: 8px;
    }

    .status-chip .dot {
        height: 7px;
        width: 7px;
        border-radius: 50%;
        display: inline-block;
    }

    .dot-green {
        background-color: var(--sm-success);
        box-shadow: 0 0 5px rgba(22, 163, 74, 0.5);
    }

    .dot-red {
        background-color: var(--sm-danger);
        box-shadow: 0 0 5px rgba(220, 38, 38, 0.5);
    }

    .dot-gray {
        background-color: #94A3B8;
    }


    /* ========================================================
       LIVE BADGE
       ======================================================== */

    .live-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        border-radius: 999px;
        padding: 5px 12px;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        float: right;
    }

    .live-badge.on {
        background-color: var(--sm-danger-soft);
        color: var(--sm-danger);
        border: 1px solid #FCA5A5;
    }

    .live-badge.off {
        background-color: #F1F5F9;
        color: #64748B;
        border: 1px solid var(--sm-border);
    }

    .live-badge .pulse {
        height: 7px;
        width: 7px;
        border-radius: 50%;
        background-color: currentColor;
        display: inline-block;
    }

    .live-badge.on .pulse {
        animation: sm-pulse 1.4s infinite;
    }

    @keyframes sm-pulse {
        0% {
            opacity: 1;
        }

        50% {
            opacity: 0.35;
        }

        100% {
            opacity: 1;
        }
    }


    /* ========================================================
       BUTTONS
       ======================================================== */

    .stButton > button {
        border-radius: 10px;
        background-color: var(--sm-accent);
        color: white !important;
        font-weight: 600;
        border: none;
        padding: 8px 18px;
        transition:
            background-color 0.15s ease,
            transform 0.1s ease;
        box-shadow:
            0 1px 2px rgba(37, 99, 235, 0.25);
    }

    .stButton > button:hover {
        background-color: var(--sm-accent-hover);
        border: none;
        color: white !important;
    }

    .stButton > button:disabled {
        background-color: #CBD5E1;
        color: #F8FAFC !important;
    }


    /* ========================================================
       DOWNLOAD BUTTON
       ======================================================== */

    .stDownloadButton > button {
        border-radius: 10px;
        font-weight: 600;
        border: 1px solid var(--sm-border);
        background-color: var(--sm-panel);
        color: var(--sm-text) !important;
    }

    .stDownloadButton > button:hover {
        border-color: var(--sm-accent);
        color: var(--sm-accent) !important;
    }


    /* ========================================================
       TABLES
       ======================================================== */

    div[data-testid="stTable"] table {
        background-color: var(--sm-panel);
        color: var(--sm-text);
        border: 1px solid var(--sm-border);
        border-radius: 14px;
    }

    div[data-testid="stDataFrame"] {
        border: 1px solid var(--sm-border);
        border-radius: 14px;
        overflow: hidden;
    }


    /* ========================================================
       METRICS
       ======================================================== */

    div[data-testid="stMetric"] {
        background-color: var(--sm-panel);
        border: 1px solid var(--sm-border);
        border-radius: 18px;
        padding: 16px;
        box-shadow: var(--sm-shadow);
    }

    div[data-testid="stMetricLabel"] {
        color: var(--sm-text-secondary) !important;
    }


    /* ========================================================
       INPUTS
       ======================================================== */

    .stTextInput input,
    .stSelectbox div[data-baseweb="select"],
    .stTextArea textarea {
        border-radius: 10px !important;
        border: 1px solid var(--sm-border) !important;
        background-color: var(--sm-panel) !important;
    }


    /* ========================================================
       EXPANDER
       ======================================================== */

    div[data-testid="stExpander"] {
        background-color: var(--sm-panel);
        border: 1px solid var(--sm-border);
        border-radius: 16px;
    }


    /* ========================================================
       FILE UPLOADER
       ======================================================== */

    [data-testid="stFileUploaderDropzone"] {
        background-color: #FAFBFD;
        border: 2px dashed #C7D2E0;
        border-radius: 20px;
    }


    /* ========================================================
       TABS
       ======================================================== */

    button[data-baseweb="tab"] {
        font-weight: 600;
    }


    /* ========================================================
       SCROLLBAR
       ======================================================== */

    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }

    ::-webkit-scrollbar-track {
        background: var(--sm-bg);
    }

    ::-webkit-scrollbar-thumb {
        background: #CBD5E1;
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: var(--sm-accent);
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# PAGE ROUTING
# ============================================================

dashboard_page = st.Page(
    "pages/dashboard.py",
    title="Dashboard",
    icon="📊",
    default=True
)

image_detection_page = st.Page(
    "pages/image_detection.py",
    title="Image Detection",
    icon="🖼️"
)

live_camera_page = st.Page(
    "pages/live_camera.py",
    title="Live Camera",
    icon="📷"
)

video_detection_page = st.Page(
    "pages/video_detection.py",
    title="Video Detection",
    icon="🎥"
)

analytics_page = st.Page(
    "pages/analytics.py",
    title="Analytics",
    icon="📈"
)

history_page = st.Page(
    "pages/history.py",
    title="Detection History",
    icon="📁"
)

settings_page = st.Page(
    "pages/settings.py",
    title="Settings",
    icon="⚙️"
)

about_page = st.Page(
    "pages/about.py",
    title="About",
    icon="ℹ️"
)


# ============================================================
# NAVIGATION SYSTEM
# ============================================================

pg = st.navigation(
    {
        "MONITORING": [
            dashboard_page,
            image_detection_page,
            live_camera_page,
            video_detection_page
        ],

        "ANALYSIS & ARCHIVE": [
            analytics_page,
            history_page
        ],

        "SYSTEM": [
            settings_page,
            about_page
        ]
    }
)


# ============================================================
# SIDEBAR BRANDING
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <div class="sidebar-brand">

            <div class="sidebar-logo">
                🛡️
            </div>

            <div class="sidebar-title">
                SMARTMASK
            </div>

            <div class="sidebar-subtitle">
                Detection AI
            </div>

            <div class="sidebar-description">
                AI-Powered Face Mask Monitoring
            </div>

        </div>

        <div class="sidebar-divider"></div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# RUN APPLICATION
# ============================================================

pg.run()
