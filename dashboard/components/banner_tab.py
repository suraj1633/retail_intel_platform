import pandas as pd
import plotly.express as px
import streamlit as st


def render_banner_tracking_tab(db_session):
    st.header("🖼️ Homepage Banner & Prime Real Estate Tracking")
    st.markdown(
        """
        Monitors homepage hero placements, brand dominance, and banner capture timing across retailer pages.
        """
    )

    from database.db_manager import BannerRecord

    banners = db_session.query(BannerRecord).all()
    if not banners:
        st.info("No homepage banner records captured yet. Banner tracking is scheduled to refresh regularly.")
        return

    banner_data = [
        {
            "Platform": b.platform,
            "Brand": b.brand,
            "Target URL": b.target_url,
            "Screenshot": b.screenshot_path,
            "Timestamp": b.timestamp,
        }
        for b in banners
    ]
    df = pd.DataFrame(banner_data)
    df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")

    platform_options = sorted(df["Platform"].dropna().unique().tolist())
    brand_options = sorted(df["Brand"].dropna().unique().tolist())

    selected_platforms = st.multiselect(
        "Filter by platform",
        platform_options,
        default=platform_options,
        key="banner_platform_filter",
    )
    selected_brands = st.multiselect(
        "Filter by brand",
        brand_options,
        default=brand_options,
        key="banner_brand_filter",
    )

    filtered_df = df[
        df["Platform"].isin(selected_platforms) & df["Brand"].isin(selected_brands)
    ].copy()

    if filtered_df.empty:
        st.warning("No banner captures match the selected filters.")
        return

    total_captures = len(filtered_df)
    brands_tracked = filtered_df["Brand"].nunique()
    latest_capture = filtered_df["Timestamp"].max()
    platform_count = filtered_df["Platform"].nunique()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Banner Captures", total_captures)
    col2.metric("Brands Tracked", brands_tracked)
    col3.metric("Platforms", platform_count)
    col4.metric("Last Capture", latest_capture.strftime("%Y-%m-%d") if pd.notna(latest_capture) else "N/A")

    left_col, right_col = st.columns([1, 1])

    with left_col:
        st.subheader("Banner Share by Brand")
        share_df = filtered_df.groupby("Brand", as_index=False).size().rename(columns={"size": "Banner Count"})
        share_chart = px.pie(
            share_df,
            names="Brand",
            values="Banner Count",
            title="Homepage Banner Share of Voice",
            hole=0.4,
        )
        st.plotly_chart(share_chart, use_container_width=True)

    with right_col:
        st.subheader("Capture Trend")
        trend_df = (
            filtered_df.assign(Date=filtered_df["Timestamp"].dt.floor("D"))
            .groupby("Date", as_index=False)
            .size()
            .rename(columns={"size": "Banner Count"})
        )
        trend_chart = px.line(
            trend_df,
            x="Date",
            y="Banner Count",
            title="Banner Captures Over Time",
            markers=True,
        )
        st.plotly_chart(trend_chart, use_container_width=True)

    st.subheader("Recent Banner Audit Captures")
    st.dataframe(
        filtered_df[["Platform", "Brand", "Timestamp", "Target URL"]].sort_values("Timestamp", ascending=False),
        use_container_width=True,
    )