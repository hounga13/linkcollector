import os
from dotenv import load_dotenv

load_dotenv()

def publish_to_twitter(product):
    API_KEY = os.getenv("TWITTER_API_KEY")
    if not API_KEY:
        print("[Twitter] 토큰 정보 없음. 포스팅 생략.")
        return False
        
    prefix = "🚨[긴급 핫딜]" if product.deal_type == "HOT_DEAL" else "🛍️[추천상품]"
    
    text = f"{prefix} {product.name}\n"
    text += f"가격: {product.price:,}원\n\n"
    text += f"👉 링크 확인: {product.affiliate_link}\n\n#쿠팡 #반짝특가 #최저가"
    
    # import tweepy
    # client = tweepy.Client(consumer_key=API_KEY ...)
    # client.create_tweet(text=text)
    
    print(f"[Twitter] 트윗 전송 완료: {product.name}")
    return True
