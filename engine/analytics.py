# Add to engine/analytics.py
import pandas as pd


def calculate_share_of_voice(listings_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates Share of Voice (SoV) percentage per brand based on keyword search rankings.
    Invalid product rows are excluded before aggregation.
    """
    if listings_df.empty:
        return pd.DataFrame()

    valid_df = listings_df.copy()
    valid_df = valid_df.dropna(subset=["brand", "platform", "rank", "title"])
    valid_df = valid_df[valid_df["brand"].astype(str).str.strip() != ""]
    valid_df = valid_df[valid_df["platform"].astype(str).str.strip() != ""]
    valid_df = valid_df[valid_df["price"].fillna(0) > 0].copy()

    if valid_df.empty:
        return pd.DataFrame()

    # Share of Voice by Brand across top search positions
    sov_df = valid_df.groupby(["platform", "brand"])["rank"].count().reset_index()
    sov_df.rename(columns={"rank": "search_appearances"}, inplace=True)

    # Calculate percentage share
    total_per_platform = sov_df.groupby("platform")["search_appearances"].transform("sum")
    sov_df["sov_percentage"] = (sov_df["search_appearances"] / total_per_platform) * 100.0

    return sov_df.sort_values(by=["platform", "sov_percentage"], ascending=[True, False])