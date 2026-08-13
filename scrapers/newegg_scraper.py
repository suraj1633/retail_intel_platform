import re
from scrapers.stealth_driver import StealthFetcher
from engine.brand_parser import parse_brand_and_oem, is_excluded_accessory

class NeweggScraper:
    def __init__(self):
        self.fetcher = StealthFetcher()
        self.api_url = "https://www.newegg.com/p/api/ProductList"

    def scrape_keyword_results(self, keyword="gaming laptop"):
        print(f"[Newegg] Fetching live product catalog via direct API endpoint...")
        
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "Origin": "https://www.newegg.com",
            "Referer": f"https://www.newegg.com/p/pl?d={keyword.replace(' ', '+')}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        }

        payload = {
            "Keyword": keyword,
            "PageNumber": 1,
            "PageSize": 36,
            "StoreType": 1
        }

        try:
            # First hit search page to set session cookies
            self.fetcher.get(f"https://www.newegg.com/p/pl?d={keyword.replace(' ', '+')}")
            
            # Request JSON payload directly
            response = self.fetcher.session.post(self.api_url, json=payload, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                items = data.get("ProductList", [])
                
                if items:
                    print(f"[Newegg] Successfully retrieved {len(items)} live items via API!")
                    return self._parse_json_items(items)
        except Exception as e:
            print(f"[Newegg] Direct API call failed: {e}. Falling back to page parsing...")

        # Fallback: Parse HTML if API returns empty
        return self._scrape_html_fallback(keyword)

    def _parse_json_items(self, items):
        scraped_products = []
        for idx, item in enumerate(items, start=1):
            description = item.get("Description", {})
            title = description.get("Title", "") or item.get("Title", "")
            
            if not title:
                continue
            
            if is_excluded_accessory(title):
                continue

            price_info = item.get("FinalPrice", 0) or item.get("UnitPrice", 0)
            try:
                price = float(price_info)
            except (ValueError, TypeError):
                price = 0.0

            item_url = item.get("ProductUrl", "")
            brand, oem, p_type = parse_brand_and_oem(title)

            scraped_products.append({
                "rank": idx,
                "title": title,
                "url": item_url,
                "price": price,
                "brand": brand,
                "oem": oem,
                "platform": "Newegg US",
                "source": "LIVE_API_FETCH"
            })
        return scraped_products

    def _scrape_html_fallback(self, keyword):
        formatted_kw = keyword.replace(" ", "+")
        url = f"https://www.newegg.com/p/pl?d={formatted_kw}"
        res = self.fetcher.get(url)
        
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(res.text, "html.parser")
        items = soup.select("div.item-cell, div.item-container")
        
        scraped_products = []
        for idx, item in enumerate(items, start=1):
            title_elem = item.select_one("a.item-title")
            price_elem = item.select_one("li.price-current")
            
            if not title_elem:
                continue
                
            title = title_elem.text.strip()
            
            if is_excluded_accessory(title):
                continue
            
            clean_price = re.sub(r"[^\d.]", "", price_elem.text) if price_elem else "0"
            price = float(clean_price) if clean_price else 0.0
            brand, oem, p_type = parse_brand_and_oem(title)

            scraped_products.append({
                "rank": idx,
                "title": title,
                "url": title_elem.get("href", ""),
                "price": price,
                "brand": brand,
                "oem": oem,
                "platform": "Newegg US",
                "source": "LIVE_HTML_PARSED"
            })
        return scraped_products