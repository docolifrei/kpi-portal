import pandas as pd
import streamlit as st

st.set_page_config(page_title="KPI AI Analytics Portal", layout="wide")
st.title("📊 KPI Analytics & Insights Portal")

# Data Upload
uploaded_file = st.file_uploader("Upload CSV Data File", type=["csv"])

if uploaded_file:
    # Read and parse date column
    df = pd.read_csv(uploaded_file)
    df["Date"] = pd.to_datetime(df["Date"])

    # Sidebar Filters
    st.sidebar.header("Filter Options")
    selected_company = st.sidebar.selectbox(
        "Select Company", df["Company"].unique()
    )
    timeframe = st.sidebar.radio(
        "Select Timeframe", ["Last Week", "Last Month", "Last 3 Months"]
    )

    # Calculate date boundary
    days_lookup = {"Last Week": 7, "Last Month": 30, "Last 3 Months": 90}
    max_date = df["Date"].max()
    start_date = max_date - pd.Timedelta(days=days_lookup[timeframe])

    # Filter dataset
    filtered_df = df[
        (df["Company"] == selected_company) & (df["Date"] >= start_date)
    ]

    st.subheader(f"Analysis for {selected_company} ({timeframe})")

    # Analyze KPIs
    for kpi_name in filtered_df["KPI"].unique():
        kpi_data = filtered_df[filtered_df["KPI"] == kpi_name].sort_values(
            "Date"
        )

        if len(kpi_data) >= 2:
            start_val = kpi_data["Value"].iloc[0]
            end_val = kpi_data["Value"].iloc[-1]
            pct_change = (
                ((end_val - start_val) / start_val) * 100
                if start_val != 0
                else 0
            )

            # Display metric card with upward/downward delta
            st.metric(
                label=kpi_name,
                value=f"{end_val:,.2f}",
                delta=f"{pct_change:+.2f}%",
            )

            # Automated Insight Engine
            if pct_change > 5:
                st.success(
                    f"**🚀 Upward Trend:** Performance rose by {pct_change:.1f}%. Capitalize on recent strategies driving this growth."
                )
            elif pct_change < -5:
                st.error(
                    f"**⚠️ Downward Trend:** Performance dropped by {abs(pct_change):.1f}%. Investigate operational bottlenecks."
                )
            else:
                st.info(
                    "**➡️ Stable Trajectory:** Metrics remain consistent over this timeframe."
                )