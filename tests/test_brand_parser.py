from engine.brand_parser import parse_brand_and_oem, is_excluded_accessory, extract_brand_badges


def test_parse_brand_and_oem_for_intel_laptop():
    brand, oem, product_type = parse_brand_and_oem("Dell Inspiron 15 Intel Core i7 laptop")
    assert brand == "Intel"
    assert oem == "Dell"
    assert product_type == "Notebook"


def test_parse_brand_and_oem_for_amd_laptop():
    brand, oem, product_type = parse_brand_and_oem("Lenovo LOQ Ryzen 7 gaming laptop")
    assert brand == "AMD"
    assert oem == "Lenovo"
    assert product_type == "Notebook"


def test_excluded_accessory_filter():
    assert is_excluded_accessory("Dell keyboard") is True
    assert is_excluded_accessory("Apple MacBook Air M3") is False


def test_extract_brand_badges():
    badges = extract_brand_badges("Intel Core Ultra 7 laptop", "Intel")
    assert "Core Ultra" in " ".join(badges)
