from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from fastapi import Depends
import models
from database import engine, get_db
from scheduler import start_scheduler, job_crawl_deals

# DB 테이블 생성
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Link Collector Admin")
templates = Jinja2Templates(directory="templates")

@app.on_event("startup")
def startup_event():
    start_scheduler()

@app.get("/")
def read_root(request: Request, db: Session = Depends(get_db)):
    products = db.query(models.Product).order_by(models.Product.id.desc()).limit(20).all()
    posts = db.query(models.Post).order_by(models.Post.id.desc()).limit(20).all()
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "products": products,
        "posts": posts
    })

@app.post("/manual_run")
def manual_run():
    job_crawl_deals()
    return {"message": "수동 크롤링이 완료되었습니다! 핫딜/베스트 상품이 수집되었습니다."}

@app.post("/add_manual_product")
def add_manual_product(
    name: str = Form(...),
    price: int = Form(...),
    affiliate_link: str = Form(...),
    deal_type: str = Form(...),
    db: Session = Depends(get_db)
):
    new_product = models.Product(
        category="수동등록",
        name=name,
        original_link=affiliate_link, # 수동은 원본과 제휴링크 동일 취급
        affiliate_link=affiliate_link,
        image_url="https://image2.coupangcdn.com/image/coupang/common/logo_coupang_w350.png", # 기본 쿠팡 로고
        price=price,
        is_trending=True,
        deal_type=deal_type
    )
    db.add(new_product)
    db.flush()
    platforms = ["GITHUB", "INSTAGRAM", "TELEGRAM", "TWITTER"]
    for p in platforms:
        db.add(models.Post(product_id=new_product.id, platform=p, post_status="PENDING"))
    db.commit()
    return {"message": f"[{name}] 수동 등록 완료! 스케줄러 대기열에 진입했습니다."}

@app.post("/update_link/{product_id}")
def update_link(product_id: int, affiliate_link: str = Form(...), db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if product:
        product.affiliate_link = affiliate_link
        db.commit()
    return {"message": "제휴 링크가 수동으로 저장되었습니다. 이제 스케줄러가 포스팅을 시작합니다!"}
