from playwright.sync_api import sync_playwright

def _parse_items(page, category, deal_type, max_count=5):
    products = []
    page.wait_for_selector("li.baby-product", timeout=10000)
    items = page.locator("li.baby-product").all()
    
    for item in items[:max_count]:
        name_el = item.locator("div.name")
        price_el = item.locator("strong.price-value")
        link_el = item.locator("a.baby-product-link")
        img_el = item.locator("img.baby-product-image")
        
        name = name_el.inner_text().strip() if name_el.count() else ""
        price_text = price_el.inner_text().strip().replace(",", "") if price_el.count() else "0"
        price = int(price_text) if price_text.isdigit() else 0
        href = link_el.get_attribute("href") if link_el.count() else ""
        
        img_url = img_el.get_attribute("src") if img_el.count() else ""
        if not img_url or "data:image" in img_url:
            img_url = img_el.get_attribute("data-src") if img_el.count() else ""
            
        if img_url and not img_url.startswith("http"):
            img_url = "https:" + img_url
            
        if href and name:
            full_link = "https://www.coupang.com" + href
            products.append({
                "name": name,
                "price": price,
                "original_link": full_link,
                "image_url": img_url,
                "category": category,
                "deal_type": deal_type,
                "is_trending": True
            })
    return products

def crawl_coupang_deals():
    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # 봇 탐지 회피용 브라우저 프로필
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            extra_http_headers={"Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7"}
        )
        page = context.new_page()
        
        # 1. 반짝 핫딜 (골드박스 타겟팅)
        try:
            page.goto("https://www.coupang.com/np/goldbox", wait_until="domcontentloaded")
            hot_deals = _parse_items(page, "골드박스", "HOT_DEAL", max_count=5)
            results.extend(hot_deals)
        except Exception as e:
            print(f"골드박스 크롤링 오류: {e}")
            
        # 2. 로켓베스트 (고평점/최저가 타겟팅)
        try:
            page.goto("https://www.coupang.com/np/best", wait_until="domcontentloaded")
            normal_deals = _parse_items(page, "베스트", "NORMAL", max_count=5)
            results.extend(normal_deals)
        except Exception as e:
            print(f"베스트상품 크롤링 오류: {e}")
            
        browser.close()

    # 봇 탐지 에러 (Access Denied 등) 발생 시 UI 테스트를 위한 더미 데이터 반환
    if not results:
        print("Coupang 보안 정책(봇 탐지)으로 인해 크롤링이 차단되었습니다! 시스템 테스트용 더미 데이터를 반환합니다.")
        results = [
            {"name": "[테스트] 삼성전자 4K UHD 스마트 TV 75인치", "price": 1250000, "original_link": "https://www.coupang.com/", "image_url": "https://thumbnail8.coupangcdn.com/thumbnails/remote/230x230ex/image/retail/images/2023/07/26/17/9/75f3a093-6c70-4f51-b847-f5da1fe3fa9b.jpg", "category": "가전", "deal_type": "HOT_DEAL", "is_trending": True},
            {"name": "[테스트] 애플 2023 맥북 프로 14 M3", "price": 2150000, "original_link": "https://www.coupang.com/", "image_url": "https://thumbnail10.coupangcdn.com/thumbnails/remote/230x230ex/image/vendor_inventory/58af/ebdb19ad43e2e5ec4682ba7acc5bafa28fdef7ca9fcfaeef5476a8b7dd5b.jpg", "category": "디지털", "deal_type": "NORMAL", "is_trending": True},
            {"name": "[테스트] 크리넥스 3겹 데코앤소프트 화장지 30롤", "price": 18900, "original_link": "https://www.coupang.com/", "image_url": "https://thumbnail6.coupangcdn.com/thumbnails/remote/230x230ex/image/retail/images/2020/09/23/15/3/ec2dfbf0-7389-4b68-ab7a-0a7ccbcc38f6.jpg", "category": "생활용품", "deal_type": "HOT_DEAL", "is_trending": True}
        ]
        
    return results

if __name__ == "__main__":
    items = crawl_coupang_deals()
    print(f"총 {len(items)}개 상품 수집 완료.")
    for item in items:
        print(f"[{item['deal_type']}] {item['name'][:20]}... - {item['price']:,}원")
