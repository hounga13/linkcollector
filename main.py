from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from fastapi import Depends
import models
from database import engine, get_db
from scheduler import start_scheduler, job_crawl_and_post

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
    # 관리자가 버튼을 통해 수동으로 즉시 실행되게 하는 API
    # 이 작업은 시간이 조금 걸릴 수 있으므로, 실제 운영시에는 BackgroundTasks를 사용하는 것이 좋습니다.
    job_crawl_and_post()
    return {"message": "수동 작업이 실행되었습니다. 서버 콘솔을 확인하세요."}
