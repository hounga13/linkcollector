from playwright.sync_api import sync_playwright

def test_scrape(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            extra_http_headers={"Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7"}
        )
        page = context.new_page()
        page.goto(url, wait_until="domcontentloaded")
        
        try:
            name = page.locator("h2.prod-buy-header__title").inner_text()
            price_text = page.locator("span.total-price > strong").inner_text()
            print(f"Success! Name: {name}, Price: {price_text}")
        except Exception as e:
            print(f"Failed. Title: {page.title()}")
            print(page.content()[:300])
        browser.close()

if __name__ == "__main__":
    test_scrape("https://www.coupang.com/vp/products/7542981504")
