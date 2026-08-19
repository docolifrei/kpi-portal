import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Support KPI AI Portal", layout="wide", page_icon="📊"
)
st.title("📊 Customer Support KPI & AI Analytics Portal")

# Interactive File Uploader
uploaded_file = st.file_uploader("Upload raw CSV dataset", type=["csv"])

if uploaded_file is not None:
    # Read and prepare dataset
    df = pd.read_csv(uploaded_file)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # Numeric data cleanup
    numeric_cols = [
        "csat_score",
        "total_aht_duration_seconds",
        "wait_time",
        "agent_speed_to_answer",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Sidebar Options
    st.sidebar.header("Filter Options")
    companies = sorted(df["company"].dropna().unique())
    selected_company = st.sidebar.selectbox("Select Company", companies)

    timeframe = st.sidebar.radio(
        "Select Timeframe", ["Last Week", "Last Month", "Last 3 Months"]
    )

    # Date calculations
    max_date = df["date"].max()
    days_map = {"Last Week": 7, "Last Month": 30, "Last 3 Months": 90}
    days_count = days_map[timeframe]

    start_date = max_date - pd.Timedelta(days=days_count)
    previous_start = start_date - pd.Timedelta(days=days_count)

    # Filtered slices
    company_df = df[df["company"] == selected_company]
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
        # KPI Cards Display
        kpi_configs = [
            {
                "label": "Total Ticket Volume",
                "col": "ticket_id",
                "type": "count",
                "better": False,
            },
            {
                "label": "Avg CSAT Score",
                "col": "csat_score",
                "type": "mean",
                "better": True,
            },
            {
                "label": "Avg Handle Time (sec)",
                "col": "total_aht_duration_seconds",
                "type": "mean",
                "better": False,
            },
            {
                "label": "Avg Wait Time (sec)",
                "col": "wait_time",
                "type": "mean",
                "better": False,
            },
        ]

        cols = st.columns(len(kpi_configs))
        for idx, kpi in enumerate(kpi_configs):
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
                else 0.0
            )

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

        # Dynamic Interactive Charts Section
        st.subheader("📈 Interactive Performance Trends")
        tab1, tab2, tab3 = st.tabs(
            ["Ticket Volume", "CSAT Score Trend", "Handle & Wait Times"]
        )

        # Prepare daily aggregated data frame
        daily_df = (
            current_df.groupby(current_df["date"].dt.date)
            .agg(
                {
                    "ticket_id": "count",
                    "csat_score": "mean",
                    "total_aht_duration_seconds": "mean",
                    "wait_time": "mean",
                }
            )
            .rename(
                columns={
                    "ticket_id": "Daily Tickets",
                    "csat_score": "CSAT Score",
                    "total_aht_duration_seconds": "Avg Handle Time (s)",
                    "wait_time": "Avg Wait Time (s)",
                }
            )
        )

        with tab1:
            st.line_chart(daily_df[["Daily Tickets"]])

        with tab2:
            st.line_chart(daily_df[["CSAT Score"]])

        with tab3:
            st.line_chart(
                daily_df[["Avg Handle Time (s)", "Avg Wait Time (s)"]]
            )

        st.divider()
        st.subheader("💡 AI Insights & Trend Highlights")

        # Automated Insights
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
                (pct_change > 0) if kpi["better"] else (pct_change < 0)
            )

            if abs(pct_change) >= 2.0:
                if is_improvement:
                    st.success(
                        f"**Positive Trend ({kpi['label']}):** Shifted by **{pct_change:+.1f}%**. Support performance improved; maintain current workflows."
                    )
                else:
                    st.error(
                        f"**Attention Needed ({kpi['label']}):** Shifted by **{pct_change:+.1f}%**. Negative trend detected; review agent queue response times."
                    )
            else:
                st.info(
                    f"**Stable Trajectory ({kpi['label']}):** Minimal movement of **{pct_change:+.1f}%** relative to previous period."
                )
