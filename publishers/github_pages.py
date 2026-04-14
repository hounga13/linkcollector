import os
import datetime
from dotenv import load_dotenv

load_dotenv()
REPO_PATH = os.getenv("GITHUB_REPO_PATH", "/tmp/mock_repo")

def publish_to_github(product):
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    safe_title = product.name.replace(" ", "-").replace("/", "")[:20]
    filename = f"{date_str}-{safe_title}.md"
    
    hot_tag = "[🔥핫딜]" if product.deal_type == "HOT_DEAL" else "[✨추천]"
    
    content = f"""---
title: "{hot_tag} {product.name}"
date: {datetime.datetime.now().isoformat()}
---

# {product.name}
## 현재 특가: {product.price:,}원

![상품이미지]({product.image_url})

👉 [최저가 바로 보러가기]({product.affiliate_link})

> 이 포스팅은 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다.
"""
    
    if not os.path.exists(REPO_PATH):
        os.makedirs(REPO_PATH, exist_ok=True)
        
    filepath = os.path.join(REPO_PATH, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
        
    # index.md 에 링크 한 줄 추가
    index_path = os.path.join(REPO_PATH, "index.md")
    if os.path.exists(index_path):
        with open(index_path, "a", encoding="utf-8") as f:
            f.write(f"\n* 👉 [{date_str} {hot_tag} {product.name}](./{filename.replace('.md', '')})")

    # git 자동 푸시 스크립트 실행
    os.system(f"cd {REPO_PATH} && git add . && git commit -m 'Auto Post: {safe_title}' && git push -u origin main")
    print(f"[GitHub Pages] 포스팅 문서 생성 성공: {filepath}")
    return True
