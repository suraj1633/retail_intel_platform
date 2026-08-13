import pandas as pd
import streamlit as st


def _build_summary(df: pd.DataFrame) -> dict:
    if df.empty:
        return {
            "visible_skus": 0,
            "brands": 0,
            "platforms": 0,
            "avg_price": 0.0,
            "top_brand": "N/A",
            "lead_platform": "N/A",
            "lowest_price": 0.0,
            "highest_price": 0.0,
        }

    return {
        "visible_skus": int(len(df)),
        "brands": int(df["brand"].nunique()),
        "platforms": int(df["platform"].nunique()),
        "avg_price": float(df["price"].fillna(0).mean()),
        "top_brand": df.groupby("brand")["title"].count().idxmax() if not df.empty else "N/A",
        "lead_platform": df["platform"].value_counts().idxmax() if not df.empty else "N/A",
        "lowest_price": float(df["price"].replace(0, pd.NA).dropna().min()) if not df["price"].dropna().empty else 0.0,
        "highest_price": float(df["price"].replace(0, pd.NA).dropna().max()) if not df["price"].dropna().empty else 0.0,
    }


def _get_exec_summary(df: pd.DataFrame) -> str:
    if df.empty:
        return "The current selection has no valid product data to summarize."

    summary = _build_summary(df)
    return (
        f"The current view includes {summary['visible_skus']} valid SKUs across {summary['brands']} brands and "
        f"{summary['platforms']} platforms. The average price is ${summary['avg_price']:.2f}, with a lowest valid offer of "
        f"${summary['lowest_price']:.2f} and a highest valid offer of ${summary['highest_price']:.2f}. "
        f"{summary['top_brand']} leads the current brand mix, while {summary['lead_platform']} is the leading platform."
    )


def _answer_question(df: pd.DataFrame, question: str) -> str:
    q = (question or "").lower().strip()
    if not q:
        return "Ask me about brand performance, pricing, platform share, or product counts."

    summary = _build_summary(df)

    if any(keyword in q for keyword in ["top brand", "leader", "best brand", "brand leader", "who leads"]):
        return (
            f"The leading brand in the current view is {summary['top_brand']} with the strongest SKU presence "
            f"across the filtered dataset."
        )
    if any(keyword in q for keyword in ["avg price", "average price", "price level", "pricing"]):
        return f"The current average product price is ${summary['avg_price']:.2f}."
    if any(keyword in q for keyword in ["lowest price", "cheapest", "minimum price"]):
        return f"The lowest valid price in the current view is ${summary['lowest_price']:.2f}."
    if any(keyword in q for keyword in ["highest price", "most expensive", "maximum price"]):
        return f"The highest valid price in the current view is ${summary['highest_price']:.2f}."
    if any(keyword in q for keyword in ["weakest platform", "worst platform", "underperforming platform", "platform underperforming"]) or ("platform" in q and ("weakest" in q or "worst" in q or "underperform" in q)):
        if df.empty:
            return "There is no valid data in the selection to assess platform performance."
        platform_counts = df["platform"].value_counts().sort_values()
        weakest_platform = platform_counts.index[0]
        weakest_count = int(platform_counts.iloc[0])
        return (
            f"The weakest platform in the current selection is {weakest_platform}, with {weakest_count} visible listings. "
            f"It currently has the lowest presence in the active dataset."
        )
    if any(keyword in q for keyword in ["underperform", "weakest brand", "worst brand", "low visibility brand", "brand is underperforming"]) or ("brand" in q and ("weakest" in q or "underperform" in q or "worst" in q)):
        if df.empty:
            return "There is no valid data in the selection to assess brand underperformance."
        brand_counts = df.groupby("brand").size().sort_values()
        weakest_brand = brand_counts.index[0]
        weakest_count = int(brand_counts.iloc[0])
        return (
            f"The weakest brand in the current selection is {weakest_brand}, with {weakest_count} visible listings. "
            f"This suggests the lightest current presence in the filtered view."
        )
    if any(keyword in q for keyword in ["platform", "marketplace", "retailer", "which platform"]):
        return (
            f"The current view includes {summary['platforms']} platform(s), with {summary['lead_platform']} leading "
            f"the product mix in this selection."
        )
    if any(keyword in q for keyword in ["brand count", "brands tracked", "how many brands"]):
        return f"There are {summary['brands']} tracked brands in the current selection."
    if any(keyword in q for keyword in ["sku count", "products", "total listings", "how many products", "visible skus"]):
        return f"There are {summary['visible_skus']} valid product listings in the active filter set."
    if any(keyword in q for keyword in ["share of voice", "sov", "visibility", "dominance"]):
        if df.empty:
            return "No visibility data is available because the current selection has no valid listings."
        brand_share = df.groupby("brand")["title"].count().sort_values(ascending=False)
        top_brand = brand_share.index[0]
        top_share = brand_share.iloc[0]
        return (
            f"{top_brand} has the strongest visibility in this dataset, contributing {top_share} listings in the current view."
        )
    if any(keyword in q for keyword in ["executive summary", "summary", "overview", "what is happening"]):
        return _get_exec_summary(df)
    if any(keyword in q for keyword in ["compliance", "audit", "score"]):
        return (
            "The current chatbot is summarizing the active product and platform snapshot. For detailed retailer compliance scoring, "
            "use the Retailer Compliance tab in the dashboard."
        )
    if any(keyword in q for keyword in ["hello", "hi", "hey", "help"]):
        return "I can answer questions about visible SKUs, average pricing, brand leaders, platform performance, underperformers, and current market mix in the filtered view."

    return (
        "I can help with the current data snapshot: try asking for the top brand, average price, product count, "
        "platform leader, weakest brand, weakest platform, or an executive summary."
    )


def render_chatbot_tab(filtered_df: pd.DataFrame):
    st.header("🤖 AI Insights Chatbot")
    st.markdown(
        "Ask quick business questions about the filtered dataset. The assistant answers from the current visible products, pricing, and brand mix."
    )

    if filtered_df.empty:
        st.info("No valid product data is available for the current filter. Adjust the filters or refresh the dataset.")
        return

    st.info(_get_exec_summary(filtered_df))

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {
                "role": "assistant",
                "content": "I’m ready. Ask me for a brand summary, price signal, platform leader, or the current SKU count.",
            }
        ]

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_question = st.chat_input("Ask about the current selection...")
    if user_question:
        st.session_state.chat_history.append({"role": "user", "content": user_question})
        with st.chat_message("user"):
            st.markdown(user_question)

        response = _answer_question(filtered_df, user_question)
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response)

    st.caption("Suggested prompts: Top brand, average price, platform leader, how many products are visible, executive summary")
