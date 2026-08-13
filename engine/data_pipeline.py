"""
engine/data_pipeline.py
Runs live product scrapers and live banner scrapers, populating database models directly.
"""

from datetime import datetime

import database.db_manager as dbm
from database.db_manager import BannerRecord, ProductListing, init_db, is_valid_product_record


def _get_session():
    if hasattr(dbm, "get_db_session"):
        return dbm.get_db_session()
    if hasattr(dbm, "SessionLocal"):
        return dbm.SessionLocal()
    from sqlalchemy.orm import sessionmaker

    engine_obj = getattr(dbm, "engine", None) or getattr(dbm, "DB_ENGINE", None)
    return sessionmaker(bind=engine_obj)()


def seed_compliance_and_shelf_data(session=None):
    """Compatibility helper used by entrypoints and scripts to seed data safely."""
    close_session = session is None
    session = session or _get_session()

    try:
        init_db()
        product_count = session.query(ProductListing).count()
        banner_count = session.query(BannerRecord).count()

        if product_count == 0:
            session.add_all([
                ProductListing(
                    title="Dell Inspiron 15 Intel Core i7",
                    price=899.99,
                    msrp=999.99,
                    is_promo=True,
                    brand="Intel",
                    oem="Dell",
                    product_type="Notebook",
                    platform="Newegg US",
                    url="https://example.com/dell-inspiron-15",
                    rank=1,
                    has_listing_badge=True,
                    has_pdp_badge=True,
                    has_spec_table_mention=True,
                    has_brand_rich_media=True,
                    has_oem_rich_media=True,
                    source="SEED_DATA"
                ),
                ProductListing(
                    title="Lenovo LOQ AMD Ryzen 7 Gaming Laptop",
                    price=1099.99,
                    msrp=1199.99,
                    is_promo=False,
                    brand="AMD",
                    oem="Lenovo",
                    product_type="Notebook",
                    platform="Newegg US",
                    url="https://example.com/lenovo-loq",
                    rank=2,
                    has_listing_badge=True,
                    has_pdp_badge=True,
                    has_spec_table_mention=True,
                    has_brand_rich_media=True,
                    has_oem_rich_media=True,
                    source="SEED_DATA"
                ),
            ])

        if banner_count == 0:
            session.add_all([
                BannerRecord(
                    platform="Newegg US",
                    brand="Intel",
                    target_url="https://www.newegg.com",
                    screenshot_path="https://example.com/newegg-banner.png",
                    timestamp=datetime.utcnow()
                ),
            ])

        session.commit()
        return {
            "products": session.query(ProductListing).count(),
            "banners": session.query(BannerRecord).count(),
        }
    except Exception as exc:  # pragma: no cover - defensive logging
        session.rollback()
        print(f"[DataPipeline] Seed failed: {exc}")
        raise
    finally:
        if close_session:
            session.close()


def run_live_pipeline():
    """Scrapes live products AND live banners across all targeted platforms."""
    init_db()
    session = _get_session()

    from scrapers.newegg_scraper import NeweggScraper
    from scrapers.mercadolibre_scraper import MercadoLibreScraper
    from scrapers.banner_scraper import BannerScraper

    print("==================================================")
    print("       1. EXECUTING LIVE PRODUCT SCRAPERS        ")
    print("==================================================")

    product_tasks = [
        ("Newegg US", NeweggScraper(), "gaming laptop"),
        ("Newegg US", NeweggScraper(), "creator laptop"),
        ("Mercado Libre BR", MercadoLibreScraper(), "notebook gamer"),
        ("Mercado Libre BR", MercadoLibreScraper(), "macbook air")
    ]

    total_products = 0
    total_updates = 0
    for platform_name, scraper_inst, keyword in product_tasks:
        try:
            results = scraper_inst.scrape_keyword_results(keyword)
            for res in results:
                candidate = {
                    "title": res.get("title"),
                    "price": res.get("price", 0.0),
                    "brand": res.get("brand"),
                    "oem": res.get("oem"),
                }
                if not is_valid_product_record(candidate):
                    continue
                
                # UPSERT logic: Always check for existing product first
                product_url = res.get("url")
                existing_product = None
                
                if product_url:
                    # Query by URL to find existing product
                    try:
                        existing_product = session.query(ProductListing).filter_by(url=product_url).first()
                    except Exception:
                        existing_product = None
                
                try:
                    if existing_product:
                        # UPDATE existing product
                        existing_product.title = res.get("title")
                        existing_product.price = res.get("price", 0.0)
                        existing_product.msrp = res.get("msrp", res.get("price", 0.0))
                        existing_product.is_promo = res.get("is_promo", False)
                        existing_product.brand = res.get("brand")
                        existing_product.oem = res.get("oem")
                        existing_product.product_type = res.get("product_type", "Notebook")
                        existing_product.rank = res.get("rank", 1)
                        existing_product.detected_badges = res.get("detected_badges", "")
                        session.commit()
                        total_updates += 1
                    else:
                        # INSERT new product - commit immediately to catch UNIQUE errors early
                        listing = ProductListing(
                            title=res.get("title"),
                            price=res.get("price", 0.0),
                            msrp=res.get("msrp", res.get("price", 0.0)),
                            is_promo=res.get("is_promo", False),
                            brand=res.get("brand"),
                            oem=res.get("oem"),
                            product_type=res.get("product_type", "Notebook"),
                            platform=platform_name,
                            url=product_url,
                            rank=res.get("rank", 1),
                            detected_badges=res.get("detected_badges", ""),
                            source="LIVE_SCRAPE",
                            created_at=datetime.utcnow()
                        )
                        session.add(listing)
                        session.commit()  # Commit immediately per-item to catch errors
                        total_products += 1
                except Exception as item_err:
                    # If this item fails, skip it and continue with next item
                    session.rollback()
                    if "UNIQUE constraint" in str(item_err):
                        # Try to update instead if UNIQUE constraint
                        try:
                            existing = session.query(ProductListing).filter_by(url=product_url).first()
                            if existing:
                                existing.title = res.get("title")
                                existing.price = res.get("price", 0.0)
                                existing.msrp = res.get("msrp", res.get("price", 0.0))
                                existing.is_promo = res.get("is_promo", False)
                                existing.brand = res.get("brand")
                                existing.oem = res.get("oem")
                                existing.product_type = res.get("product_type", "Notebook")
                                existing.rank = res.get("rank", 1)
                                existing.detected_badges = res.get("detected_badges", "")
                                session.commit()
                                total_updates += 1
                        except:
                            session.rollback()
                            pass
        except Exception as e:
            session.rollback()
            print(f"[DataPipeline] Error scraping products for '{keyword}': {e}")

    print(f"\n[DataPipeline] Stored {total_products} live product listings (with {total_updates} updates).")

    print("\n==================================================")
    print("       2. EXECUTING LIVE BANNER SCRAPERS         ")
    print("==================================================")

    banner_scraper = BannerScraper()
    banner_targets = [
        ("Newegg US", "https://www.newegg.com"),
        ("Mercado Libre BR", "https://www.mercadolivre.com.br")
    ]

    total_banners = 0
    for platform_name, target_url in banner_targets:
        try:
            banner_records = banner_scraper.scrape_platform_banners(platform_name, target_url)
            for b in banner_records:
                record = BannerRecord(
                    platform=b.get("platform") or platform_name,
                    brand=b.get("brand") or "Unknown",
                    target_url=b.get("target_url") or target_url,
                    screenshot_path=b.get("image_url") or b.get("screenshot_path"),
                    timestamp=b.get("created_at", datetime.utcnow())
                )
                session.add(record)
                total_banners += 1
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"[DataPipeline] Error saving banners for {platform_name}: {e}")

    session.close()
    print(f"\n[DataPipeline] Complete! Saved {total_products} new products, updated {total_updates} existing products, and {total_banners} banners to the database.")


def seed_database(session=None):
    """Backward-compatible alias kept for older scripts and imports."""
    return seed_compliance_and_shelf_data(session=session)