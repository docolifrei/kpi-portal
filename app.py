import pandas as pd
import streamlit as st

# Configure the Streamlit page layout
st.set_page_config(page_title="Support KPI AI Portal", layout="wide")
st.title("📊 Customer Support KPI & AI Analytics Portal")

# Interactive File Uploader
uploaded_file = st.file_uploader("Upload raw CSV dataset", type=["csv"])

if uploaded_file is not None:
    # Read the dataset
    df = pd.read_csv(uploaded_file)

    # Convert the 'date' column to proper datetime format
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # Clean numeric columns to ensure proper math operations
    numeric_cols = [
        "csat_score",
        "total_aht_duration_seconds",
        "wait_time",
        "agent_speed_to_answer",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Sidebar Filters
    st.sidebar.header("Filter Options")

    # Filter 1: Company selection
    companies = sorted(df["company"].dropna().unique())
    selected_company = st.sidebar.selectbox("Select Company", companies)

    # Filter 2: Date range selection
    timeframe = st.sidebar.radio(
        "Select Timeframe", ["Last Week", "Last Month", "Last 3 Months"]
    )

    # Define date range bounds based on dataset max date
    max_date = df["date"].max()
    days_map = {"Last Week": 7, "Last Month": 30, "Last 3 Months": 90}
    days_count = days_map[timeframe]

    start_date = max_date - pd.Timedelta(days=days_count)
    previous_start = start_date - pd.Timedelta(days=days_count)

    # Filter data for selected company
    company_df = df[df["company"] == selected_company]

    # Current period vs Previous period slices for comparison
    current_df = company_df[
        (company_df["date"] >= start_date) & (company_df["date"] <= max_date)
    ]
    previous_df = company_df[
        (company_df["date"] >= previous_start)
        & (company_df["date"] < start_date)
    ]

    st.subheader(f"Dashboard for {selected_company}")
    st.caption(
        f"Data range: {start_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}"
    )

    if current_df.empty:
        st.warning("No records found for the selected timeframe.")
    else:
        # Define KPI configuration dictionary
        kpi_configs = [
            {
                "label": "Total Ticket Volume",
                "col": "ticket_id",
                "type": "count",
                "higher_is_better": False,
            },
            {
                "label": "Avg CSAT Score",
                "col": "csat_score",
                "type": "mean",
                "higher_is_better": True,
            },
            {
                "label": "Avg Handle Time (sec)",
                "col": "total_aht_duration_seconds",
                "type": "mean",
                "higher_is_better": False,
            },
            {
                "label": "Avg Wait Time (sec)",
                "col": "wait_time",
                "type": "mean",
                "higher_is_better": False,
            },
        ]

        # Display KPIs in side-by-side columns
        cols = st.columns(len(kpi_configs))

        for idx, kpi in enumerate(kpi_configs):
            col_name = kpi["col"]

            # Calculate current period metric
            if kpi["type"] == "count":
                curr_val = len(current_df)
                prev_val = len(previous_df)
            else:
                curr_val = current_df[col_name].mean()
                prev_val = (
                    previous_df[col_name].mean() if not previous_df.empty else 0
                )

            # Calculate percentage change (delta)
            if prev_val and prev_val > 0:
                pct_change = ((curr_val - prev_val) / prev_val) * 100
            else:
                pct_change = 0.0

            # Render KPI Card
            with cols[idx]:
                val_str = (
                    f"{curr_val:,.1f}"
                    if kpi["type"] == "mean"
                    else f"{curr_val:,}"
                )
                st.metric(
                    label=kpi["label"],
                    value=val_str,
                    delta=f"{pct_change:+.1f}%",
                )

        st.divider()
        st.subheader("💡 AI Insights & Trend Highlights")

        # Generate automated insights per KPI
        for kpi in kpi_configs:
            col_name = kpi["col"]
            curr_val = (
                len(current_df)
                if kpi["type"] == "count"
                else current_df[col_name].mean()
            )
            prev_val = (
                len(previous_df)
                if kpi["type"] == "count"
                else (
                    previous_df[col_name].mean() if not previous_df.empty else 0
                )
            )

            pct_change = (
                ((curr_val - prev_val) / prev_val) * 100
                if prev_val and prev_val > 0
                else 0
            )
            is_improvement = (
                (pct_change > 0)
                if kpi["higher_is_better"]
                else (pct_change < 0)
            )

            if abs(pct_change) >= 2.0:
                if is_improvement:
                    st.success(
                        f"**Positive Trend ({kpi['label']}):** Shifted by **{pct_change:+.1f}%**. Actionable Insight: Support performance improved during this period; maintain current team workflows."
                    )
                else:
                    st.error(
                        f"**Attention Needed ({kpi['label']}):** Shifted by **{pct_change:+.1f}%**. Actionable Insight: Negative trend detected; review agent staffing levels and queue resolution."
                    )
            else:
                st.info(
                    f"**Stable Trajectory ({kpi['label']}):** Minimal movement of **{pct_change:+.1f}%** relative to previous period."
                )
