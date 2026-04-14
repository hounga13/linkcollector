from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    page.goto("https://www.coupang.com/np/goldbox", wait_until="networkidle")
    print(page.title())
    with open("page.html", "w") as f:
        f.write(page.content())
    browser.close()
