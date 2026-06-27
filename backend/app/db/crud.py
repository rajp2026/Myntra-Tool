from sqlalchemy.orm import Session
from . import models

def create_scrape_job(db: Session):
    job = models.ScrapeJob()
    db.add(job)
    db.commit()
    db.refresh(job)
    return job

def update_job_status(db: Session, job_id: int, status: str):
    job = db.query(models.ScrapeJob).filter(models.ScrapeJob.id == job_id).first()
    if job:
        job.status = status
        db.commit()

def save_product(db: Session, job_id: int, product_data: dict):
    # Ensure rating is float or None
    rating = product_data.get("rating")
    if rating is not None:
        try:
            rating = float(rating)
        except ValueError:
            rating = None
            
    prod = models.Product(
        job_id=job_id,
        product_id=str(product_data.get("product_id")),
        status=product_data.get("status"),
        title=product_data.get("title"),
        brand=product_data.get("brand"),
        description=product_data.get("description"),
        images=product_data.get("images", []),
        rating=rating,
        ratings_count=product_data.get("ratings_count"),
        category=product_data.get("category"),
        mrp=product_data.get("mrp"),
        discounted_price=product_data.get("discounted_price"),
        error=product_data.get("error")
    )
    db.add(prod)
    db.commit()

def save_category_ad(db: Session, job_id: int, category_name: str, ad_data: dict):
    rating = ad_data.get("rating")
    if rating is not None:
        try:
            rating = float(rating)
        except ValueError:
            rating = None

    ad = models.CategoryAd(
        job_id=job_id,
        category_name=category_name,
        product_id=str(ad_data.get("product_id")),
        name=ad_data.get("name"),
        brand=ad_data.get("brand"),
        rating=rating,
        price=ad_data.get("price"),
        mrp=ad_data.get("mrp"),
        image=ad_data.get("image")
    )
    db.add(ad)
    db.commit()

def get_latest_job(db: Session):
    job = db.query(models.ScrapeJob).order_by(models.ScrapeJob.id.desc()).first()
    if not job:
        return None
    
    # Format the data to match the frontend expectations
    products = [
        {
            "product_id": p.product_id,
            "status": p.status,
            "title": p.title,
            "brand": p.brand,
            "description": p.description,
            "images": p.images,
            "rating": p.rating,
            "ratings_count": p.ratings_count,
            "category": p.category,
            "mrp": p.mrp,
            "discounted_price": p.discounted_price,
            "error": p.error
        } for p in job.products
    ]
    
    category_ads = {}
    for ad in job.ads:
        if ad.category_name not in category_ads:
            category_ads[ad.category_name] = []
        category_ads[ad.category_name].append({
            "product_id": ad.product_id,
            "name": ad.name,
            "brand": ad.brand,
            "rating": ad.rating,
            "price": ad.price,
            "mrp": ad.mrp,
            "image": ad.image
        })
        
    successful = len([p for p in products if p["status"] == "success"])
    failed = len([p for p in products if p["status"] != "success"])
    
    return {
        "job_id": job.id,
        "status": job.status,
        "products": products,
        "category_ads": category_ads,
        "summary": {
            "total": len(products),
            "successful": successful,
            "failed": failed
        }
    }
