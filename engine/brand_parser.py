import re

BRANDS = {
    "Intel": [r"intel", r"core\s*i[3579]", r"core\s*ultra", r"celeron", r"pentium"],
    "AMD": [r"amd", r"ryzen", r"threadripper", r"radeon"],
    "Qualcomm": [r"qualcomm", r"snapdragon"],
    "Apple": [r"apple", r"\bm1\b", r"\bm2\b", r"\bm3\b", r"\bm4\b"]
}

OEMS = ["Dell", "HP", "Lenovo", "Acer", "Asus", "MSI", "Apple", "Razer", "Alienware", "Gigabyte"]

PRODUCT_TYPES = {
    "Notebook": [r"laptop", r"notebook", r"macbook", r"convertible"],
    "Desktop": [r"desktop", r"pc gaming", r"tower", r"mini pc"],
    "Tablet": [r"ipad", r"tablet"],
    "Component": [r"processor", r"cpu", r"graphics card", r"gpu", r"motherboard"],
    "Workstation": [r"workstation", r"thinkstation", r"precision"]
}

BADGE_PATTERNS = {
    "Intel": [r"\bcore\b", r"\bcore ultra\b", r"\bevo\b", r"\bvpro\b"],
    "AMD": [r"\bryzen\b", r"\bryzen ai\b", r"\bthreadripper\b"],
    "Qualcomm": [r"\bsnapdragon\b", r"\bsnapdragon x elite\b", r"\bcopilot\+\b"],
    "Apple": [r"\bm1\b", r"\bm2\b", r"\bm3\b", r"\bm4\b", r"\bapple silicon\b"]
}

def is_excluded_accessory(title: str) -> bool:
    """Checks if listing is an excluded accessory (monitors, keyboards, gift cards)."""
    title_lower = title.lower()
    excluded_keywords = ["monitor", "keyboard", "mouse", "headset", "camera", "gift card", "case only"]
    return any(keyword in title_lower for keyword in excluded_keywords)

def parse_brand_and_oem(title: str):
    """
    Parses product title to extract Brand, OEM, and Product Type.
    Returns: (brand, oem, product_type)
    """
    title_lower = title.lower()
    
    # Identify Brand
    detected_brand = "Other / Unknown"
    for brand, patterns in BRANDS.items():
        if any(re.search(pattern, title_lower) for pattern in patterns):
            detected_brand = brand
            break

    # Identify OEM
    detected_oem = None
    for oem in OEMS:
        if re.search(r"\b" + re.escape(oem.lower()) + r"\b", title_lower):
            detected_oem = oem
            break
            
    # Apple products carry Apple in both Brand and OEM
    if detected_brand == "Apple" and not detected_oem:
        detected_oem = "Apple"

    # Identify Product Type
    detected_type = "Notebook"  # Default fallback
    for p_type, patterns in PRODUCT_TYPES.items():
        if any(re.search(pattern, title_lower) for pattern in patterns):
            detected_type = p_type
            break

    return detected_brand, detected_oem, detected_type

def extract_brand_badges(title: str, brand: str) -> list:
    """Detects brand certification badges from product title."""
    found_badges = []
    patterns = BADGE_PATTERNS.get(brand, [])
    for pattern in patterns:
        if re.search(pattern, title, re.IGNORECASE):
            found_badges.append(pattern.replace(r"\b", "").replace("\\", "").title())
    return found_badges

def detect_product_type(title: str) -> str:
    title_lower = title.lower()
    if any(w in title_lower for w in ["workstation", "thinkstation", "precision"]):
        return "Workstation"
    elif any(w in title_lower for w in ["desktop", "tower", "pc gamer", "all-in-one"]):
        return "Desktop"
    elif any(w in title_lower for w in ["tablet", "ipad", "surface"]):
        return "Tablet"
    elif any(w in title_lower for w in ["processor", "i7-", "i9-", "ryzen 7", "graphics card", "rtx"]):
        return "Component"
    return "Notebook"  # Default fallback