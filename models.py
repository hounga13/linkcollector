from sqlalchemy import Boolean, Column, Integer, String, DateTime
from sqlalchemy.sql import func
from database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, index=True)
    name = Column(String, index=True)
    original_link = Column(String)
    affiliate_link = Column(String, nullable=True)
    image_url = Column(String)
    price = Column(Integer)
    is_trending = Column(Boolean, default=False)
    deal_type = Column(String, default="NORMAL") # NORMAL, HOT_DEAL
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, index=True)
    platform = Column(String) # GITHUB, INSTAGRAM, TELEGRAM, TWITTER
    post_status = Column(String, default="PENDING") # PENDING, SUCCESS, FAILED
    post_url = Column(String, nullable=True)
    posted_at = Column(DateTime(timezone=True), nullable=True)
