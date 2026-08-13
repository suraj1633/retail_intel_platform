try:
    from curl_cffi import requests as cffi_requests
    HAS_CURL_CFFI = True
except ImportError:
    # Fallback to standard requests if curl_cffi is not available
    import requests as cffi_requests
    HAS_CURL_CFFI = False

from playwright.async_api import async_playwright
import asyncio

class StealthFetcher:
    """Fast HTTP fetcher using browser impersonation (TLS/JA4 fingerprinting) or standard requests."""
    def __init__(self):
        if HAS_CURL_CFFI:
            self.session = cffi_requests.Session(impersonate="chrome120")
        else:
            self.session = cffi_requests.Session()
            # Add anti-detection headers for standard requests
            self.session.headers.update({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            })

    def get(self, url, headers=None, timeout=15):
        default_headers = {
            "Accept-Language": "en-US,en;q=0.9",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        }
        if headers:
            default_headers.update(headers)
        return self.session.get(url, headers=default_headers, timeout=timeout)


class PlaywrightStealthBrowser:
    """Headless Playwright browser configured for quick DOM rendering."""
    def __init__(self):
        pass

    async def get_page(self, url):
        p = await async_playwright().start()
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-web-security"
            ]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            locale="en-US"
        )
        page = await context.new_page()
        
        # Mask navigator.webdriver
        await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # Navigate without waiting for long-polling network requests
        await page.goto(url, timeout=20000, wait_until="domcontentloaded")
        return page, browser, p