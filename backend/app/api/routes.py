import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException, WebSocket, Depends, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.services.csv_service import get_product_ids
from app.services.api_scraper import process_products
from app.db.database import get_db
from app.db import crud

router = APIRouter()

pending_jobs = {}

@router.post("/upload")
async def upload_csv(file: UploadFile = File(...)):
    """
    Accept a CSV file, extract the product_id column, and return a job_id for WebSocket streaming.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Only .csv files are accepted.",
        )

    try:
        product_ids = get_product_ids(file.file)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to parse CSV: {exc}",
        )

    if not product_ids:
        raise HTTPException(
            status_code=400,
            detail="No product IDs found in CSV.",
        )

    job_id = str(uuid.uuid4())
    pending_jobs[job_id] = product_ids
    return {"job_id": job_id}


@router.websocket("/ws/scrape/{job_id}")
async def websocket_scrape(websocket: WebSocket, job_id: str, db: Session = Depends(get_db)):
    await websocket.accept()
    if job_id not in pending_jobs:
        await websocket.close(code=1008, reason="Job not found")
        return
    
    product_ids = pending_jobs.pop(job_id)
    
    # Create Job in DB
    db_job = crud.create_scrape_job(db)
    
    try:
        async for event in process_products(product_ids):
            # Save to DB based on event type
            if event["type"] == "product":
                crud.save_product(db, db_job.id, event["data"])
            elif event["type"] == "ad":
                for ad_data in event["data"]:
                    crud.save_category_ad(db, db_job.id, event["category"], ad_data)
            
            # Send to frontend
            await websocket.send_json(event)
            
        crud.update_job_status(db, db_job.id, "completed")
    except WebSocketDisconnect:
        crud.update_job_status(db, db_job.id, "cancelled")
    except Exception as e:
        crud.update_job_status(db, db_job.id, "failed")
        await websocket.send_json({"type": "error", "data": str(e)})
        
    await websocket.close()


@router.get("/history/latest")
def get_latest_history(db: Session = Depends(get_db)):
    """Fetch the latest scrape job to restore state on refresh."""
    job = crud.get_latest_job(db)
    if not job:
        return {"job_id": None}
    return job