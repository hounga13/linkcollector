from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from models import Product, Post
from database import SessionLocal
from crawler import crawl_coupang_deals
from partner_api import get_coupang_deeplink
from publishers import publish_to_github, publish_to_instagram, publish_to_telegram, publish_to_twitter
import datetime

scheduler = BackgroundScheduler()

def job_crawl_deals():
    db = SessionLocal()
    try:
        print(f"[{datetime.datetime.now()}] 스케줄러: 상품 크롤링 수집 시작")
        crawled_items = crawl_coupang_deals()
        if not crawled_items: return
            
        urls = [i["original_link"] for i in crawled_items]
        deeplink_data = get_coupang_deeplink(urls) or []
        link_map = {d.get("originalUrl"): d.get("shortenUrl") for d in deeplink_data if d.get("originalUrl")}

        platforms = ["GITHUB", "INSTAGRAM", "TELEGRAM", "TWITTER"]
        
        for item in crawled_items:
            existing = db.query(Product).filter(Product.original_link == item["original_link"]).first()
            if not existing:
                new_product = Product(
                    category=item["category"],
                    name=item["name"],
                    original_link=item["original_link"],
                    affiliate_link=link_map.get(item["original_link"]),
                    image_url=item["image_url"],
                    price=item["price"],
                    is_trending=item["is_trending"],
                    deal_type=item["deal_type"]
                )
                db.add(new_product)
                db.flush()
                
                # 모든 플랫폼에 대해 PENDING 포스트 등록
                for p in platforms:
                    db.add(Post(product_id=new_product.id, platform=p, post_status="PENDING"))
        db.commit()
    except Exception as e:
        print(f"Crawler Job Error: {e}")
        db.rollback()
    finally:
        db.close()

def job_post_queue():
    db = SessionLocal()
    try:
        # 우선순위 로직: HOT_DEAL 상품부터 먼저 검색
        pending_posts_hot = db.query(Post).join(Product, Post.product_id == Product.id).filter(
            Post.post_status == "PENDING",
            Product.deal_type == "HOT_DEAL"
        ).all()
        
        pending_posts_normal = db.query(Post).join(Product, Post.product_id == Product.id).filter(
            Post.post_status == "PENDING",
            Product.deal_type == "NORMAL"
        ).all()
        
        # 핫딜이 있으면 핫딜 위주로 한 번에 여러 개(혹은 전량) 즉시 전송, 일반은 속도 조절 
        target_posts = pending_posts_hot if pending_posts_hot else pending_posts_normal[:2]

        for post in target_posts:
            product = db.query(Product).filter(Product.id == post.product_id).first()
            if not product or not product.affiliate_link:
                continue
                
            print(f"[{product.deal_type}] 포스팅 시도: {product.name} -> {post.platform}")
            success = False
            
            if post.platform == "GITHUB":
                success = publish_to_github(product)
            elif post.platform == "INSTAGRAM":
                success = publish_to_instagram(product)
            elif post.platform == "TELEGRAM":
                success = publish_to_telegram(product)
            elif post.platform == "TWITTER":
                success = publish_to_twitter(product)
                
            if success:
                post.post_status = "SUCCESS"
            else:
                post.post_status = "FAILED"
            post.posted_at = datetime.datetime.now()
            
        db.commit()
    except Exception as e:
        print(f"Post Queue Job Error: {e}")
        db.rollback()
    finally:
        db.close()

def start_scheduler():
    # 1. 30분 마다 새상품 크롤링
    scheduler.add_job(job_crawl_deals, trigger=IntervalTrigger(minutes=30), id='crawl_job', replace_existing=True)
    
    # 2. 5분 마다 대기열 포스팅 봇 가동 (핫딜은 발견 시 5분 내로 전부 쏘고, 리뷰 등의 일반 상품은 천천히 분배)
    scheduler.add_job(job_post_queue, trigger=IntervalTrigger(minutes=5), id='post_job', replace_existing=True)
    
    scheduler.start()
    print("스케줄러 가동: 크롤러(30분) / 포스팅봇(5분 단기)")
