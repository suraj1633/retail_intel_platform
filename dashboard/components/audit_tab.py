import pandas as pd
import plotly.express as px
import streamlit as st

from engine.audit_scorer import calculate_s1_p5_score


def _status(value):
    """Convert scorer output into a readable dashboard status."""
    if value is None:
        return "⚠️ N/A"
    return "✅ Pass" if value else "❌ Fail"


def render_retailer_audit_tab(listings_df):
    """
    Render the S1-P5 Retailer Compliance Audit dashboard.

    S1 - Brand present in listing/search title
    S2 - Brand/product badge present on listing tile
    P1 - Brand present in PDP title
    P2 - Brand/product badge present on PDP
    P3 - Brand represented in specification table
    P4 - Brand rich media present on PDP
    P5 - OEM rich media present on PDP

    The individual listing score comes directly from
    calculate_s1_p5_score(). Notebook/Desktop 85/15 weighting
    is handled separately by calculate_overall_compliance().
    """

    st.header("📋 Retailer Compliance Audits (S1-P5 Rubric)")

    st.markdown(
        """
        Evaluates brand presence on listing tiles (S1-S2)
        and product detail pages (P1-P5).

        **Scoring:** Each listing receives a 0-100% S1-P5 compliance score.
        Notebook/Desktop 85% / 15% weighting is handled separately.
        """
    )

    # ------------------------------------------------------------------
    # No data
    # ------------------------------------------------------------------

    if listings_df is None or listings_df.empty:
        st.warning("No data available for audit scoring.")
        return

    # Work on a copy so the original dataframe is not modified.
    listings_df = listings_df.copy()

    # ------------------------------------------------------------------
    # Calculate S1-P5 for every listing
    # ------------------------------------------------------------------

    audit_results = []

    for _, row in listings_df.iterrows():

        row_dict = row.to_dict()

        scores = calculate_s1_p5_score(row_dict)

        title = row.get(
            "title",
            row.get("name", "")
        )

        title = str(title or "")

        if len(title) > 50:
            title_display = title[:50] + "..."
        else:
            title_display = title

        audit_results.append(
            {
                "Title": title_display,
                "Brand": row.get(
                    "brand",
                    row.get("oem", "Unknown")
                ),
                "Platform": row.get(
                    "platform",
                    row.get("retailer", "Unknown")
                ),

                "S1 Title Brand": _status(
                    scores.get("s1_title_brand")
                ),

                "S2 Tile Badge": _status(
                    scores.get("s2_tile_badge")
                ),

                "P1 PDP Title": _status(
                    scores.get("p1_pdp_title")
                ),

                "P2 PDP Badge": _status(
                    scores.get("p2_pdp_badge")
                ),

                "P3 Spec Table": _status(
                    scores.get("p3_spec_table")
                ),

                "P4 Brand Media": _status(
                    scores.get("p4_brand_rich_media")
                ),

                "P5 OEM Media": _status(
                    scores.get("p5_oem_rich_media")
                ),

                "Raw Score": float(
                    scores.get("raw_score", 0)
                ),

                "Weighted Score": float(
                    scores.get("weighted_score", 0)
                ),
            }
        )

    audit_df = pd.DataFrame(audit_results)

    if audit_df.empty:
        st.warning("No audit results were generated.")
        return

    # ------------------------------------------------------------------
    # Sort by score
    # ------------------------------------------------------------------

    audit_df = audit_df.sort_values(
        "Raw Score",
        ascending=False
    ).reset_index(drop=True)

    # ------------------------------------------------------------------
    # Filters
    # ------------------------------------------------------------------

    st.subheader("🔎 Filters")

    filter_col1, filter_col2 = st.columns(2)

    platform_options = sorted(
        audit_df["Platform"]
        .fillna("Unknown")
        .astype(str)
        .unique()
        .tolist()
    )

    brand_options = sorted(
        audit_df["Brand"]
        .fillna("Unknown")
        .astype(str)
        .unique()
        .tolist()
    )

    with filter_col1:
        selected_platforms = st.multiselect(
            "Filter by platform",
            platform_options,
            default=platform_options,
            key="audit_platform_filter",
        )

    with filter_col2:
        selected_brands = st.multiselect(
            "Filter by brand",
            brand_options,
            default=brand_options,
            key="audit_brand_filter",
        )

    filtered_df = audit_df[
        audit_df["Platform"].astype(str).isin(selected_platforms)
        & audit_df["Brand"].astype(str).isin(selected_brands)
    ].copy()

    if filtered_df.empty:
        st.warning(
            "No listings match the selected platform and brand filters."
        )
        return

    # ------------------------------------------------------------------
    # Summary metrics
    # ------------------------------------------------------------------

    avg_score = filtered_df["Raw Score"].mean()

    rule_columns = [
        "S1 Title Brand",
        "S2 Tile Badge",
        "P1 PDP Title",
        "P2 PDP Badge",
        "P3 Spec Table",
        "P4 Brand Media",
        "P5 OEM Media",
    ]

    valid_mask = filtered_df[rule_columns].ne("⚠️ N/A")

    pass_count = (
        filtered_df[rule_columns]
        .eq("✅ Pass")
        .where(valid_mask)
        .sum()
        .sum()
    )

    total_valid_checks = valid_mask.to_numpy().sum()

    pass_rate = (
        (pass_count / total_valid_checks) * 100
        if total_valid_checks
        else 0.0
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Average Score",
        f"{avg_score:.1f}%"
    )

    col2.metric(
        "Pass Rate",
        f"{pass_rate:.1f}%"
    )

    col3.metric(
        "Listings Audited",
        len(filtered_df)
    )

    # ------------------------------------------------------------------
    # Compliance tiers
    # ------------------------------------------------------------------

    st.subheader("📊 Compliance Health")

    tier_labels = [
        "Critical",
        "Needs Attention",
        "Healthy",
    ]

    tier_counts = pd.cut(
        filtered_df["Raw Score"],
        bins=[
            -0.01,
            59.99,
            84.99,
            100.0,
        ],
        labels=tier_labels,
        include_lowest=True,
    ).value_counts().reindex(
        tier_labels,
        fill_value=0
    )

    tier_col1, tier_col2, tier_col3 = st.columns(3)

    tier_col1.metric(
        "Healthy",
        int(tier_counts["Healthy"])
    )

    tier_col2.metric(
        "Needs Attention",
        int(tier_counts["Needs Attention"])
    )

    tier_col3.metric(
        "Critical",
        int(tier_counts["Critical"])
    )

    # ------------------------------------------------------------------
    # Failure analysis
    # ------------------------------------------------------------------

    failure_counts = {
        label: int(
            (filtered_df[label] == "❌ Fail").sum()
        )
        for label in rule_columns
    }

    failure_df = pd.DataFrame(
        {
            "Rule": list(failure_counts.keys()),
            "Failures": list(failure_counts.values()),
        }
    ).sort_values(
        "Failures",
        ascending=False
    )

    if not failure_df.empty:
        worst_rule = failure_df.iloc[0]["Rule"]
        worst_count = failure_df.iloc[0]["Failures"]

        st.info(
            f"Primary issue to fix: **{worst_rule}** "
            f"({worst_count} failures)"
        )

    # ------------------------------------------------------------------
    # Failure chart
    # ------------------------------------------------------------------

    failure_chart = px.bar(
        failure_df,
        x="Failures",
        y="Rule",
        orientation="h",
        color="Failures",
        title="Top Failure Drivers by Compliance Rule",
        text_auto=True,
    )

    failure_chart.update_layout(
        yaxis_title="Compliance Rule",
        xaxis_title="Number of Failures",
    )

    st.plotly_chart(
        failure_chart,
        width="stretch",
    )

    # ------------------------------------------------------------------
    # Score distribution
    # ------------------------------------------------------------------

    score_hist = px.histogram(
        filtered_df,
        x="Raw Score",
        nbins=10,
        title="S1-P5 Compliance Score Distribution",
        color_discrete_sequence=["#4C78A8"],
    )

    score_hist.update_xaxes(
        title_text="Compliance Score (%)"
    )

    score_hist.update_yaxes(
        title_text="Listings"
    )

    st.plotly_chart(
        score_hist,
        width="stretch",
    )

    # ------------------------------------------------------------------
    # Brand vs rule pass-rate matrix
    # ------------------------------------------------------------------

    def calculate_rule_pass_rate(series):
        valid = series[series != "⚠️ N/A"]

        if len(valid) == 0:
            return float("nan")

        return (
            (valid == "✅ Pass").mean() * 100
        )

    brand_rule_matrix = (
        filtered_df
        .groupby("Brand")[rule_columns]
        .agg(calculate_rule_pass_rate)
        .T
    )

    if not brand_rule_matrix.empty:

        heatmap = px.imshow(
            brand_rule_matrix,
            labels={
                "x": "Brand",
                "y": "Rule",
                "color": "Pass Rate %",
            },
            color_continuous_scale="RdYlGn",
            title="Brand vs. Rule Pass Rate Heatmap",
            aspect="auto",
        )

        heatmap.update_xaxes(
            side="bottom"
        )

        st.plotly_chart(
            heatmap,
            width="stretch",
        )

    # ------------------------------------------------------------------
    # Average score by brand
    # ------------------------------------------------------------------

    brand_scores = (
        filtered_df
        .groupby("Brand", as_index=False)["Raw Score"]
        .mean()
        .rename(
            columns={
                "Raw Score": "Avg Compliance Score"
            }
        )
        .sort_values(
            "Avg Compliance Score",
            ascending=True
        )
    )

    brand_chart = px.bar(
        brand_scores,
        x="Avg Compliance Score",
        y="Brand",
        orientation="h",
        color="Brand",
        title="Average Compliance Score by Brand",
        text_auto=".1f",
    )

    brand_chart.update_xaxes(
        title_text="Average Compliance Score (%)"
    )

    st.plotly_chart(
        brand_chart,
        width="stretch",
    )

    # ------------------------------------------------------------------
    # Platform scores
    # ------------------------------------------------------------------

    platform_scores = (
        filtered_df
        .groupby("Platform", as_index=False)["Raw Score"]
        .mean()
        .rename(
            columns={
                "Raw Score": "Avg Compliance Score"
            }
        )
    )

    platform_chart = px.bar(
        platform_scores,
        x="Platform",
        y="Avg Compliance Score",
        color="Platform",
        title="Average Compliance Score by Platform",
        text_auto=".1f",
    )

    platform_chart.update_yaxes(
        title_text="Average Compliance Score (%)"
    )

    st.plotly_chart(
        platform_chart,
        width="stretch",
    )

    # ------------------------------------------------------------------
    # Top underperformers
    # ------------------------------------------------------------------

    st.subheader("⚠️ Top Underperformers")

    underperformers = (
        filtered_df
        .sort_values(
            "Raw Score",
            ascending=True
        )
        .head(5)
        .copy()
    )

    underperformers_display = underperformers[
        [
            "Title",
            "Brand",
            "Platform",
            "Raw Score",
        ]
    ].copy()

    underperformers_display["Raw Score"] = (
        underperformers_display["Raw Score"]
        .map(lambda x: f"{x:.1f}%")
    )

    underperformers_display = underperformers_display.rename(
        columns={
            "Raw Score": "Compliance Score"
        }
    )

    st.dataframe(
        underperformers_display,
        width="stretch",
        hide_index=True,
    )

    # ------------------------------------------------------------------
    # Full audit table
    # ------------------------------------------------------------------

    st.subheader("📋 Detailed S1-P5 Audit Results")

    display_df = filtered_df.copy()

    display_df["Raw Score"] = (
        display_df["Raw Score"]
        .map(lambda x: f"{x:.1f}%")
    )

    display_df["Weighted Score"] = (
        display_df["Weighted Score"]
        .map(lambda x: f"{x:.1f}%")
    )

    display_columns = [
        "Title",
        "Brand",
        "Platform",
        "S1 Title Brand",
        "S2 Tile Badge",
        "P1 PDP Title",
        "P2 PDP Badge",
        "P3 Spec Table",
        "P4 Brand Media",
        "P5 OEM Media",
        "Raw Score",
        "Weighted Score",
    ]

    display_df = display_df[display_columns]

    def style_status(value):
        if value == "✅ Pass":
            return "color: green; font-weight: 600"

        if value == "❌ Fail":
            return "color: red; font-weight: 600"

        if value == "⚠️ N/A":
            return "color: orange; font-weight: 600"

        return ""

    styled_df = display_df.style.map(
        style_status,
        subset=[
            "S1 Title Brand",
            "S2 Tile Badge",
            "P1 PDP Title",
            "P2 PDP Badge",
            "P3 Spec Table",
            "P4 Brand Media",
            "P5 OEM Media",
        ],
    )

    st.dataframe(
        styled_df,
        width="stretch",
        hide_index=True,
    )

    # ------------------------------------------------------------------
    # CSV export
    # ------------------------------------------------------------------

    st.subheader("⬇️ Export")

    csv_data = filtered_df.copy()

    csv_data["Raw Score"] = (
        csv_data["Raw Score"]
        .map(lambda x: f"{x:.1f}%")
    )

    csv_data["Weighted Score"] = (
        csv_data["Weighted Score"]
        .map(lambda x: f"{x:.1f}%")
    )

    st.download_button(
        label="Download Audit CSV",
        data=csv_data.to_csv(index=False).encode("utf-8"),
        file_name="retail_audit_export.csv",
        mime="text/csv",
    )