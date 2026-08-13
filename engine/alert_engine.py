"""
engine/alert_engine.py
Monitors retail listings and audit records for price drops and compliance issues.
Returns Pandas DataFrames expected by Streamlit components.
"""

import pandas as pd

def check_price_drops(df_or_session, discount_threshold=0.08, threshold_pct=None):
    """
    Checks for products where prices drop below thresholds or discount margins.
    Returns a pandas DataFrame.
    """
    alerts = []
    
    threshold = discount_threshold if discount_threshold is not None else (threshold_pct / 100.0 if threshold_pct else 0.08)

    # Case 1: Called with Pandas DataFrame (Dashboard UI)
    if isinstance(df_or_session, pd.DataFrame):
        if df_or_session.empty:
            return pd.DataFrame(columns=["title", "platform", "price", "issue"])
        
        for _, row in df_or_session.iterrows():
            title = row.get("title", "Unknown Product")
            price = row.get("price", 0)
            platform = row.get("platform", "Unknown Platform")
            
            if "msrp" in row and row["msrp"] > 0:
                discount = (row["msrp"] - price) / row["msrp"]
                if discount >= threshold:
                    alerts.append({
                        "title": title,
                        "platform": platform,
                        "price": price,
                        "issue": f"Price drop of {discount * 100:.1f}% exceeds threshold ({threshold * 100:.0f}%)"
                    })
            elif price > 0 and price < 500:  # Baseline threshold rule
                alerts.append({
                    "title": title,
                    "platform": platform,
                    "price": price,
                    "issue": f"Listing price (${price}) flagged for pricing alert"
                })

    # Case 2: Called with SQLAlchemy DB Session
    else:
        try:
            from database.db_manager import ProductListing
            listings = df_or_session.query(ProductListing).all()
            for item in listings:
                if item.price > 0 and item.price < 500:
                    alerts.append({
                        "title": item.title,
                        "platform": item.platform,
                        "price": item.price,
                        "issue": f"Price below threshold (${item.price})"
                    })
        except Exception as e:
            print(f"[AlertEngine] DB Session price check error: {e}")
            
    # Always return a DataFrame to satisfy `.empty` check in app.py
    if not alerts:
        return pd.DataFrame(columns=["title", "platform", "price", "issue"])
    
    return pd.DataFrame(alerts)


def check_compliance_drops(df_or_session, min_score=75.0, **kwargs):
    """
    Monitors overall compliance scores across platforms.
    Returns a pandas DataFrame.
    """
    compliance_alerts = []
    
    if isinstance(df_or_session, pd.DataFrame):
        if not df_or_session.empty:
            for _, row in df_or_session.iterrows():
                score = row.get("overall_score", 100.0)
                if score < min_score:
                    compliance_alerts.append({
                        "brand": row.get("brand", "Unknown"),
                        "platform": row.get("platform", "Unknown"),
                        "score": score,
                        "issue": f"Compliance score dropped to {score:.1f}%"
                    })
    else:
        try:
            from database.db_manager import AuditRecord
            audits = df_or_session.query(AuditRecord).all()
            for audit in audits:
                if audit.overall_score < min_score:
                    compliance_alerts.append({
                        "brand": audit.brand,
                        "platform": audit.platform,
                        "score": audit.overall_score,
                        "issue": f"Compliance score dropped to {audit.overall_score:.1f}%"
                    })
        except Exception as e:
            print(f"[AlertEngine] DB Session compliance check error: {e}")
            
    if not compliance_alerts:
        return pd.DataFrame(columns=["brand", "platform", "score", "issue"])
        
    return pd.DataFrame(compliance_alerts)