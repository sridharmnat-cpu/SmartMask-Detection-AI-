import streamlit as st
import pandas as pd
from src.config import APP_TITLE, APP_SUBTITLE, MODEL_PATH
from src.database import get_history_df
from src.detector import load_model
import cv2

# ============================================================
# PAGE HEADER / HERO
# ============================================================
st.markdown(
    """
    <div class="sm-badge">● AI MONITORING SYSTEM</div>
    """,
    unsafe_allow_html=True
)
st.title(APP_TITLE)
st.caption(APP_SUBTITLE)
st.write("---")

# ============================================================
# FETCH REAL DATABASE METRICS
# ============================================================
try:
    df = get_history_df(sort_by="Newest First")
except Exception as e:
    df = pd.DataFrame()

# Compute aggregates
if not df.empty:
    total_detections = int(df["total_persons"].sum())
    total_mask = int(df["mask_count"].sum())
    total_no_mask = int(df["no_mask_count"].sum())
    avg_conf = float(df[df["confidence"] > 0]["confidence"].mean()) if not df[df["confidence"] > 0].empty else 0.0
else:
    total_detections = 0
    total_mask = 0
    total_no_mask = 0
    avg_conf = 0.0

# ============================================================
# TOP STATUS AND STATS BLOCK
# ============================================================
col_status, col_stats = st.columns([1, 3])

with col_status:
    st.subheader("System Status")

    # Model Loading check
    try:
        load_model(MODEL_PATH)
        model_text = "● LOADED"
        model_color = "#16A34A"
        model_loaded = True
    except Exception:
        model_text = "● ERROR"
        model_color = "#DC2626"
        model_loaded = False

    # Camera Access check (try opening device 0 briefly and release it immediately)
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        cap.release()
        cap = cv2.VideoCapture(0)

    if cap.isOpened():
        camera_text = "● READY"
        camera_color = "#16A34A"
        cap.release()
    else:
        camera_text = "● OFFLINE"
        camera_color = "#DC2626"
        cap.release()

    # Main System Online status
    system_text = "● ONLINE" if model_loaded else "● DEGRADED"
    system_color = "#16A34A" if model_loaded else "#DC2626"

    # Visual status card - written with zero indentation to prevent markdown raw code block bugs
    status_panel_html = f"""<div style="background-color: #FFFFFF; border: 1px solid #E4E8EF; border-radius: 18px; padding: 22px; box-shadow: 0 1px 2px rgba(15,23,42,0.05), 0 6px 16px rgba(15,23,42,0.05);">
<div style="font-size: 11px; font-weight: 700; color: #64748B; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 6px;">SYSTEM STATUS</div>
<div style="font-size: 16px; font-weight: 800; color: {system_color}; margin-bottom: 18px;">{system_text}</div>
<div style="font-size: 11px; font-weight: 700; color: #64748B; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 6px;">YOLO MODEL</div>
<div style="font-size: 16px; font-weight: 800; color: {model_color}; margin-bottom: 18px;">{model_text}</div>
<div style="font-size: 11px; font-weight: 700; color: #64748B; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 6px;">WEBCAM CAMERA</div>
<div style="font-size: 16px; font-weight: 800; color: {camera_color};">{camera_text}</div>
</div>"""

    st.markdown(status_panel_html, unsafe_allow_html=True)

with col_stats:
    st.subheader("Key Performance Indicators")

    # Custom HTML layout for 5 KPI cards - written with zero indentation
    kpis_html = f"""<div style="display: flex; justify-content: space-between; gap: 12px; flex-wrap: wrap;">
<div style="flex: 1; min-width: 140px; background-color: #FFFFFF; border: 1px solid #E4E8EF; border-radius: 18px; padding: 20px; text-align: center; box-shadow: 0 1px 2px rgba(15,23,42,0.05), 0 6px 16px rgba(15,23,42,0.05);">
<div style="font-size: 11px; font-weight: 700; color: #64748B; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 8px;">Total Detections</div>
<div style="font-size: 28px; font-weight: 800; color: #2563EB;">{total_detections}</div>
</div>
<div style="flex: 1; min-width: 140px; background-color: #FFFFFF; border: 1px solid #E4E8EF; border-radius: 18px; padding: 20px; text-align: center; box-shadow: 0 1px 2px rgba(15,23,42,0.05), 0 6px 16px rgba(15,23,42,0.05);">
<div style="font-size: 11px; font-weight: 700; color: #64748B; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 8px;">Mask Detected</div>
<div style="font-size: 28px; font-weight: 800; color: #16A34A;">{total_mask}</div>
</div>
<div style="flex: 1; min-width: 140px; background-color: #FFFFFF; border: 1px solid #E4E8EF; border-radius: 18px; padding: 20px; text-align: center; box-shadow: 0 1px 2px rgba(15,23,42,0.05), 0 6px 16px rgba(15,23,42,0.05);">
<div style="font-size: 11px; font-weight: 700; color: #64748B; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 8px;">No Mask</div>
<div style="font-size: 28px; font-weight: 800; color: #DC2626;">{total_no_mask}</div>
</div>
<div style="flex: 1; min-width: 140px; background-color: #FFFFFF; border: 1px solid #E4E8EF; border-radius: 18px; padding: 20px; text-align: center; box-shadow: 0 1px 2px rgba(15,23,42,0.05), 0 6px 16px rgba(15,23,42,0.05);">
<div style="font-size: 11px; font-weight: 700; color: #64748B; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 8px;">Average Confidence</div>
<div style="font-size: 28px; font-weight: 800; color: #D97706;">{avg_conf:.1%}</div>
</div>
<div style="flex: 1; min-width: 140px; background-color: #FFFFFF; border: 1px solid #E4E8EF; border-radius: 18px; padding: 20px; text-align: center; box-shadow: 0 1px 2px rgba(15,23,42,0.05), 0 6px 16px rgba(15,23,42,0.05);">
<div style="font-size: 11px; font-weight: 700; color: #64748B; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 8px;">Current Status</div>
<div style="font-size: 28px; font-weight: 800; color: #16A34A;">ONLINE</div>
</div>
</div>"""

    st.markdown(kpis_html, unsafe_allow_html=True)

# ============================================================
# RECENT MONITORING ACTIVITY
# ============================================================
st.write("---")
st.subheader("Recent Activity Feed")

if df.empty:
    st.info("No activity recorded yet. Start monitoring to see alerts here.")
else:
    # Select key columns for feed
    feed_df = df[["timestamp", "source", "total_persons", "mask_count", "no_mask_count", "confidence", "alert_triggered"]].head(5)

    for idx, row in feed_df.iterrows():
        time_str = row["timestamp"]
        src = row["source"]
        tot = row["total_persons"]
        masks = row["mask_count"]
        no_masks = row["no_mask_count"]
        conf = row["confidence"]

        # Display style card depending on violations
        if no_masks > 0:
            violation_feed_html = f"""<div style="background-color: #FEF2F2; border-left: 4px solid #DC2626; padding: 14px 16px; border-radius: 12px; margin-bottom: 8px;">
<strong style="color:#7F1D1D;">[ALERT] {time_str}</strong> <span style="color:#7F1D1D;">— {no_masks} Safety Violation(s) detected from <em>{src}</em>!</span><br>
<span style="color:#7F1D1D; font-size: 13px;">Total: {tot} faces | Masks: {masks} | No Masks: {no_masks} (Avg Confidence: {conf:.1%})</span>
</div>"""
            st.markdown(violation_feed_html, unsafe_allow_html=True)
        else:
            compliant_feed_html = f"""<div style="background-color: #ECFDF3; border-left: 4px solid #16A34A; padding: 14px 16px; border-radius: 12px; margin-bottom: 8px;">
<strong style="color:#14532D;">[INFO] {time_str}</strong> <span style="color:#14532D;">— Secure scan completed from <em>{src}</em>.</span><br>
<span style="color:#14532D; font-size: 13px;">Total: {tot} faces | Masks: {masks} (Avg Confidence: {conf:.1%})</span>
</div>"""
            st.markdown(compliant_feed_html, unsafe_allow_html=True)