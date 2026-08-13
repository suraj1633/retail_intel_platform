"""
dashboard/app.py
Streamlit UI layout querying live database models directly.
"""

import pandas as pd
import streamlit as st

import database.db_manager as dbm
from database.db_manager import BannerRecord, ProductListing, init_db, is_valid_product_record
from dashboard.components.audit_tab import render_retailer_audit_tab
from dashboard.components.banner_tab import render_banner_tracking_tab
from dashboard.components.chatbot import render_chatbot_tab
from dashboard.components.sku_explorer import render_sku_explorer_tab
from dashboard.components.sos_tab import render_share_of_voice_tab
from engine.data_pipeline import seed_compliance_and_shelf_data

st.set_page_config(
    page_title="Retail Intelligence Platform",
    page_icon="📊",
    layout="wide",
)


def build_listings_dataframe(listings):
    """Normalize ORM rows into a DataFrame with the full audit metadata used by the dashboard."""
    rows = []
    for listing in listings:
        record = {
            "title": getattr(listing, "title", ""),
            "price": getattr(listing, "price", 0.0),
            "msrp": getattr(listing, "msrp", 0.0),
            "is_promo": getattr(listing, "is_promo", False),
            "brand": getattr(listing, "brand", "Unknown") or "Unknown",
            "oem": getattr(listing, "oem", "Unknown") or "Unknown",
            "platform": getattr(listing, "platform", "Unknown") or "Unknown",
            "product_type": getattr(listing, "product_type", "Notebook") or "Notebook",
            "url": getattr(listing, "url", ""),
            "rank": getattr(listing, "rank", 1),
            "source": getattr(listing, "source", "LIVE_SCRAPE"),
            "has_listing_badge": getattr(listing, "has_listing_badge", False),
            "has_pdp_badge": getattr(listing, "has_pdp_badge", False),
            "has_spec_table_mention": getattr(listing, "has_spec_table_mention", False),
            "has_brand_rich_media": getattr(listing, "has_brand_rich_media", False),
            "has_oem_rich_media": getattr(listing, "has_oem_rich_media", False),
            "Detected Badges": getattr(listing, "detected_badges", "Standard"),
        }
        if is_valid_product_record(record):
            rows.append(record)
    return pd.DataFrame(rows)


def get_session():
    if hasattr(dbm, "get_db_session"):
        return dbm.get_db_session()
    if hasattr(dbm, "SessionLocal"):
        return dbm.SessionLocal()
    from sqlalchemy.orm import sessionmaker

    engine_obj = getattr(dbm, "engine", None) or getattr(dbm, "DB_ENGINE", None)
    return sessionmaker(bind=engine_obj)()


def main():
    init_db()
    db_session = get_session()

    try:
        if db_session.query(ProductListing).count() == 0:
            seed_compliance_and_shelf_data(session=db_session)

        st.title("🛒 Retail Intelligence & Compliance Platform")
        st.caption("Multi-brand visibility, banner quality, and retailer compliance monitoring across retailer pages.")

        listings = db_session.query(ProductListing).all()
        listings_df = build_listings_dataframe(listings)

        st.sidebar.header("Global Filters")
        st.sidebar.caption("Use filters to focus the current business view.")
        if listings_df.empty:
            filtered_df = listings_df
            st.sidebar.info("No product records yet. The app is ready to populate with live data.")
        else:
            platforms = ["All"] + list(listings_df["platform"].unique())
            selected_platform = st.sidebar.selectbox("Select Platform", platforms)
            filtered_df = listings_df.copy()
            if selected_platform != "All":
                filtered_df = filtered_df[filtered_df["platform"] == selected_platform]

            st.sidebar.markdown("---")
            st.sidebar.subheader("Data Quality")
            st.sidebar.metric("Valid SKUs", len(filtered_df))
            st.sidebar.metric("Brands in View", filtered_df["brand"].nunique() if not filtered_df.empty else 0)
            st.sidebar.metric("Platforms in View", filtered_df["platform"].nunique() if not filtered_df.empty else 0)

        if not filtered_df.empty:
            brand_summary = (
                filtered_df.groupby("brand", as_index=False)
                .agg(Products=("title", "count"), Avg_Price=("price", "mean"), Platforms=("platform", "nunique"))
                .sort_values(["Products", "Avg_Price"], ascending=[False, True])
                .reset_index(drop=True)
            )
            brand_summary["Avg_Price"] = brand_summary["Avg_Price"].map(lambda v: f"${v:,.2f}")

            top_brand = brand_summary.iloc[0]["brand"] if not brand_summary.empty else "N/A"
            top_platform = filtered_df["platform"].value_counts().idxmax() if not filtered_df.empty else "N/A"

            st.subheader("Executive Overview")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Visible SKUs", len(filtered_df))
            col2.metric("Brands Tracked", filtered_df["brand"].nunique())
            col3.metric("Platforms", filtered_df["platform"].nunique())
            col4.metric("Top Brand", top_brand)

            st.caption(f"Leading platform in view: {top_platform}")
            st.dataframe(
                brand_summary.head(10),
                width="stretch",
                hide_index=True,
            )

        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📋 Retailer Compliance Audits",
            "🖼️ Banner & Real Estate Tracking",
            "📊 Share of Shelf (SoS)",
            "🔍 SKU Explorer",
            "🤖 AI Insights Chatbot",
        ])

        with tab1:
            render_retailer_audit_tab(filtered_df)

        with tab2:
            render_banner_tracking_tab(db_session)

        with tab3:
            render_share_of_voice_tab(filtered_df)

        with tab4:
            render_sku_explorer_tab(filtered_df)

        with tab5:
            render_chatbot_tab(filtered_df)

    finally:
        db_session.close()


if __name__ == "__main__":
    main()