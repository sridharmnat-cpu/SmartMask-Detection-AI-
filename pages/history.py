import streamlit as st
import pandas as pd
import os
from datetime import datetime
from src.database import get_history_df, clear_history
from src.config import VIOLATION_DIR

st.markdown('<div class="sm-badge">● ARCHIVE & COMPLIANCE LOG</div>', unsafe_allow_html=True)
st.title("Detection History & Archive")
st.caption("Browse, search, filter compliance records, download violation screenshots, and export CSV logs.")
st.write("---")

# ============================================================
# FILTER & CONTROLS TOOLBAR
# ============================================================
col_f1, col_f2, col_f3 = st.columns([2, 1, 1])

with col_f1:
    search_query = st.text_input("🔍 Search by Source Name", placeholder="e.g. Webcam, image.jpg")

with col_f2:
    filter_cat = st.selectbox("Category Filter", ["All", "Violations Only", "No Violations"])

with col_f3:
    sort_by = st.selectbox("Sort Order", [
        "Newest First",
        "Oldest First",
        "Highest Violation Count",
        "Highest Confidence"
    ])

# ============================================================
# FETCH DATA
# ============================================================
try:
    df = get_history_df(
        search_query=search_query,
        filter_category=filter_cat,
        sort_by=sort_by
    )
except Exception as e:
    df = pd.DataFrame()
    st.error(f"Error reading database: {e}")

# ============================================================
# ACTIONS PANEL (EXPORT & PURGE)
# ============================================================
if not df.empty:
    col_act1, col_act2 = st.columns([3, 1])

    with col_act1:
        # Convert df to CSV bytes
        csv_bytes = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Export Log to CSV",
            data=csv_bytes,
            file_name=f"maskguard_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

    with col_act2:
        # Confirmation box for purge
        if st.button("Clear All History", type="secondary"):
            st.session_state.confirm_purge = True

        if st.session_state.get("confirm_purge", False):
            st.warning("Are you absolutely sure you want to permanently delete all history logs and screenshots?")
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                if st.button("Yes, Purge"):
                    clear_history()
                    st.success("History log deleted successfully.")
                    st.session_state.confirm_purge = False
                    st.rerun()
            with col_p2:
                if st.button("Cancel"):
                    st.session_state.confirm_purge = False
                    st.rerun()

    # ============================================================
    # SUMMARY STRIP
    # ============================================================
    total_rows = len(df)
    total_violation_rows = int((df["no_mask_count"] > 0).sum())
    st.markdown(
        f"""
        <div style="display:flex; gap:10px; margin: 6px 0 18px 0; flex-wrap:wrap;">
        <div style="background:#FFFFFF; border:1px solid #E4E8EF; border-radius:14px; padding:10px 16px;">
        <span style="font-size:11px; color:#64748B; font-weight:700; text-transform:uppercase; letter-spacing:0.06em;">Records</span>
        <span style="font-size:16px; font-weight:800; color:#0F172A; margin-left:8px;">{total_rows}</span>
        </div>
        <div style="background:#FFFFFF; border:1px solid #E4E8EF; border-radius:14px; padding:10px 16px;">
        <span style="font-size:11px; color:#64748B; font-weight:700; text-transform:uppercase; letter-spacing:0.06em;">Violations</span>
        <span style="font-size:16px; font-weight:800; color:#DC2626; margin-left:8px;">{total_violation_rows}</span>
        </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ============================================================
    # DATA TABLE RENDERING
    # ============================================================
    # Style the DataFrame display
    display_df = df.copy()
    display_df["alert_triggered"] = display_df["alert_triggered"].apply(lambda x: "⚠️ VIOLATION" if x == 1 else "✓ Compliant")
    display_df["confidence"] = display_df["confidence"].apply(lambda x: f"{x:.1%}")

    # Hide id and screenshot_path from main visual table
    visible_df = display_df[["timestamp", "source", "total_persons", "mask_count", "no_mask_count", "confidence", "alert_triggered"]]
    st.dataframe(visible_df, width="stretch")

    # ============================================================
    # VIOLATION SCREENSHOTS VIEW SECTION
    # ============================================================
    st.write("---")
    st.subheader("Violation Screenshot Archive")

    # Filter rows with saved screenshots
    screenshot_rows = df[df["screenshot_path"].notna() & (df["screenshot_path"] != "")]

    if screenshot_rows.empty:
        st.info("No violation screenshots are logged in this query.")
    else:
        # Create a dropdown selector to preview the image
        shot_options = {}
        for idx, row in screenshot_rows.iterrows():
            filename = os.path.basename(row["screenshot_path"])
            label = f"{row['timestamp']} | Source: {row['source']} | Violations: {row['no_mask_count']} ({filename})"
            shot_options[label] = row["screenshot_path"]

        selected_label = st.selectbox("Select a violation log to preview screenshot:", list(shot_options.keys()))
        selected_path = shot_options[selected_label]

        # Verify file exists on disk
        if os.path.exists(selected_path):
            st.image(selected_path, caption=selected_label, width="stretch")

            # Download file button
            with open(selected_path, "rb") as img_file:
                st.download_button(
                    label="Download Original Screenshot File",
                    data=img_file,
                    file_name=os.path.basename(selected_path),
                    mime="image/jpeg"
                )
        else:
            st.error(f"Error: Screenshot file could not be found at path: {selected_path}")

else:
    st.info("No matching records found in the database. Perform a scan or adjust your filter query.")