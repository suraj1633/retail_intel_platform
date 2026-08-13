"""
scrapers/banner_scraper.py
Live scraper for homepage and category banners across supported platforms.
"""

from curl_cffi import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

class BannerScraper:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,pt-BR;q=0.8"
        }

    def scrape_platform_banners(self, platform_name: str, target_url: str) -> list:
        """Extracts live homepage/category banner elements from retail platforms."""
        print(f"[BannerScraper] Capturing live banners from {platform_name} ({target_url})...")
        results = []

        try:
            res = requests.get(target_url, headers=self.headers, impersonate="chrome124", timeout=15)
            if res.status_code != 200:
                print(f"[BannerScraper] HTTP {res.status_code} for {platform_name}")
                return results

            soup = BeautifulSoup(res.text, "html.parser")

            # 1. Newegg Banners
            if "newegg" in platform_name.lower():
                banner_elems = soup.select(".swiper-slide img, .home-banner img, .swiper-wrapper img")
                for idx, img in enumerate(banner_elems, start=1):
                    src = img.get("src") or img.get("data-src")
                    alt = img.get("alt") or f"Newegg Banner #{idx}"
                    if src and ("http" in src):
                        results.append({
                            "platform": platform_name,
                            "banner_type": "Homepage Hero",
                            "position": f"Hero Slot #{idx}",
                            "title": alt[:100],
                            "image_url": src,
                            "target_url": target_url,
                            "status": "Active",
                            "created_at": datetime.utcnow()
                        })

            # 2. Mercado Libre Banners
            elif "mercado" in platform_name.lower():
                banner_elems = soup.select(".slick-slide img, .ui-navigation-banner img, .andes-carousel-snapping__slide img")
                for idx, img in enumerate(banner_elems, start=1):
                    src = img.get("src") or img.get("data-src")
                    alt = img.get("alt") or f"Mercado Libre Banner #{idx}"
                    if src and ("http" in src):
                        results.append({
                            "platform": platform_name,
                            "banner_type": "Homepage Carousel",
                            "position": f"Slide #{idx}",
                            "title": alt[:100],
                            "image_url": src,
                            "target_url": target_url,
                            "status": "Active",
                            "created_at": datetime.utcnow()
                        })

            # 3. Amazon / Generic Banners
            else:
                banner_elems = soup.select("#gw-layout img, .a-carousel-card img, .desktop-banner img")
                for idx, img in enumerate(banner_elems, start=1):
                    src = img.get("src") or img.get("data-src")
                    alt = img.get("alt") or f"{platform_name} Banner #{idx}"
                    if src and ("http" in src):
                        results.append({
                            "platform": platform_name,
                            "banner_type": "Homepage Top Banner",
                            "position": f"Position #{idx}",
                            "title": alt[:100],
                            "image_url": src,
                            "target_url": target_url,
                            "status": "Active",
                            "created_at": datetime.utcnow()
                        })

            print(f"[BannerScraper] Extracted {len(results)} live banner records from {platform_name}.")
            return results

        except Exception as e:
            print(f"[BannerScraper] Error scraping banners for {platform_name}: {e}")
            return []