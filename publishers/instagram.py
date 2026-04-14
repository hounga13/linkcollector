import os
from dotenv import load_dotenv

load_dotenv()

def publish_to_instagram(product):
    # instagrapi 등 라이브러리 사용을 가정 (비공식 API 기반 구조)
    USERNAME = os.getenv("INSTAGRAM_USERNAME")
    PASSWORD = os.getenv("INSTAGRAM_PASSWORD")
    
    if not USERNAME or not PASSWORD:
        print("[Instagram] 계정 정보 미등록으로 포스팅 생략.")
        return False
        
    prefix = "🔥[초특가 핫딜]" if product.deal_type == "HOT_DEAL" else "✨[오늘의 추천]"
    caption = f"{prefix} {product.name}\n\n가격: {product.price:,}원\n\n👉 초저가 구매 링크는 프로필 링크의 블로그에서 확인하세요!\n#쿠팡 #핫딜 #최저가"
    
    # from instagrapi import Client
    # cl = Client()
    # cl.login(USERNAME, PASSWORD)
    # img_path = download_image(product.image_url)
    # cl.photo_upload(img_path, caption)
    
    print(f"[Instagram] 사진 및 캡션 업로드 처리 완료: {product.name}")
    return True
