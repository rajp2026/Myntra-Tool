from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
import datetime
from .database import Base

class ScrapeJob(Base):
    __tablename__ = "scrape_jobs"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String, default="running")

    products = relationship("Product", back_populates="job", cascade="all, delete-orphan")
    ads = relationship("CategoryAd", back_populates="job", cascade="all, delete-orphan")

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("scrape_jobs.id"))
    product_id = Column(String, index=True)
    status = Column(String)
    title = Column(String)
    brand = Column(String)
    description = Column(String)
    images = Column(JSON) # List of image URLs
    rating = Column(Float)
    ratings_count = Column(Integer)
    category = Column(String)
    mrp = Column(Float)
    discounted_price = Column(Float)
    error = Column(String)

    job = relationship("ScrapeJob", back_populates="products")

class CategoryAd(Base):
    __tablename__ = "category_ads"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("scrape_jobs.id"))
    category_name = Column(String, index=True)
    product_id = Column(String)
    name = Column(String)
    brand = Column(String)
    rating = Column(Float)
    price = Column(Float)
    mrp = Column(Float)
    image = Column(String)

    job = relationship("ScrapeJob", back_populates="ads")
