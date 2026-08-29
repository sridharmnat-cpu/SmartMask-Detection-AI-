import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src.database import get_history_df

st.markdown('<div class="sm-badge">● HISTORICAL ANALYTICS</div>', unsafe_allow_html=True)
st.title("Safety Analytics Dashboard")
st.caption("Visual compliance summaries compiled from historical logs.")
st.write("---")

# ============================================================
# LOAD REAL HISTORY FROM DATABASE
# ============================================================
try:
    df = get_history_df(sort_by="Oldest First")
except Exception as e:
    df = pd.DataFrame()
    st.error(f"Failed to query database: {e}")

if df.empty:
    st.info("No monitoring history found. Start scanning using the Live Camera or Image Detection to build analytical charts.")
else:
    # Set proper types
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Grid structure for charts
    col_c1, col_c2 = st.columns(2)

    # ------------------------------------------------------------
    # CHART 1: COMPLIANCE RATIO (PIE)
    # ------------------------------------------------------------
    with col_c1:
        st.subheader("Compliance Ratio")
        total_masks = df["mask_count"].sum()
        total_violations = df["no_mask_count"].sum()

        if total_masks == 0 and total_violations == 0:
            st.warning("No faces logged in history yet.")
        else:
            pie_data = pd.DataFrame({
                "Category": ["Compliant (Mask)", "Violation (No Mask)"],
                "Count": [total_masks, total_violations]
            })

            fig_pie = px.pie(
                pie_data,
                values="Count",
                names="Category",
                color="Category",
                color_discrete_map={
                    "Compliant (Mask)": "#16A34A",
                    "Violation (No Mask)": "#DC2626"
                },
                hole=0.4
            )
            fig_pie.update_layout(
                paper_bgcolor="#FFFFFF",
                plot_bgcolor="#FFFFFF",
                font_color="#0F172A",
                margin=dict(l=20, r=20, t=20, b=20),
                legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
            )
            st.plotly_chart(fig_pie, width="stretch")

    # ------------------------------------------------------------
    # CHART 2: DETECTION TRENDS (LINE)
    # ------------------------------------------------------------
    with col_c2:
        st.subheader("Detection Trends Over Time")

        # Group by timestamp (date/hour) for cleaner charts if dataset is large
        df_sorted = df.sort_values("timestamp")

        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=df_sorted["timestamp"],
            y=df_sorted["mask_count"],
            name="Masks Detected",
            line=dict(color="#16A34A", width=2),
            mode="lines+markers"
        ))
        fig_trend.add_trace(go.Scatter(
            x=df_sorted["timestamp"],
            y=df_sorted["no_mask_count"],
            name="Violations (No Mask)",
            line=dict(color="#DC2626", width=2),
            mode="lines+markers"
        ))

        fig_trend.update_layout(
            paper_bgcolor="#FFFFFF",
            plot_bgcolor="#FFFFFF",
            font_color="#0F172A",
            xaxis=dict(gridcolor="#E4E8EF"),
            yaxis=dict(gridcolor="#E4E8EF"),
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
            margin=dict(l=40, r=40, t=20, b=20)
        )
        st.plotly_chart(fig_trend, width="stretch")

    st.write("---")
    col_c3, col_c4 = st.columns(2)

    # ------------------------------------------------------------
    # CHART 3: AVERAGE CONFIDENCE SCATTER/TREND
    # ------------------------------------------------------------
    with col_c3:
        st.subheader("Inference Confidence Trend")
        fig_conf = px.area(
            df_sorted,
            x="timestamp",
            y="confidence",
            labels={"confidence": "Average Confidence"},
            color_discrete_sequence=["#D97706"]
        )
        fig_conf.update_layout(
            paper_bgcolor="#FFFFFF",
            plot_bgcolor="#FFFFFF",
            font_color="#0F172A",
            xaxis=dict(gridcolor="#E4E8EF"),
            yaxis=dict(gridcolor="#E4E8EF", tickformat=".0%"),
            margin=dict(l=40, r=40, t=20, b=20)
        )
        st.plotly_chart(fig_conf, width="stretch")

    # ------------------------------------------------------------
    # CHART 4: VIOLATIONS HOURLY PROFILE (BAR)
    # ------------------------------------------------------------
    with col_c4:
        st.subheader("Violation Incidents by Source")

        # Aggregate violations by source
        source_df = df.groupby("source")["no_mask_count"].sum().reset_index()
        # Only show sources with violations
        source_df = source_df[source_df["no_mask_count"] > 0]

        if source_df.empty:
            st.info("No safety violations have been logged yet.")
        else:
            fig_bar = px.bar(
                source_df,
                x="source",
                y="no_mask_count",
                color="no_mask_count",
                color_continuous_scale=["#F87171", "#991B1B"],
                labels={"no_mask_count": "Violation Count"}
            )
            fig_bar.update_layout(
                paper_bgcolor="#FFFFFF",
                plot_bgcolor="#FFFFFF",
                font_color="#0F172A",
                xaxis=dict(gridcolor="#E4E8EF"),
                yaxis=dict(gridcolor="#E4E8EF"),
                coloraxis_showscale=False,
                margin=dict(l=40, r=40, t=20, b=20)
            )
            st.plotly_chart(fig_bar, width="stretch")