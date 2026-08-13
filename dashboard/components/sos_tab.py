import pandas as pd
import plotly.express as px
import streamlit as st

from engine.analytics import calculate_share_of_voice


def render_share_of_voice_tab(listings_df):
    st.header("📊 Share of Voice (SoV) & Search Visibility")
    st.markdown(
        """
        Compares brand visibility across retailer search pages, helping rank market share and keyword dominance.
        """
    )

    if listings_df.empty:
        st.warning("No product listing data available.")
        return

    sov_df = calculate_share_of_voice(listings_df)
    if sov_df.empty:
        st.info("No search visibility data is available for the current dataset.")
        return

    platform_options = sorted(sov_df["platform"].dropna().unique().tolist())
    brand_options = sorted(sov_df["brand"].dropna().unique().tolist())

    selected_platforms = st.multiselect(
        "Filter by platform",
        platform_options,
        default=platform_options,
        key="sov_platform_filter",
    )
    selected_brands = st.multiselect(
        "Filter by brand",
        brand_options,
        default=brand_options,
        key="sov_brand_filter",
    )

    filtered_df = sov_df[
        sov_df["platform"].isin(selected_platforms) & sov_df["brand"].isin(selected_brands)
    ].copy()

    if filtered_df.empty:
        st.warning("No Share of Voice data matches the selected filters.")
        return

    total_search_appearances = int(filtered_df["search_appearances"].sum())
    top_brand_name = filtered_df.sort_values("sov_percentage", ascending=False).iloc[0]["brand"]
    top_brand_share = float(filtered_df.sort_values("sov_percentage", ascending=False).iloc[0]["sov_percentage"])
    avg_platform_share = float(filtered_df.groupby("platform")["sov_percentage"].mean().mean())

    col1, col2, col3 = st.columns(3)
    col1.metric("Search Appearances", total_search_appearances)
    col2.metric("Top Brand", top_brand_name)
    col3.metric("Average Platform Share", f"{avg_platform_share:.1f}%")

    st.subheader("Share of Voice by Platform")
    platform_bar = px.bar(
        filtered_df,
        x="platform",
        y="sov_percentage",
        color="brand",
        barmode="group",
        title="Brand Share of Voice by Platform",
        text_auto=".1f",
    )
    st.plotly_chart(platform_bar, use_container_width=True)

    left_col, right_col = st.columns([1, 1])

    with left_col:
        st.subheader("Brand Visibility Distribution")
        pie_fig = px.pie(
            filtered_df,
            names="brand",
            values="search_appearances",
            title="Brand Search Presence",
            hole=0.4,
        )
        st.plotly_chart(pie_fig, use_container_width=True)

    with right_col:
        st.subheader("Platform Summary")
        platform_summary = (
            filtered_df.groupby("platform", as_index=False)["sov_percentage"].sum()
            .rename(columns={"sov_percentage": "Total Share %"})
        )
        st.dataframe(platform_summary.sort_values("Total Share %", ascending=False), use_container_width=True)

    st.subheader("Detailed Share by Brand and Platform")
    st.dataframe(
        filtered_df[["platform", "brand", "search_appearances", "sov_percentage"]].sort_values(
            ["platform", "sov_percentage"], ascending=[True, False]
        ),
        use_container_width=True,
    )

    st.caption(f"Leading brand in the selected view: {top_brand_name} with {top_brand_share:.1f}% share of voice.")