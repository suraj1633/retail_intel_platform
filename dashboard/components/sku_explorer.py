import pandas as pd
import plotly.express as px
import streamlit as st

from engine.brand_parser import extract_brand_badges


def render_sku_explorer_tab(listings_df):
    st.header("🔍 SKU Explorer & Product Drill-Down")
    st.markdown("Review live listings, badge quality, pricing, and retailer placement by brand and platform.")

    if listings_df.empty:
        st.warning("No listings to display.")
        return

    working_df = listings_df.copy()
    working_df["Detected Badges"] = working_df.apply(
        lambda r: ", ".join(extract_brand_badges(r["title"], r["brand"])) or "Standard",
        axis=1,
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        selected_brand = st.multiselect(
            "Filter by Brand",
            options=sorted(working_df["brand"].dropna().unique().tolist()),
            key="sku_brand_filter",
        )
    with col2:
        selected_oem = st.multiselect(
            "Filter by OEM",
            options=sorted(working_df["oem"].dropna().unique().tolist()),
            key="sku_oem_filter",
        )
    with col3:
        selected_platform = st.multiselect(
            "Filter by Platform",
            options=sorted(working_df["platform"].dropna().unique().tolist()),
            key="sku_platform_filter",
        )

    filtered_df = working_df.copy()
    if selected_brand:
        filtered_df = filtered_df[filtered_df["brand"].isin(selected_brand)]
    if selected_oem:
        filtered_df = filtered_df[filtered_df["oem"].isin(selected_oem)]
    if selected_platform:
        filtered_df = filtered_df[filtered_df["platform"].isin(selected_platform)]

    if filtered_df.empty:
        st.warning("No SKU records match the current filters.")
        return

    total_skus = len(filtered_df)
    avg_price = float(filtered_df["price"].fillna(0).mean())
    brands = filtered_df["brand"].nunique()
    top_platform = filtered_df["platform"].value_counts().idxmax()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("SKUs Visible", total_skus)
    col2.metric("Avg Price", f"${avg_price:,.2f}")
    col3.metric("Brands", brands)
    col4.metric("Lead Platform", top_platform)

    left_col, right_col = st.columns([1, 1])

    with left_col:
        st.subheader("Price Distribution")
        price_chart = px.histogram(
            filtered_df,
            x="price",
            nbins=12,
            title="SKU Price Spread",
            color_discrete_sequence=["#4C78A8"],
        )
        st.plotly_chart(price_chart, use_container_width=True)

    with right_col:
        st.subheader("Badge Presence")
        badge_counts = filtered_df["Detected Badges"].value_counts().reset_index()
        badge_counts.columns = ["Badge", "Count"]
        badge_chart = px.bar(
            badge_counts,
            x="Badge",
            y="Count",
            title="Detected Badge Distribution",
            text_auto=True,
        )
        st.plotly_chart(badge_chart, use_container_width=True)

    st.subheader("Marketplace SKU Detail")
    st.dataframe(
        filtered_df[["rank", "brand", "oem", "title", "price", "platform", "Detected Badges", "source"]].sort_values(
            ["platform", "rank"], ascending=[True, True]
        ),
        use_container_width=True,
    )