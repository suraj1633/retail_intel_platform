import pandas as pd

from dashboard.components.chatbot import _answer_question, _build_summary
from database.db_manager import is_valid_product_record
from engine.analytics import calculate_share_of_voice
from engine.audit_scorer import compute_audit_score, calculate_overall_compliance, calculate_s1_p5_score


def test_compute_audit_score():
    result = compute_audit_score(
        {"title": "Dell Intel Core Ultra laptop", "has_badge": True},
        {"title": "Dell Intel Core Ultra laptop", "has_pdp_badge": True, "specs": {"cpu": "Intel Core Ultra"}, "has_brand_rich_media": True, "has_oem_rich_media": True},
        "Intel"
    )
    assert result["score"] > 0
    assert result["s1_title_brand"] is True


def test_calculate_overall_compliance():
    assert calculate_overall_compliance(90, 60) == 85.5


def test_calculate_s1_p5_score():
    result = calculate_s1_p5_score({
        "title": "Apple MacBook Air M3",
        "product_type": "Notebook",
        "has_listing_badge": True,
        "has_pdp_badge": True,
        "has_spec_table_mention": True,
        "has_brand_rich_media": True,
        "has_oem_rich_media": True,
    })
    assert result["s1_title_brand"] is True
    assert result["s2_tile_badge"] is True
    assert result["p2_pdp_badge"] is True
    assert result["p3_spec_table"] is True
    assert result["p4_brand_rich_media"] is True
    assert result["p5_oem_rich_media"] is True
    assert result["weighted_score"] > 0


def test_calculate_s1_p5_score_ignores_missing_pdp_fields():
    result = calculate_s1_p5_score({
        "title": "Notebook Gamer Asus TUF Gaming F15 Core i7",
        "brand": "Asus",
        "product_type": "Notebook",
        "source": "LIVE_SCRAPE",
    })
    assert result["s1_title_brand"] is True
    assert result["s2_tile_badge"] is None
    assert result["p2_pdp_badge"] is None
    assert result["p3_spec_table"] is None
    assert result["p4_brand_rich_media"] is None
    assert result["p5_oem_rich_media"] is None
    assert result["weighted_score"] > 70


def test_calculate_s1_p5_score_reads_csv_style_badge_signals():
    result = calculate_s1_p5_score({
        "title": "Dell Inspiron 15 Intel Core i7",
        "brand": "Dell",
        "oem": "Intel",
        "product_type": "Notebook",
        "source": "LIVE_SCRAPE",
        "Detected Badges": "Core, Core Ultra",
        "has_listing_badge": False,
        "has_pdp_badge": True,
        "has_spec_table_mention": True,
        "has_brand_rich_media": False,
        "has_oem_rich_media": True,
    })
    assert result["s1_title_brand"] is True
    assert result["s2_tile_badge"] is True
    assert result["p1_pdp_title"] is True
    assert result["p2_pdp_badge"] is True
    assert result["p3_spec_table"] is True
    assert result["p4_brand_rich_media"] is False
    assert result["p5_oem_rich_media"] is True


def test_is_valid_product_record_rejects_zero_or_missing_price():
    assert is_valid_product_record({"title": "Valid Laptop", "price": 899.99, "brand": "Dell"}) is True
    assert is_valid_product_record({"title": "Zero Price Laptop", "price": 0, "brand": "Dell"}) is False
    assert is_valid_product_record({"title": "", "price": 400, "brand": "Dell"}) is False
    assert is_valid_product_record({"title": "Missing Price", "price": None, "brand": "Dell"}) is False


def test_chatbot_summary_and_question_logic():
    df = pd.DataFrame([
        {"brand": "Intel", "platform": "Newegg US", "title": "Intel laptop", "price": 1000},
        {"brand": "Intel", "platform": "Newegg US", "title": "Intel notebook", "price": 1200},
        {"brand": "AMD", "platform": "Mercado Libre BR", "title": "AMD laptop", "price": 800},
    ])

    summary = _build_summary(df)
    assert summary["visible_skus"] == 3
    assert summary["brands"] == 2
    assert summary["lead_platform"] in {"Newegg US", "Mercado Libre BR"}

    response = _answer_question(df, "What is the average price?")
    assert "average product price" in response.lower()
    assert "$1000" in response or "$1000.00" in response

    weakest_brand_response = _answer_question(df, "Which brand is underperforming?")
    assert "weakest brand" in weakest_brand_response.lower() or "underperform" in weakest_brand_response.lower()

    weakest_platform_response = _answer_question(df, "Which platform is weakest?")
    assert "weakest platform" in weakest_platform_response.lower() or "lowest presence" in weakest_platform_response.lower()


def test_calculate_share_of_voice_filters_invalid_rows():
    df = pd.DataFrame([
        {"brand": "Intel", "platform": "Newegg US", "title": "Intel laptop", "price": 1000, "rank": 1},
        {"brand": "", "platform": "Newegg US", "title": "Missing brand", "price": 0, "rank": 2},
        {"brand": "AMD", "platform": "", "title": "Missing platform", "price": 500, "rank": 3},
        {"brand": "Intel", "platform": "Newegg US", "title": "Intel notebook", "price": 1200, "rank": 4},
    ])

    result = calculate_share_of_voice(df)
    assert result["brand"].str.len().gt(0).all()
    assert result["platform"].str.len().gt(0).all()
    assert result["search_appearances"].sum() == 2
