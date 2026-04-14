import os
import requests
from dotenv import load_dotenv

load_dotenv()

def publish_to_telegram(product):
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
    
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("[Telegram] 토큰 정보가 없어 전송을 생략합니다.")
        return False
        
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    
    prefix = "🔥[초특가 핫딜]🔥\n" if product.deal_type == "HOT_DEAL" else "✨[추천 아이템]✨\n"
    
    caption = f"{prefix}\n{product.name}\n\n"
    caption += f"💰 가격: {product.price:,}원\n\n"
    caption += f"👉 바로 구매하기: {product.affiliate_link}"
    
    data = {"chat_id": TELEGRAM_CHAT_ID, "caption": caption, "photo": product.image_url}
    
    res = requests.post(url, data=data)
    if res.status_code == 200:
        print("[Telegram] 메시지 전송 성공!")
        return True
    else:
        print(f"[Telegram] 전송 실패: {res.text}")
        return False
