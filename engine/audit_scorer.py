"""
Retail Intelligence Platform
S1-P5 Retailer Compliance Audit Scoring

Rules:
S1 = Brand present in listing title
S2 = Brand/product badge present on listing tile
P1 = Brand present in PDP title
P2 = PDP badge present
P3 = Brand/spec mention present in specification table
P4 = Brand rich media present
P5 = OEM rich media present

Missing evidence is treated as N/A, not as a failure.

Notebook/Desktop weighting:
Notebook = 85%
Desktop  = 15%
"""

from typing import Any, Dict, Optional


# ---------------------------------------------------------------------------
# BRAND KEYWORDS
# ---------------------------------------------------------------------------

BRAND_KEYWORDS = {
    "intel": [
        "intel",
        "core",
        "core ultra",
        "intel core",
    ],
    "amd": [
        "amd",
        "ryzen",
    ],
    "qualcomm": [
        "qualcomm",
        "snapdragon",
    ],
    "apple": [
        "apple",
        "m1",
        "m2",
        "m3",
        "m4",
        "silicon",
    ],
}


def _normalize(value: Any) -> str:
    """Convert a value to normalized lowercase text."""
    if value is None:
        return ""

    return str(value).strip().lower()


def _coerce_bool(value: Any) -> Optional[bool]:
    """
    Convert common boolean-like values into True / False / None.

    None means there is no usable evidence.
    """

    if value is None:
        return None

    if isinstance(value, bool):
        return value

    if isinstance(value, (int, float)):
        return bool(value)

    if isinstance(value, str):
        normalized = value.strip().lower()

        if normalized in {
            "",
            "none",
            "null",
            "n/a",
            "na",
            "unknown",
            "not available",
        }:
            return None

        if normalized in {
            "true",
            "yes",
            "y",
            "1",
            "present",
            "detected",
            "pass",
        }:
            return True

        if normalized in {
            "false",
            "no",
            "n",
            "0",
            "absent",
            "not detected",
            "fail",
        }:
            return False

    return bool(value)


# ---------------------------------------------------------------------------
# BRAND HELPERS
# ---------------------------------------------------------------------------

def _brand_keywords_for(brand: str):
    """
    Return keywords associated with the supplied brand.

    Unknown brands fall back to the brand name itself.
    """

    normalized_brand = _normalize(brand)

    if not normalized_brand:
        return []

    return BRAND_KEYWORDS.get(
        normalized_brand,
        [normalized_brand],
    )


def _contains_brand(text: str, brand: str) -> bool:
    """
    Determine whether brand-related keywords appear in text.
    """

    text = _normalize(text)
    keywords = _brand_keywords_for(brand)

    if not text or not keywords:
        return False

    return any(keyword in text for keyword in keywords)


# ---------------------------------------------------------------------------
# BADGE HELPERS
# ---------------------------------------------------------------------------

def _badge_signal_text(item_dict: Dict[str, Any]) -> str:
    """
    Collect possible badge fields into one searchable string.

    Supports several field names so the scorer remains compatible
    with existing scraped/transformed data.
    """

    candidate_keys = [
        "Detected Badges",
        "detected_badges",
        "badge",
        "badges",
        "listing_badges",
        "has_badge",
        "has_listing_badge",
    ]

    parts = []

    for key in candidate_keys:
        if key not in item_dict:
            continue

        value = item_dict.get(key)

        if value is None:
            continue

        if isinstance(value, (list, tuple, set)):
            parts.extend(str(v) for v in value)
        else:
            parts.append(str(value))

    return " ".join(parts).strip().lower()


def _extract_bool(
    item_dict: Dict[str, Any],
    *keys: str,
) -> Optional[bool]:
    """
    Look through multiple possible field names.

    The first explicitly available boolean-like value is returned.
    """

    for key in keys:
        if key not in item_dict:
            continue

        value = _coerce_bool(item_dict.get(key))

        if value is not None:
            return value

    return None


# ---------------------------------------------------------------------------
# SPECIFICATION HELPERS
# ---------------------------------------------------------------------------

def _specification_text(item_dict: Dict[str, Any]) -> str:
    """
    Collect specification information from common fields.

    Supports:
        specs
        specifications
        spec_table
        specification_table
    """

    values = []

    candidate_keys = [
        "specs",
        "specifications",
        "spec_table",
        "specification_table",
    ]

    for key in candidate_keys:
        if key not in item_dict:
            continue

        value = item_dict.get(key)

        if value is None:
            continue

        if isinstance(value, dict):
            for k, v in value.items():
                values.append(str(k))
                values.append(str(v))
        elif isinstance(value, (list, tuple, set)):
            values.extend(str(v) for v in value)
        else:
            values.append(str(value))

    return " ".join(values).strip().lower()


# ---------------------------------------------------------------------------
# ORIGINAL GENERIC SCORER
# ---------------------------------------------------------------------------

def compute_audit_score(
    listing_data: Dict[str, Any],
    pdp_data: Dict[str, Any],
    brand: str,
) -> Dict[str, Any]:
    """
    Evaluate S1-P5 using separate listing and PDP dictionaries.

    This function is kept for compatibility with existing project code.
    """

    # -------------------------
    # S1 - Listing title brand
    # -------------------------

    listing_title = _normalize(
        listing_data.get("title", "")
    )

    s1 = (
        _contains_brand(listing_title, brand)
        if listing_title
        else None
    )

    # -------------------------
    # S2 - Listing tile badge
    # -------------------------

    s2 = _extract_bool(
        listing_data,
        "has_listing_badge",
        "has_badge",
    )

    if s2 is None:
        badge_text = _badge_signal_text(listing_data)

        if badge_text and badge_text not in {
            "standard",
            "none",
            "na",
            "n/a",
            "unknown",
        }:
            s2 = True

    # -------------------------
    # P1 - PDP title brand
    # -------------------------

    pdp_title = _normalize(
        pdp_data.get("title", "")
    )

    p1 = (
        _contains_brand(pdp_title, brand)
        if pdp_title
        else None
    )

    # -------------------------
    # P2 - PDP badge
    # -------------------------

    p2 = _extract_bool(
        pdp_data,
        "has_pdp_badge",
        "pdp_badge",
    )

    # -------------------------
    # P3 - Specification table
    # -------------------------

    specs_text = _specification_text(pdp_data)

    p3 = (
        _contains_brand(specs_text, brand)
        if specs_text
        else None
    )

    # -------------------------
    # P4 - Brand rich media
    # -------------------------

    p4 = _extract_bool(
        pdp_data,
        "has_brand_rich_media",
        "brand_rich_media",
    )

    # -------------------------
    # P5 - OEM rich media
    # -------------------------

    p5 = _extract_bool(
        pdp_data,
        "has_oem_rich_media",
        "oem_rich_media",
    )

    checks = [
        s1,
        s2,
        p1,
        p2,
        p3,
        p4,
        p5,
    ]

    available_checks = [
        value
        for value in checks
        if value is not None
    ]

    if available_checks:
        raw_score = (
            sum(bool(value) for value in available_checks)
            / len(available_checks)
        ) * 100
    else:
        raw_score = 0.0

    return {
        "s1_title_brand": s1,
        "s2_tile_badge": s2,
        "p1_pdp_title": p1,
        "p2_pdp_badge": p2,
        "p3_spec_table": p3,
        "p4_brand_rich_media": p4,
        "p5_oem_rich_media": p5,
        "score": round(raw_score, 2),
    }


# ---------------------------------------------------------------------------
# NOTEBOOK / DESKTOP WEIGHTING
# ---------------------------------------------------------------------------

def calculate_overall_compliance(
    notebook_score: float,
    desktop_score: float,
) -> float:
    """
    Calculate final compliance using:

        Notebook = 85%
        Desktop  = 15%
    """

    return round(
        (0.85 * float(notebook_score))
        + (0.15 * float(desktop_score)),
        2,
    )


# ---------------------------------------------------------------------------
# MAIN DASHBOARD SCORER
# ---------------------------------------------------------------------------

def calculate_s1_p5_score(
    item_dict: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Calculate S1-P5 compliance for a single listing.

    Expected/common fields:

        title
        brand
        oem
        platform
        product_type

        has_listing_badge
        has_badge
        Detected Badges

        pdp_title
        product_title

        has_pdp_badge
        has_spec_table_mention
        has_brand_rich_media
        has_oem_rich_media

        specs / specifications / spec_table

    Returns:

        s1_title_brand
        s2_tile_badge
        p1_pdp_title
        p2_pdp_badge
        p3_spec_table
        p4_brand_rich_media
        p5_oem_rich_media

        raw_score
        weighted_score
    """

    # -----------------------------------------------------------------------
    # BASIC DATA
    # -----------------------------------------------------------------------

    title = _normalize(
        item_dict.get("title", "")
    )

    pdp_title = _normalize(
        item_dict.get("pdp_title")
        or item_dict.get("product_title")
        or item_dict.get("title", "")
    )

    brand = _normalize(
        item_dict.get("brand")
        or item_dict.get("oem")
        or ""
    )

    product_type = _normalize(
        item_dict.get("product_type")
        or "notebook"
    )

    # -----------------------------------------------------------------------
    # S1 - BRAND IN LISTING TITLE
    # -----------------------------------------------------------------------

    if title and brand:
        s1 = _contains_brand(title, brand)
    else:
        s1 = None

    # -----------------------------------------------------------------------
    # S2 - LISTING TILE BADGE
    # -----------------------------------------------------------------------

    listing_badge_value = _extract_bool(
        item_dict,
        "has_listing_badge",
        "has_badge",
    )

    badge_signal_text = _badge_signal_text(item_dict)

    badge_keywords = [
        "intel",
        "core",
        "core ultra",
        "amd",
        "ryzen",
        "apple",
        "m1",
        "m2",
        "m3",
        "m4",
        "qualcomm",
        "snapdragon",
        "badge",
        "featured",
        "premium",
    ]

    badge_string_value = None

    if badge_signal_text and badge_signal_text not in {
        "standard",
        "none",
        "na",
        "n/a",
        "unknown",
    }:
        badge_string_value = any(
            keyword in badge_signal_text
            for keyword in badge_keywords
        )

    if listing_badge_value is not None:
        s2 = listing_badge_value

    elif badge_string_value is not None:
        s2 = badge_string_value

    else:
        s2 = None

    # -----------------------------------------------------------------------
    # P1 - BRAND IN PDP TITLE
    # -----------------------------------------------------------------------

    if pdp_title and brand:
        p1 = _contains_brand(
            pdp_title,
            brand,
        )
    else:
        p1 = None

    # -----------------------------------------------------------------------
    # P2 - PDP BADGE
    # -----------------------------------------------------------------------

    p2 = _extract_bool(
        item_dict,
        "has_pdp_badge",
        "pdp_badge",
    )

    # -----------------------------------------------------------------------
    # P3 - SPECIFICATION TABLE
    # -----------------------------------------------------------------------

    has_spec_table_mention = _extract_bool(
        item_dict,
        "has_spec_table_mention",
    )

    specs_text = _specification_text(item_dict)

    if has_spec_table_mention is not None:
        p3 = has_spec_table_mention

    elif specs_text and brand:
        p3 = _contains_brand(
            specs_text,
            brand,
        )

    else:
        p3 = None

    # -----------------------------------------------------------------------
    # P4 - BRAND RICH MEDIA
    # -----------------------------------------------------------------------

    p4 = _extract_bool(
        item_dict,
        "has_brand_rich_media",
        "brand_rich_media",
    )

    # -----------------------------------------------------------------------
    # P5 - OEM RICH MEDIA
    # -----------------------------------------------------------------------

    p5 = _extract_bool(
        item_dict,
        "has_oem_rich_media",
        "oem_rich_media",
    )

    # -----------------------------------------------------------------------
    # CALCULATE RAW SCORE
    # -----------------------------------------------------------------------

    checks = [
        s1,
        s2,
        p1,
        p2,
        p3,
        p4,
        p5,
    ]

    available_checks = [
        value
        for value in checks
        if value is not None
    ]

    if available_checks:
        raw_score = (
            sum(bool(value) for value in available_checks)
            / len(available_checks)
        ) * 100
    else:
        raw_score = 0.0

    raw_score = round(
        raw_score,
        2,
    )

    # -----------------------------------------------------------------------
    # NOTEBOOK / DESKTOP WEIGHT
    # -----------------------------------------------------------------------
    #
    # IMPORTANT:
    #
    # The 85/15 weighting should normally be applied when combining
    # Notebook and Desktop results.
    #
    # We therefore do NOT multiply an individual Notebook listing's
    # score by 0.85 here.
    #
    # Instead:
    #
    # final = notebook_score * 0.85 + desktop_score * 0.15
    #
    # This prevents a Notebook listing with 100% compliance from being
    # displayed incorrectly as 85%.
    # -----------------------------------------------------------------------

    weighted_score = raw_score

    # -----------------------------------------------------------------------
    # RESULT
    # -----------------------------------------------------------------------

    return {
        "s1_title_brand": s1,
        "s2_tile_badge": s2,
        "p1_pdp_title": p1,
        "p2_pdp_badge": p2,
        "p3_spec_table": p3,
        "p4_brand_rich_media": p4,
        "p5_oem_rich_media": p5,
        "raw_score": raw_score,
        "weighted_score": weighted_score,
    }